"""Bounded JSON endpoint using the original saved NLP classifier."""
from functools import lru_cache
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MAX_CHARS = 12_000
MAX_BYTES = 64_000


@lru_cache(maxsize=1)
def get_model():
    import nltk
    nltk.data.path.insert(0, str(ROOT / "nltk_data"))
    # Fail closed rather than use the original module's offline fallback.
    from nltk.corpus import stopwords, wordnet
    wordnet.ensure_loaded()
    stopwords.words("english")
    from model_runtime import load_weights
    return load_weights(ROOT / "bundle/model.json")


def analyze_payload(payload: object) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        raise ValueError("Send a JSON object with a text field containing a message.")
    text = payload["text"].strip()
    if not text:
        raise ValueError("Paste a message before analyzing it.")
    if len(text) > MAX_CHARS:
        raise ValueError("Keep the message under 12,000 characters.")
    model = get_model()
    from bundle.preprocessing import nltk_preprocess
    from model_runtime import predict_weights
    processed = nltk_preprocess(text)
    result = predict_weights(model, processed, top_k=8)
    tokens = processed.split()
    result.update({
        "tokens": tokens[:160],
        "token_count": len(tokens),
        "tokens_truncated": len(tokens) > 160,
        "limited_evidence": result["matched_features"] < 3,
        "model": "NLTK + TF-IDF + logistic regression",
    })
    return result


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Do not log user-supplied message text or request bodies.
        return

    def respond(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            get_model()
            self.respond(200, {"status": "ready", "model": "nltk_preprocessed", "version": "1.0.0"})
        except Exception as exc:
            print(f"Model initialization failed: {type(exc).__name__}", file=sys.stderr)
            self.respond(503, {"error": "The model is temporarily unavailable. Please try again shortly."})

    def do_POST(self):
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return self.respond(415, {"error": "Use application/json for the request."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.respond(400, {"error": "Invalid request length."})
        if length <= 0:
            return self.respond(400, {"error": "Paste a message before analyzing it."})
        if length > MAX_BYTES:
            return self.respond(413, {"error": "Keep the message under 12,000 characters."})
        try:
            payload = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeError):
            return self.respond(400, {"error": "The request must contain valid JSON."})
        try:
            result = analyze_payload(payload)
        except ValueError as exc:
            return self.respond(400, {"error": str(exc)})
        except Exception as exc:
            print(f"Inference failed: {type(exc).__name__}", file=sys.stderr)
            return self.respond(503, {"error": "The model is temporarily unavailable. Please try again shortly."})
        self.respond(200, result)
