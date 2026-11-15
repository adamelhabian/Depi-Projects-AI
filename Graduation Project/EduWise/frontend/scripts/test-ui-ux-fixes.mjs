import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { existsSync } from 'node:fs';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const distDir = resolve('dist');

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
    if (!filePath.startsWith(distDir)) {
      res.writeHead(403).end();
      return;
    }
    const data = await readFile(filePath);
    res.setHeader('Content-Type', mime[extname(filePath)] || 'application/octet-stream');
    res.end(data);
  } catch {
    res.writeHead(404).end();
  }
});

await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const baseUrl = process.argv[2] || `http://127.0.0.1:${port}`;
console.log(`Verifying UI/UX improvements at ${baseUrl}...`);

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

try {
  // Test 1: Desktop verification (1440px)
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'ar-EG',
  });
  const page = await context.newPage();
  await page.goto(`${baseUrl}/#overview`);
  await page.waitForSelector('.hero-banner.compact-hero');

  // Check 1: Logo accessible name
  const logoAria = await page.getAttribute('.logo-link', 'aria-label');
  console.log(`Logo aria-label: "${logoAria}"`);
  assert(logoAria.includes('EduFlow AI'), 'Logo aria-label must include "EduFlow AI"');

  // Check 2: Breadcrumb divider
  const breadcrumbDivider = await page.$('.breadcrumb .breadcrumb-divider');
  assert(breadcrumbDivider, 'Breadcrumb must have .breadcrumb-divider span');
  console.log('Breadcrumb divider token verified.');

  // Check 3: Font sizes
  const statTopFontSize = await page.evaluate(() => {
    const el = document.querySelector('.stat-top');
    return window.getComputedStyle(el).fontSize;
  });
  console.log(`Stat top font size: ${statTopFontSize}`);
  assert(parseFloat(statTopFontSize) >= 12, 'Stat top font size must be >= 12px');

  const statParaFontSize = await page.evaluate(() => {
    const el = document.querySelector('.stat-card > p');
    return window.getComputedStyle(el).fontSize;
  });
  console.log(`Stat card paragraph font size: ${statParaFontSize}`);
  assert(parseFloat(statParaFontSize) >= 12, 'Stat card p font size must be >= 12px');

  // Check 4: Language button touch target
  const langBtnBox = await page.locator('.language-button').boundingBox();
  console.log(`Language button dimensions: ${langBtnBox.width}x${langBtnBox.height}px`);
  assert(langBtnBox.height >= 38, 'Language button height must be at least 38px');

  // Check 5: Skip link styling
  const skipLinkBg = await page.evaluate(() => {
    const el = document.querySelector('.skip-link');
    return window.getComputedStyle(el).backgroundColor;
  });
  console.log(`Skip link background color: ${skipLinkBg}`);

  // Test 2: Tablet Viewport (768px portrait)
  console.log('\n--- Testing Tablet Viewport (768px) ---');
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.waitForTimeout(200);

  const sidebarDisplay = await page.evaluate(() => {
    const sidebar = document.querySelector('.sidebar.desktop-sidebar');
    return window.getComputedStyle(sidebar).display;
  });
  const mobileMenuDisplay = await page.evaluate(() => {
    const btn = document.querySelector('.mobile-menu');
    return window.getComputedStyle(btn).display;
  });
  console.log(`At 768px: sidebar display = ${sidebarDisplay}, mobile menu display = ${mobileMenuDisplay}`);
  assert.equal(sidebarDisplay, 'none', 'At 768px, desktop sidebar must be hidden to prevent content compression');
  assert.notEqual(mobileMenuDisplay, 'none', 'At 768px, mobile menu button must be visible');

  // Test 3: Secretary Overview Financial Pulse
  console.log('\n--- Testing Secretary Role Overview ---');
  await page.selectOption('.demo-toolbar select', 'secretary');
  await page.waitForTimeout(300);

  const secretaryCard = await page.$('.secretary-pulse-card');
  assert(secretaryCard, 'Secretary role must display .secretary-pulse-card');
  const secretaryPulseText = await secretaryCard.innerText();
  console.log('Secretary pulse card snippet:', secretaryPulseText.split('\n')[0]);

  console.log('\n=============================================');
  console.log('ALL UI/UX FIXES VERIFIED SUCCESSFULLY ON BUILD!');
  console.log('=============================================');
} finally {
  await browser.close();
  server.close();
}
