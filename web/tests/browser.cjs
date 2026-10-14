/* Run against the local server or BASE_URL=https://deployment npm run test:ui. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {})});
  const page = await browser.newPage({viewport: {width: 1440, height: 1100}, deviceScaleFactor: 1});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(process.env.BASE_URL || 'http://127.0.0.1:4180', {waitUntil: 'networkidle'});
  await page.locator('#analyze-button').click();
  await page.locator('#error-message').waitFor({state: 'visible'});
  assert.match(await page.locator('#error-message').innerText(), /Paste a message/);
  await page.locator('[data-example="urgent"]').click();
  assert.match(await page.locator('#message').inputValue(), /example.invalid/);
  await page.locator('#analyze-button').click();
  await page.locator('#result-panel.phishing').waitFor({timeout: 65000});
  assert.match(await page.locator('#result-title').innerText(), /phishing/);
  assert.ok(await page.locator('.term-row').count() > 0);
  assert.match(await page.locator('#probability-value').innerText(), /\d+%/);
  await page.locator('#tokens-tab').click();
  assert.ok(await page.locator('.token').count() > 0);
  assert.ok((await page.locator('#token-list').innerText()).includes('urltoken'));
  await page.locator('#tokens-tab').press('ArrowLeft');
  assert.equal(await page.locator('#overview-tab').getAttribute('aria-selected'), 'true');
  await page.locator('#message').fill('changed message');
  assert.equal(await page.locator('#result-details').isVisible(), false);
  await page.locator('[data-example="everyday"]').click();
  await page.locator('#message').press('Control+Enter');
  await page.locator('#result-panel.benign').waitFor({timeout: 65000});
  await page.locator('#clear-button').click();
  assert.equal(await page.locator('#message').inputValue(), '');
  assert.equal(await page.locator('#lens-value').isVisible(), false);
  await page.locator('#message').fill('<img src=x onerror="window.injected=true"> zzzzqqqqvvvv');
  await page.locator('#analyze-button').click();
  await page.locator('#result-indicator').filter({hasText: 'Analysis complete'}).waitFor({timeout: 65000});
  await page.locator('#tokens-tab').click();
  assert.equal(await page.evaluate(() => window.injected), undefined);
  assert.equal(await page.locator('#token-list img').count(), 0);
  await page.locator('[data-example="urgent"]').click();
  await page.locator('#analyze-button').click();
  await page.locator('#result-panel.phishing').waitFor({timeout: 65000});
  await page.locator('#model-notes details').evaluate(node => { node.open = true; });
  const out = path.join(__dirname, '../test-results');
  fs.mkdirSync(out, {recursive: true});
  await page.screenshot({path: path.join(out, 'desktop.png'), fullPage: true});
  for (const width of [390, 320, 768]) {
    await page.setViewportSize({width, height: 844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `No overflow at ${width}px`);
  }
  await page.setViewportSize({width: 390, height: 844});
  await page.screenshot({path: path.join(out, 'mobile.png'), fullPage: true});
  // Exercise failure and cancellation without relying on an outage.
  await page.route('**/api/analyze', route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: 'Test service unavailable.'})}));
  await page.locator('#analyze-button').click();
  await page.locator('#error-message').waitFor({state: 'visible'});
  assert.equal(await page.locator('#error-message').innerText(), 'Test service unavailable.');
  await page.unroute('**/api/analyze');
  let release;
  await page.route('**/api/analyze', async route => {
    await new Promise(resolve => { release = resolve; });
    await route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({label:'phishing', phishing_probability:0.9, influential_terms:[], tokens:[], token_count:0, matched_features:0, limited_evidence:true})}).catch(() => {});
  });
  await page.locator('#analyze-button').click();
  await page.waitForFunction(() => document.querySelector('#result-panel').getAttribute('aria-busy') === 'true');
  await page.locator('#clear-button').click();
  if (release) release();
  await page.waitForTimeout(300);
  assert.equal(await page.locator('#result-details').isVisible(), false);
  assert.equal(await page.locator('#message').inputValue(), '');
  assert.equal(await page.locator('#analyze-button').isEnabled(), true);
  assert.deepEqual(errors, []);
  console.log('PASS: real phishing/benign inference, tabs, keyboard, reset, safe rendering, responsive 320/390/768px, API errors, pending-request cancellation.');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
