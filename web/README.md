# Phish Lens

A responsive web interface for the existing phishing-message classifier.

**Production:** https://phish-lens-topaz.vercel.app

Paste an English message, inspect its uncalibrated phishing probability and local term contributions, or switch to the processed token view. Three examples, keyboard submission, loading/error handling, and reset are included. Editing text cancels any pending request and clears the previous prediction.

## Run locally

From the repository root, with Python 3.13:

```powershell
python -m venv web/.venv
web/.venv/Scripts/python -m pip install -r web/requirements-dev.txt
web/.venv/Scripts/python web/export_model.py
web/.venv/Scripts/python web/prepare.py
web/.venv/Scripts/python web/dev.py
```

Open http://127.0.0.1:4180. The first model load takes a few seconds.

`export_model.py` exports the original saved model's vocabulary, IDF values, logistic weights, and intercept into an ignored deployment bundle alongside the unchanged preprocessing module. `prepare.py` downloads the public WordNet and English stopwords corpora and verifies their SHA-256 hashes. No retraining takes place. Re-export after changing the original model or preprocessing files.

## Verify

```powershell
web/.venv/Scripts/python -m unittest discover -s web/tests -v
node --check web/public/app.js
cd web
npm install
npx playwright install chromium
npm run test:ui
```

The browser check needs the local server running. To check production:

```powershell
$env:BASE_URL = 'https://phish-lens-topaz.vercel.app'
npm run test:ui
```

The API tests exercise validation, parity against the original pipeline across 20 varied messages to 12 decimal places, synthetic phishing/benign samples, low-evidence input, token response limits, malformed JSON, content types, body size, and cache headers. Browser checks exercise real inference, token tabs, keyboard use, stale-result clearing, safe text rendering, 320/390/768 px layouts, errors, and request cancellation. Screenshots are written to ignored `test-results/`.

## Deploy

Run `export_model.py` and `prepare.py` locally first so the model weights and preprocessing module are present under `bundle/`, then:

```powershell
cd web
vercel deploy --prod --scope atul013s-projects
```

Vercel serves `public/` and runs `api/analyze.py` as a Python function. `pyproject.toml` and `requirements.txt` declare only NLTK; `requirements-dev.txt` adds scikit-learn and joblib for model export and parity tests. `.python-version` selects Python 3.13. The compact runtime computes the original sparse TF-IDF normalization and logistic probability directly from the exported weights, avoiding Vercel's scientific-stack bundle limit. The build downloads checksum-verified corpora and includes them with the model. The local virtual environment, test artifacts, and corpora are excluded from upload.

## Limits and privacy

The original model uses TF-IDF and logistic regression, trained on 120 messages from a synthetic 200-message educational dataset. A 1.00 F1 score on 40 synthetic test messages does not demonstrate real-world reliability. English only; probabilities are uncalibrated. Explanations show weighted feature contributions, not causal reasoning. Unknown vocabulary is explicitly flagged. No sender, URL reputation, header, or attachment inspection occurs.

Messages are sent over HTTPS to the model server. The application does not persist request bodies, log message contents, fetch embedded links, or use third-party AI services. Vercel processes requests and may retain platform request metadata. Google Fonts receives normal font requests. Never use a benign prediction as permission to open a link or attachment; verify independently through a trusted channel.

Original coursework and the Streamlit demo are preserved.
