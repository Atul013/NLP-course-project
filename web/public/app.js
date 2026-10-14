'use strict';

const $ = (id) => document.getElementById(id);
const message = $('message');
const form = $('analyze-form');
const resultPanel = $('result-panel');
const analyzeButton = $('analyze-button');
const clearButton = $('clear-button');
const examples = {
  urgent: 'Subject: Urgent account verification required\n\nYour account will be disabled within 24 hours. Verify your password immediately at https://example.invalid/login to avoid losing access.',
  everyday: 'Subject: Project review reminder\n\nReminder: our project review is tomorrow at 10 AM. The agenda is in the shared calendar. Please bring your progress notes. See you there!',
  ambiguous: 'Subject: A new sign-in to your account\n\nWe noticed a sign-in from a new device. If this was not you, open the app directly and review your recent activity. Do not share your password or verification code.'
};
let request = null;
let generation = 0;

function selectTab(name, focus = false) {
  for (const tab of ['overview', 'tokens']) {
    const selected = tab === name;
    $(`${tab}-tab`).setAttribute('aria-selected', String(selected));
    $(`${tab}-tab`).tabIndex = selected ? 0 : -1;
    $(`${tab}-view`).hidden = !selected;
  }
  if (focus) $(`${name}-tab`).focus();
}

function setBusy(busy) {
  resultPanel.setAttribute('aria-busy', String(busy));
  resultPanel.classList.toggle('loading', busy);
  analyzeButton.disabled = busy;
  analyzeButton.querySelector('span').textContent = busy ? 'Looking closer…' : 'Analyze message';
}

function resetResult() {
  resultPanel.classList.remove('phishing', 'benign');
  $('lens-value').hidden = true;
  $('empty-eye').style.display = '';
  $('lens-progress').style.strokeDashoffset = '502.655';
  $('result-title').textContent = 'A fresh pair of eyes.';
  $('result-description').textContent = 'Add a message to reveal its language signals.';
  $('result-indicator').textContent = 'Ready when you are';
  $('result-details').hidden = true;
  $('influential-terms').replaceChildren();
  const empty = document.createElement('p');
  empty.className = 'token-empty';
  empty.textContent = 'Analyze a message to explore its processed tokens.';
  $('token-list').replaceChildren(empty);
  $('token-summary').textContent = '';
}

function invalidate() {
  generation++;
  if (request) request.abort();
  request = null;
  setBusy(false);
  resetResult();
  $('error-message').hidden = true;
  $('character-count').textContent = `${message.value.length.toLocaleString()} / 12,000`;
  clearButton.disabled = !message.value.length;
}

