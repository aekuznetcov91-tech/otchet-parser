import unittest
import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestChikharevSalesPlan(unittest.TestCase):
    def test_01_files_parity(self):
        root_kam = os.path.join(BASE_DIR, 'js', 'kam-dashboard.js')
        site_kam = os.path.join(BASE_DIR, 'site', 'js', 'kam-dashboard.js')
        with open(root_kam, 'r', encoding='utf-8') as f1, open(site_kam, 'r', encoding='utf-8') as f2:
            self.assertEqual(f1.read(), f2.read(), "js/kam-dashboard.js and site/js/kam-dashboard.js must be identical")

    def test_02_chikharev_plans_in_node(self):
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

        // Filter for Alexei Chikharev
        setKamManagerFilter('Алексей Чихарев');
        const agg = getKamAggregatedData({ mode: 'month', month: '2026-09' });

        console.log('Overall plan:', agg.summary.overall_plan);
        console.log('Sum partner plans:', agg.summary.sum_partner_plans);

        if (agg.summary.overall_plan !== 550) {
            console.error('FAIL: overall_plan expected 550, got:', agg.summary.overall_plan);
            process.exit(1);
        }
        if (agg.summary.sum_partner_plans !== 553) {
            console.error('FAIL: sum_partner_plans expected 553, got:', agg.summary.sum_partner_plans);
            process.exit(2);
        }

        // Verify key partners
        const expectedPlans = {
            "1070": 10, // БорисХоф
            "1099": 1,  // Деливери Кар
            "1059": 10, // Измайлово
            "1042": 2,  // Автодин
            "1133": 6,  // Тауэр Орехово
            "1111": 20, // У Сервис
            "1154": 20, // Автодом
            "1130": 25, // АСЦ
            "1120": 60, // Маркар Групп
            "1052": 30, // Квазар
            "1095": 1,  // КМ/ч
            "1091": 50, // Кунцево
            "1160": 2,  // Автопассаж
            "1044": 5,  // Мейджер
            "1135": 8,  // ЭрСи Автотрейд
            "1227": 7,  // Фаворит
            "1261": 15, // Империя(независимость)
            "1076": 70, // Автопрестиж
            "1102": 3,  // Автокласс
            "1050": 1,  // Автоград
            "1258": 10, // Важная персона
            "1117": 2,  // Парус
            "1041": 15, // Радар
            "1090": 1,  // Анкар
            "1124": 25, // Млада Авто
            "1126": 2,  // Автоцентр Лада
            "1040": 10, // Авто Премиум Тверь
            "1046": 8,  // Звезда Ярославии
            "1087": 5,  // Автоимпорт
            "1082": 76, // Диалог
            "1201": 10, // КАН АВТО
            "1233": 23, // Барс Авто
            "1054": 20  // Апельсин
        };

        let verifiedCount = 0;
        agg.partners.forEach(p => {
            const sid = String(p.id);
            if (expectedPlans[sid] !== undefined) {
                if (p.plan !== expectedPlans[sid]) {
                    console.error(`FAIL: Partner ${sid} (${p.name}): expected plan ${expectedPlans[sid]}, got ${p.plan}`);
                    process.exit(3);
                }
                verifiedCount++;
            }
        });

        console.log(`Verified ${verifiedCount} of ${Object.keys(expectedPlans).length} target partners in table.`);
        if (verifiedCount !== Object.keys(expectedPlans).length) {
            console.error('FAIL: Not all expected partners were found in the table!');
            process.exit(4);
        }

        console.log('SUCCESS_ALL_PLANS_MATCHED');
        process.exit(0);
        """
        proc = subprocess.run(['node', '-e', script_code], cwd=BASE_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node verification failed: {proc.stdout} {proc.stderr}")
        self.assertIn('SUCCESS_ALL_PLANS_MATCHED', proc.stdout)

if __name__ == '__main__':
    unittest.main()
