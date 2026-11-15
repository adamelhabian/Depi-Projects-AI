import { spawn, execFileSync } from 'node:child_process';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const origin='http://127.0.0.1:4186';
const server=spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','4186','--strictPort'],{cwd:root,windowsHide:true,stdio:'ignore'});
let browser;
try{
 let ready=false;
 for(let i=0;i<40;i++){if(server.exitCode!==null)throw Error('Local preview could not start.');try{ready=(await fetch(origin)).ok;}catch{}if(ready)break;await new Promise(r=>setTimeout(r,250));}
 if(!ready)throw Error('Local preview did not become ready.');
 if(process.env.LOGO_REVIEW_ONLY!=='1')execFileSync(process.execPath,['scripts/export-brand.mjs'],{cwd:root,env:{...process.env,BRAND_ORIGIN:origin},stdio:'inherit',windowsHide:true});
 browser=await chromium.launch({channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:2});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 const expectedPaths=[...((await readFile(resolve(root,'public/brand/logo-explorations/05-forward-pages-color.svg'),'utf8')).matchAll(/ d="([^"]+)"/g))].map(m=>m[1]);
 const approved=await(await page.request.get(origin+'/brand/mark.svg')).text();
 const actualPaths=[...approved.matchAll(/ d="([^"]+)"/g)].map(m=>m[1]);
 if(JSON.stringify(expectedPaths)!==JSON.stringify(actualPaths))throw Error('Approved geometry differs from option 05.');
 const result={geometry:'Exact paths from original option 05',desktop:await page.locator('.brand').first().evaluate(el=>({src:el.querySelector('img').getAttribute('src'),loaded:el.querySelector('img').naturalWidth>0,width:el.getBoundingClientRect().width,direction:getComputedStyle(el).direction,transform:getComputedStyle(el.querySelector('img')).transform}))};
 if(!result.desktop.loaded||!result.desktop.src.includes('forward-pages'))throw Error('App is not displaying the approved logo.');
 await mkdir(resolve(root,'test-results'),{recursive:true});
 await page.screenshot({path:resolve(root,'test-results/approved-logo-desktop-en.png')});
 await page.getByRole('button',{name:'Switch to Arabic'}).click();
 await page.evaluate(()=>document.fonts.ready);
 if(await page.locator('html').getAttribute('dir')!=='rtl')throw Error('Arabic direction did not activate.');
 const arabicDirection=await page.locator('.brand').first().evaluate(el=>getComputedStyle(el).direction);
 if(arabicDirection!=='ltr')throw Error('Logo direction changed in Arabic.');
 await page.screenshot({path:resolve(root,'test-results/approved-logo-desktop-ar.png')});
 await page.setViewportSize({width:390,height:844});
 result.mobile=await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth}));
 if(result.mobile.overflow)throw Error('Mobile layout overflow.');
 await page.screenshot({path:resolve(root,'test-results/approved-logo-mobile-ar.png')});
 result.assets=[];
 for(const file of ['/favicon.svg','/favicon-32.png','/apple-touch-icon.png','/brand/mark.svg','/brand/mark-reversed.svg','/brand/mark-mono.svg','/brand/eduflow-wordmark.png','/brand/eduflow-wordmark-reversed.png','/brand/eduflow-mark-4096.png','/brand/eduflow-approved-logo.zip']){
  const response=await page.request.get(origin+file);if(!response.ok())throw Error(`Asset missing: ${file}`);result.assets.push({file,status:response.status()});
 }
 result.highResolution=await page.evaluate(async()=>{const result=[];for(const src of ['/brand/eduflow-wordmark.png','/brand/eduflow-wordmark-reversed.png','/brand/eduflow-mark-4096.png']){const img=new Image();img.src=src;await img.decode();const canvas=document.createElement('canvas');canvas.width=1;canvas.height=1;const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);result.push({src,width:img.naturalWidth,height:img.naturalHeight,cornerAlpha:ctx.getImageData(0,0,1,1).data[3]});}return result;});
 if(result.highResolution.some(x=>x.width!==4096||x.cornerAlpha!==0))throw Error('High resolution or transparency verification failed.');
 await page.goto(origin+'/brand/index.html',{waitUntil:'networkidle'});
 result.brandGuide=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflowing:[...document.querySelectorAll('body *')].filter(el=>el.getBoundingClientRect().right>innerWidth+1||el.getBoundingClientRect().left< -1).slice(0,12).map(el=>({tag:el.tagName,class:el.className,width:el.getBoundingClientRect().width,left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right}))}));
 if(errors.length)throw Error(errors.join('\n'));
 result.browserErrors=errors;
 await writeFile(resolve(root,'test-results/approved-logo-review.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result,null,2));
}finally{if(browser)await browser.close();server.kill();}
