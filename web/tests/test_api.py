"""API contract and real saved-model integration tests."""
import sys
import unittest
import json
import threading
import tomllib
import subprocess
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class ApiTests(unittest.TestCase):
    def test_runtime_without_scientific_packages(self):
        root = Path(__file__).resolve().parents[1]
        script = '''
import importlib.abc
import sys
class BlockScientific(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'numpy', 'scipy', 'sklearn', 'joblib'}:
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, BlockScientific())
from api.analyze import analyze_payload
result = analyze_payload({'text': 'urgent account verify password at https://example.invalid'})
assert result['label'] == 'phishing'
assert result['influential_terms']
'''
        result = subprocess.run([sys.executable, "-c", script], cwd=root, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deployment_runtime_declares_model_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        configuration = tomllib.loads((root / "pyproject.toml").read_text())
        self.assertEqual(configuration["project"]["dependencies"], ["nltk==3.9.2"])

    def test_api_exists(self):
        self.assertTrue((Path(__file__).resolve().parents[1] / "api/analyze.py").exists())

    def test_invalid_payloads(self):
        from api.analyze import analyze_payload
        for payload in [None, [], {}, {"text": 12}, {"text": "  "}, {"text": "x" * 12001}]:
            with self.subTest(payload=str(payload)[:40]), self.assertRaises(ValueError):
                analyze_payload(payload)

    def test_saved_model_prediction_and_explanation(self):
        from api.analyze import analyze_payload
        result = analyze_payload({"text": "Urgent: your account will be disabled. Verify your password at https://example.invalid/login"})
        self.assertEqual(result["label"], "phishing")
        self.assertGreaterEqual(result["phishing_probability"], 0.5)
        self.assertIn("uncalibrated", result["probability_note"].lower())
        self.assertTrue(result["influential_terms"])
        self.assertIn("urltoken", result["tokens"])

    def test_benign_example(self):
        from api.analyze import analyze_payload
        result = analyze_payload({"text": "Reminder: our project review is tomorrow at 10 AM. The agenda is in the shared calendar."})
        self.assertEqual(result["label"], "benign")

    def test_unknown_vocabulary_is_explicit(self):
        from api.analyze import analyze_payload
        result = analyze_payload({"text": "zzzzqqqqvvvv"})
        self.assertEqual(result["matched_features"], 0)
        self.assertTrue(result["limited_evidence"])

    def test_matches_original_inference(self):
        from api.analyze import analyze_payload, get_model
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "phishing-message-detection/src"))
        from phishdetect.inference import predict_message
        from phishdetect.inference import load_model
        model = load_model(Path(__file__).resolve().parents[2] / "phishing-message-detection/artifacts/phishing_detector.joblib")
        samples = [
            "Do not share your password. We are meeting tomorrow.",
            "URGENT urgent urgent account verify password now https://example.invalid",
            "Hi team, agenda for tomorrow's meeting is attached.",
            "zzzzqqqqvvvv", "a ! 1234", "not no never NOT",
            "<script>alert('x')</script> please verify your account",
            "Résumé café 東京 account access", "password " * 500,
            "", "payment invoice refund claim prize bank security update",
        ]
        samples += [f"{word} {word} team tomorrow click https://example.invalid" for word in ["verify", "invoice", "account", "password", "urgent", "meeting", "project", "not", "disabled", "security"]]
        for text in samples:
            if not text:
                continue
            with self.subTest(text=text[:60]):
                original = predict_message(model, text, top_k=8)
                actual = analyze_payload({"text": text})
                self.assertEqual(actual["label"], original["label"])
                self.assertAlmostEqual(actual["phishing_probability"], original["phishing_probability"], places=12)
                self.assertEqual([x["term"] for x in actual["influential_terms"]], [x["term"] for x in original["influential_terms"]])
                for a, b in zip(actual["influential_terms"], original["influential_terms"]):
                    self.assertAlmostEqual(a["contribution"], b["contribution"], places=12)

    def test_token_response_is_bounded(self):
        from api.analyze import analyze_payload
        result = analyze_payload({"text": "meeting " * 500})
        self.assertEqual(len(result["tokens"]), 160)
        self.assertTrue(result["tokens_truncated"])


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api.analyze import handler
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, data, content_type="application/json"):
        connection = HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request("POST", "/api/analyze", data, {"Content-Type": content_type})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), json.loads(response.read())
        connection.close()
        return result

    def test_bad_json(self):
        status, _, body = self.post(b"{")
        self.assertEqual(status, 400)
        self.assertIn("valid JSON", body["error"])

    def test_content_type(self):
        self.assertEqual(self.post(b"hello", "text/plain")[0], 415)

    def test_oversized_request(self):
        self.assertEqual(self.post(b"x" * 64001)[0], 413)

    def test_real_prediction_is_not_cached(self):
        status, headers, body = self.post(json.dumps({"text": "team meeting tomorrow"}).encode())
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn(body["label"], ["phishing", "benign"])


if __name__ == "__main__":
    unittest.main()
