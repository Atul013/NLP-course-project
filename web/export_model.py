"""Export the existing fitted linear pipeline without retraining it."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "phishing-message-detection"
sys.path.insert(0, str(SOURCE / "src"))


def export():
    import joblib
    model_path = SOURCE / "artifacts/phishing_detector.joblib"
    model = joblib.load(model_path)
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    expected = {
        "analyzer": "word", "token_pattern": r"(?u)\b\w\w+\b",
        "ngram_range": (1, 2), "norm": "l2", "use_idf": True,
        "sublinear_tf": True, "binary": False, "lowercase": False,
        "strip_accents": None, "tokenizer": None, "stop_words": None,
    }
    params = vectorizer.get_params()
    for key, value in expected.items():
        if params[key] != value:
            raise ValueError(f"Unsupported vectorizer setting: {key}")
    if list(classifier.classes_) != [0, 1]:
        raise ValueError("Expected binary benign/phishing classes")
    if params["preprocessor"].__name__ != "nltk_preprocess":
        raise ValueError("Expected the original NLTK preprocessor")
    payload = {
        "format": "phish-lens-linear-v1",
        "source_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "vocabulary": {key: int(value) for key, value in vectorizer.vocabulary_.items()},
        "idf": vectorizer.idf_.tolist(),
        "coefficients": classifier.coef_[0].tolist(),
        "intercept": float(classifier.intercept_[0]),
        "token_pattern": params["token_pattern"],
    }
    bundle = ROOT / "bundle"
    bundle.mkdir(exist_ok=True)
    (bundle / "model.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(SOURCE / "src/phishdetect/preprocessing.py", bundle / "preprocessing.py")
    print(f"Exported {len(payload['vocabulary'])} features from original model {payload['source_sha256'][:12]}")


if __name__ == "__main__":
    export()
