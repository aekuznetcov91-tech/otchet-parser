import unittest
import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestKamSubrowsAndAllocation(unittest.TestCase):
    def test_01_files_parity(self):
        root_kam = os.path.join(BASE_DIR, 'js', 'kam-dashboard.js')
        site_kam = os.path.join(BASE_DIR, 'site', 'js', 'kam-dashboard.js')
        with open(root_kam, 'r', encoding='utf-8') as f1, open(site_kam, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/kam-dashboard.js and site/js/kam-dashboard.js must be identical")

    def test_02_id1040_in_registries(self):
        reg_file = os.path.join(BASE_DIR, 'partners_registry.json')
        with open(reg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        partners = data.get('partners', [])
        p1040 = next((p for p in partners if p.get('partner_id') == 1040), None)
        self.assertIsNotNone(p1040, "ID 1040 missing in partners_registry.json")
        self.assertEqual(p1040.get('canonical_name'), 'Авто Премиум Тверь')
        self.assertEqual(p1040.get('kam'), 'Алексей Чихарев')
        self.assertNotEqual(p1040.get('holding'), 'ONLIN', "Holding for 1040 must not be ONLIN")
        self.assertEqual(p1040.get('holding'), 'Авто Премиум')
        for alias in p1040.get('bitrix_aliases', []) + p1040.get('bi_aliases', []):
            self.assertNotIn('onlin', alias.lower().split(), "Generic 'onlin' must not be in aliases")

    def test_03_kam_aggregation_subrows_and_allocation(self):
        script_code = """
        const fs = require('fs');
        const path = require('path');
        const d = JSON.parse(fs.readFileSync('data.json', 'utf8'));

        global.window = { dataPayload: d };
        global.currentFilterConfig = { mode: 'month', month: '2026-09' };
        global.localStorage = { getItem: () => null, setItem: () => {} };
        global.sessionStorage = { getItem: () => null, setItem: () => {} };

        global.document = {
            querySelectorAll: () => [],
            getElementById: () => null
        };

        const kamCode = fs.readFileSync(path.join('js', 'kam-dashboard.js'), 'utf8');
        eval(kamCode);

        // 1. Check under Darienko
        setKamManagerFilter('Светлана Дариенко');
        const aggDarienko = getKamAggregatedData({ mode: 'month', month: '2026-09' });
        const p1040Darienko = aggDarienko.partners.filter(p => p.id === 1040);
        if (p1040Darienko.length > 0) {
            console.error('FAIL: ID 1040 found under Darienko:', p1040Darienko.length);
            process.exit(1);
        }

        // 2. Check under Chikharev
        setKamManagerFilter('Алексей Чихарев');
        const aggChikharev = getKamAggregatedData({ mode: 'month', month: '2026-09' });
        const p1040Chikharev = aggChikharev.partners.filter(p => p.id === 1040);
        if (p1040Chikharev.length === 0) {
            console.error('FAIL: ID 1040 missing under Chikharev');
            process.exit(2);
        }

        // 3. Check for any partner with brands but 0 cities
        setKamManagerFilter('all');
        const aggAll = getKamAggregatedData({ mode: 'month', month: '2026-09' });
        let emptyCitiesCount = 0;
        aggAll.partners.forEach(p => {
            const cCount = Object.keys(p.cities || {}).length;
            const bCount = Object.keys(p.brands || {}).length;
            if (bCount > 0 && cCount === 0) {
                emptyCitiesCount++;
            }
        });
        if (emptyCitiesCount > 0) {
            console.error('FAIL: Partners with brands but 0 cities:', emptyCitiesCount);
            process.exit(3);
        }

        console.log('SUCCESS');
        process.exit(0);
        """
        proc = subprocess.run(['node', '-e', script_code], cwd=BASE_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node verification failed: {proc.stdout} {proc.stderr}")
        self.assertIn('SUCCESS', proc.stdout)

if __name__ == '__main__':
    unittest.main()
