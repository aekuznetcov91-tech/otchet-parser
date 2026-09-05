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
            os.path.join(JS_DIR, 'banking-dashboard.js')
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

if __name__ == '__main__':
    unittest.main()
