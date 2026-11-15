import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { createWorkspace } from '../src/domain/workspace.js';
import { applyContent } from '../src/domain/content.js';
const output = path.resolve('test-results'); mkdirSync(output, { recursive: true });
const executablePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser = await chromium.launch({ headless: true, ...(existsSync(executablePath) ? { executablePath } : {}) });
const base = process.argv[2] || process.env.DEMO_URL || 'http://127.0.0.1:5173';
const results = [];
async function check(name, fn, seed) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1080 }, reducedMotion: 'reduce', acceptDownloads: true });
  const page = await context.newPage(), errors = []; page.on('pageerror', e => errors.push(e.message));
  if (seed) await context.addInitScript(value => { if (!localStorage.getItem('seeded')) { localStorage.setItem('eduflow.workspace.v3', JSON.stringify(value)); localStorage.setItem('seeded', 'yes'); } }, seed);
  await context.tracing.start({ screenshots: true, snapshots: true });
  try { await page.goto(base); await visible(page.getByRole('heading', { name: 'Good morning, Youssef' })); await fn(page, context); assert.deepEqual(errors, []); results.push(name); console.log(`PASS ${name}`); }
  catch (error) { await page.screenshot({ path: path.join(output, `failure-${results.length}.png`), fullPage: true }); await context.tracing.stop({ path: path.join(output, `failure-${results.length}.zip`) }); console.error(errors); throw error; }
  finally { await context.close(); }
}
const visible = locator => locator.waitFor({ state: 'visible', timeout: 10000 });
const nav = async (page, route) => { await page.evaluate(hash => { location.hash = hash; }, route); };
const readState = page => page.evaluate(() => JSON.parse(localStorage.getItem('eduflow.workspace.v3')));
async function saved(page) { await visible(page.getByText('Saved locally in this demo.', { exact: true }).first()); }
try {
  await check('dashboard image, grouped nav and filtered financial metric', async page => {
    await page.getByRole('img', { name: 'Teacher preparing a lesson in a blue and cream studio', exact: true }).evaluate(img => img.decode());
    await page.screenshot({ path: path.join(output, 'workspace-desktop.png'), fullPage: true });
    await page.getByRole('link', { name: /Outstanding balance/ }).click();
    await visible(page.getByRole('heading', { name: 'Charges & collections', exact: true })); assert.equal(await page.getByLabel('Balance filter').inputValue(), 'due');
  });
  await check('student create, multi enrollment, duplicate codes and CSV', async page => {
    await nav(page, 'students'); await page.getByRole('button', { name: 'Add student', exact: true }).click(); const dialog = page.getByRole('dialog');
    await dialog.getByLabel('Student code').fill('TEST-1'); await dialog.getByLabel('English name').fill('=1+1'); await dialog.getByLabel('Arabic name').fill('يوسف Test'); await dialog.getByRole('button', { name: 'Save', exact: true }).click(); await dialog.waitFor({ state: 'hidden' });
    await page.getByLabel('Search name, code or phone').fill('TEST-1'); const row = page.getByRole('row').filter({ hasText: 'TEST-1' }); await visible(row); await row.getByRole('button', { name: 'Enroll', exact: true }).click(); await dialog.getByRole('button', { name: 'Add enrollment' }).click(); await saved(page); await dialog.getByLabel('Additional group').selectOption('group-2'); await dialog.getByRole('button', { name: 'Add enrollment' }).click(); await page.keyboard.press('Escape'); assert.equal((await readState(page)).enrollments.filter(e => e.studentId === 'student-' || e.studentId === (undefined)).length, 0);
    const student = (await readState(page)).students.find(s => s.code === 'TEST-1'); assert.equal((await readState(page)).enrollments.filter(e => e.studentId === student.id).length, 2);
    const download = page.waitForEvent('download'); await page.getByRole('button', { name: 'CSV', exact: true }).click(); await (await download).saveAs(path.join(output, 'students-safe.csv'));
    await page.getByRole('button', { name: 'Add student', exact: true }).click(); await dialog.getByLabel('Student code').fill('test-1'); await dialog.getByLabel('English name').fill('Duplicate'); await dialog.getByLabel('Arabic name').fill('مكرر'); await dialog.getByRole('button', { name: 'Save', exact: true }).click(); await visible(dialog.getByRole('alert')); assert.equal(await dialog.getByLabel('English name').inputValue(), 'Duplicate'); await page.keyboard.press('Escape');
  });
  await check('session attendance, correction, duplicate and second session same day', async page => {
    await nav(page, 'attendance'); await page.getByLabel('Find student or code').fill('EF-1001'); const row = page.getByRole('row').filter({ hasText: 'EF-1001' }); await row.getByRole('button', { name: 'Record', exact: true }).click(); await saved(page); await row.getByLabel('Correction reason').fill('duplicate attempt'); await row.getByRole('button', { name: 'Correct', exact: true }).click(); await visible(row.getByRole('alert')); assert.equal((await readState(page)).attendance.length, 1);
    await row.getByLabel('Attendance state').selectOption('late'); await row.getByLabel('Correction reason').fill('Arrival corrected'); await row.getByRole('button', { name: 'Correct', exact: true }).click(); await saved(page); assert.equal((await readState(page)).attendance[0].history.length, 1);
    await page.getByRole('button', { name: 'Add session', exact: true }).click(); const dialog = page.getByRole('dialog'); await dialog.getByLabel('Session title').fill('Evening revision'); await dialog.getByRole('button', { name: 'Save', exact: true }).click(); await dialog.waitFor({ state: 'hidden' }); const s = (await readState(page)).sessions.at(-1); await page.getByLabel('Session', { exact: true }).selectOption(s.id); await row.getByRole('button', { name: 'Record', exact: true }).click(); await saved(page); assert.equal((await readState(page)).attendance.length, 2); await page.reload(); assert.equal((await readState(page)).attendance.length, 2);
  });
  await check('failed payment retains entries; retry and double-click commit only once; refund audit', async page => {
    await page.getByRole('button', { name: 'Settings', exact: true }).click(); await page.getByRole('button', { name: 'Simulate next save failure' }).click(); await page.keyboard.press('Escape');
    await nav(page, 'payments'); await page.getByRole('row').filter({ hasText: 'Omar Ahmed' }).getByRole('button', { name: 'Record payment', exact: true }).click(); const dialog = page.getByRole('dialog'); await dialog.getByLabel('Payment amount').fill('300.25'); await dialog.getByLabel('Payment reference').fill('RETRY-1'); await dialog.getByRole('button', { name: 'Record payment', exact: true }).click(); await visible(dialog.getByRole('alert')); assert.equal(await dialog.getByLabel('Payment amount').inputValue(), '300.25'); assert.equal(await dialog.getByLabel('Payment reference').inputValue(), 'RETRY-1');
    await dialog.getByRole('button', { name: 'Record payment', exact: true }).evaluate(button => { button.click(); button.click(); }); await dialog.waitFor({ state: 'hidden' }); let s = await readState(page); assert.equal(s.payments.filter(p => p.reference === 'RETRY-1').length, 1); const allocated = s.allocations.find(a => a.paymentId === s.payments.find(p => p.reference === 'RETRY-1').id); assert.equal(allocated.amountMinor, 30025);
    await page.getByLabel('Rows per page').last().selectOption('50');
    await page.getByRole('row').filter({ hasText: 'RETRY-1' }).getByRole('button', { name: 'Refund / void' }).click(); const alert = page.getByRole('alertdialog'); await alert.getByLabel('Refund · EGP').fill('100'); await alert.getByLabel('Reason · required').fill('Partial return'); await alert.getByRole('button', { name: 'Confirm adjustment' }).click(); await alert.waitFor({ state: 'hidden' }); s = await readState(page); assert.equal(s.adjustments[0].amountMinor, 10000); assert.equal(s.payments.find(p => p.reference === 'RETRY-1').amountMinor, 30025);
  });
  await check('role-specific navigation, default dashboards and forbidden deep links', async page => {
    await nav(page, 'attendance'); await page.getByRole('button', { name: 'Add session', exact: true }).click(); const futureDialog = page.getByRole('dialog'); await futureDialog.getByLabel('Session title').fill('Future teacher lesson'); await futureDialog.getByLabel('Date · Africa/Cairo').fill('2099-01-01'); await futureDialog.getByRole('button', { name: 'Save', exact: true }).click(); await futureDialog.waitFor({ state: 'hidden' });
    await page.getByLabel('Role preview', { exact: true }).selectOption('teacher'); await visible(page.getByRole('heading', { name: 'Today & upcoming sessions', exact: true })); await visible(page.getByRole('link').filter({ hasText: 'Future teacher lesson' }));
    await page.getByLabel('Role preview', { exact: true }).selectOption('teacher'); await visible(page.getByRole('heading', { name: 'More room for teaching.' })); assert.equal(await page.getByRole('navigation').getByRole('link', { name: 'Charges & collections' }).count(), 0); await nav(page, 'payments'); await visible(page.getByRole('heading', { name: 'This page is unavailable for this role' })); await nav(page, 'students'); assert.equal(await page.getByRole('button', { name: 'Add student', exact: true }).count(), 0);
    await page.getByLabel('Role preview', { exact: true }).selectOption('secretary'); await visible(page.getByRole('heading', { name: 'A well-organized day starts here.' })); await nav(page, 'studio'); await visible(page.getByRole('heading', { name: 'This page is unavailable for this role' }));
  });
  await check('PDF validation, failed processing status and no invented progress', async page => {
    await nav(page, 'materials'); const file = page.getByLabel('Choose PDF', { exact: true }); await file.setInputFiles({ name: 'fake.pdf', mimeType: 'application/pdf', buffer: Buffer.from('NOT PDF') }); await visible(page.getByText('The file does not have a valid PDF header.', { exact: true }));
    await page.getByRole('button', { name: 'Settings', exact: true }).click(); await page.getByRole('button', { name: 'Simulate next save failure' }).click(); await page.keyboard.press('Escape');
    await file.setInputFiles({ name: 'notes.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\n%%EOF') });
    const retry = page.getByRole('button', { name: 'Retry metadata registration', exact: true }); await visible(retry);
    assert.equal((await readState(page)).materials.filter(m => m.title[0] === 'notes.pdf').length, 0);
    await retry.click(); await visible(page.getByRole('heading', { name: 'notes.pdf' }));
    assert.equal((await readState(page)).materials.filter(m => m.title[0] === 'notes.pdf').length, 1);
    assert.equal((await readState(page)).materials[0].status, 'failed'); assert.equal(await page.getByRole('progressbar').count(), 0);
  });
  await check('unsupported generation fails explicitly; editing resets review; student/key exports stay separate', async page => {
    await nav(page, 'studio'); await page.getByLabel('Question count').fill('50'); await page.getByRole('button', { name: 'Generate draft · demo' }).click(); await visible(page.getByRole('alert').filter({ hasText: 'Not enough demo questions' })); await page.getByLabel('Question count').fill('3'); await page.getByRole('button', { name: 'Generate draft · demo' }).click(); await visible(page.getByRole('button', { name: 'Mark teacher-reviewed', exact: true }));
    assert.equal(await page.getByRole('button', { name: 'Word · student', exact: true }).isDisabled(), true); await page.getByRole('button', { name: 'Mark teacher-reviewed', exact: true }).click(); await saved(page); await page.getByLabel('Variant', { exact: true }).selectOption('C');
    const studentPopup = page.waitForEvent('popup'); await page.getByRole('button', { name: 'Print / save PDF · student', exact: true }).click(); const student = await studentPopup; await visible(student.getByRole('heading', { name: /Student copy/ })); assert.equal(await student.getByText(/Answer:|Newton’s second law:/).count(), 0); await student.screenshot({ path: path.join(output, 'student-print.png'), fullPage: true }); await student.close();
    const keyPopup = page.waitForEvent('popup'); await page.getByRole('button', { name: 'Print / save PDF · answer key', exact: true }).click(); const key = await keyPopup; await visible(key.getByRole('heading', { name: /Answer key/ })); assert.equal(await key.getByText(/Answer:/).count(), 3); await key.close();
    for (const [name, filename] of [['Word · student', 'student-en.docx'], ['Word · answer key', 'key-en.docx'], ['PowerPoint · student', 'student-en.pptx']]) { const download = page.waitForEvent('download'); await page.getByRole('button', { name, exact: true }).click(); await (await download).saveAs(path.join(output, filename)); }
    await page.getByLabel('Question text', { exact: true }).first().fill('Teacher edited question'); await page.getByRole('button', { name: 'Save edits as draft' }).click(); await saved(page); assert.equal((await readState(page)).drafts[0].status, 'draft'); assert.equal(await page.getByRole('button', { name: 'Word · student', exact: true }).isDisabled(), true);
  });
  await check('automation event dedupe, editable review and explicit non-delivery', async page => {
    await nav(page, 'attendance'); await page.getByLabel('Find student or code').fill('EF-1001'); const row = page.getByRole('row').filter({ hasText: 'EF-1001' }); await row.getByLabel('Attendance state').selectOption('absent'); await row.getByRole('button', { name: 'Record', exact: true }).click(); await saved(page);
    await nav(page, 'automations'); await page.getByRole('switch').first().click(); await page.getByRole('button', { name: 'Run once · demo' }).first().click(); await visible(page.getByRole('button', { name: 'Mark reviewed', exact: true })); const textbox = page.getByLabel('Message · English and Arabic stored separately'); await textbox.fill('Please follow up with the center. Edited.'); await page.getByRole('button', { name: 'Save edit', exact: true }).click(); await page.getByRole('button', { name: 'Mark reviewed', exact: true }).click(); await page.getByRole('button', { name: 'Approve draft', exact: true }).click(); await visible(page.getByText('Approved · not delivered', { exact: true })); await page.getByRole('button', { name: 'Run once · demo' }).first().click(); await visible(page.getByText(/already produced follow-up/)); const s = await readState(page); assert.equal(s.automationRuns.length, 1); assert.equal(s.drafts[0].delivery, 'unavailable');
  });
  await check('reports show definitions, no-data rate and evidence boundaries', async page => { await nav(page, 'analytics'); await visible(page.getByRole('heading', { name: 'Learning evidence' })); assert.equal((await page.getByText('—', { exact: true }).count()) > 0, true); await page.screenshot({ path: path.join(output, 'reports.png'), fullPage: true }); });
  await check('Arabic RTL, 320/390 mobile all routes, dialog keyboard and Arabic exports', async page => {
    await page.getByRole('button', { name: 'Switch to Arabic' }).click(); assert.equal(await page.locator('html').getAttribute('dir'), 'rtl');
    for (const width of [390, 320]) { await page.setViewportSize({ width, height: 844 }); for (const route of ['overview', 'students', 'attendance', 'payments', 'materials', 'studio', 'automations', 'analytics']) { await nav(page, route); await visible(page.getByRole('main').getByRole('heading', { level: 1 })); assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `${route}/${width} overflow`); } }
    await nav(page, 'students'); await page.getByRole('button', { name: 'إضافة طالب', exact: true }).focus(); await page.keyboard.press('Enter'); const dialog = page.getByRole('dialog'); await visible(dialog); await page.keyboard.press('Tab'); assert.equal(await page.evaluate(() => Boolean(document.activeElement.closest('[role="dialog"]'))), true);
    await dialog.getByLabel('كود الطالب').fill('AR-CHECK'); await dialog.getByRole('button', { name: 'حفظ', exact: true }).click(); await visible(dialog.getByRole('alert').filter({ hasText: 'راجع البيانات المطلوبة.' })); assert.equal(await dialog.getByLabel('كود الطالب').inputValue(), 'AR-CHECK');
    await page.keyboard.press('Escape'); await dialog.waitFor({ state: 'hidden' }); assert.equal(await page.getByRole('button', { name: 'إضافة طالب', exact: true }).evaluate(e => e === document.activeElement), true);
    await page.getByRole('button', { name: 'فتح القائمة' }).click(); await visible(page.getByRole('dialog')); await page.keyboard.press('Escape');
    await nav(page, 'studio'); await page.getByRole('button', { name: 'تجهيز مسودة · تجريبي' }).click(); await page.getByRole('button', { name: 'تأكيد مراجعة المدرّس', exact: true }).click(); await visible(page.getByText('تم الحفظ محلياً في الديمو.', { exact: true }).first());
    for (const [name, filename] of [['Word · الطالب', 'student-ar.docx'], ['PowerPoint · الطالب', 'student-ar.pptx']]) { const download = page.waitForEvent('download'); await page.getByRole('button', { name, exact: true }).click(); await (await download).saveAs(path.join(output, filename)); }
    const popup = page.waitForEvent('popup'); await page.getByRole('button', { name: 'طباعة / حفظ PDF · الطالب' }).click(); const print = await popup; assert.equal(await print.locator('html').getAttribute('dir'), 'rtl'); await print.screenshot({ path: path.join(output, 'student-ar-print.png'), fullPage: true }); await print.close(); await nav(page, 'overview'); await page.setViewportSize({ width: 390, height: 844 }); await page.screenshot({ path: path.join(output, 'workspace-ar-mobile.png'), fullPage: true });
  });
} finally { await browser.close(); }
console.log(`\n${results.length} workflow checks passed.`);
