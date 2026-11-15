import { chromium } from 'playwright';
import { mkdir, copyFile, readdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { exportLogoAssets } from './export-logo-assets.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const brand = resolve(root, 'public/brand');
const fonts = resolve(brand, 'fonts');
await mkdir(fonts, { recursive: true });
await copyFile(resolve(root, 'public/images/educator-blue.webp'), resolve(brand, 'educator-blue.webp'));
await copyFile(resolve(root, 'public/images/materials-blue.webp'), resolve(brand, 'materials-blue.webp'));
await copyFile(resolve(root, 'public/images/ASSETS.md'), resolve(brand, 'IMAGE-CREDITS.md'));
await copyFile(resolve(root, 'docs/BRAND-PHILOSOPHY.md'), resolve(brand, 'PHILOSOPHY.md'));
const fontFiles = [
  ['@fontsource/ibm-plex-sans-arabic/files/ibm-plex-sans-arabic-arabic-400-normal.woff2', 'plex-arabic-400.woff2'],
  ['@fontsource/ibm-plex-sans-arabic/files/ibm-plex-sans-arabic-arabic-600-normal.woff2', 'plex-arabic-600.woff2'],
  ['@fontsource/ibm-plex-sans-arabic/files/ibm-plex-sans-arabic-arabic-700-normal.woff2', 'plex-arabic-700.woff2'],
  ['@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-600-normal.woff2', 'jakarta-600.woff2'],
  ['@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-normal.woff2', 'jakarta-700.woff2'],
  ['@fontsource/dm-sans/files/dm-sans-latin-400-normal.woff2', 'dm-400.woff2'],
];
for (const [from, to] of fontFiles) await copyFile(resolve(root, 'node_modules', from), resolve(fonts, to));
for (const [pkg, to] of [['ibm-plex-sans-arabic', 'PLEX-LICENSE.txt'], ['plus-jakarta-sans', 'JAKARTA-LICENSE.txt'], ['dm-sans', 'DM-SANS-LICENSE.txt']]) {
  await copyFile(resolve(root, 'node_modules/@fontsource', pkg, 'LICENSE'), resolve(fonts, to));
}
// DM Mono is checked in with its license; the remaining fonts are package-owned.
const luminance = hex => {
  const c = hex.replace('#', '').match(/../g).map(v => parseInt(v, 16) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
  return c[0] * .2126 + c[1] * .7152 + c[2] * .0722;
};
const pairs = [
  ['Primary button', '#ffffff', '#315da8'], ['Primary hover', '#ffffff', '#264e90'],
  ['Ink on paper', '#14243b', '#f8f9ff'], ['Apricot label', '#301400', '#f2b880'],
  ['Blue container', '#001a41', '#d8e2ff'], ['Muted body', '#555f74', '#f8f9ff'],
  ['Success', '#123723', '#d5eddd'], ['Warning', '#624100', '#ffedcf'], ['Error', '#410002', '#ffdad6'],
];
const contrast = pairs.map(([use, foreground, background]) => {
  const a = luminance(foreground), b = luminance(background);
  const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
  return { use, foreground, background, ratio: Number(ratio.toFixed(2)), normalTextAA: ratio >= 4.5 };
});
await writeFile(resolve(brand, 'contrast.json'), JSON.stringify({ scope: 'Brand color pairs only; not a full WCAG audit.', pairs: contrast }, null, 2) + '\n');
if (contrast.some(x => !x.normalTextAA)) throw new Error('A selected brand text pair needs adjustment.');
if (process.argv.includes('--prepare')) { console.log('Prepared local brand fonts and contrast report.'); process.exit(0); }

const browser = await chromium.launch(process.platform === 'win32' ? { channel: 'msedge' } : {});
try {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1300 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const origin = process.env.BRAND_ORIGIN || 'http://127.0.0.1:4173';
  await page.goto(origin, { waitUntil: 'networkidle' });
  await page.evaluate(() => localStorage.setItem('eduflow.language.v1', JSON.stringify('ar')));
  await page.setViewportSize({ width: 1440, height: 1000 });
  for (const view of ['overview', 'materials']) {
    await page.goto(`${origin}/#${view}`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: resolve(brand, `preview-${view}.png`) });
  }
  await page.route('**/brand/preview-*.png', route => route.fulfill({ path: resolve(brand, new URL(route.request().url()).pathname.split('/').pop()) }));
  await page.setViewportSize({ width: 1600, height: 1300 });
  const response = await page.goto(`${origin}/brand/index.html`, { waitUntil: 'networkidle' });
  if (!response?.ok()) throw new Error('Start the local preview before exporting the brand kit.');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.images].map(img => { img.loading = 'eager'; return img.decode(); })));
  const loaded = await page.evaluate(() => [...document.images].every(img => img.complete && img.naturalWidth > 0) && document.fonts.check('600 20px Plex') && document.fonts.check('700 20px Jakarta'));
  if (!loaded || errors.length) throw new Error(`Visual assets did not load: ${errors.join(', ')}`);
  const board = page.locator('#brand-board');
  await board.screenshot({ path: resolve(brand, 'eduflow-brand-board.png') });
  await page.locator('#presentation-template').screenshot({ path: resolve(brand, 'eduflow-presentation-cover.png') });
  await page.locator('#social-template').screenshot({ path: resolve(brand, 'eduflow-social.png') });
  const box = await board.boundingBox();
  await page.addStyleTag({ content: `@media print {html,body { width:${box.width}px !important; margin:0 !important; padding:0 !important; } .brand-board { width:${box.width}px; }}` });
  await page.pdf({ path: resolve(brand, 'eduflow-brand-board.pdf'), width: `${box.width}px`, height: `${box.height + 1}px`, printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } });
  await page.emulateMedia({ media: 'screen' });
  await page.addStyleTag({ content: 'html,body,.logo-card {background:transparent!important;} .export-lockup {padding:12px;}' });
  await page.locator('#lockup-primary').screenshot({ path: resolve(brand, 'eduflow-wordmark.png'), omitBackground: true });
  await page.locator('#lockup-reversed').screenshot({ path: resolve(brand, 'eduflow-wordmark-reversed.png'), omitBackground: true });
  await page.goto(`${origin}/brand/index.html`, { waitUntil: 'networkidle' });
  await page.setViewportSize({ width: 390, height: 844 });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  if (overflow) throw new Error('Brand guide overflows the mobile viewport.');
  await mkdir(resolve(root, 'test-results'), { recursive: true });
  await page.screenshot({ path: resolve(root, 'test-results/brand-guide-mobile.png'), fullPage: true });
  console.log(`Exported brand board, transparent wordmarks and application templates. ${contrast.length} color pairs meet 4.5:1. Mobile guide fits 390px.`);
} finally { await browser.close(); }

// Keep the approved 4096px transparent logos and app icons in every brand export.
await exportLogoAssets();

// Archive native sources and generated deliverables, excluding the archive itself.
if (process.platform === 'win32') {
  const escaped = brand.replaceAll("'", "''");
  execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', `$ErrorActionPreference = 'Stop'; $brandFiles = Get-ChildItem -LiteralPath '${escaped}' | Where-Object { $_.Name -notin @('eduflow-brand-kit.zip', 'learning-editorial.png') }; Compress-Archive -LiteralPath $brandFiles.FullName -DestinationPath '${escaped}/eduflow-brand-kit.zip' -Force`], { stdio: 'pipe' });
} else {
  execFileSync('zip', ['-r', 'eduflow-brand-kit.zip', ...((await readdir(brand)).filter(x => !['eduflow-brand-kit.zip', 'learning-editorial.png'].includes(x)))], { cwd: brand, stdio: 'pipe' });
}
console.log('Saved public/brand/eduflow-brand-kit.zip');
