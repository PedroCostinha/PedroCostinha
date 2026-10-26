/* Read-only QA of the README in GitHub's real branch UI, never the main profile.
 * Run: node scripts/review_arcade_github.cjs
 * Optional: ARCADE_BROWSER=firefox; ARCADE_REVIEW_REF=<published commit SHA>.
 * Uses the same optional Playwright dependency as preview_arcade.cjs.
 */
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium, firefox } = require('playwright');

async function main() {
  const engine = process.env.ARCADE_BROWSER || 'chrome';
  assert(['chrome', 'firefox'].includes(engine));
  const ref = process.env.ARCADE_REVIEW_REF || 'feat/arcade-barrel-quest';
  assert.notEqual(ref, 'main', 'This QA targets only the review branch or commit');
  const url = 'https://github.com/PedroCostinha/PedroCostinha/tree/'
    + ref.split('/').map(encodeURIComponent).join('/');
  const output = path.resolve(__dirname, '..', 'docs', 'arcade', 'github', engine);
  await fs.mkdir(output, { recursive: true });
  const browser = engine === 'firefox' ? await firefox.launch({ headless: true })
    : await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, colorScheme: 'dark', reducedMotion: 'no-preference' });
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    assert.equal(response.status(), 200);
    const article = page.locator('article').first();
    await article.waitFor({ state: 'visible' });
    await page.waitForLoadState('load');
    const details = article.locator('details').filter({ hasText: 'Ember-7' });
    assert.equal(await details.count(), 1);
    assert.equal(await details.evaluate(e => e.open), false, 'New preview is initially collapsed');
    const openWithKeyboard = async () => {
      const summary = details.locator('summary');
      if (await details.evaluate(e => e.open)) await summary.press('Space');
      await summary.press('Enter');
      await page.waitForTimeout(200);
      const enterOpened = await details.evaluate(e => e.open);
      if (!enterOpened) await summary.press('Space');
      await page.waitForFunction(() => document.querySelector('article details')?.open, null, { timeout: 5000 });
      return enterOpened ? 'Enter' : 'Space';
    };
    const disclosureKey = await openWithKeyboard();
    assert.equal(await details.evaluate(e => e.open), true, 'Disclosure opens with keyboard');
    const image = details.locator('img');
    await image.evaluate(img => img.decode());
    const animatedSrc = await image.evaluate(img => img.currentSrc);
    assert(animatedSrc.endsWith('/assets/arcade/barrel-quest.svg'));
    const codeQuest = article.locator('img[alt^="CODE QUEST V2"]');
    await codeQuest.evaluate(img => img.decode());
    assert(await codeQuest.evaluate(img => img.naturalWidth > 0));
    assert((await codeQuest.evaluate(img => img.currentSrc)).endsWith('/assets/code-quest/code-quest.svg'));
    assert.equal(await article.locator('source[media="(prefers-reduced-motion: reduce)"]').count(), 3);
    assert.equal(await details.getByRole('link', { name: 'Prévia estática e acessível' }).count(), 1);
    await article.locator('img').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())));
    await page.evaluate(() => document.fonts.ready);
    await article.screenshot({ path: path.join(output, 'desktop-readme.png') });
    const before = await image.screenshot();
    await page.waitForTimeout(800);
    assert(!before.equals(await image.screenshot()), 'GitHub branch image animates');

    await page.emulateMedia({ reducedMotion: 'reduce' });
    // A live preference change must select the static source without needing
    // a second GitHub document navigation or losing the open disclosure.
    await page.waitForFunction(() => document.querySelector('article details img')?.currentSrc
      .endsWith('/assets/arcade/barrel-quest-static.svg'), null, { timeout: 15000 });
    const disclosureRemainedOpen = await details.evaluate(e => e.open);
    assert(disclosureRemainedOpen);
    await image.evaluate(img => img.decode());
    const staticSrc = await image.evaluate(img => img.currentSrc);
    assert(staticSrc.endsWith('/assets/arcade/barrel-quest-static.svg'));
    await codeQuest.evaluate(img => img.decode());
    assert((await codeQuest.evaluate(img => img.currentSrc)).endsWith('/assets/code-quest/code-quest-static.svg'));
    await article.locator('img').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    assert.equal(await image.evaluate(img => img.currentSrc), staticSrc, 'Static source remains selected');
    assert.deepEqual(await image.evaluate(img => [img.naturalWidth, img.naturalHeight]), [1200, 650]);
    await details.screenshot({ path: path.join(output, 'desktop-reduced-motion.png') });
    await page.setViewportSize({ width: 390, height: 844 });
    // The profile banner selects a different image after this resize. Wait
    // for its decode before measuring or capturing the lower README section.
    await article.locator('img').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())));
    const mobile = await image.boundingBox();
    assert(mobile.width <= 390);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await details.scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(output, 'mobile-reduced-motion.png') });
    const control = await browser.newPage();
    await control.setContent('<details><summary>Barrel Quest</summary>Controle local</details>');
    await control.locator('summary').press('Enter');
    const localEnterOpened = await control.locator('details').evaluate(e => e.open);
    await control.close();
    const result = { engine, version: await browser.version(), url: page.url(), ref,
      testedAt: new Date().toISOString(), httpStatus: response.status(), animatedSrc, staticSrc,
      disclosureKey, disclosureRemainedOpen, localEnterOpened,
      checks: ['real GitHub branch README', 'initially collapsed', 'keyboard disclosure', 'CODE QUEST image decoded',
        'picture sources preserved', 'animated image changes', 'static source decoded and selected', 'reduced motion for both games', '390px no overflow'],
      limitation: 'This is a branch preview, not the profile published from main; no Safari or screen reader execution.' };
    await fs.writeFile(path.join(output, 'qa.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result, null, 2));
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
