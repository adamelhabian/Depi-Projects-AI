import { mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = resolve(root, 'public/brand/logo-explorations');
await mkdir(out, { recursive: true });
const blue = '#315DA8', apricot = '#F2B880', ink = '#14243B', paper = '#F8F9FF';
const concepts = [
  { id: '01-open-book', title: 'صفحة جديدة', en: 'Open possibilities', description: 'كتاب مفتوح بخطوط هادية؛ التعليم هو نقطة البداية.',
    shapes: (b,a) => `<path d="M48 29C36 20 23 19 10 22v47c14-3 26-1 38 8 12-9 24-11 38-8V22c-13-3-26-2-38 7Z" fill="${b}"/><path d="M48 37v31M22 33c6 0 12 2 17 5M22 45c6 0 12 2 17 5M57 39c6-4 12-6 17-6M57 51c6-4 12-6 17-6" stroke="${paper}" stroke-width="5" stroke-linecap="round"/><path d="M64 12h20v20L64 12Z" fill="${a}"/>` },
  { id: '02-flow-e', title: 'انسياب', en: 'A clearer flow', description: 'حرف e في مسار متصل؛ بساطة وحركة في علامة واحدة.',
    shapes: (b,a) => `<path d="M72 65A29 29 0 1 1 75 37c2 4 3 8 3 12H31" fill="none" stroke="${b}" stroke-width="13" stroke-linecap="round"/><circle cx="78" cy="21" r="8" fill="${a}"/>` },
  { id: '03-ef-monogram', title: 'توقيع EF', en: 'Made to connect', description: 'حروف الاسم بتكوين هندسي؛ حضور قوي في أيقونة صغيرة.',
    shapes: (b,a) => `<path d="M13 17h36v13H26v12h19v12H26v12h23v13H13V17Zm42 0h29v13H68v12h14v12H68v25H55V17Z" fill="${b}"/><rect x="71" y="66" width="13" height="13" rx="3" fill="${a}"/>` },
  { id: '04-connected-loop', title: 'حلقة وصل', en: 'One connected space', description: 'مسارات مترابطة تجمع الإدارة والمحتوى والمتابعة.',
    shapes: (b,a) => `<path d="M26 48V34a22 22 0 0 1 44 0v28a14 14 0 0 1-28 0V34a14 14 0 0 1 28 0v14" fill="none" stroke="${b}" stroke-width="11" stroke-linecap="round"/><path d="M26 47v15a22 22 0 0 0 44 0" fill="none" stroke="${b}" stroke-width="11" stroke-linecap="round"/><circle cx="26" cy="46" r="8" fill="${a}"/>` },
  { id: '05-forward-pages', title: 'خطوة لقدّام', en: 'Learning in motion', description: 'صفحات متتابعة تتحوّل لسهم؛ تقدّم وترتيب من أول نظرة.',
    shapes: (b,a) => `<path d="m13 19 31 29-31 29V59l12-11-12-11V19Z" fill="${b}"/><path d="m37 19 31 29-31 29V59l12-11-12-11V19Z" fill="${b}"/><path d="m62 31 18 17-18 17V31Z" fill="${a}"/>` },
  { id: '06-learning-gateway', title: 'أفق جديد', en: 'Room to grow', description: 'بوابة مفتوحة وشمس صغيرة؛ مساحة أوسع للتعلّم والنمو.',
    shapes: (b,a) => `<path d="M16 78V43a32 32 0 0 1 64 0v35H66V43a18 18 0 0 0-36 0v35H16Z" fill="${b}"/><path d="M41 78V57a7 7 0 0 1 14 0v21H41Z" fill="${b}"/><circle cx="77" cy="17" r="9" fill="${a}"/>` },
];
const svg = (c, mode='color') => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="none"><title>EduFlow AI — ${c.en}</title>${c.shapes(mode==='reversed'?paper:mode==='mono'?ink:blue,mode==='mono'?ink:apricot)}</svg>`;
for (const c of concepts) for (const mode of ['color','mono','reversed']) await writeFile(resolve(out, `${c.id}-${mode}.svg`), svg(c,mode));
const cards = concepts.map((c,i) => `<article class="concept ${i===1||i===4?'dark':''}" id="${c.id}"><div class="card-top"><span class="number">0${i+1}</span><span dir="ltr" class="en">${c.en}</span></div><div class="lockup" id="lockup-${i}" dir="ltr"><img src="${c.id}-${i===1||i===4?'reversed':'color'}.svg" alt=""/><span>EduFlow<span class="ai">AI</span></span></div><div class="card-bottom"><div><h2>${c.title}</h2><p>${c.description}</p></div><div class="small-marks" aria-label="معاينة الأيقونة بأحجام صغيرة"><img width="16" height="16" src="${c.id}-${i===1||i===4?'reversed':'color'}.svg" alt="16px"/><img width="24" height="24" src="${c.id}-${i===1||i===4?'reversed':'color'}.svg" alt="24px"/><img width="32" height="32" src="${c.id}-${i===1||i===4?'reversed':'color'}.svg" alt="32px"/></div></div><div class="downloads"><a href="${c.id}-color.svg" download>SVG ملون ↙</a><a href="${c.id}-mono.svg" download>لون واحد ↙</a><a href="${c.id}-reversed.svg" download>نسخة فاتحة ↙</a><a href="${c.id}-wordmark.png" download>PNG شفاف ↙</a></div></article>`).join('');
const html = `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EduFlow AI — 6 logo directions</title><style>
@font-face{font-family:Plex;src:url('../fonts/plex-arabic-400.woff2')}@font-face{font-family:Plex;src:url('../fonts/plex-arabic-600.woff2');font-weight:600}@font-face{font-family:Jakarta;src:url('../fonts/jakarta-700.woff2');font-weight:700}
*{box-sizing:border-box}body{margin:0;background:${paper};color:${ink};font-family:Plex,sans-serif}a{color:inherit}#board{max-width:1560px;margin:auto;padding:58px 60px 30px}.header{display:flex;justify-content:space-between;align-items:start;margin-bottom:38px;gap:24px}.eyebrow{font:700 11px Jakarta,sans-serif;letter-spacing:2px;color:${blue};display:block;margin-bottom:12px}h1{font-size:38px;font-weight:600;margin:0;line-height:1.4}.intro{font-size:15px;margin:8px 0 0;color:#555f74}.palette{display:flex;align-items:center;gap:7px;direction:ltr;padding-top:12px}.swatch{width:26px;height:26px;border-radius:50%;border:1px solid #14243b16}.edition{font:700 10px Jakarta,sans-serif;margin-top:12px;direction:ltr;letter-spacing:1px;text-align:left}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;direction:ltr}.concept{border:1px solid #e1e5ef;border-radius:20px;background:white;min-width:0;overflow:hidden;direction:rtl}.card-top{display:flex;justify-content:space-between;align-items:center;direction:ltr;padding:22px 25px 0}.number{font:700 13px Jakarta,sans-serif;color:${blue}}.en{font:700 10px Jakarta,sans-serif;letter-spacing:.4px;color:#667087}.lockup{display:flex;align-items:center;justify-content:center;gap:13px;min-height:174px;padding:20px 12px;color:${ink};width:max-content;max-width:100%;margin:auto}.lockup>img{width:69px;height:69px;flex-shrink:0}.lockup>span{font:700 30px Jakarta,sans-serif;letter-spacing:-1.3px;white-space:nowrap;display:flex;align-items:center;gap:8px}.ai{font-size:10px;letter-spacing:.3px;color:${blue};background:#e8eef9;border-radius:6px;padding:5px 6px}.card-bottom{padding:0 25px 22px;min-height:105px;display:flex;gap:16px;justify-content:space-between;align-items:end}h2{font-size:21px;margin:0 0 6px;font-weight:600}p{margin:0;font-size:12px;line-height:1.9;max-width:250px;color:#555f74}.small-marks{display:flex;align-items:center;gap:7px;direction:ltr;padding-bottom:5px;flex-shrink:0}.dark{background:${blue};border-color:${blue};color:${paper}}.dark .number{color:${apricot}}.dark .en,.dark p{color:#e1e9f7}.dark .lockup{color:${paper}}.dark .ai{color:${apricot};background:#ffffff18}.downloads{padding:12px 20px;background:#f2f5fb;display:flex;flex-wrap:wrap;gap:13px;font-size:11px}.downloads a{text-decoration:none}.downloads a:hover{text-decoration:underline}.dark .downloads{background:#264e90}.footer{display:flex;align-items:center;justify-content:space-between;margin-top:24px;padding-top:20px;border-top:1px solid #dce2ef;font-size:12px;color:#555f74}.footer b{font:700 11px Jakarta,sans-serif;letter-spacing:1px}.exporting .downloads{display:none}.page-actions{max-width:1440px;padding:0 0 40px;margin:auto;display:flex;gap:12px}.page-actions a{display:inline-block;background:${blue};color:white;text-decoration:none;padding:12px 20px;border-radius:10px;font-size:14px}.page-actions a.secondary{background:#e8eef9;color:${blue}}
@media(max-width:1100px){#board{padding:32px 24px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.page-actions{padding:0 24px 30px}}@media(max-width:660px){.header{display:block}h1{font-size:30px}.palette{margin-top:18px}.edition{text-align:right}.grid{grid-template-columns:1fr}.lockup{min-height:165px}.footer{align-items:start;gap:15px}.footer span{max-width:210px}.page-actions{flex-wrap:wrap}.small-marks{gap:4px}.card-bottom{padding:0 18px 20px}.lockup>span{font-size:29px}}
</style></head><body><main id="board"><header class="header"><div><span class="eyebrow" dir="ltr">EDUFLOW AI / LOGO EXPLORATIONS</span><h1>٦ أفكار. هوية واحدة.</h1><p class="intro">التعليم، الوضوح، والحركة — ستة اتجاهات لهوية EduFlow AI.</p></div><div><div class="palette"><span class="swatch" style="background:${blue}"></span><span class="swatch" style="background:${apricot}"></span><span class="swatch" style="background:${ink}"></span><span class="swatch" style="background:${paper}"></span></div><div class="edition">BLUE × APRICOT / 2026</div></div></header><div class="grid">${cards}</div><footer class="footer"><span>بدائل للمقارنة بنفس ألوان وخطوط الموقع.</span><b dir="ltr">LESS ADMIN. MORE TEACHING.</b></footer></main><nav class="page-actions" aria-label="تحميل البدائل"><a href="eduflow-logo-options.zip" download>تحميل كل الملفات ↙</a><a class="secondary" href="eduflow-logo-options.png" download>تحميل لوحة المقارنة ↙</a><a class="secondary" href="../">دليل الهوية ←</a></nav></body></html>`;
await writeFile(resolve(out,'index.html'),html);
await writeFile(resolve(out,'README.md'),`# EduFlow AI — Logo explorations\n\nSix alternatives using the existing palette: ${blue}, ${apricot}, ${ink}, ${paper}.\nFonts: Plus Jakarta Sans and IBM Plex Sans Arabic (the site's existing licensed fonts).\n\nEach concept includes editable SVG symbols in color, mono and reversed treatments; transparent PNG wordmarks; and a PNG icon. The numbered comparison board matches the filenames.\nSVG symbols contain only native paths/shapes, with no font or external resource dependency. PNG wordmarks are raster exports of the local fonts.\n\n${concepts.map(c=>`- ${c.id}: ${c.title} — ${c.en}`).join('\n')}\n\nCreated as additional options; the active website logo is unchanged.\n`);

// A private, temporary local server makes the export independent of the app's running preview.
const mime={'.html':'text/html; charset=utf-8','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'};
const publicRoot=resolve(root,'public');
const server=createServer(async(req,res)=>{try{const raw=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const target=resolve(publicRoot,'.'+raw+(raw.endsWith('/')?'index.html':''));if(!target.startsWith(publicRoot+'/')&&!target.startsWith(publicRoot+'\\')){res.writeHead(403).end();return;}res.setHeader('Content-Type',mime[target.slice(target.lastIndexOf('.'))]||'application/octet-stream');res.end(await readFile(target));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const url=`http://127.0.0.1:${server.address().port}/brand/logo-explorations/`;
const browser=await chromium.launch({channel:'msedge'});
try{
 const page=await browser.newPage({viewport:{width:1560,height:1100},deviceScaleFactor:2});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 if(!await page.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)))throw Error('Missing image');
 await page.locator('body').evaluate(e=>e.classList.add('exporting'));
 await page.locator('#board').screenshot({path:resolve(out,'eduflow-logo-options.png')});
 for(let i=0;i<concepts.length;i++){
  const c=concepts[i];
  await page.locator(`[id="${c.id}"]`).screenshot({path:resolve(out,`${c.id}-preview.png`)});
  // Export the same composition in primary colors on a genuinely transparent canvas.
  await page.locator(`#lockup-${i}`).evaluate((el,c)=>{el.style.color='#14243B';el.style.minHeight='110px';el.querySelector('img').src=c+'-color.svg';},c.id);
 }
 await page.addStyleTag({content:'html,body,.concept{background:transparent!important}.lockup .ai{color:#315DA8!important;background:#e8eef9!important}'});
 for(let i=0;i<concepts.length;i++){
  await page.locator(`#lockup-${i}`).screenshot({path:resolve(out,`${concepts[i].id}-wordmark.png`),omitBackground:true});
 }
 for(const c of concepts){
  await page.setViewportSize({width:256,height:256});
  await page.setContent(`<html><head><style>html,body{margin:0;background:transparent}img{width:256px;height:256px;display:block}</style></head><body><img src="${url+c.id}-color.svg" /></body></html>`);
  await page.locator('img').evaluate(img=>img.decode());
  await page.screenshot({path:resolve(out,`${c.id}-icon.png`),omitBackground:true});
 }
 await page.setViewportSize({width:390,height:844});await page.goto(url,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 await page.screenshot({path:resolve(out,'mobile-preview.png'),fullPage:true});
 if(errors.length)throw Error(errors.join('\n'));
 console.log('Exported six logo directions: 18 native SVGs, 6 transparent wordmarks, 6 PNG icons, 6 concept previews, comparison board and mobile preview. All images loaded; no browser errors; mobile fits 390px.');
}finally{await browser.close();server.close();}
