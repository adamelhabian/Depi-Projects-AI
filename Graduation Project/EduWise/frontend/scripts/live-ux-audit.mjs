import { chromium } from 'playwright';
import { existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const liveUrl = process.argv[2] || 'https://eduflow-ai-brand.vercel.app';
const outputDir = resolve('test-results/live-audit');
mkdirSync(outputDir, { recursive: true });

console.log(`Starting automated UI/UX deep scan on ${liveUrl}...`);

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

const viewports = [
  { name: 'mobile-small', width: 360, height: 740 },
  { name: 'mobile-standard', width: 390, height: 844 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 }
];

const auditFindings = [];

for (const vp of viewports) {
  const context = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 1
  });
  const page = await context.newPage();

  for (const lang of ['ar', 'en']) {
    await page.goto(`${liveUrl}#overview`);
    await page.waitForLoadState('networkidle');

    // Language toggle check
    const isAr = lang === 'ar';
    const currentDir = await page.evaluate(() => document.documentElement.dir || 'rtl');
    if ((isAr && currentDir !== 'rtl') || (!isAr && currentDir === 'rtl')) {
      await page.locator('.language-button').click();
      await page.waitForTimeout(100);
    }

    // 1. Horizontal Scroll Check
    const hasHorizontalOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth || document.body.scrollWidth > window.innerWidth;
    });
    if (hasHorizontalOverflow) {
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      auditFindings.push({
        severity: 'HIGH',
        category: 'Responsive Layout',
        page: 'overview',
        viewport: vp.name,
        lang,
        issue: `Horizontal overflow detected: scrollWidth (${scrollWidth}px) exceeds viewport width (${vp.width}px).`
      });
    }

    // 2. Touch targets (< 44px on mobile)
    if (vp.width <= 768) {
      const smallTargets = await page.evaluate(() => {
        const interactive = Array.from(document.querySelectorAll('button, a.btn, input, select'));
        const tiny = [];
        for (const el of interactive) {
          if (el.offsetParent === null) continue; // hidden
          const rect = el.getBoundingClientRect();
          if ((rect.width > 0 && rect.width < 40) || (rect.height > 0 && rect.height < 36)) {
            tiny.push({
              tag: el.tagName,
              className: el.className,
              text: el.innerText.trim().slice(0, 20),
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            });
          }
        }
        return tiny;
      });
      if (smallTargets.length > 0) {
        auditFindings.push({
          severity: 'MEDIUM',
          category: 'Touch Ergonomics',
          page: 'overview',
          viewport: vp.name,
          lang,
          issue: `Found ${smallTargets.length} interactive elements with height < 36px or width < 40px`,
          details: smallTargets.slice(0, 5)
        });
      }
    }

    // 3. Text size readability (< 12px)
    const tinyTexts = await page.evaluate(() => {
      const elements = Array.from(document.querySelectorAll('p, span, small, label, h1, h2, h3, a, button, td, th'));
      const found = [];
      for (const el of elements) {
        if (el.offsetParent === null) continue;
        const fs = parseFloat(window.getComputedStyle(el).fontSize);
        if (fs < 11.5 && el.innerText.trim().length > 0) {
          found.push({
            tag: el.tagName,
            text: el.innerText.trim().slice(0, 25),
            fontSize: `${fs}px`,
            className: el.className
          });
        }
      }
      return found;
    });
    if (tinyTexts.length > 0) {
      auditFindings.push({
        severity: 'LOW',
        category: 'Typography & Readability',
        page: 'overview',
        viewport: vp.name,
        lang,
        issue: `Found text elements under 11.5px: ${tinyTexts.map(t => `${t.text} (${t.fontSize})`).join(', ')}`
      });
    }

    // 4. Modal inspection (Workspace settings)
    await page.locator('.topbar-actions .icon-button').first().click();
    await page.waitForTimeout(200);
    const modalVisible = await page.locator('[role="dialog"]').isVisible();
    if (modalVisible) {
      const modalBox = await page.locator('[role="dialog"]').boundingBox();
      if (modalBox && modalBox.width > vp.width) {
        auditFindings.push({
          severity: 'HIGH',
          category: 'Modal Usability',
          page: 'settings-modal',
          viewport: vp.name,
          lang,
          issue: `Settings modal width (${modalBox.width}px) exceeds screen width (${vp.width}px)`
        });
      }
      await page.keyboard.press('Escape');
      await page.waitForTimeout(100);
    }
  }

  await context.close();
}

console.log('AUDIT COMPLETED WITH FINDINGS:');
console.log(JSON.stringify(auditFindings, null, 2));

await browser.close();
