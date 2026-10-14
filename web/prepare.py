"""Prepare original model sources and build-time NLTK data. No training."""
from pathlib import Path
import hashlib
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "phishing-message-detection"
CHECKSUMS = {
    "wordnet": "cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59",
    "stopwords": "48c0e52d8b52546e827f53761fb30300c0ab94f70660d28bd65ba0a86270946b",
}


def prepare():
    bundle = ROOT / "bundle"
    if not (bundle / "model.json").exists() or not (bundle / "preprocessing.py").exists():
        raise RuntimeError("Run export_model.py locally before deployment")
    corpora = ROOT / "nltk_data/corpora"
    corpora.mkdir(parents=True, exist_ok=True)
    for name, checksum in CHECKSUMS.items():
        target = corpora / f"{name}.zip"
        if not target.exists():
            url = f"https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/{name}.zip"
            with urlopen(url, timeout=90) as response:
                data = response.read()
            target.write_bytes(data)
        if hashlib.sha256(target.read_bytes()).hexdigest() != checksum:
            raise RuntimeError(f"The {name} corpus checksum changed; review before deploying")
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise RuntimeError(f"Invalid {name} archive")
        print(f"Prepared {name}: {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    prepare()
