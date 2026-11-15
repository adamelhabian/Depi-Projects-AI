import { chromium } from 'playwright';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const brand = resolve(root, 'public/brand');

// Export the approved native paths directly, with no bitmap enlargement.
export async function exportLogoAssets() {
  const font = (await readFile(resolve(brand, 'fonts/jakarta-700.woff2'))).toString('base64');
  const mark = await readFile(resolve(brand, 'mark.svg'), 'utf8');
  const reversed = await readFile(resolve(brand, 'mark-reversed.svg'), 'utf8');
  const favicon = await readFile(resolve(root, 'public/favicon.svg'), 'utf8');
  const browser = await chromium.launch({ channel: 'msedge' });
  const png = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1024, height: 256 }, deviceScaleFactor: 4 });
    const style = `<style>@font-face{font-family:Jakarta;src:url(data:font/woff2;base64,${font});font-weight:700}*{box-sizing:border-box}html,body{margin:0;background:transparent}.lockup{width:1024px;height:256px;display:flex;align-items:center;justify-content:center;gap:28px;padding:32px;direction:ltr}.lockup>svg{width:170px;height:151px;flex-shrink:0}.name{font:700 116px/1 Jakarta,sans-serif;letter-spacing:-6px;white-space:nowrap}.ai{font:700 26px/1 Jakarta,sans-serif;letter-spacing:.5px;border-radius:12px;padding:14px 16px;margin-left:-12px;align-self:center}</style>`;
    for (const [name, symbol, color] of [['eduflow-wordmark.png',mark,'#14243B'],['eduflow-wordmark-reversed.png',reversed,'#F8F9FF']]) {
      await page.setContent(`${style}<div class="lockup" style="color:${color}">${symbol}<span class="name">EduFlow</span><span class="ai" style="background:#F2B880;color:#301400">AI</span></div>`);
      await page.evaluate(()=>document.fonts.ready);
      if (!await page.evaluate(()=>document.fonts.check('700 116px Jakarta'))) throw Error('Logo font did not load.');
      await page.screenshot({path:resolve(brand,name),omitBackground:true}); png.push(name);
    }
    for (const [name, size, symbol, destination] of [
      ['eduflow-mark-4096.png',4096,mark,brand],
      ['eduflow-mark-reversed-4096.png',4096,reversed,brand],
      ['eduflow-icon-192.png',192,favicon,brand],
      ['eduflow-icon-512.png',512,favicon,brand],
      ['favicon-32.png',32,favicon,resolve(root,'public')],
      ['apple-touch-icon.png',180,favicon,resolve(root,'public')],
    ]) {
      await page.setViewportSize({width:size/4,height:size/4});
      await page.setContent(`<style>html,body{margin:0;background:transparent}svg{width:100vw;height:100vh;display:block}</style>${symbol}`);
      await page.screenshot({path:resolve(destination,name),omitBackground:true});
      if(destination===brand)png.push(name);
    }
    await page.setViewportSize({width:1200,height:570});
    await page.setContent(`${style}<style>body{background:#F8F9FF}.lockup{width:1100px;height:228px;margin:30px auto 0}.dark{background:#14243B;color:#F8F9FF;border-radius:24px;margin-top:8px}.label{font:700 12px Jakarta;letter-spacing:2px;text-align:center;color:#315DA8;margin-top:26px}</style><div class="label">EDUFLOW AI / APPROVED LOGO / LEARNING IN MOTION</div><div class="lockup">${mark}<span class="name" style="color:#14243B">EduFlow</span><span class="ai" style="background:#F2B880;color:#301400">AI</span></div><div class="lockup dark">${reversed}<span class="name">EduFlow</span><span class="ai" style="background:#F2B880;color:#301400">AI</span></div>`);
    await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:resolve(brand,'eduflow-approved-logo-preview.png')});
    png.push('eduflow-approved-logo-preview.png');
  } finally { await browser.close(); }
  // Confirm actual pixel dimensions, rather than relying on export filenames.
  for(const file of ['eduflow-wordmark.png','eduflow-wordmark-reversed.png','eduflow-mark-4096.png','eduflow-mark-reversed-4096.png']){
    const bytes=await readFile(resolve(brand,file));
    if(bytes.readUInt32BE(16)!==4096)throw Error(`${file} is not 4096px wide.`);
  }
  await writeFile(resolve(brand,'APPROVED-LOGO.md'),'# Approved logo — Learning in motion\n\nApproved option 05 from the original logo exploration board (two forward page chevrons and an apricot terminal).\n\n- mark.svg, mark-reversed.svg, mark-mono.svg: native vector paths; no fonts or linked resources.\n- eduflow-wordmark.png and eduflow-wordmark-reversed.png: 4096 × 1024, transparent.\n- eduflow-mark-4096.png and eduflow-mark-reversed-4096.png: 4096 × 4096, transparent.\n- eduflow-icon-192.png and eduflow-icon-512.png: app icons.\n- eduflow-approved-logo-preview.png: light and dark preview.\n\nUse SVG on the website. Keep arrows pointing right in both Arabic and English. Do not stretch, add effects, or reverse the geometry.\n');
  const files=['mark.svg','mark-reversed.svg','mark-mono.svg','APPROVED-LOGO.md',...png];
  const q=s=>`'${s.replaceAll("'","''")}'`;
  execFileSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',`$ErrorActionPreference='Stop'; Compress-Archive -LiteralPath @(${files.map(n=>q(resolve(brand,n))).join(',')}) -DestinationPath ${q(resolve(brand,'eduflow-approved-logo.zip'))} -Force`],{windowsHide:true});
  console.log('Approved logo exported: native SVGs, transparent 4096px wordmarks and symbols, app icons and ZIP.');
}
