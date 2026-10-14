# Phish Lens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify, and deploy the approved phishing detector web app.

**Architecture:** Static frontend in `web/public/`, Python Vercel endpoint in `web/api/analyze.py`, and fitted classifier weights exported by `web/export_model.py`. The compact runtime mirrors the original pipeline's TF-IDF and logistic inference; unchanged preprocessing and checksum-pinned NLTK data are bundled. Keep original project sources authoritative.

**Tech Stack:** HTML, CSS, JavaScript, Python, NLTK 3.9.2, scikit-learn 1.8.0, Vercel Functions.

**Spec:** `docs/superpowers/specs/2026-10-14-phish-lens-design.md`

## Global Constraints

- Reuse the saved classifier without retraining; preserve coursework.
- No paid AI API, message persistence, or link fetching.
- Explicitly label the probability uncalibrated and the dataset synthetic.
- Public deployment is authorized. No Git commit or push is necessary for deployment.

## Review Focus

- Empty, non-string, malformed, and oversized requests return clear client errors.
- Model/version or missing-corpus errors do not become fabricated predictions.
- Editing or clearing text invalidates old results and pending requests.
- User text and model terms render as text, never executable HTML or links.
- Mobile overflow, keyboard focus, reduced motion, and API failure remain usable.

### Task 1: Inference service

**Files:** `web/api/analyze.py`, `web/prepare.py`, `web/requirements.txt`, `web/vercel.json`, `web/tests/test_api.py`, `web/dev.py`.

**Interfaces:** `analyze_payload(payload: object) -> dict`, `handler` HTTP class at `/api/analyze`; response extends the original prediction with processed tokens and coverage.

- [x] Write request validation and real-model integration tests; run and confirm missing API failure.
- [x] Implement bounded JSON API, prepare bundle, pinned dependencies, and local dev server.
- [x] Install isolated dependencies and prepare corpora; run tests for valid, invalid, and low-coverage inputs.

### Task 2: Interactive frontend

**Files:** `web/public/index.html`, `web/public/style.css`, `web/public/app.js`.

**Interfaces:** `POST /api/analyze` with `{text: string}`; response uses original prediction fields.

- [x] Build approved responsive design, samples, loading, reset, error states, results, and model notes.
- [x] Verify JavaScript syntax, browser user flows, safe text rendering, mobile layout, and editing/reset cancellation.

### Task 3: Deployment and handoff

**Files:** `web/README.md`, root README link, deployment receipt.

- [x] Review the complete diff and run API checks.
- [x] Deploy the web directory to the connected Vercel account as `phish-lens`.
- [x] Inspect build result and test live page plus API. Record URL and limitations.

## Execution ledger

- Initial tree clean. Saved model was made with scikit-learn 1.8.0; host has 1.6.0. Use isolated pinned runtime rather than modifying global packages.
- Ruling: implement in the authorized workspace as additive files; no history rewrite or Git publication required.
- Vercel connector rejected the known scope; the authenticated local CLI created and deployed the new project in `atul013s-projects`.
- Ruling: the full scientific runtime exceeded Vercel's 225 MB function limit. Export the existing model weights and mirror its fixed sparse-vector math with standard Python; retain unchanged NLTK preprocessing. No retraining or heuristic substitutions. Parity verified over 20 inputs to 12 decimal places, including term order and contributions.
- First deployment failed live readiness because runtime metadata omitted dependencies; a regression check now pins the runtime dependency declaration. A clean lightweight build subsequently passed.
- Fresh code review found no critical/important findings. The minor corpus reproducibility concern was resolved with SHA-256 checks.
- Verification: 13 unittest cases passed; compact runtime also works with NumPy/SciPy/scikit-learn/joblib imports blocked. JavaScript syntax check passed.
- Public production browser verification passed: phishing/benign inference, terms, tokens, keyboard, reset, safe text rendering, 320/390/768 px layout, API failures, and cancellation. Production page and readiness endpoint returned HTTP 200; no-store, nosniff, and CSP confirmed.
- Final deployment: `dpl_CWjNK6MX3RAgZJhCf7NpaqRM1f8n`; canonical URL https://phish-lens-topaz.vercel.app .

- Repository renamed to `Atul013/NLP-course-project`; source links, About metadata, report, release notes, and README refreshed. Release deployment: `dpl_7mFD9PYudg2W3ZSruUvUcpn2uL1E`.
