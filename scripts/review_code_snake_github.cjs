// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PedroCostinha
// Read-only real GitHub QA. Never replaces GitHub markup or styles.
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium, firefox } = require('playwright');
const sharp = require('sharp');
const crypto = require('node:crypto');

async function main() {
  const ref = process.env.ARCADE_REVIEW_REF;
  assert(ref && ref !== 'main', 'Supply an immutable review commit');
  const engine = process.env.ARCADE_BROWSER || 'chrome';
  assert(['chrome', 'firefox'].includes(engine));
  const output = path.resolve(process.env.SNAKE_EVIDENCE_DIR || `docs/code-snake-final/github/${engine}`);
  await fs.mkdir(output, { recursive: true });
  const browser = engine === 'firefox' ? await firefox.launch({ headless: true })
    : await chromium.launch({ channel: 'chrome', headless: true });
  const views = [], errors = [], verifiedStaticAssets = new Map();
  const url = `https://github.com/PedroCostinha/PedroCostinha/tree/${ref}`;
  try {
    const page = await browser.newPage({ colorScheme: 'dark', reducedMotion: 'no-preference' });
    page.setDefaultTimeout(60000);
    page.on('pageerror', e => errors.push(String(e)));
    assert.equal((await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })).status(), 200);
    const article = page.locator('article').first();
    await article.waitFor();
    const barrel = article.locator('img[alt^="Barrel Quest:"]');
    const snake = article.locator('img[alt^="Code Snake:"]');
    const quest = article.locator('img[alt^="CODE QUEST V2"]');
    for (const width of [320, 390, 768, 1440]) {
      await page.setViewportSize({ width, height: 844 });
      await page.emulateMedia({ reducedMotion: 'no-preference' });
      await article.locator('img').evaluateAll(imgs => Promise.all(imgs.map(i => i.decode())));
      await page.evaluate(() => document.fonts.ready);
      // Let the authored opening fade finish before documenting the sprites.
      await page.waitForTimeout(2200);
      const images = [];
      for (const [name, locator] of [['barrel', barrel], ['snake', snake], ['quest', quest]]) {
        images.push(await locator.evaluate((i, name) => {
          const r = i.getBoundingClientRect();
          return { name, src: i.currentSrc, width: r.width, height: r.height, x: r.x, right: r.right,
            natural: [i.naturalWidth, i.naturalHeight], hiddenByDisclosure: !!i.closest('details:not([open])') };
        }, name));
      }
      assert(images.every(i => i.natural[0] && !i.hiddenByDisclosure && i.x >= 0 && i.right <= width));
      assert(images[0].src.endsWith('/barrel-quest.svg'));
      assert(images[1].src.endsWith(width <= 600 ? '/code-snake-mobile.svg' : '/code-snake.svg'));
      const dimensions = await article.evaluate(e => ({ width: e.clientWidth, scrollWidth: e.scrollWidth,
        pageWidth: document.documentElement.scrollWidth, viewport: innerWidth }));
      assert(dimensions.pageWidth <= width && dimensions.scrollWidth <= dimensions.width);
      if (process.env.EXPECT_STACKED === '1') {
        assert(images[0].width >= dimensions.width * .94, 'Barrel fills the README content width');
        assert(images[1].width >= dimensions.width * .94, 'Snake fills the README content width');
        assert.equal(await article.locator('table').count(), 0);
      }
      const clip = await article.evaluate(e => {
        const heading = [...e.querySelectorAll('h2')].find(h => h.textContent.includes('ARCADE COLLECTION'));
        const a = heading.getBoundingClientRect(), b = e.querySelector('details').getBoundingClientRect();
        return { x: Math.floor(e.getBoundingClientRect().x), y: Math.floor(a.y + scrollY),
          width: Math.floor(e.getBoundingClientRect().width), height: Math.ceil(b.bottom - a.y) };
      });
      await barrel.scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(output, `github-${width}-viewport.png`) });
      const motion = [];
      for (const [name, img] of [['barrel', barrel], ['snake', snake]]) {
        // Offscreen SVG images may defer their animation clock until painted.
        await img.scrollIntoViewIfNeeded(); await page.waitForTimeout(1200);
        const a = await img.screenshot(); await page.waitForTimeout(900);
        const b = await img.screenshot();
        await fs.writeFile(path.join(output, `github-${width}-${name}-motion-a.png`), a);
        await fs.writeFile(path.join(output, `github-${width}-${name}-motion-b.png`), b);
        assert(!a.equals(b), `${name} animates without interaction`);
        motion.push(name);
      }
      // Unstick GitHub's own README tabs before the document crop.
      await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(100);
      await page.screenshot({ path: path.join(output, `github-${width}-showcase.png`), clip, fullPage: true });
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.waitForFunction(() => [...document.querySelectorAll('article img')]
        .filter(i => /^(Barrel Quest:|Code Snake:|CODE QUEST V2)/.test(i.alt))
        .every(i => i.currentSrc.includes('-static')));
      await article.locator('img').evaluateAll(imgs => Promise.all(imgs.map(i => i.decode())));
      await page.waitForTimeout(800);
      const still = [];
      for (const [name, img] of [['barrel', barrel], ['snake', snake], ['quest', quest]]) {
        await img.evaluate(i => i.decode());
        // Settle the scroll and compositor before comparing a static crop.
        await img.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
        const a = await img.screenshot(); await page.waitForTimeout(650); const b = await img.screenshot();
        await fs.writeFile(path.join(output, `github-${width}-${name}-static.png`), a);
        await fs.writeFile(path.join(output, `github-${width}-${name}-static-b.png`), b);
        const aa = await sharp(a).ensureAlpha().raw().toBuffer(), bb = await sharp(b).ensureAlpha().raw().toBuffer();
        assert.equal(aa.length, bb.length);
        let changed = 0, maxDelta = 0, totalDelta = 0;
        for (let i = 0; i < aa.length; i++) { const d = Math.abs(aa[i] - bb[i]); if (d) changed++; maxDelta = Math.max(maxDelta, d); totalDelta += d; }
        const src = await img.evaluate(i => i.currentSrc);
        let svg = verifiedStaticAssets.get(src);
        if (!svg) {
          const response = await page.request.get(src);
          assert.equal(response.status(), 200);
          svg = await response.body();
          const relative = 'assets/' + src.split('/assets/')[1];
          const local = await fs.readFile(path.resolve(__dirname, '..', relative));
          assert(svg.equals(local), 'The selected static resource matches the reviewed SVG bytes');
          assert(!svg.toString().includes('@keyframes'), 'Selected static SVG has no keyframes');
          verifiedStaticAssets.set(src, svg);
        }
        if (name === 'snake') assert(src.endsWith(width <= 600 ? '/code-snake-static-mobile.svg' : '/code-snake-static.svg'));
        const sample = { name, src, exact: a.equals(b), changedChannels: changed, maxDelta,
          changedFraction: changed / aa.length, meanDelta: totalDelta / aa.length,
          sha256: crypto.createHash('sha256').update(svg).digest('hex') };
        await fs.writeFile(path.join(output, `github-${width}-${name}-static-comparison.json`), JSON.stringify(sample, null, 2));
        // Compare raster only after exact SVG-byte verification. Chrome can
        // quantize a few antialiased edge channels differently after scrolling.
        assert(maxDelta <= 32 && changed / aa.length <= .03 && sample.meanDelta <= .03,
          `Static pixels stable: ${JSON.stringify(sample)}`);
        still.push(sample);
      }
      views.push({ width, dimensions, images, motion, still });
      await fs.writeFile(path.join(output, 'results.json'), JSON.stringify({ ref, url, engine,
        version: browser.version(), complete: false, views, errors }, null, 2));
    }
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify({ ref, url, engine, version: browser.version(),
      testedAt: new Date().toISOString(), complete: true, views, errors, limitation: 'Branch README; Safari, physical mobile and screen reader pending.' }, null, 2));
    console.log(JSON.stringify({ engine, ref, views: views.map(v => ({ width: v.width, images: v.images })) }));
  } finally { await browser.close(); }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
