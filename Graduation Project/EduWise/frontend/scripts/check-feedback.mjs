import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { createWorkspace, applyOperation } from '../src/domain/workspace.js';
mkdirSync('test-results',{recursive:true});
let data=createWorkspace('2026-10-23T10:00:00Z');
const group=data.students.filter(p=>data.enrollments.some(e=>e.studentId===p.id&&e.groupId==='group-1'));
for(let i=0;i<group.length;i++) data=applyOperation(data,'attendance.record',{studentId:group[i].id,sessionId:'session-1',status:i===7?'absent':'present'},{role:'admin',id:`reg-${i}`,now:'2026-10-23T11:00:00Z'});
const browser=await chromium.launch({channel:'msedge',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
await context.addInitScript(seed=>{if(!localStorage.getItem('feedback-seeded')){localStorage.setItem('eduflow.workspace.v3',JSON.stringify(seed));localStorage.setItem('feedback-seeded','1');}},data);
const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
const go=async route=>{await page.goto(`http://127.0.0.1:4173/#${route}`);await page.locator('main h1').waitFor();};
try{
 await go('analytics'); assert.ok(await page.getByText('87.5%',{exact:true}).count());
 await page.getByLabel('From · Cairo date').fill('2030-01-01');await page.getByLabel('To · Cairo date').fill('2030-01-31');
 assert.equal(await page.getByText('87.5%',{exact:true}).count(),0);assert.equal(await page.locator('main').getByText('No matching results',{exact:true}).count(),1);
 await go('students');await page.getByRole('link',{name:'Omar Ahmed',exact:true}).click();await page.getByRole('heading',{name:'Omar Ahmed',exact:true}).waitFor();
 await page.getByRole('button',{name:'Edit profile',exact:true}).click();await page.getByLabel('Guardian name').fill('Parent example');await page.getByLabel('Guardian phone').fill('01012345678');await page.getByLabel('Notes · optional').fill('Follow up next session');await page.getByRole('button',{name:'Save',exact:true}).click();await page.getByRole('dialog').waitFor({state:'hidden'});
 assert.ok(await page.getByText('Parent example',{exact:true}).count());
 await page.screenshot({path:'test-results/feedback-profile.png',fullPage:true});
 await go('payments');await page.getByRole('button',{name:'View receipt',exact:true}).first().click();await page.getByRole('heading',{name:'Payment receipt',exact:true}).waitFor();assert.ok(await page.locator('.receipt-document').innerText());await page.keyboard.press('Escape');
 for(const width of [390,320]){await page.setViewportSize({width,height:844});for(const route of ['overview','students','analytics','payments','attendance','students?studentId=student-1&status=all']){await go(route);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${route} overflow ${width}`);}}
 await page.screenshot({path:'test-results/feedback-mobile.png',fullPage:true});
 await page.getByRole('button',{name:'Switch to Arabic',exact:true}).click();
 for(const route of ['students?studentId=student-1&status=all','analytics','payments']){await go(route);assert.equal(await page.locator('html').getAttribute('dir'),'rtl');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Arabic overflow ${route}`);}
 await page.screenshot({path:'test-results/feedback-arabic.png',fullPage:true});
 assert.deepEqual(errors,[]);console.log('PASS: report 87.5%, future empty state, profile edit persistence, receipt preview, six routes at 320/390px, no page errors');
}finally{await browser.close();}
