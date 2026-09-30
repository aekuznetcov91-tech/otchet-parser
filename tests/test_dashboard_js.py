import os
import unittest
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(BASE_DIR, 'site')
JS_DIR = os.path.join(SITE_DIR, 'js')
DATA_JSON_PATH = os.path.join(SITE_DIR, 'data.json')
NODE_BIN = os.path.join(BASE_DIR, 'scratch', 'tools', 'node-v20.18.0-darwin-arm64', 'bin', 'node')

class TestDashboardJavaScript(unittest.TestCase):

    def setUp(self):
        self.js_files = [
            os.path.join(JS_DIR, 'utils.js'),
            os.path.join(JS_DIR, 'tables.js'),
            os.path.join(JS_DIR, 'charts.js'),
            os.path.join(JS_DIR, 'debtors.js'),
            os.path.join(JS_DIR, 'data-loader.js'),
            os.path.join(JS_DIR, 'lead-geo.js'),
            os.path.join(JS_DIR, 'banking-dashboard.js'),
            os.path.join(JS_DIR, 'kam-dashboard.js')
        ]

    def test_js_files_exist(self):
        for f in self.js_files:
            self.assertTrue(os.path.exists(f), f'File {f} is missing')

    def test_js_syntax_with_node(self):
        if not os.path.exists(NODE_BIN):
            self.skipTest('Local node binary not found')
        for f in self.js_files:
            res = subprocess.run([NODE_BIN, '--check', f], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f'Syntax error in {f}: ' + res.stderr)

    def test_get_debtor_channel_badge_defined_and_functional(self):
        if not os.path.exists(NODE_BIN):
            self.skipTest('Local node binary not found')

        utils_path = os.path.join(JS_DIR, 'utils.js')
        debtors_path = os.path.join(JS_DIR, 'debtors.js')
        test_script = """
const fs = require('fs');
global.window = global;
global.document = { getElementById: () => null };
const vm = require('vm');
const ctx = vm.createContext(global);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);

if (typeof ctx.getDebtorChannelBadge !== 'function') { console.error('getDebtorChannelBadge missing'); process.exit(1); }
const mp2 = ctx.getDebtorChannelBadge('МП2');
const online = ctx.getDebtorChannelBadge('Online');
const fdc = ctx.getDebtorChannelBadge('ФДЦ');
if (!mp2.includes('МП2') || !online.includes('Online') || !fdc.includes('ФДЦ')) { process.exit(1); }
console.log('OK');
""" % (utils_path, debtors_path)

        res = subprocess.run([NODE_BIN, '-e', test_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'Badge test failed: ' + res.stderr)
        self.assertIn('OK', res.stdout)

    def test_render_waiting_table_runtime(self):
        if not os.path.exists(NODE_BIN):
            self.skipTest('Local node binary not found')

        utils_path = os.path.join(JS_DIR, 'utils.js')
        tables_path = os.path.join(JS_DIR, 'tables.js')
        test_script = """
const fs = require('fs');
const vm = require('vm');
global.window = global;
let htmlResult = '';
global.document = {
    getElementById: (id) => (id === 'tableWaitingContainer' ? { set innerHTML(val) { htmlResult = val; }, get innerHTML() { return htmlResult; } } : null),
    querySelectorAll: () => []
};
global.db = [
    { Brand: 'JETOUR', B2C: 'МП2', WaitQty: 5, WaitMonth: '2026-08' },
    { Brand: 'JETOUR', B2C: 'Online', WaitQty: 2, WaitMonth: '2026-08' },
    { Brand: 'LADA', B2C: 'ФДЦ', WaitQty: 3, WaitMonth: '2026-08' }
];
global.setupSmartSearch = () => {};
const ctx = vm.createContext(global);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);
ctx.renderWaitingTable({ mode: 'month', month: '2026-08' });

if (!htmlResult.includes('tableWaiting') || !htmlResult.includes('МП2 (Опт)') || !htmlResult.includes('Online')) {
    console.error('Waiting table failed:', htmlResult); process.exit(1);
}
console.log('OK');
""" % (utils_path, tables_path)

        res = subprocess.run([NODE_BIN, '-e', test_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'renderWaitingTable runtime test failed: ' + res.stderr)
        self.assertIn('OK', res.stdout)

    def test_render_debtors_table_runtime_with_real_data(self):
        if not os.path.exists(NODE_BIN):
            self.skipTest('Local node binary not found')
        if not os.path.exists(DATA_JSON_PATH):
            self.skipTest('site/data.json not found')

        utils_path = os.path.join(JS_DIR, 'utils.js')
        debtors_path = os.path.join(JS_DIR, 'debtors.js')
        test_script = """
const fs = require('fs');
const vm = require('vm');
const data = JSON.parse(fs.readFileSync('%s', 'utf8'));
global.window = global;
let htmlResult = '';
global.document = {
    getElementById: () => ({ innerText: '', set innerHTML(val) { htmlResult = val; }, get innerHTML() { return htmlResult; } }),
    querySelectorAll: () => []
};
global.rawDebtorsList = data.debtors || [];
global.currentFilterConfig = { mode: 'all' };
const ctx = vm.createContext(global);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('%s', 'utf8'), ctx);
ctx.renderDebtorsTable({ mode: 'all' });

if (!htmlResult.includes('tableDebtors') || !htmlResult.includes('Канал')) {
    console.error('Debtors table failed:', htmlResult); process.exit(1);
}
console.log('OK');
""" % (DATA_JSON_PATH, utils_path, debtors_path)

        res = subprocess.run([NODE_BIN, '-e', test_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f'renderDebtorsTable with real data failed: ' + res.stderr)
        self.assertIn('OK', res.stdout)

    def test_kam_dashboard_sync(self):
        root_kam = os.path.join(BASE_DIR, 'js', 'kam-dashboard.js')
        site_kam = os.path.join(JS_DIR, 'kam-dashboard.js')
        self.assertTrue(os.path.exists(root_kam), "js/kam-dashboard.js missing")
        self.assertTrue(os.path.exists(site_kam), "site/js/kam-dashboard.js missing")
        with open(root_kam, 'r', encoding='utf-8') as f1, open(site_kam, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/kam-dashboard.js and site/js/kam-dashboard.js must be identical")

    def test_kam_dashboard_mtd_and_debts_structure(self):
        site_kam = os.path.join(JS_DIR, 'kam-dashboard.js')
        with open(site_kam, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('getMtdDynamicsHtml', content)
        self.assertIn('getDebtsHtml', content)
        self.assertIn('getBrandDebtsHtml', content)
        self.assertIn('openDebtorsTabForPartner', content)
        self.assertIn('MTD <span class="text-[10px] text-blue-500 block font-normal">(прошлый мес.)</span>', content)
        self.assertIn('Долги <span class="text-[10px] text-amber-500 block font-normal">(ожидание ДКП)</span>', content)
        self.assertIn('mtd_deals', content)
        self.assertIn('debts_count', content)

    def test_utils_sync_and_format_brands_presentation(self):
        root_utils = os.path.join(BASE_DIR, 'js', 'utils.js')
        site_utils = os.path.join(JS_DIR, 'utils.js')
        self.assertTrue(os.path.exists(root_utils), "js/utils.js missing")
        self.assertTrue(os.path.exists(site_utils), "site/js/utils.js missing")
        with open(root_utils, 'r', encoding='utf-8') as f1, open(site_utils, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/utils.js and site/js/utils.js must be identical")

        root_index = os.path.join(BASE_DIR, 'index.html')
        site_index = os.path.join(SITE_DIR, 'index.html')
        with open(root_index, 'r', encoding='utf-8') as f1, open(site_index, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "index.html and site/index.html must be identical")

        with open(site_index, 'r', encoding='utf-8') as f:
            index_content = f.read()
        self.assertIn('copyBrandsPresentationText', index_content, "index.html must include copyBrandsPresentationText button")

        with open(site_utils, 'r', encoding='utf-8') as f:
            utils_content = f.read()
        self.assertIn('function formatBrandsForPresentation', utils_content)
        self.assertIn('function copyBrandsPresentationText', utils_content)

    def test_tables_mtd_dynamics_sync_and_structure(self):
        root_tables = os.path.join(BASE_DIR, 'js', 'tables.js')
        site_tables = os.path.join(JS_DIR, 'tables.js')
        self.assertTrue(os.path.exists(root_tables), "js/tables.js missing")
        self.assertTrue(os.path.exists(site_tables), "site/js/tables.js missing")
        with open(root_tables, 'r', encoding='utf-8') as f1, open(site_tables, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/tables.js and site/js/tables.js must be identical")

        with open(site_tables, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('isMtd', content, "tables.js must define isMtd")
        self.assertIn('maxCurDay', content, "tables.js must compute maxCurDay for MTD comparison")
        self.assertIn('mtdBadgeB2CBrands', content, "tables.js must update mtdBadgeB2CBrands")
        self.assertIn('mtdBadgeB2CStruct', content, "tables.js must update mtdBadgeB2CStruct")
        self.assertIn('mtdTitleAttr', content, "tables.js must set informative mtdTitleAttr")

        site_index = os.path.join(SITE_DIR, 'index.html')
        with open(site_index, 'r', encoding='utf-8') as f:
            index_content = f.read()
        self.assertIn('mtdBadgeB2CBrands', index_content, "index.html must have mtdBadgeB2CBrands element")
        self.assertIn('mtdBadgeB2CStruct', index_content, "index.html must have mtdBadgeB2CStruct element")

    def test_lead_geo_modal_period_sync(self):
        root_geo = os.path.join(BASE_DIR, 'js', 'lead-geo.js')
        site_geo = os.path.join(JS_DIR, 'lead-geo.js')
        self.assertTrue(os.path.exists(root_geo), "js/lead-geo.js missing")
        self.assertTrue(os.path.exists(site_geo), "site/js/lead-geo.js missing")
        with open(root_geo, 'r', encoding='utf-8') as f1, open(site_geo, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/lead-geo.js and site/js/lead-geo.js must be identical")

        with open(site_geo, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('getActiveLeadGeoMonth', content, "lead-geo.js must define getActiveLeadGeoMonth helper")
        self.assertIn('c.month === activeMonth', content, "lead-geo.js drilldowns must filter clients by activeMonth")
        self.assertIn('Период: ${periodLabel}', content, "lead-geo.js drilldowns must display period in subtitle")

if __name__ == '__main__':
    unittest.main()

