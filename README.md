# NLP Course Project

**Phish Lens: explainable phishing-message detection using NLP**, with the original text-preprocessing assignment preserved alongside it.

**[Open the live app](https://phish-lens-topaz.vercel.app)** · **[Download v1.0.0](https://github.com/Atul013/NLP-course-project/releases/tag/v1.0.0)** · **[Read the project report](phishing-message-detection/report/Phishing_Message_Detection_Report.pdf)**

**Atul** · B.Tech CSE (Artificial Intelligence), Semester 7
Adi Shankara Institute of Engineering & Technology

---

## Phish Lens

Paste an English email or message to explore a trained classifier's prediction, uncalibrated phishing probability, influential words, and processed tokens. The responsive web interface includes examples, keyboard controls, and clear loading and error states.

![Phish Lens message analysis interface](docs/screenshots/phish-lens-desktop.png)

The project compares raw-text and NLTK-preprocessed TF-IDF features with logistic regression. NLTK handles tokenization, selective stopword removal, URL/email placeholders, and WordNet lemmatization. Negation is preserved.

| Pipeline | Validation F1 | Test precision | Test recall | Test F1 |
|---|---:|---:|---:|---:|
| Raw text | 0.9744 | 0.9524 | 1.0000 | 0.9756 |
| NLTK preprocessed | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

These recorded results come from a **200-message synthetic educational dataset**, split into 120 training, 40 validation, and 40 test messages. The perfect synthetic test score does not establish real-world reliability. Probabilities are uncalibrated; the model does not inspect senders, attachments, headers, or URL reputation.

The Vercel API uses the saved model's exported vocabulary, IDF values, coefficients, and intercept with the original NLTK preprocessing. Compact inference matches the original pipeline's probabilities and term contributions to 12 decimal places across 20 varied verification inputs. No retraining or paid AI API is involved.

### Run the web app

Use Python 3.13. From the repository root in PowerShell:

```powershell
python -m venv web/.venv
web/.venv/Scripts/python -m pip install -r web/requirements-dev.txt
web/.venv/Scripts/python web/export_model.py
web/.venv/Scripts/python web/prepare.py
web/.venv/Scripts/python web/dev.py
```

Open **http://127.0.0.1:4180**. See [web setup and deployment](web/README.md) for browser checks and Vercel deployment, or [model reproduction](phishing-message-detection/README.md) for training and the original Streamlit demo.

### Verification

```powershell
web/.venv/Scripts/python -m unittest discover -s web/tests -v
```

13 API/runtime tests cover validation, model parity, bounded responses, and the lightweight runtime. The browser suite verifies real phishing/benign inference, tokens, keyboard controls, reset, safe text rendering, API failure, cancellation, and responsive layouts down to 320 px. [Deployment receipt](web/deployment.json).

Messages are sent to the server for analysis. The application does not persist message text or fetch embedded links. This is an educational prototype; verify suspicious requests independently through a trusted channel.

## Repository guide

| Path | Contents |
|---|---|
| [web/](web/) | Phish Lens frontend, compact API, export tools, tests, and deployment setup |
| [phishing-message-detection/](phishing-message-detection/) | Training pipeline, saved model, metrics, dataset provenance, course notebook, and Streamlit app |
| [Project report](phishing-message-detection/report/Phishing_Message_Detection_Report.pdf) | Course report and [editable source](phishing-message-detection/report/Phishing_Message_Detection_Report.md) |
| [Releases](https://github.com/Atul013/NLP-course-project/releases) | Versioned source bundle, reports, model, and evaluation artifacts |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

## Original assignment: text preprocessing

The original notebook and submission report remain available below.

The assignment asks for a self-introduction paragraph covering *Name, Place, Schooling, Family,
Current status, Achievements, Hobbies, Interests, Strengths and Weaknesses*, and for a full text
preprocessing pipeline applied to it.

The raw paragraph here is written deliberately as **noisy, real-world text** — HTML tags, HTML
entities, a URL, an email address, emoji, contractions, digits, irregular casing and inconsistent
whitespace. A clean paragraph would make most preprocessing steps invisible; noisy text makes the
effect of every stage measurable.

## Pipeline

| # | Stage | Purpose |
|---|-------|---------|
| 1 | Noise removal (HTML, URL, email, emoji) | Strip non-linguistic markup |
| 2 | Contraction expansion | `I'm` → `I am` |
| 3 | Case folding | Collapse `Python`/`python` to one token |
| 4 | Number handling | Remove digits / normalise |
| 5 | Punctuation removal | Drop non-semantic symbols |
| 6 | Whitespace normalisation | Single-space, trimmed |
| 7 | Sentence tokenisation | Split into sentences |
| 8 | Word tokenisation | Split into tokens |
| 9 | Stopword removal (negation preserved) | Drop low-information words |
| 10 | Stemming — Porter / Snowball / Lancaster | Crude suffix stripping, compared |
| 11 | POS tagging | Grammatical category per token |
| 12 | POS-aware lemmatisation | Dictionary-correct base forms |
| 13 | Named Entity Recognition | Extract people, places, organisations |
| 14 | Frequency distribution & N-grams | Corpus statistics |
| 15 | Bag of Words & TF-IDF | Numeric feature representation |

## Results

| Stage | Tokens | Unique tokens |
|-------|--------|---------------|
| Raw text | 291 | 202 |
| Tokenised | 280 | 182 |
| Stopwords removed | 158 | 143 |
| Lemmatised (POS-aware) | 158 | 140 |

**45.7% token reduction**, vocabulary reduced from 202 to 140 unique terms.

## Notes worth reading

1. **Ordering is not arbitrary.** Contractions must be expanded before punctuation is stripped, or
   `didn't` becomes the junk token `didnt`. URLs must be removed before punctuation, or one link
   explodes into a dozen fragments. NER must run before lowercasing, because capitalisation is one
   of the strongest entity features — so the pipeline branches a case-preserved copy of the text.
2. **Naive lemmatisation is a silent failure.** `WordNetLemmatizer` defaults to `pos='n'`, so verbs
   pass through unchanged (`studying` stays `studying`) and nothing raises an error. Mapping Penn
   Treebank tags to WordNet tags first is what makes it work — the notebook shows both side by side.
3. **Default stopword lists need editing.** NLTK's list removes `not`, `no` and `nor`, which inverts
   meaning. They are explicitly retained here.
4. **Stemmers are compared, not assumed.** Lancaster over-stems (`atul` → `at`, `science` → `sci`);
   Porter is conservative but still produces non-words. Lemmatisation wins when output must stay
   human-readable.

## Run it

### Phish Lens web app

The phishing detector now has a dedicated web interface: **[Open Phish Lens](https://phish-lens-topaz.vercel.app)**.
It uses the existing saved classifier and shows predictions, influential terms, and processed tokens.
See [web/README.md](web/README.md) for local setup, checks, and deployment details.

### Google Colab
Open `NLP_Assignment1_Text_Preprocessing.ipynb` in Colab, uncomment the `!pip install` line in the
setup cell, and run all cells.

### Locally
```bash
pip install -r requirements.txt
jupyter notebook NLP_Assignment1_Text_Preprocessing.ipynb
```

NLTK corpora (`punkt`, `stopwords`, `wordnet`, `averaged_perceptron_tagger`, `maxent_ne_chunker`,
`words`) download automatically in the setup cell.

## Files

| File | Description |
|------|-------------|
| `NLP_Assignment1_Text_Preprocessing.ipynb` | The executed notebook, all outputs saved |
| `NLP_Assignment1_Report.docx` | Submission report — code, outputs, repo link |
| `requirements.txt` | Pinned dependencies |
