/* Optional browser regression: NODE_PATH must expose Playwright; see README. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
    const browser = await chromium.launch({
        executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: true
    });
    try {
        const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
        const errors = [];
        let cloudWrites = 0;
        page.on('pageerror', error => errors.push(error.message));
        // Exercise editing in an isolated browser profile without changing real cloud plans.
        await page.route('**/api/kam-plans', route => {
            if (route.request().method() !== 'GET') cloudWrites++;
            return route.fulfill({ status: 200, contentType: 'application/json', body: '{"kam_plans":{},"partner_plans":{}}' });
        });
        await page.goto(process.env.DASHBOARD_URL || 'http://127.0.0.1:8088', { waitUntil: 'domcontentloaded', timeout: 90000 });
        await page.waitForFunction(() => window.dataPayload?.sys_db?.length > 0);
        for (const [month, count] of [['2026-08', '1 776'], ['2026-09', '1 559'], ['2026-10', '21']]) {
            await page.selectOption('#monthFilter', month);
            assert.equal((await page.locator('#kpiSales').innerText()).trim(), count);
        }
        await page.selectOption('#monthFilter', 'custom');
        await page.locator('#dateFrom').fill('2026-09-01');
        await page.locator('#dateTo').fill('2026-09-30');
        await page.locator('#dateTo').blur();
        assert.equal((await page.locator('#kpiSales').innerText()).trim(), '1 559');
        await page.selectOption('#monthFilter', '2026-09');
        for (const id of ['tab-dashboard', 'tab-dynamics', 'tab-dyn-months', 'tab-partners', 'tab-kam', 'tab-managers', 'tab-funnel', 'tab-lead-geo', 'tab-banking', 'tab-details']) {
            await page.locator(`button[onclick="switchTab('${id}', this)"]`).click();
            assert(await page.locator('#' + id).isVisible(), id);
            console.log('Tab OK:', id);
        }
        await page.locator('button[onclick="switchTab(\'tab-kam\', this)"]').click();
        for (const kam of ['Алексей Чихарев', 'Андрей Кузнецов', 'Светлана Дариенко', 'Валерия Солдатова', 'Евгения Добролюбова', 'all']) {
            await page.locator(`.kam-select-pill[data-kam="${kam}"]`).click();
            assert(await page.locator('#kamTableContainer tbody tr').count() > 0);
        }
        const toggle = page.locator('#kamTableContainer [onclick^="toggleKamPartnerRows"]').first();
        await toggle.click();
        assert(await page.locator('#kamTableContainer tr[class*="kam-subrow-"]:visible').count() > 0);
        await page.evaluate(() => openKamLoginModal('admin'));
        await page.selectOption('#kamLoginSelect', 'admin');
        await page.locator('#kamLoginPin').fill(await page.evaluate(() => KAM_AUTH_ACCOUNTS.admin.pins[0]));
        await page.locator('#kamLoginForm button[type="submit"]').click();
        assert(await page.locator('#kamLoginModal').evaluate(el => el.classList.contains('hidden')));
        const plan = page.locator('#kamTableContainer input[onchange^="onPartnerPlanChange"]').first();
        await plan.fill('123');
        await plan.blur();
        assert(await page.evaluate(() => Object.values(getKamPlansStore().partner_plans).includes(123)));
        const output = path.resolve('scratch/refactor');
        fs.mkdirSync(output, { recursive: true });
        const downloadPromise = page.waitForEvent('download');
        await page.locator('button[onclick="exportKamReportToExcel()"]').click();
        const download = await downloadPromise;
        const exportPath = path.join(output, 'kam-report.xlsx');
        await download.saveAs(exportPath);
        assert(fs.statSync(exportPath).size > 1000);
        await page.screenshot({ path: path.join(output, 'kam.png') });
        await page.locator('button[onclick="switchTab(\'tab-dashboard\', this)"]').click();
        await page.locator('button[onclick="forceDataUpdate(this)"]').click();
        await page.waitForFunction(() => document.getElementById('kpiSales').innerText.trim() === '1 559');
        await page.screenshot({ path: path.join(output, 'dashboard.png') });
        assert.deepEqual(errors, []);
        console.log('Browser OK: periods, 10 tabs, 5 KAMs, subrows, local plan editing, XLSX download, refresh. Intercepted cloud writes:', cloudWrites);
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
