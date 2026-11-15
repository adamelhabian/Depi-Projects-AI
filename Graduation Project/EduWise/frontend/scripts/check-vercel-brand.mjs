import { chromium } from 'playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const origin=new URL(process.argv[2]).origin;
if(!origin.startsWith('https://')||!new URL(origin).hostname.endsWith('.vercel.app'))throw Error('Expected an HTTPS Vercel deployment URL.');
const browser=await chromium.launch({channel:'msedge'});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto(origin+'/brand/',{waitUntil:'networkidle'});
 if(!response.ok())throw Error(`Public brand URL failed: ${response.status()}`);
 await page.locator('#brand-board').waitFor();
 await page.evaluate(()=>document.fonts.ready);
 await page.evaluate(()=>Promise.all([...document.images].map(img=>{img.loading='eager';return img.decode();})));
 const result={url:origin+'/brand/',publicStatus:response.status(),assets:[]};
 for(const file of ['/','/brand/brand.css','/brand/brand.js','/brand/mark.svg','/brand/mark-reversed.svg','/brand/fonts/jakarta-700.woff2','/brand/eduflow-wordmark.png','/brand/eduflow-mark-4096.png','/brand/eduflow-approved-logo.zip','/brand/eduflow-brand-kit.zip','/favicon.svg']){
  const r=await page.request.head(origin+file);if(!r.ok())throw Error(`Public asset failed: ${file} ${r.status()}`);result.assets.push({path:file,status:r.status()});
 }
 const liveMark=await(await page.request.get(origin+'/brand/mark.svg')).body();
 const sourceMark=await readFile(resolve(root,'public/brand/mark.svg'));
 const hash=b=>createHash('sha256').update(b).digest('hex');
 if(hash(liveMark)!==hash(sourceMark))throw Error('Live logo differs from the approved logo.');
 await page.locator('[data-logo-tone="dark"]').click();
 await page.locator('#lockup-primary img').evaluate(img=>img.decode());
 if(!await page.locator('#lockup-primary img').getAttribute('src').then(x=>x.includes('reversed')))throw Error('Live logo interaction failed.');
 await page.locator('[data-logo-tone="light"]').click();
 await page.locator('[data-product-view="materials"]').click();
 await page.locator('#product-preview-image').evaluate(img=>img.decode());
 await page.locator('[data-product-view="overview"]').click();
 await page.locator('#product-preview-image').evaluate(img=>img.decode());
 await page.setViewportSize({width:390,height:844});
 result.mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if(result.mobileOverflow)throw Error('Live brand page overflows on mobile.');
 await mkdir(resolve(root,'test-results'),{recursive:true});
 await page.screenshot({path:resolve(root,'test-results/vercel-brand-mobile.png'),fullPage:true});
 await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:resolve(root,'test-results/vercel-brand-desktop.png')});
 await page.goto(origin+'/',{waitUntil:'networkidle'});
 await page.locator('.brand img').first().waitFor({state:'attached'});
 if(!await page.locator('.brand img').first().getAttribute('src').then(x=>x.includes('forward-pages')))throw Error('Live demo logo is incorrect.');
 if(errors.length)throw Error(errors.join('\n'));
 result.logoMatches=true;result.interactions=true;result.demo=true;result.browserErrors=errors;
 await writeFile(resolve(root,'test-results/vercel-brand-live-check.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
