import unittest
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestSoldatovaAudit(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(BASE_DIR, 'data.json'), 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def test_01_leon_auto_split(self):
        sys_partners = self.data.get('sys_db_partners', [])
        # Yoshkar-Ola Leon records must be Dobrolyubova
        yola_records = [r for r in sys_partners if r.get('PartnerId') == 1016 or 'online ооо "леон"' in str(r.get('RawPartner','')).lower()]
        self.assertTrue(len(yola_records) > 0, "Expected at least 1 record for Leon Auto Yoshkar-Ola")
        for r in yola_records:
            self.assertEqual(r.get('KAM'), 'Евгения Добролюбова')
            self.assertEqual(r.get('PartnerId'), 1016)

        # Krasnodar Leon records must be Soldatova
        krd_records = [r for r in sys_partners if r.get('PartnerId') == 1023]
        self.assertTrue(len(krd_records) > 0, "Expected at least 1 record for Leon Auto Krasnodar")
        for r in krd_records:
            self.assertEqual(r.get('KAM'), 'Валерия Солдатова')

    def test_02_optima_merged(self):
        sys_partners = self.data.get('sys_db_partners', [])
        # 1007 must not exist in sys_db_partners, must be 1030
        donor_records = [r for r in sys_partners if r.get('PartnerId') == 1007]
        self.assertEqual(len(donor_records), 0, "Partner 1007 should be merged into 1030")
        target_records = [r for r in sys_partners if r.get('PartnerId') == 1030]
        self.assertTrue(len(target_records) > 0)
        for r in target_records:
            self.assertEqual(r.get('KAM'), 'Валерия Солдатова')

    def test_03_wagner_autoretail_split(self):
        sys_partners = self.data.get('sys_db_partners', [])
        krd = [r for r in sys_partners if r.get('PartnerId') == 1285 and 'КРАСНОДАР' in str(r.get('RawPartner','')).upper()]
        spb = [r for r in sys_partners if r.get('PartnerId') == 1285 and 'СПБ' in str(r.get('RawPartner','')).upper()]
        self.assertTrue(len(krd) > 0, "Expected Krasnodar Autoretail records")
        self.assertTrue(len(spb) > 0, "Expected SPb Autoretail records")
        for r in krd:
            self.assertEqual(r.get('KAM'), 'Валерия Солдатова')
        for r in spb:
            self.assertEqual(r.get('KAM'), 'Светлана Дариенко')

    def test_04_transfor_tehnotemp_globus_merged(self):
        sys_partners = self.data.get('sys_db_partners', [])
        # Transfor: 632021 merged into 1003
        self.assertEqual(len([r for r in sys_partners if r.get('PartnerId') == 632021]), 0)
        # Tehno-Temp: 632016 merged into 1004
        self.assertEqual(len([r for r in sys_partners if r.get('PartnerId') == 632016]), 0)
        # Globus: 1182 and 632045 merged into 1013
        self.assertEqual(len([r for r in sys_partners if r.get('PartnerId') in [1182, 632045]]), 0)

    def test_05_rmotors_all_cities_darienko(self):
        sys_partners = self.data.get('sys_db_partners', [])
        rm_records = [r for r in sys_partners if r.get('PartnerId') == 1025 or 'р-моторс' in str(r.get('RawPartner','')).lower()]
        self.assertTrue(len(rm_records) > 0)
        for r in rm_records:
            self.assertEqual(r.get('KAM'), 'Светлана Дариенко')
            self.assertEqual(r.get('PartnerId'), 1025)

    def test_06_alarm_ozerki_merged(self):
        sys_partners = self.data.get('sys_db_partners', [])
        self.assertEqual(len([r for r in sys_partners if r.get('PartnerId') == 632048]), 0)

if __name__ == '__main__':
    unittest.main()
