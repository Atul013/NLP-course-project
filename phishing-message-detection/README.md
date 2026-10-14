# Phishing Message Detection using NLP

A small, reproducible course project that compares raw-text TF-IDF with an
NLTK-preprocessed TF-IDF pipeline, both using logistic regression. The demo
classifies English email/message text as `phishing` or `benign`, shows the
model's **uncalibrated** phishing probability, and exposes influential terms.

**[Open Phish Lens](https://phish-lens-topaz.vercel.app)** for the deployed web interface.
The [web app guide](../web/README.md) explains local setup, model export, tests, and deployment.
[Versioned downloads and reports](https://github.com/Atul013/NLP-course-project/releases) are available in Releases.

> Educational prototype only. Do not use its output as a security decision or
> click/open message content based on this classifier.

## Verified result

Run on 6 October 2026 with Python 3.12, seed 42, and the pinned 200-row
synthetic educational dataset:

| Pipeline | Validation F1 | Test precision | Test recall | Test F1 |
|---|---:|---:|---:|---:|
| Raw text | 0.9744 | 0.9524 | 1.0000 | 0.9756 |
| NLTK preprocessed | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The perfect 40-message test score is **not evidence of production readiness**.
The corpus is tiny, balanced, curated, and synthetic; closely templated cues
make the task easier than real inbox traffic. See `artifacts/metrics.json`,
`artifacts/split_ids.json`, and the report for the auditable result.

## Dataset and safeguards

- Source: [Phishing and Benign Email Dataset](https://huggingface.co/datasets/Teddyha/phishing_benign_email_dataset)
- Upstream revision: `ce65d43`; local download is SHA-256 verified.
- License stated by the dataset card: MIT.
- True labels are used unchanged: 100 `phishing`, 100 `benign`. Spam/ham data
  is not renamed as phishing.
- Subject and body are joined; exact duplicate texts are removed **before** a
  fixed-seed, stratified 60/20/20 train/validation/test split.
- TF-IDF is inside each scikit-learn pipeline and is fitted only on training
  data. Validation chooses the pipeline; the test set is evaluated once.

The raw dataset is intentionally not copied into this repository. The pinned
download script records provenance and checks its checksum.

## NLTK requirement

The NLTK pipeline uses `TreebankWordTokenizer`, WordNet lemmatization,
selective English stopword filtering that retains negation, and explicit
URL/email placeholders. It remains importable offline, but a reproducible
training run installs the WordNet and stopwords corpora:

```bash
python -m nltk.downloader wordnet omw-1.4 stopwords
```

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m nltk.downloader wordnet omw-1.4 stopwords
python download_data.py
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python train.py
PYTHONPATH=src streamlit run app.py
```

Windows PowerShell uses `$env:PYTHONPATH = "src"` before the final three
commands. The demo opens locally and does not call a paid API.

## Contents

- `src/phishdetect/`: loading, preprocessing, modeling, and explanation code
- `train.py`: deduplicate, split, compare, evaluate, and save artifacts
- `app.py`: Streamlit demo
- `notebooks/phishing_detection.ipynb`: executable course notebook
- `tests/`: leakage/split, NLTK, and inference smoke tests
- `artifacts/`: model, split IDs, metrics, comparison CSV, errors, and figure
- `report/`: editable report and generated PDF
- `SUBMISSION_CHECKLIST.md`: human-only registration/upload steps

## Limitations

English only; synthetic and small source; no header/reputation/attachment
inspection; no temporal or external-corpus evaluation; probabilities are not
calibrated; linear term explanations are local coefficient contributions, not
causal explanations. Real phishing changes rapidly and benign security notices
can resemble attacks. Use a larger, independently reviewed real-world corpus
and cross-source testing before considering operational use.
