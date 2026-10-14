# Phish Lens

Approved in chat on 14 October 2026: polish the phishing detector into a standout web app and deploy it to Vercel.

Use a light lavender workspace, dark plum typography, a large message editor, and a lens-shaped result visualization. Show the existing model's prediction, uncalibrated phishing probability, and influential terms. Include phishing and benign samples, reset, mobile layouts, keyboard support, and concise methodology and limitations. Preserve the original coursework and Streamlit app.

Implementation choices: vanilla HTML/CSS/JavaScript with a same-origin Python API, packaged in `web/`. Reuse the saved scikit-learn pipeline without retraining. Export its fitted weights for compact deployment, with probability and contribution parity checked against the original pipeline. Bundle required NLTK corpora so inference does not silently change online. No paid AI API, no message persistence, no link fetching. The hosting provider processes submitted text; do not promise that text stays on-device.

Palette: lavender #f4f0fb, plum #30243e, purple #7251ae, paper #ffffff, green #326451, warning #a84d3f. Use a distinctive geometric sans heading and a readable system body. The lens is the memorable visual; surrounding controls stay quiet.

Deploy a new `phish-lens` project in the connected Vercel account. Verify live API inference and the public interface before reporting completion. Do not claim calibrated safety or production readiness from the synthetic dataset.
