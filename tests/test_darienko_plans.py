import unittest
import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestDarienkoSalesPlan(unittest.TestCase):
    def test_01_files_parity(self):
        root_kam = os.path.join(BASE_DIR, 'js', 'kam-dashboard.js')
        site_kam = os.path.join(BASE_DIR, 'site', 'js', 'kam-dashboard.js')
        with open(root_kam, 'r', encoding='utf-8') as f1, open(site_kam, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/kam-dashboard.js and site/js/kam-dashboard.js must be identical")

    def test_02_darienko_plans_in_node(self):
        script_code = """
        const fs = require('fs');
        const path = require('path');
        const d = JSON.parse(fs.readFileSync('data.json', 'utf8'));

        const localStoreMock = {};
        global.window = { dataPayload: d };
        global.currentFilterConfig = { mode: 'month', month: '2026-09' };
        global.localStorage = {
            getItem: (k) => localStoreMock[k] || null,
            setItem: (k, v) => { localStoreMock[k] = String(v); },
            removeItem: (k) => { delete localStoreMock[k]; }
        };
        global.sessionStorage = {
            getItem: () => null,
            setItem: () => {}
        };
        global.document = {
            querySelectorAll: () => [],
            getElementById: () => null
        };

        const kamCode = fs.readFileSync(path.join('js', 'kam-dashboard.js'), 'utf8');
        eval(kamCode);

        // 1. Verify Svetlana Darienko
        setKamManagerFilter('Светлана Дариенко');
        const aggDarienko = getKamAggregatedData({ mode: 'month', month: '2026-09' });

        console.log('Darienko overall plan:', aggDarienko.summary.overall_plan);
        console.log('Darienko sum partner plans:', aggDarienko.summary.sum_partner_plans);

        if (aggDarienko.summary.overall_plan !== 329) {
            console.error('FAIL: Darienko overall_plan expected 329, got:', aggDarienko.summary.overall_plan);
            process.exit(1);
        }
        if (aggDarienko.summary.sum_partner_plans !== 329) {
            console.error('FAIL: Darienko sum_partner_plans expected 329, got:', aggDarienko.summary.sum_partner_plans);
            process.exit(2);
        }

        const expectedDarienko = {
            "1285": 12, // Вагнер Авто / Авторитэйл
            "1002": 36, // Аларм-Моторс ГК
            "632032": 7, // Премиум Авто ONLINE
            "1005": 20, // Восток Авто
            "1163": 41, // Автохолдинг Максимум
            "1083": 16, // ООО "НЕВААВТО"
            "1017": 56, // Автопродикс
            "1063": 37, // Автополе
            "1192": 11, // ИАТ
            "1011": 9,  // ГК Сигма
            "1280": 8,  // Сократ (Моторленд СПб)
            "1032": 11, // ГК Форсаж
            "1001": 4,  // Автостиль СПб и Великий Новгород
            "1025": 7,  // Р-Моторс ЛАДА
            "1022": 8,  // Прагматика
            "1021": 1,  // Элан Моторс (Санкт Петербург)
            "1254": 3,  // Автотим
            "1219": 9,  // Элке Авто
            "1242": 1,  // Рус-Авто Трейд
            "1031": 14, // ГК ДИНАМИКА
            "1027": 1,  // Ай-Би-Эм
            "1245": 9,  // Картель
            "1257": 1,  // АлексМоторс
            "1068": 7   // Сармат
        };

        let darienkoVerified = 0;
        aggDarienko.partners.forEach(p => {
            const sid = String(p.id);
            if (expectedDarienko[sid] !== undefined) {
                if (p.plan !== expectedDarienko[sid]) {
                    console.error(`FAIL: Darienko partner ${sid} (${p.name}): expected plan ${expectedDarienko[sid]}, got ${p.plan}`);
                    process.exit(3);
                }
                darienkoVerified++;
            }
        });

        console.log(`Verified ${darienkoVerified} of ${Object.keys(expectedDarienko).length} target Darienko partners.`);
        if (darienkoVerified !== Object.keys(expectedDarienko).length) {
            console.error('FAIL: Not all expected Darienko partners found in table!');
            process.exit(4);
        }

        // 2. Verify Alexei Chikharev still 100% intact
        setKamManagerFilter('Алексей Чихарев');
        const aggChikharev = getKamAggregatedData({ mode: 'month', month: '2026-09' });
        if (aggChikharev.summary.overall_plan !== 550 || aggChikharev.summary.sum_partner_plans !== 553) {
            console.error('FAIL: Chikharev plans altered! Got overall:', aggChikharev.summary.overall_plan, 'sum:', aggChikharev.summary.sum_partner_plans);
            process.exit(5);
        }

        console.log('SUCCESS_ALL_DARIENKO_AND_CHIKHAREV_PLANS_VERIFIED');
        process.exit(0);
        """
        proc = subprocess.run(['node', '-e', script_code], cwd=BASE_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node verification failed: {proc.stdout} {proc.stderr}")
        self.assertIn('SUCCESS_ALL_DARIENKO_AND_CHIKHAREV_PLANS_VERIFIED', proc.stdout)

if __name__ == '__main__':
    unittest.main()