function renderResult(result) {
  const phishing = result.label === 'phishing';
  const probability = Math.round(result.phishing_probability * 100);
  resultPanel.classList.add(phishing ? 'phishing' : 'benign');
  $('empty-eye').style.display = 'none';
  $('lens-value').hidden = false;
  $('probability-value').replaceChildren(document.createTextNode(String(probability)));
  const percent = document.createElement('span');
  percent.textContent = '%';
  $('probability-value').append(percent);
  $('lens-progress').style.strokeDashoffset = String(502.655 * (1 - result.phishing_probability));
  $('result-indicator').textContent = 'Analysis complete';
  $('result-title').textContent = result.limited_evidence ? 'Too little familiar language.' : phishing ? 'Leans toward phishing.' : 'Leans toward benign.';
  $('result-description').textContent = result.limited_evidence
    ? `The model matched only ${result.matched_features} known feature${result.matched_features === 1 ? '' : 's'}. Its probability has little supporting evidence; try a fuller English message.`
    : phishing ? 'The language resembles phishing examples in the training set. Verify the request through a trusted channel.' : 'The language resembles benign examples in the training set. This does not verify the sender or establish safety.';
  const terms = $('influential-terms');
  terms.replaceChildren();
  const maxContribution = Math.max(...result.influential_terms.map(term => Math.abs(term.contribution)), 0.001);
  for (const term of result.influential_terms) {
    const row = document.createElement('div');
    row.className = `term-row ${term.direction}`;
    const name = document.createElement('span');
    name.className = 'term-name';
    name.textContent = term.term;
    const track = document.createElement('span');
    track.className = 'term-track';
    track.setAttribute('aria-hidden', 'true');
    const fill = document.createElement('span');
    fill.className = 'term-fill';
    fill.style.width = `${Math.max(2, Math.abs(term.contribution) / maxContribution * 100)}%`;
    track.append(fill);
    const direction = document.createElement('span');
    direction.className = 'term-direction';
    direction.textContent = term.direction === 'phishing' ? '↑ Phishing' : '↓ Benign';
    row.title = `Weighted contribution: ${term.contribution.toFixed(4)} toward ${term.direction}`;
    row.append(name, track, direction);
    terms.append(row);
  }
  if (!result.influential_terms.length) {
    const empty = document.createElement('p');
    empty.className = 'token-empty';
    empty.textContent = 'No known model features were found in this message.';
    terms.append(empty);
  }
  $('result-details').hidden = false;
  const tokens = $('token-list');
  tokens.replaceChildren();
  for (const token of result.tokens) {
    const chip = document.createElement('span');
    chip.className = 'token';
    chip.textContent = token;
    tokens.append(chip);
  }
  if (!result.tokens.length) {
    const empty = document.createElement('p');
    empty.className = 'token-empty';
    empty.textContent = 'No tokens remain after preprocessing.';
    tokens.append(empty);
  }
  $('token-summary').textContent = `${result.token_count} processed tokens · ${result.matched_features} matched model features${result.tokens_truncated ? ' · Showing the first 160 tokens' : ''}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (analyzeButton.disabled) return;
  invalidate();
  const text = message.value.trim();
  if (!text) {
    $('error-message').textContent = 'Paste a message or choose an example to begin.';
    $('error-message').hidden = false;
    message.focus();
    return;
  }
  const version = generation;
  const controller = new AbortController();
  request = controller;
  let timedOut = false;
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 65000);
  setBusy(true);
  selectTab('overview');
  $('result-title').textContent = 'Looking a little closer…';
  $('result-description').textContent = 'The first analysis may take a moment while the model wakes up.';
  $('result-indicator').textContent = 'Analyzing language';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text}), signal: controller.signal
    });
    const result = await response.json();
    if (version !== generation) return;
    if (!response.ok) throw new Error(result.error || 'Analysis is unavailable. Try again shortly.');
    renderResult(result);
  } catch (error) {
    if (version !== generation) return;
    resetResult();
    $('error-message').textContent = timedOut ? 'The model took too long to respond. Please try again.' : error.name === 'SyntaxError' || error instanceof TypeError ? 'Could not reach the model. Check your connection and try again.' : error.message;
    $('error-message').hidden = false;
    $('result-indicator').textContent = 'Analysis interrupted';
  } finally {
    clearTimeout(timeout);
    if (version === generation) {
      request = null;
      setBusy(false);
    }
  }
});

message.addEventListener('input', invalidate);
message.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    form.requestSubmit();
  }
});
clearButton.addEventListener('click', () => {
  message.value = '';
  invalidate();
  selectTab('overview');
  message.focus();
});
document.querySelectorAll('[data-example]').forEach(button => {
  button.addEventListener('click', () => {
    message.value = examples[button.dataset.example];
    invalidate();
    selectTab('overview');
    message.focus({preventScroll: true});
    if (window.innerWidth < 621) form.scrollIntoView({behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
  });
});
for (const name of ['overview', 'tokens']) {
  const tab = $(`${name}-tab`);
  tab.addEventListener('click', () => selectTab(name));
  tab.addEventListener('keydown', (event) => {
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      selectTab(event.key === 'Home' ? 'overview' : event.key === 'End' ? 'tokens' : name === 'overview' ? 'tokens' : 'overview', true);
    }
  });
}
