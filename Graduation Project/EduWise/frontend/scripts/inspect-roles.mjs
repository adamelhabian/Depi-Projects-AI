import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { existsSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const distDir = resolve('dist');
const outputDir = resolve('test-results/role-audit');
mkdirSync(outputDir, { recursive: true });

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
};

const server = createServer(async (req, res) => {
  try {
    let pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (pathname === '/' || pathname === '') pathname = '/index.html';
    const filePath = resolve(distDir, '.' + pathname);
    if (!filePath.startsWith(distDir)) { res.writeHead(403).end(); return; }
    const data = await readFile(filePath);
    res.setHeader('Content-Type', mime[extname(filePath)] || 'application/octet-stream');
    res.end(data);
  } catch {
    res.writeHead(404).end();
  }
});

await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const baseUrl = `http://127.0.0.1:${port}`;
console.log(`Auditing roles at ${baseUrl}...`);

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

const roles = ['teacher', 'secretary', 'admin'];
const langs = ['ar', 'en'];

for (const lang of langs) {
  for (const role of roles) {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 850 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const consoleErrors = [];
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
    page.on('pageerror', err => consoleErrors.push(err.message));

    await page.goto(`${baseUrl}#overview`);
    await page.waitForLoadState('networkidle');

    // Set language
    const currentDir = await page.evaluate(() => document.documentElement.dir || 'rtl');
    const isAr = lang === 'ar';
    if ((isAr && currentDir !== 'rtl') || (!isAr && currentDir === 'rtl')) {
      await page.locator('.language-button').click();
      await page.waitForTimeout(100);
    }

    // Switch role via toolbar select
    await page.locator('.demo-toolbar select').selectOption(role);
    await page.waitForTimeout(200);

    const hero = page.locator('.hero-banner.compact-hero');
    await hero.waitFor({ state: 'visible' });
    const heroBox = await hero.boundingBox();
    assert(heroBox, 'Hero banner must exist');

    const button = page.locator('.hero-actions .btn');
    await button.waitFor({ state: 'visible' });
    const btnBox = await button.boundingBox();
    assert(btnBox, 'Hero button must exist');

    console.log(`[${role.toUpperCase()} - ${lang.toUpperCase()}] Hero height: ${heroBox.height}px (btn bottom: ${btnBox.y + btnBox.height} vs hero bottom: ${heroBox.y + heroBox.height})`);

    // Verify button is strictly inside hero banner with breathing room
    assert(btnBox.y + btnBox.height <= heroBox.y + heroBox.height - 4,
      `[${role} - ${lang}] Button is clipped! btnBottom (${btnBox.y + btnBox.height}) > heroBottom (${heroBox.y + heroBox.height})`);
    
    // Verify hero height is <= 160px
    assert(heroBox.height <= 160, `[${role} - ${lang}] Hero height ${heroBox.height}px must be <= 160px`);

    // Check directional arrow flip in RTL
    if (lang === 'ar') {
      const arrowTransform = await page.evaluate(() => {
        const arrow = document.querySelector('.hero-actions .btn .directional');
        return arrow ? window.getComputedStyle(arrow).transform : 'none';
      });
      assert(arrowTransform.includes('matrix(-1') || arrowTransform.includes('-1'),
        `[${role} - ${lang}] Directional arrow must be flipped in RTL, got: ${arrowTransform}`);
    }

    // Screenshot overview
    await page.screenshot({
      path: resolve(outputDir, `${role}-${lang}-overview.png`),
      fullPage: false,
    });

    assert.equal(consoleErrors.length, 0, `[${role} - ${lang}] Console errors: ${consoleErrors.join(', ')}`);
    await context.close();
  }
}

console.log('ALL ROLES PASSED HERO & OVERVIEW AUDIT!');
await browser.close();
server.close();
process.exit(0);
