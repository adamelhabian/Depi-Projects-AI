import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { existsSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const distDir = resolve('dist');
const outputDir = resolve('test-results/verify-improvements');
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
console.log(`Targeting test server at ${baseUrl}`);

const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({
  headless: true,
  ...(existsSync(executablePath) ? { executablePath } : {}),
});

try {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'ar-EG',
  });
  const page = await context.newPage();

  console.log('--- 1. Testing Overview Layout Reordering & Compact Hero ---');
  await page.goto(`${baseUrl}/#overview`);
  await page.waitForSelector('.hero-banner.compact-hero');
  const heroBox = await page.locator('.hero-banner.compact-hero').boundingBox();
  console.log(`Compact hero banner height: ${heroBox.height}px (must be <= 160px)`);
  assert(heroBox.height <= 160, 'Hero banner must be compact (<= 160px)');

  const statsBox = await page.locator('.stats-grid.overview-stats').boundingBox();
  console.log(`Stats grid top offset: ${statsBox.y}px (must be visible well above 600px fold)`);
  assert(statsBox.y < 450, 'Operational stats must appear above the fold');
  await page.screenshot({ path: `${outputDir}/01-overview-compact.png` });

  console.log('--- 2. Testing Date Range Validation in Analytics ---');
  await page.goto(`${baseUrl}/#analytics`);
  await page.waitForSelector('.panel');

  const fromInput = page.locator('input[type="date"]').first();
  const toInput = page.locator('input[type="date"]').nth(1);

  // Set invalid range: from > to
  await fromInput.fill('2026-10-25');
  await toInput.fill('2026-10-20');

  const alertError = page.locator('p[role="alert"].form-error').first();
  await alertError.waitFor({ state: 'visible', timeout: 5000 });
  const errorMsg = await alertError.textContent();
  console.log(`Analytics date error shown: "${errorMsg}"`);
  assert(errorMsg.includes('تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له') || errorMsg.includes('Start date must be on or before end date.'), 'Must show exact date range error');

  // Verify false tables or empty state are suppressed
  const hasNoRecords = await page.locator('.empty-state').count();
  assert.equal(hasNoRecords, 0, 'Must NOT show misleading "No records" empty state for invalid date range');
  await page.screenshot({ path: `${outputDir}/02-analytics-invalid-date.png` });

  // Correct dates to single-day range
  await fromInput.fill('2026-10-23');
  await toInput.fill('2026-10-23');
  await page.waitForSelector('.report-stats');
  const alertCountAfter = await page.locator('p[role="alert"].form-error').count();
  assert.equal(alertCountAfter, 0, 'Error should disappear after correction');
  console.log('Single day range (2026-10-23 to 2026-10-23) displays valid sessions and reports.');
  await page.screenshot({ path: `${outputDir}/03-analytics-single-day.png` });

  console.log('--- 3. Testing Payments Date Range & Receipt Localization ---');
  await page.goto(`${baseUrl}/#payments`);
  await page.waitForSelector('.ledger-panel');

  // Test Payments Date Filter Invalid Range
  const payFrom = page.locator('.ledger-panel input[type="date"]').first();
  const payTo = page.locator('.ledger-panel input[type="date"]').nth(1);
  await payFrom.fill('2026-10-25');
  await payTo.fill('2026-10-20');
  const payAlert = page.locator('.ledger-panel p[role="alert"].form-error').first();
  await payAlert.waitFor({ state: 'visible', timeout: 5000 });
  const payMsg = await payAlert.textContent();
  console.log(`Payments date error shown: "${payMsg}"`);
  assert(payMsg.includes('تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له') || payMsg.includes('Start date must be on or before end date.'));

  // Reset to All Dates
  await page.locator('button', { hasText: /كل التواريخ|All dates/ }).click();
  await page.waitForSelector('.ledger-panel .data-table');

  // Open Receipt Modal
  await page.locator('button', { hasText: /عرض الإيصال|View receipt/ }).first().click();
  await page.waitForSelector('.receipt-document');
  const receiptText = await page.locator('.receipt-document').textContent();
  console.log('Receipt content preview:', receiptText.slice(0, 200).replace(/\s+/g, ' '));

  assert(receiptText.includes('نقدي') || receiptText.includes('Cash'), 'Payment method must be localized in receipt');
  assert(!receiptText.includes('user-admin'), 'Internal raw employee ID user-admin must not appear in receipt user-facing text');
  assert(receiptText.includes('يوسف محمد') || receiptText.includes('Youssef Mohamed'), 'Employee name must be resolved');
  await page.screenshot({ path: `${outputDir}/04-receipt-modal.png` });

  // Close receipt
  await page.keyboard.press('Escape');

  console.log('--- 4. Testing Table Action Buttons & Archive Styling ---');
  await page.goto(`${baseUrl}/#students`);
  await page.waitForSelector('.data-table');

  const actionBtn = page.locator('.row-actions .btn').first();
  const btnFontSize = await actionBtn.evaluate(el => window.getComputedStyle(el).fontSize);
  const btnHeight = await actionBtn.evaluate(el => el.getBoundingClientRect().height);
  console.log(`Action button font-size: ${btnFontSize}, height: ${btnHeight}px`);
  const sizeNum = parseFloat(btnFontSize);
  assert(sizeNum >= 13, `Button font size must be at least 13px (got ${btnFontSize})`);

  const archiveBtn = page.locator('.row-actions .btn-archive').first();
  const archiveCount = await archiveBtn.count();
  assert(archiveCount > 0, 'Archive button must have distinct .btn-archive class');
  await page.screenshot({ path: `${outputDir}/05-students-action-buttons.png` });

  console.log('--- 5. Testing Table Column Sorting (Actions has no sort) ---');
  // Check the table headers in Students table
  const actionsTh = page.locator('.data-table th.table-th-static');
  const actionsThCount = await actionsTh.count();
  console.log(`Non-sortable static headers count: ${actionsThCount}`);
  assert(actionsThCount > 0, 'Actions column must have static header without sort button or arrows');

  const sortButtons = page.locator('.data-table th .table-sort');
  const sortBtnTexts = await sortButtons.allTextContents();
  console.log('Sortable column headers:', sortBtnTexts.map(s => s.trim().split(/\s+/)[0]));
  for (const text of sortBtnTexts) {
    assert(!text.includes('إجراءات') && !text.includes('Actions'), 'Actions column must never contain a sort trigger');
  }

  console.log('--- 6. Testing Human-Readable Educational Grades ---');
  // First test in English
  await page.goto(`${baseUrl}/#students?studentId=student-1`);
  await page.waitForSelector('.profile-facts');
  const profileFactsEn = await page.locator('.profile-facts').textContent();
  console.log('Student facts (EN):', profileFactsEn.slice(0, 150).replace(/\s+/g, ' '));
  assert(profileFactsEn.includes('Grade 12'), 'Grade in English must display "Grade 12"');

  // Now switch to Arabic via localStorage or language toggle button
  await page.evaluate(() => {
    localStorage.setItem('eduflow.language.v1', JSON.stringify('ar'));
    window.dispatchEvent(new Event('storage'));
  });
  await page.reload();
  await page.waitForSelector('.profile-facts');
  const profileFactsAr = await page.locator('.profile-facts').textContent();
  console.log('Student facts (AR):', profileFactsAr.slice(0, 150).replace(/\s+/g, ' '));
  assert(profileFactsAr.includes('الصف الثالث الثانوي'), 'Grade in Arabic must display "الصف الثالث الثانوي"');
  await page.screenshot({ path: `${outputDir}/06-student-profile-grade-ar.png` });

  // Check Materials library grade labels in Arabic
  await page.goto(`${baseUrl}/#materials`);
  await page.waitForSelector('.material-record');
  const materialCardText = await page.locator('.material-record').first().textContent();
  console.log('Material record snippet (AR):', materialCardText.slice(0, 150).replace(/\s+/g, ' '));
  assert(materialCardText.includes('الثالث الثانوي'), 'Materials must display localized grade in Arabic');
  await page.screenshot({ path: `${outputDir}/07-materials-grade-ar.png` });

  // Test Analytics Date Error in Arabic
  await page.goto(`${baseUrl}/#analytics`);
  await page.waitForSelector('.panel');
  const arFrom = page.locator('input[type="date"]').first();
  const arTo = page.locator('input[type="date"]').nth(1);
  await arFrom.fill('2026-10-25');
  await arTo.fill('2026-10-20');
  const arAlert = page.locator('p[role="alert"].form-error').first();
  await arAlert.waitFor({ state: 'visible', timeout: 5000 });
  const arMsg = await arAlert.textContent();
  console.log(`Analytics date error in Arabic: "${arMsg}"`);
  assert(arMsg.includes('تاريخ البداية لازم يكون قبل تاريخ النهاية أو مساوي له'), 'Must show exact Arabic date error');
  await page.screenshot({ path: `${outputDir}/08-analytics-error-ar.png` });

  // Test Receipt Modal in Arabic
  await page.goto(`${baseUrl}/#payments`);
  await page.waitForSelector('.ledger-panel .data-table');
  await page.locator('button', { hasText: /عرض الإيصال/ }).first().click();
  await page.waitForSelector('.receipt-document');
  const arReceipt = await page.locator('.receipt-document').textContent();
  console.log('Arabic receipt preview snippet:', arReceipt.slice(0, 250).replace(/\s+/g, ' '));
  assert(arReceipt.includes('نقدي'), 'Payment method must be "نقدي"');
  assert(arReceipt.includes('يوسف محمد'), 'Employee name must be "يوسف محمد"');
  assert(!arReceipt.includes('user-admin'), 'user-admin must NOT appear in receipt');
  assert(arReceipt.includes('ج.م.'), 'Currency must be EGP / ج.م.');
  await page.screenshot({ path: `${outputDir}/09-receipt-modal-ar.png` });

  console.log('\n========================================');
  console.log('ALL 6 VERIFICATION CHECKS PASSED 100%!');
  console.log('========================================\n');
} finally {
  await browser.close();
  server.close();
}
