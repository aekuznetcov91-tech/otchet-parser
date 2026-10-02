"""Behavior contracts for independent sale and prepayment periods."""
import os
import subprocess
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
NODE_BIN = BASE_DIR / 'scratch/tools/node-v20.18.0-darwin-arm64/bin/node'


class TestPeriodFiltering(unittest.TestCase):
    def test_period_selection_contract(self):
        if not NODE_BIN.exists():
            self.skipTest('Local node binary not found')
        script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const context = vm.createContext({window: {}, document: {getElementById: () => null}});
for (const file of ['utils.js', 'data-loader.js']) {
    vm.runInContext(fs.readFileSync('site/js/' + file, 'utf8'), context);
}
const rows = [
    {id: 'cross-month', SaleQty: 1, PrepayQty: 1, SaleMonth: '2026-10', PrepayMonth: '2026-09', DealDate: 46296, PrepayDate: 46295},
    {id: 'prepay-only', SaleQty: 0, PrepayQty: 1, SaleMonth: '2026-10', PrepayMonth: '2026-10', DealDate: 46296, PrepayDate: 46296},
    {id: 'no-date', SaleQty: 1, PrepayQty: 0, SaleMonth: '2026-10', DealDate: 0},
    {id: 'outside', SaleQty: 1, PrepayQty: 1, SaleMonth: '2026-11', PrepayMonth: '2026-11', DealDate: 46327, PrepayDate: 46327},
    {id: 'missing-qty', DealDate: 46296, PrepayDate: 46296}
];
rows.forEach(Object.freeze);
Object.freeze(rows);
function selected(config) {
    const before = JSON.stringify(config);
    const result = context.selectDashboardData(rows, Object.freeze(config));
    assert.equal(JSON.stringify(config), before);
    for (const row of [...result.sDb, ...result.pDb]) assert(rows.includes(row));
    return JSON.parse(JSON.stringify({sales: result.sDb.map(r => r.id), prepays: result.pDb.map(r => r.id)}));
}
assert.deepEqual(selected({mode: 'all'}), {
    sales: ['cross-month', 'no-date', 'outside'], prepays: ['cross-month', 'prepay-only', 'outside']
});
assert.deepEqual(selected({mode: 'month', month: '2026-10'}), {
    sales: ['cross-month', 'no-date'], prepays: ['prepay-only']
});
assert.deepEqual(selected({mode: 'month', month: '2026-09'}), {
    sales: [], prepays: ['cross-month']
});
const day = context.excelToJSDate(46296);
assert.deepEqual(selected({mode: 'custom', from: day, to: day}), {
    sales: ['cross-month', 'missing-qty'], prepays: ['prepay-only', 'missing-qty']
});
assert.deepEqual(selected({mode: 'custom', from: new Date(day.getTime() + 1), to: new Date(day.getTime() + 1000)}), {
    sales: [], prepays: []
});
assert.deepEqual(selected({mode: 'unknown'}), {sales: [], prepays: []});
assert.equal(context.selectDashboardData([], {mode: 'all'}).sDb.length, 0);
// The existing UI entry point must delegate using current global state.
context.fixtureRows = rows;
vm.runInContext("db = fixtureRows; currentFilterConfig = {mode: 'month', month: '2026-09'}", context);
assert.equal(context.getFilteredData().pDb[0], rows[0]);
console.log('OK');
"""
        for timezone in ('UTC', 'Europe/Moscow', 'America/New_York'):
            with self.subTest(timezone=timezone):
                result = subprocess.run(
                    [str(NODE_BIN), '-e', script], cwd=BASE_DIR,
                    env={**os.environ, 'TZ': timezone},
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
