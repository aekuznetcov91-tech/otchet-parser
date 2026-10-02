"""Pinned history and domain invariants independent of module layout."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / 'scratch/tools/node-v20.18.0-darwin-arm64/bin/node'


class TestBusinessContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / 'site/data.json').read_text())

    def test_closed_months_preserve_exact_row_contents(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/closed_months.json').read_text())
        for month, expected in fixtures.items():
            with self.subTest(month=month):
                rows = [r for r in self.payload['sys_db'] if month in (r.get('SaleMonth'), r.get('PrepayMonth'))]
                encoded = sorted(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')) for r in rows)
                self.assertEqual(len(rows), expected['rows'])
                self.assertEqual(hashlib.sha256('\n'.join(encoded).encode()).hexdigest(), expected['sha256'])
        self.assertEqual(fixtures['2026-08']['sales'], 1776)

    def test_revenue_excludes_vat(self):
        for row in self.payload['sys_db']:
            if row.get('SaleQty', 0) > 0 and row.get('Comm', 0) > 0:
                self.assertAlmostEqual(row['Revenue'], round(row['Comm'] / 1.22, 2), places=2)

    def test_partner_transfer_registry_has_no_duplicates(self):
        keys = [(r.get('PartnerId') if r.get('PartnerId') is not None else r.get('Partner'),
                 r.get('ClientId'), r.get('Month'))
                for r in self.payload['sys_db_partners'] if r.get('Type') == 'Лид']
        self.assertEqual(len(keys), len(set(keys)))

    def test_kam_totals_rooftops_and_lead_fallback(self):
        if not NODE.exists(): self.skipTest('Local node binary not found')
        script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert/strict');
const payload = JSON.parse(fs.readFileSync('site/data.json', 'utf8'));
const originalPayload = JSON.stringify(payload);
const ctx = vm.createContext({setTimeout: () => {}, window: {dataPayload: payload},
    localStorage: {getItem: () => null, setItem: () => {}},
    sessionStorage: {getItem: () => null, setItem: () => {}},
    document: {querySelectorAll: () => [], getElementById: () => null}});
vm.runInContext(fs.readFileSync('site/js/utils.js', 'utf8'), ctx);
vm.runInContext(fs.readFileSync('site/js/kam-dashboard.js', 'utf8'), ctx);
for (const month of ['2026-08', '2026-09', '2026-10', 'all']) {
    ctx.window.selectedKamMonth = month;
    const cfg = {mode: month === 'all' ? 'all' : 'month', month};
    const agg = ctx.getKamAggregatedData(cfg), s = agg.summary;
    assert.equal(s.trans_leads, agg.partners.reduce((sum, p) => sum + p.trans_leads, 0));
    assert.equal(s.total_deals, agg.partners.reduce((sum, p) => sum + p.total_deals, 0));
    assert.equal(s.rooftops.length, new Set(s.rooftops.map(r => r.key)).size);
    assert.equal(s.active_rooftops_count, s.rooftops.filter(r => r.deals_count > 0).length);
    assert.equal(s.total_assigned_rooftops, s.active_rooftops_count + s.sleeping_rooftops_count);

}

assert.equal(JSON.stringify(payload), originalPayload, 'Aggregation must not mutate source data');
const kam = 'Алексей Чихарев';
ctx.window.dataPayload = {
    partners_registry: [{partner_id: 42, canonical_name: 'Тестовый дилер', kam,
        oem_data: [{city: 'Москва', brands: ['LADA', 'HAVAL'], responsible: kam},
                   {city: 'Казань', brands: ['LADA'], responsible: kam}]}],
    sys_db_partners: [
        {PartnerId: 42, Partner: 'Тестовый дилер', KAM: kam, Month: '2026-09', Type: 'Лид', Qty: 2, Brand: 'LADA'},
        {PartnerId: 42, Partner: 'Тестовый дилер', KAM: kam, Month: '2026-09', Type: 'Сделка', Qty: 1, Brand: 'LADA', City: 'Москва'}
    ],
    lead_geo_dealers: {regions: [{dealers: [{dealer_name: 'Тестовый дилер', total_clients: 10, trans_clients: 8, top_brands: ['LADA']}]}]}
};
ctx.window.selectedKamMonth = '2026-09';
let result = ctx.getKamAggregatedData({mode: 'month', month: '2026-09'});
assert.equal(result.summary.trans_leads, 2, 'Geo transfers must not be added to registry transfers');
assert.equal(result.summary.total_assigned_rooftops, 3);
assert.equal(result.summary.active_rooftops_count, 1);
ctx.window.dataPayload.sys_db_partners = ctx.window.dataPayload.sys_db_partners.filter(r => r.Type !== 'Лид');
result = ctx.getKamAggregatedData({mode: 'month', month: '2026-09'});
assert.equal(result.summary.trans_leads, 8, 'Geo transfers are the fallback when the registry has no leads');

"""
        result = subprocess.run([str(NODE), '-e', script], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
