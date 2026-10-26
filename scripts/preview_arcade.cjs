/* Optional visual QA: npm install --no-save playwright sharp (outside production).
 * Requires Chrome, or set ARCADE_BROWSER=firefox after playwright install firefox.
 * ARCADE_BROWSER_CHANNEL=msedge also selects an installed Chromium browser.
 * Run: node scripts/preview_arcade.cjs
 * Production SVG generation remains Python standard library only.
 */
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium, firefox } = require('playwright');
const sharp = require('sharp');

async function main() {
  const root = path.resolve(__dirname, '..');
  const assetDir = path.join(root, 'assets', 'arcade');
  const browserName = process.env.ARCADE_BROWSER || 'chrome';
  assert(['chrome', 'firefox'].includes(browserName), 'ARCADE_BROWSER must be chrome or firefox');
  const evidenceDir = path.join(root, 'docs', 'arcade', ...(browserName === 'firefox' ? ['firefox'] : []));
  await fs.mkdir(evidenceDir, { recursive: true });
  const animated = await fs.readFile(path.join(assetDir, 'barrel-quest.svg'), 'utf8');
  const staticSvg = await fs.readFile(path.join(assetDir, 'barrel-quest-static.svg'), 'utf8');
  const snapshot = JSON.parse(await fs.readFile(path.join(root, 'assets', 'code-quest', 'calendar.json'), 'utf8'));
  const readme = await fs.readFile(path.join(root, 'README.md'), 'utf8');
  const picture = readme.match(/<picture>\s*<source media="\(prefers-reduced-motion: reduce\)" srcset="assets\/arcade\/[\s\S]*?<\/picture>/)[0];
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    if (url.pathname === '/assets/arcade/barrel-quest.svg' || url.pathname === '/assets/arcade/barrel-quest-static.svg') {
      res.setHeader('Content-Type', 'image/svg+xml');
      res.end(url.pathname.includes('-static') ? staticSvg : animated);
    } else if (url.pathname === '/') {
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.end('<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">'
        + '<style>body{margin:0;background:#0d0d0f}img{display:block;width:100%;height:auto}</style>' + picture);
    } else { res.writeHead(404); res.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = browserName === 'firefox' ? await firefox.launch({ headless: true })
      : await chromium.launch({ headless: true, channel: process.env.ARCADE_BROWSER_CHANNEL || 'chrome' });
    const page = await browser.newPage({ viewport: { width: 1200, height: 650 }, reducedMotion: 'no-preference' });
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    const frames = [], observations = [];
    const checkpoints = [
      [0, 'INICIO / FADE'], [.55, 'EMBER-7 / PARADO'], [1.35, 'CAMINHADA'], [2.2, 'CORRIDA'],
      [3.84, 'SALTO / PISO 01'], [6.1, 'SUBIDA / ESCADA'], [15, 'SALTO / PISO 03'],
      [29.5, `CONCLUSAO / ${snapshot.total} PONTOS`], [31.5, 'REINICIO / OCULTO'], [32.25, 'NOVO CICLO']
    ];
    for (const [time, label] of checkpoints) {
      // Freeze CSS timelines at a deterministic time, only inside the QA page.
      const frozen = animated.replace('</svg>', `<style>*{animation-play-state:paused!important;animation-delay:-${time}s!important}</style></svg>`);
      await page.setContent('<style>html,body{margin:0;background:#0D0D0F}</style>' + frozen);
      const state = await page.evaluate(() => {
        const css = e => getComputedStyle(e);
        const effectiveOpacity = e => {
          let value = 1;
          for (; e; e = e.parentElement) {
            if (css(e).display === 'none') return 0;
            value *= Number(css(e).opacity);
          }
          return value;
        };
        const matrix = new DOMMatrix(css(document.querySelector('.runner')).transform);
        return { x: matrix.e, y: matrix.f,
          poses: [...document.querySelectorAll('.pose')].filter(e => Number(css(e).opacity) > .99).length,
          score: [...document.querySelectorAll('.scoreframe')].filter(e => Number(css(e).opacity) > .99).map(e => e.textContent),
          fade: Number(css(document.querySelector('.cinematic')).opacity),
          completionOpacity: effectiveOpacity(document.querySelector('.complete')) };
      });
      assert.equal(state.poses, 1, `Exactly one pose at ${time}s`);
      assert.equal(state.score.length, 1, `Exactly one score at ${time}s`);
      if (time === 0 || time === 32.25) { assert.equal(state.x, 160); assert.equal(state.score[0], '000000'); }
      if (time === 0 || time === 31.5) {
        assert(state.fade < .1, `Reset hidden at ${time}s`);
        assert(state.completionOpacity < .1, `Completion banner also fades at ${time}s`);
      }
      if (time === 6.1) { assert.equal(state.x, 760); assert(state.y > 465 && state.y < 550); }
      if (time === 15) { assert(Math.abs(state.x - 460) < .1); assert(state.y < 362); }
      if (time === 29.5) { assert.equal(state.score[0], String(snapshot.total).padStart(6, '0')); assert.equal(state.x, 760); }
      const png = await page.screenshot();
      if (time === 29.5 && browserName === 'chrome') await fs.writeFile(path.join(assetDir, 'preview.png'), png);
      observations.push({ time, ...state });
      const thumb = await sharp(png).resize(600, 325).png().toBuffer();
      const title = Buffer.from(`<svg width="600" height="30"><rect width="600" height="30" fill="#181219"/><text x="16" y="20" font-family="monospace" font-size="13" fill="#ECC5CD">${time.toFixed(2)}s / ${label}</text></svg>`);
      frames.push(await sharp({ create: { width: 600, height: 355, channels: 4, background: '#0D0D0F' } })
        .composite([{ input: title, top: 0, left: 0 }, { input: thumb, top: 30, left: 0 }]).png().toBuffer());
    }
    await sharp({ create: { width: 1200, height: Math.ceil(frames.length / 2) * 355, channels: 4, background: '#0D0D0F' } })
      .composite(frames.map((input, i) => ({ input, left: (i % 2) * 600, top: Math.floor(i / 2) * 355 })))
      .png().toFile(path.join(evidenceDir, 'frames.png'));

    // Fade masks both the final position and the start-of-loop reset.
    for (const time of [0, 31.5]) {
      await page.setContent(animated.replace('</svg>', `<style>*{animation-play-state:paused!important;animation-delay:-${time}s!important}</style></svg>`));
      const opacity = await page.locator('.cinematic').first().evaluate(e => Number(getComputedStyle(e).opacity));
      assert(opacity < .1, `Reset hidden at ${time}s`);
    }
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.setContent(animated);
    assert.equal(await page.evaluate(() => document.getAnimations().length), 0);
    assert.equal(await page.locator('.moving').first().evaluate(e => getComputedStyle(e).display), 'none');
    assert.equal(await page.locator('.still').first().evaluate(e => getComputedStyle(e).display), 'inline');
    const description = await page.locator('desc').textContent();
    assert(description.includes(`${snapshot.total} contribuições`));
    assert(description.includes('não representam novos commits'));
    await page.setContent('<style>html,body{margin:0}</style>' + staticSvg);
    assert.equal(await page.evaluate(() => document.getAnimations().length), 0);
    await page.getByRole('img', { name: /Barrel Quest/ }).count().then(count => assert.equal(count, 1));
    await page.screenshot({ path: path.join(evidenceDir, 'desktop-static.png') });

    const base = `http://127.0.0.1:${server.address().port}/`;
    await page.goto(base);
    await page.locator('img').evaluate(img => img.decode());
    assert((await page.locator('img').evaluate(img => img.currentSrc)).endsWith('barrel-quest-static.svg'));
    for (const width of [320, 390, 768, 1200]) {
      await page.setViewportSize({ width, height: 650 });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (width === 390) await page.locator('img').screenshot({ path: path.join(evidenceDir, 'mobile-static.png') });
    }
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.reload();
    await page.locator('img').evaluate(img => img.decode());
    assert((await page.locator('img').evaluate(img => img.currentSrc)).endsWith('barrel-quest.svg'));
    const movingA = await page.locator('img').screenshot();
    await page.waitForTimeout(800);
    const movingB = await page.locator('img').screenshot();
    assert(!movingA.equals(movingB), 'SVG also animates when embedded as an image');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.reload();
    await page.locator('img').evaluate(img => img.decode());
    const stillA = await page.locator('img').screenshot();
    await page.waitForTimeout(800);
    assert(stillA.equals(await page.locator('img').screenshot()), 'Static image remains unchanged over time');
    assert.equal(errors.length, 0);
    const result = { engine: browserName, browser: await browser.version(), frames: observations,
      assertions: 'poses, exact score, jump, climb, hidden reset and next cycle, reduced motion, accessible description, static SVG, picture selection, 320/390/768/1200px overflow, image animation and static stability',
      pageErrors: errors, outputDirectory: path.relative(root, evidenceDir).split(path.sep).join('/') };
    await fs.writeFile(path.join(evidenceDir, 'qa.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
