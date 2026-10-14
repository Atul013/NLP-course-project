# Changelog

## v1.0.0 - 2026-10-14

- Publish Phish Lens at https://phish-lens-topaz.vercel.app with a responsive message editor, probability visualization, influential terms, processed tokens, and sample messages.
- Preserve the saved NLTK/TF-IDF/logistic-regression model and the original Streamlit demo, training notebook, evaluation artifacts, and text-preprocessing coursework.
- Add a compact inference runtime with parity against the original pipeline over 20 varied inputs to 12 decimal places; checksum-verify required NLTK corpora.
- Add bounded API input, safe text rendering, keyboard controls, cancellation, error handling, 13 API/runtime tests, and live browser verification.
- Rename the repository to `NLP-course-project`; update project links, report, setup instructions, and submission checklist.
- Provide versioned source/runtime bundles, reports, saved model, and metrics through GitHub Releases.

The reported model metrics remain those from the original small synthetic dataset. This release does not add training data, retrain the model, or establish production security reliability.
