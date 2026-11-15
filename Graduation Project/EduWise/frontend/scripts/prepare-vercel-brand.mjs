import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { resolve, dirname, relative, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import { chromium } from 'playwright';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const releaseName=process.argv[2]||'eduflow-ai-brand';
if(!/^[a-z0-9-]+$/.test(releaseName))throw Error('Use a simple lowercase release directory name.');
const stage=resolve(root,'.deploy',releaseName);
const output=resolve(stage,'.vercel/output');
const staticRoot=resolve(output,'static');
await mkdir(resolve(root,'.deploy'),{recursive:true});
// Preserve any previously prepared release rather than silently mixing builds.
await mkdir(stage);
await mkdir(output,{recursive:true});
await cp(resolve(root,'dist'),staticRoot,{recursive:true});
await writeFile(resolve(output,'config.json'),JSON.stringify({version:3,routes:[
 {src:'^/brand$',status:308,headers:{Location:'/brand/'}},
 {src:'^/brand/$',dest:'/brand/index.html'},
 {src:'^/$',dest:'/index.html'},
 {handle:'filesystem'},
]},null,2)+'\n');

const manifest=[];
async function walk(dir){for(const item of await readdir(dir,{withFileTypes:true})){const file=resolve(dir,item.name);if(item.isDirectory())await walk(file);else{
 const name=relative(staticRoot,file).replaceAll('\\','/');
 if(/(^|\/)(\.env(?:\..*)?|\.git|node_modules|test-results)(\/|$)/i.test(name))throw Error(`Unexpected deployment file: ${name}`);
 const bytes=await readFile(file);manifest.push({file:name,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
}}}
await walk(staticRoot);
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.zip':'application/zip'};
const server=createServer(async(req,res)=>{try{let pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(pathname.endsWith('/'))pathname+='index.html';const target=resolve(staticRoot,'.'+pathname);if(!target.startsWith(staticRoot+'/')&&!target.startsWith(staticRoot+'\\')){res.writeHead(403).end();return;}res.setHeader('Content-Type',mime[extname(target)]||'application/octet-stream');res.end(await readFile(target));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;
try{
 browser=await chromium.launch({channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto(origin+'/brand/',{waitUntil:'networkidle'});
 if(!response.ok())throw Error('Brand page failed.');
 await page.evaluate(()=>document.fonts.ready);
 await page.evaluate(()=>Promise.all([...document.images].map(img=>{img.loading='eager';return img.decode();})));
 const links=await page.locator('[src],a[href],link[href]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('src')||n.getAttribute('href')).filter(Boolean));
 for(const link of links){if(/^(?:#|https?:|data:|mailto:)/.test(link))continue;const url=new URL(link,origin+'/brand/');const r=await page.request.get(url.href);if(!r.ok())throw Error(`Broken deployment asset: ${link} (${r.status()})`);}
 await page.locator('[data-logo-tone="dark"]').click();
 if(!await page.locator('#lockup-primary img').getAttribute('src').then(s=>s.includes('mark-reversed.svg')))throw Error('Dark logo preview failed.');
 await page.locator('[data-logo-tone="light"]').click();
 await page.locator('[data-product-view="materials"]').click();
 await page.locator('#product-preview-image').evaluate(img=>img.decode());
 await page.locator('[data-product-view="overview"]').click();
 await page.locator('#product-preview-image').evaluate(img=>img.decode());
 await page.setViewportSize({width:390,height:844});
 await page.evaluate(()=>document.fonts.ready);
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Brand page overflows on mobile.');
 await page.goto(origin+'/',{waitUntil:'networkidle'});
 await page.locator('.brand img').first().waitFor({state:'attached'});
 if(!await page.locator('.brand img').first().getAttribute('src').then(s=>s.includes('forward-pages')))throw Error('Demo uses a different logo.');
 if(errors.length)throw Error(errors.join('\n'));
 const png=await readFile(resolve(staticRoot,'brand/eduflow-wordmark.png'));
 if(png.readUInt32BE(16)!==4096)throw Error('High-resolution logo is missing.');
 await writeFile(resolve(stage,'release-manifest.json'),JSON.stringify({scope:'EduFlow AI brand guide and linked local demo',page:'/brand/',files:manifest,verification:{brandPage:true,localLinks:true,interactiveLogo:true,productPreviews:true,mobile390:true,demoLogo:true,logoWidth:4096,browserErrors:errors}},null,2)+'\n');
 console.log(JSON.stringify({stage,files:manifest.length,bytes:manifest.reduce((s,f)=>s+f.bytes,0),verified:'Brand page, linked assets/downloads, interactions, 390px mobile layout and demo logo.'},null,2));
}finally{if(browser)await browser.close();server.close();}
