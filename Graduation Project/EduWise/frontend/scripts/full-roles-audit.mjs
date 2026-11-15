import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { existsSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const distDir = resolve('dist');
const outputDir = resolve('test-results/full-roles-audit');
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
console.log(`Starting comprehensive role audit across all pages at ${baseUrl}...`);

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

const roleRoutes = {
  admin: ['overview', 'students', 'students?studentId=student-1', 'attendance', 'payments', 'studio', 'materials', 'automations', 'analytics'],
  teacher: ['overview', 'students', 'students?studentId=student-1', 'attendance', 'studio', 'materials', 'automations', 'analytics'],
  secretary: ['overview', 'students', 'students?studentId=student-1', 'attendance', 'payments'],
};

for (const lang of ['ar', 'en']) {
  for (const [role, routes] of Object.entries(roleRoutes)) {
    console.log(`--- Testing [${role.toUpperCase()} - ${lang.toUpperCase()}] ---`);
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', err => consoleErrors.push(err.message));

    // Initial visit
    await page.goto(`${baseUrl}#overview`);
    await page.waitForLoadState('networkidle');

    // Set language
    const currentDir = await page.evaluate(() => document.documentElement.dir || 'rtl');
    const isAr = lang === 'ar';
    if ((isAr && currentDir !== 'rtl') || (!isAr && currentDir === 'rtl')) {
      await page.locator('.language-button').click();
      await page.waitForTimeout(100);
    }

    // Switch role
    await page.locator('.demo-toolbar select').selectOption(role);
    await page.waitForTimeout(150);

    for (const route of routes) {
      await page.goto(`${baseUrl}#${route}`);
      await page.waitForTimeout(150);

      // Verify no unexpected error panel displayed
      const errorPanel = page.locator('section.panel[role="alert"]');
      const hasError = await errorPanel.count();
      assert.equal(hasError, 0, `[${role} - ${lang}] Error alert found on #${route}`);

      // Verify page is not "unavailable"
      const unavailableHeading = page.locator('h1', { hasText: /This page is unavailable|الصفحة غير متاحة/ });
      const isUnavailable = await unavailableHeading.count();
      assert.equal(isUnavailable, 0, `[${role} - ${lang}] Page #${route} incorrectly blocked`);

      const cleanRouteName = route.replace(/[^a-zA-Z0-9]/g, '_');
      await page.screenshot({
        path: resolve(outputDir, `${role}-${lang}-${cleanRouteName}.png`),
      });
      console.log(`  ✓ Route #${route} rendered cleanly`);
    }

    assert.equal(consoleErrors.length, 0, `[${role} - ${lang}] Console errors: ${consoleErrors.join(', ')}`);
    await context.close();
  }
}

console.log('ALL ROUTES ACROSS ALL 3 ROLES AND BOTH LANGUAGES AUDITED 100% CLEAN!');
await browser.close();
server.close();
process.exit(0);
