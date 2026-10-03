/* Run against a local server; see README. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
 const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/kam-plans',r=>r.fulfill({status:200,contentType:'application/json',body:'{"kam_plans":{},"partner_plans":{}}'}));
  await page.goto('http://127.0.0.1:8088',{waitUntil:'domcontentloaded',timeout:90000});
  await page.waitForFunction(()=>window.dataPayload?.sys_db?.length>0);
  await page.locator('button[onclick="switchTab(\'tab-funnel\', this)"]').click();
  for (const month of ['2026-08','2026-09','2026-01','all']) {
   await page.evaluate(m=>setFunnelMonth(m),month);
   for (const brand of ['ALL','JETOUR','НЕ ОПРЕДЕЛЁН']) {
    await page.evaluate(b=>selectFunnelBrand(b),brand);
    const text=await page.locator('#funnelDynamicView').innerText();
    assert(!/NaN|undefined|Infinity/.test(text));
    assert(text.includes('Нет данных'));
    const card=await page.locator('#funnelKpiCards > div').first().innerText();
    const expected=await page.evaluate(({month,brand})=>{
     const m=window.brandFunnelFullData.by_month[month];
     const n=(brand==='ALL'?m.calculator:m.brands[brand].calculator)?.calc.events;
     return n==null?'Нет данных':n.toLocaleString('ru-RU');
    },{month,brand});
    assert(card.includes(expected));
   }
  }
  await page.evaluate(()=>{setFunnelMonth('2026-09');selectFunnelBrand('ALL');});
  fs.mkdirSync('scratch/calculator',{recursive:true});
  await page.screenshot({path:'scratch/calculator/funnel-desktop.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:'scratch/calculator/funnel-mobile.png',fullPage:false});
  assert.deepEqual(errors,[]);
  console.log('Funnel browser OK: 4 periods, 3 brand scopes, missing values, real snapshot totals, desktop/mobile.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
