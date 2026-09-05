/**
 * banking-dashboard.js
 * ====================
 * ТОП-10 и Антитоп-10 Партнеров по Банковскому проникновению:
 * СБЕР vs Другие Банки vs Наличные.
 * Точный перенос аналитического дашборда из проекта передачи лидов.
 */

const DEFAULT_BANKING_PAYLOAD = {
  "top10_sber_share": [
    {
      "partner": "ООО \"ВОРОНЕЖ-АВТО-СИТИ\" Online",
      "macro": "Центрально-Черноземный",
      "city": "Воронеж",
      "total_deals": 16,
      "sber_deals": 14,
      "other_banks_deals": 0,
      "cash_deals": 2,
      "credits_total": 14,
      "sber_ratio_total": 87.5,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 12.5,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "ONLINE O&J (ООО \"ОПТИМА КУБАНЬ\")",
      "macro": "Юг",
      "city": "Краснодар",
      "total_deals": 10,
      "sber_deals": 6,
      "other_banks_deals": 0,
      "cash_deals": 4,
      "credits_total": 6,
      "sber_ratio_total": 60.0,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 40.0,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "ООО \"ЭЛКЕ АВТО\" ONLINE",
      "macro": "Сибирь",
      "city": "Томск",
      "total_deals": 14,
      "sber_deals": 8,
      "other_banks_deals": 0,
      "cash_deals": 6,
      "credits_total": 8,
      "sber_ratio_total": 57.1,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 42.9,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "КВАЗАР",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 16,
      "sber_deals": 9,
      "other_banks_deals": 2,
      "cash_deals": 5,
      "credits_total": 11,
      "sber_ratio_total": 56.2,
      "sber_ratio_credit": 81.8,
      "ob_ratio_total": 12.5,
      "ob_ratio_credit": 18.2,
      "cash_ratio_total": 31.2,
      "competing_banks_str": "Sovcombank (1), VTB (1)",
      "top_competing_bank": "Sovcombank (1)"
    },
    {
      "partner": "Online Вагнер Авто / Авторитэйл",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 18,
      "sber_deals": 9,
      "other_banks_deals": 5,
      "cash_deals": 4,
      "credits_total": 14,
      "sber_ratio_total": 50.0,
      "sber_ratio_credit": 64.3,
      "ob_ratio_total": 27.8,
      "ob_ratio_credit": 35.7,
      "cash_ratio_total": 22.2,
      "competing_banks_str": "БАНК УРАЛСИБ (2), VTB (1), Кредит Европа Банк (Россия) (1)",
      "top_competing_bank": "БАНК УРАЛСИБ (2)"
    },
    {
      "partner": "ONLINE Башавтоком (ООО \"БАШАВТОКОМ-В\")",
      "macro": "Волга",
      "city": "Уфа",
      "total_deals": 20,
      "sber_deals": 9,
      "other_banks_deals": 0,
      "cash_deals": 11,
      "credits_total": 9,
      "sber_ratio_total": 45.0,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 55.0,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "ONLINE ФДЦ Автопрестиж",
      "macro": "Юг",
      "city": "Волгоград",
      "total_deals": 30,
      "sber_deals": 12,
      "other_banks_deals": 1,
      "cash_deals": 17,
      "credits_total": 13,
      "sber_ratio_total": 40.0,
      "sber_ratio_credit": 92.3,
      "ob_ratio_total": 3.3,
      "ob_ratio_credit": 7.7,
      "cash_ratio_total": 56.7,
      "competing_banks_str": "ЛОКО-Банк (1)",
      "top_competing_bank": "ЛОКО-Банк (1)"
    },
    {
      "partner": "Аларм-Моторс ГК",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 15,
      "sber_deals": 6,
      "other_banks_deals": 2,
      "cash_deals": 7,
      "credits_total": 8,
      "sber_ratio_total": 40.0,
      "sber_ratio_credit": 75.0,
      "ob_ratio_total": 13.3,
      "ob_ratio_credit": 25.0,
      "cash_ratio_total": 46.7,
      "competing_banks_str": "Sovcombank (1), Alfa-BANK (1)",
      "top_competing_bank": "Sovcombank (1)"
    },
    {
      "partner": "СберАвто",
      "macro": "Северо-Запад",
      "city": "Великий Новгород",
      "total_deals": 19,
      "sber_deals": 7,
      "other_banks_deals": 3,
      "cash_deals": 9,
      "credits_total": 10,
      "sber_ratio_total": 36.8,
      "sber_ratio_credit": 70.0,
      "ob_ratio_total": 15.8,
      "ob_ratio_credit": 30.0,
      "cash_ratio_total": 47.4,
      "competing_banks_str": "Sovcombank (2), Alfa-BANK (1)",
      "top_competing_bank": "Sovcombank (2)"
    },
    {
      "partner": "Приоритет_Автогермес",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 22,
      "sber_deals": 8,
      "other_banks_deals": 3,
      "cash_deals": 11,
      "credits_total": 11,
      "sber_ratio_total": 36.4,
      "sber_ratio_credit": 72.7,
      "ob_ratio_total": 13.6,
      "ob_ratio_credit": 27.3,
      "cash_ratio_total": 50.0,
      "competing_banks_str": "VTB (1), Alfa-BANK (1), Кредит Европа Банк (Россия) (1)",
      "top_competing_bank": "VTB (1)"
    }
  ],
  "top10_sber_volume": [
    {
      "partner": "ONLINE АВТОГЕРМЕС-ЗАПАД (ООО \"АВТОГЕРМЕС-ЗАПАД\")",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 472,
      "sber_deals": 35,
      "other_banks_deals": 32,
      "cash_deals": 405,
      "credits_total": 67,
      "sber_ratio_total": 7.4,
      "sber_ratio_credit": 52.2,
      "ob_ratio_total": 6.8,
      "ob_ratio_credit": 47.8,
      "cash_ratio_total": 85.8,
      "competing_banks_str": "VTB (14), Alfa-BANK (9), Sovcombank (4)",
      "top_competing_bank": "VTB (14)"
    },
    {
      "partner": "ООО \"ТЦ \"КУНЦЕВО ЛИМИТЕД\" ONLINE",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 95,
      "sber_deals": 27,
      "other_banks_deals": 0,
      "cash_deals": 68,
      "credits_total": 27,
      "sber_ratio_total": 28.4,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 71.6,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "Online ООО Самарские автомобили – М Север",
      "macro": "Урал",
      "city": "Пермь",
      "total_deals": 67,
      "sber_deals": 22,
      "other_banks_deals": 9,
      "cash_deals": 36,
      "credits_total": 31,
      "sber_ratio_total": 32.8,
      "sber_ratio_credit": 71.0,
      "ob_ratio_total": 13.4,
      "ob_ratio_credit": 29.0,
      "cash_ratio_total": 53.7,
      "competing_banks_str": "Кредит Европа Банк (Россия) (3), OTP Bank (2), БыстроБанк (2)",
      "top_competing_bank": "Кредит Европа Банк (Россия) (3)"
    },
    {
      "partner": "ONLINE ООО \"ПРОДИКС\"",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 51,
      "sber_deals": 17,
      "other_banks_deals": 1,
      "cash_deals": 33,
      "credits_total": 18,
      "sber_ratio_total": 33.3,
      "sber_ratio_credit": 94.4,
      "ob_ratio_total": 2.0,
      "ob_ratio_credit": 5.6,
      "cash_ratio_total": 64.7,
      "competing_banks_str": "Sovcombank (1)",
      "top_competing_bank": "Sovcombank (1)"
    },
    {
      "partner": "ООО \"МАРКАР ГРУПП\" ONLINE",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 139,
      "sber_deals": 16,
      "other_banks_deals": 81,
      "cash_deals": 42,
      "credits_total": 97,
      "sber_ratio_total": 11.5,
      "sber_ratio_credit": 16.5,
      "ob_ratio_total": 58.3,
      "ob_ratio_credit": 83.5,
      "cash_ratio_total": 30.2,
      "competing_banks_str": "TBank (30), VTB (25), OTP Bank (20)",
      "top_competing_bank": "TBank (30)"
    },
    {
      "partner": "ООО \"АВТОТРИУМФ\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 50,
      "sber_deals": 15,
      "other_banks_deals": 6,
      "cash_deals": 29,
      "credits_total": 21,
      "sber_ratio_total": 30.0,
      "sber_ratio_credit": 71.4,
      "ob_ratio_total": 12.0,
      "ob_ratio_credit": 28.6,
      "cash_ratio_total": 58.0,
      "competing_banks_str": "Акционерное общество МС Банк Рус (4), БАНК УРАЛСИБ (1), Alfa-BANK (1)",
      "top_competing_bank": "Акционерное общество МС Банк Рус (4)"
    },
    {
      "partner": "ООО \"ВОРОНЕЖ-АВТО-СИТИ\" Online",
      "macro": "Центрально-Черноземный",
      "city": "Воронеж",
      "total_deals": 16,
      "sber_deals": 14,
      "other_banks_deals": 0,
      "cash_deals": 2,
      "credits_total": 14,
      "sber_ratio_total": 87.5,
      "sber_ratio_credit": 100.0,
      "ob_ratio_total": 0.0,
      "ob_ratio_credit": 0.0,
      "cash_ratio_total": 12.5,
      "competing_banks_str": "Нет других банков",
      "top_competing_bank": "—"
    },
    {
      "partner": "ООО \"НЕВААВТО\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 40,
      "sber_deals": 13,
      "other_banks_deals": 1,
      "cash_deals": 26,
      "credits_total": 14,
      "sber_ratio_total": 32.5,
      "sber_ratio_credit": 92.9,
      "ob_ratio_total": 2.5,
      "ob_ratio_credit": 7.1,
      "cash_ratio_total": 65.0,
      "competing_banks_str": "OTP Bank (1)",
      "top_competing_bank": "OTP Bank (1)"
    },
    {
      "partner": "ООО \"АВТОПРОФИЛЬ\" ONLINE",
      "macro": "Волго-Вятка",
      "city": "Нижний Новгород",
      "total_deals": 89,
      "sber_deals": 13,
      "other_banks_deals": 27,
      "cash_deals": 49,
      "credits_total": 40,
      "sber_ratio_total": 14.6,
      "sber_ratio_credit": 32.5,
      "ob_ratio_total": 30.3,
      "ob_ratio_credit": 67.5,
      "cash_ratio_total": 55.1,
      "competing_banks_str": "OTP Bank (17), Sovcombank (8), TBank (2)",
      "top_competing_bank": "OTP Bank (17)"
    },
    {
      "partner": "ONLINE ФДЦ Автопрестиж",
      "macro": "Юг",
      "city": "Волгоград",
      "total_deals": 30,
      "sber_deals": 12,
      "other_banks_deals": 1,
      "cash_deals": 17,
      "credits_total": 13,
      "sber_ratio_total": 40.0,
      "sber_ratio_credit": 92.3,
      "ob_ratio_total": 3.3,
      "ob_ratio_credit": 7.7,
      "cash_ratio_total": 56.7,
      "competing_banks_str": "ЛОКО-Банк (1)",
      "top_competing_bank": "ЛОКО-Банк (1)"
    }
  ],
  "antitop10_ob_share": [
    {
      "partner": "ООО \"МАРКАР ГРУПП\" ONLINE",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 139,
      "sber_deals": 16,
      "other_banks_deals": 81,
      "cash_deals": 42,
      "credits_total": 97,
      "sber_ratio_total": 11.5,
      "sber_ratio_credit": 16.5,
      "ob_ratio_total": 58.3,
      "ob_ratio_credit": 83.5,
      "cash_ratio_total": 30.2,
      "competing_banks_str": "TBank (30), VTB (25), OTP Bank (20)",
      "top_competing_bank": "TBank (30)"
    },
    {
      "partner": "ООО \"МАКСИМУМ КРЕДИТ\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 30,
      "sber_deals": 3,
      "other_banks_deals": 16,
      "cash_deals": 11,
      "credits_total": 19,
      "sber_ratio_total": 10.0,
      "sber_ratio_credit": 15.8,
      "ob_ratio_total": 53.3,
      "ob_ratio_credit": 84.2,
      "cash_ratio_total": 36.7,
      "competing_banks_str": "Акционерное общество МС Банк Рус (12), БАНК УРАЛСИБ (2), Sovcombank (1)",
      "top_competing_bank": "Акционерное общество МС Банк Рус (12)"
    },
    {
      "partner": "ONLINE ООО \"ДИАЛОГ АВТО\"",
      "macro": "Волга",
      "city": "Набережные Челны",
      "total_deals": 22,
      "sber_deals": 3,
      "other_banks_deals": 9,
      "cash_deals": 10,
      "credits_total": 12,
      "sber_ratio_total": 13.6,
      "sber_ratio_credit": 25.0,
      "ob_ratio_total": 40.9,
      "ob_ratio_credit": 75.0,
      "cash_ratio_total": 45.5,
      "competing_banks_str": "Sovcombank (8), БАНК УРАЛСИБ (1)",
      "top_competing_bank": "Sovcombank (8)"
    },
    {
      "partner": "ООО \"ДИНАМИКА ВОЛОГДА\" ONLINE",
      "macro": "Северо-Запад",
      "city": "Вологда",
      "total_deals": 25,
      "sber_deals": 1,
      "other_banks_deals": 8,
      "cash_deals": 16,
      "credits_total": 9,
      "sber_ratio_total": 4.0,
      "sber_ratio_credit": 11.1,
      "ob_ratio_total": 32.0,
      "ob_ratio_credit": 88.9,
      "cash_ratio_total": 64.0,
      "competing_banks_str": "OTP Bank (6), БАНК УРАЛСИБ (2)",
      "top_competing_bank": "OTP Bank (6)"
    },
    {
      "partner": "ООО \"АВТОПОЛЕ Н\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 61,
      "sber_deals": 10,
      "other_banks_deals": 19,
      "cash_deals": 32,
      "credits_total": 29,
      "sber_ratio_total": 16.4,
      "sber_ratio_credit": 34.5,
      "ob_ratio_total": 31.1,
      "ob_ratio_credit": 65.5,
      "cash_ratio_total": 52.5,
      "competing_banks_str": "Акционерное общество МС Банк Рус (9), OTP Bank (7), TBank (1)",
      "top_competing_bank": "Акционерное общество МС Банк Рус (9)"
    },
    {
      "partner": "ООО \"АВТОМИР-ТРЕЙД\" online",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 68,
      "sber_deals": 4,
      "other_banks_deals": 21,
      "cash_deals": 43,
      "credits_total": 25,
      "sber_ratio_total": 5.9,
      "sber_ratio_credit": 16.0,
      "ob_ratio_total": 30.9,
      "ob_ratio_credit": 84.0,
      "cash_ratio_total": 63.2,
      "competing_banks_str": "Sovcombank (11), VTB (5), Alfa-BANK (5)",
      "top_competing_bank": "Sovcombank (11)"
    },
    {
      "partner": "Online Фининвест",
      "macro": "Юг",
      "city": "Ростов-на-Дону",
      "total_deals": 62,
      "sber_deals": 11,
      "other_banks_deals": 19,
      "cash_deals": 32,
      "credits_total": 30,
      "sber_ratio_total": 17.7,
      "sber_ratio_credit": 36.7,
      "ob_ratio_total": 30.6,
      "ob_ratio_credit": 63.3,
      "cash_ratio_total": 51.6,
      "competing_banks_str": "TBank (8), VTB (4), OTP Bank (4)",
      "top_competing_bank": "TBank (8)"
    },
    {
      "partner": "ООО \"АВТОПРОФИЛЬ\" ONLINE",
      "macro": "Волго-Вятка",
      "city": "Нижний Новгород",
      "total_deals": 89,
      "sber_deals": 13,
      "other_banks_deals": 27,
      "cash_deals": 49,
      "credits_total": 40,
      "sber_ratio_total": 14.6,
      "sber_ratio_credit": 32.5,
      "ob_ratio_total": 30.3,
      "ob_ratio_credit": 67.5,
      "cash_ratio_total": 55.1,
      "competing_banks_str": "OTP Bank (17), Sovcombank (8), TBank (2)",
      "top_competing_bank": "OTP Bank (17)"
    },
    {
      "partner": "Online ГК Диалог \\ ООО \"Управляющая компания Диалог\"",
      "macro": "Волга",
      "city": "Казань",
      "total_deals": 63,
      "sber_deals": 11,
      "other_banks_deals": 19,
      "cash_deals": 33,
      "credits_total": 30,
      "sber_ratio_total": 17.5,
      "sber_ratio_credit": 36.7,
      "ob_ratio_total": 30.2,
      "ob_ratio_credit": 63.3,
      "cash_ratio_total": 52.4,
      "competing_banks_str": "Sovcombank (9), Alfa-BANK (3), Кредит Европа Банк (Россия) (3)",
      "top_competing_bank": "Sovcombank (9)"
    },
    {
      "partner": "Online Вагнер Авто / Авторитэйл",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 18,
      "sber_deals": 9,
      "other_banks_deals": 5,
      "cash_deals": 4,
      "credits_total": 14,
      "sber_ratio_total": 50.0,
      "sber_ratio_credit": 64.3,
      "ob_ratio_total": 27.8,
      "ob_ratio_credit": 35.7,
      "cash_ratio_total": 22.2,
      "competing_banks_str": "БАНК УРАЛСИБ (2), VTB (1), Кредит Европа Банк (Россия) (1)",
      "top_competing_bank": "БАНК УРАЛСИБ (2)"
    }
  ],
  "antitop10_ob_volume": [
    {
      "partner": "ООО \"МАРКАР ГРУПП\" ONLINE",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 139,
      "sber_deals": 16,
      "other_banks_deals": 81,
      "cash_deals": 42,
      "credits_total": 97,
      "sber_ratio_total": 11.5,
      "sber_ratio_credit": 16.5,
      "ob_ratio_total": 58.3,
      "ob_ratio_credit": 83.5,
      "cash_ratio_total": 30.2,
      "competing_banks_str": "TBank (30), VTB (25), OTP Bank (20)",
      "top_competing_bank": "TBank (30)"
    },
    {
      "partner": "ONLINE АВТОГЕРМЕС-ЗАПАД (ООО \"АВТОГЕРМЕС-ЗАПАД\")",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 472,
      "sber_deals": 35,
      "other_banks_deals": 32,
      "cash_deals": 405,
      "credits_total": 67,
      "sber_ratio_total": 7.4,
      "sber_ratio_credit": 52.2,
      "ob_ratio_total": 6.8,
      "ob_ratio_credit": 47.8,
      "cash_ratio_total": 85.8,
      "competing_banks_str": "VTB (14), Alfa-BANK (9), Sovcombank (4)",
      "top_competing_bank": "VTB (14)"
    },
    {
      "partner": "ONLINE ООО \"АМКАПИТАЛ\"",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 130,
      "sber_deals": 7,
      "other_banks_deals": 29,
      "cash_deals": 94,
      "credits_total": 36,
      "sber_ratio_total": 5.4,
      "sber_ratio_credit": 19.4,
      "ob_ratio_total": 22.3,
      "ob_ratio_credit": 80.6,
      "cash_ratio_total": 72.3,
      "competing_banks_str": "OTP Bank (10), Sovcombank (6), Alfa-BANK (6)",
      "top_competing_bank": "OTP Bank (10)"
    },
    {
      "partner": "ООО \"АВТОПРОФИЛЬ\" ONLINE",
      "macro": "Волго-Вятка",
      "city": "Нижний Новгород",
      "total_deals": 89,
      "sber_deals": 13,
      "other_banks_deals": 27,
      "cash_deals": 49,
      "credits_total": 40,
      "sber_ratio_total": 14.6,
      "sber_ratio_credit": 32.5,
      "ob_ratio_total": 30.3,
      "ob_ratio_credit": 67.5,
      "cash_ratio_total": 55.1,
      "competing_banks_str": "OTP Bank (17), Sovcombank (8), TBank (2)",
      "top_competing_bank": "OTP Bank (17)"
    },
    {
      "partner": "ООО \"АВТОМИР-ТРЕЙД\" online",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 68,
      "sber_deals": 4,
      "other_banks_deals": 21,
      "cash_deals": 43,
      "credits_total": 25,
      "sber_ratio_total": 5.9,
      "sber_ratio_credit": 16.0,
      "ob_ratio_total": 30.9,
      "ob_ratio_credit": 84.0,
      "cash_ratio_total": 63.2,
      "competing_banks_str": "Sovcombank (11), VTB (5), Alfa-BANK (5)",
      "top_competing_bank": "Sovcombank (11)"
    },
    {
      "partner": "ООО \"АВТОПОЛЕ Н\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 61,
      "sber_deals": 10,
      "other_banks_deals": 19,
      "cash_deals": 32,
      "credits_total": 29,
      "sber_ratio_total": 16.4,
      "sber_ratio_credit": 34.5,
      "ob_ratio_total": 31.1,
      "ob_ratio_credit": 65.5,
      "cash_ratio_total": 52.5,
      "competing_banks_str": "Акционерное общество МС Банк Рус (9), OTP Bank (7), TBank (1)",
      "top_competing_bank": "Акционерное общество МС Банк Рус (9)"
    },
    {
      "partner": "Online Фининвест",
      "macro": "Юг",
      "city": "Ростов-на-Дону",
      "total_deals": 62,
      "sber_deals": 11,
      "other_banks_deals": 19,
      "cash_deals": 32,
      "credits_total": 30,
      "sber_ratio_total": 17.7,
      "sber_ratio_credit": 36.7,
      "ob_ratio_total": 30.6,
      "ob_ratio_credit": 63.3,
      "cash_ratio_total": 51.6,
      "competing_banks_str": "TBank (8), VTB (4), OTP Bank (4)",
      "top_competing_bank": "TBank (8)"
    },
    {
      "partner": "Online ГК Диалог \\ ООО \"Управляющая компания Диалог\"",
      "macro": "Волга",
      "city": "Казань",
      "total_deals": 63,
      "sber_deals": 11,
      "other_banks_deals": 19,
      "cash_deals": 33,
      "credits_total": 30,
      "sber_ratio_total": 17.5,
      "sber_ratio_credit": 36.7,
      "ob_ratio_total": 30.2,
      "ob_ratio_credit": 63.3,
      "cash_ratio_total": 52.4,
      "competing_banks_str": "Sovcombank (9), Alfa-BANK (3), Кредит Европа Банк (Россия) (3)",
      "top_competing_bank": "Sovcombank (9)"
    },
    {
      "partner": "ООО \"МАКСИМУМ КРЕДИТ\" online",
      "macro": "Северо-Запад",
      "city": "Санкт-Петербург",
      "total_deals": 30,
      "sber_deals": 3,
      "other_banks_deals": 16,
      "cash_deals": 11,
      "credits_total": 19,
      "sber_ratio_total": 10.0,
      "sber_ratio_credit": 15.8,
      "ob_ratio_total": 53.3,
      "ob_ratio_credit": 84.2,
      "cash_ratio_total": 36.7,
      "competing_banks_str": "Акционерное общество МС Банк Рус (12), БАНК УРАЛСИБ (2), Sovcombank (1)",
      "top_competing_bank": "Акционерное общество МС Банк Рус (12)"
    },
    {
      "partner": "АО \"РОЛЬФ\" ONLINE",
      "macro": "Москва",
      "city": "Москва",
      "total_deals": 176,
      "sber_deals": 9,
      "other_banks_deals": 16,
      "cash_deals": 151,
      "credits_total": 25,
      "sber_ratio_total": 5.1,
      "sber_ratio_credit": 36.0,
      "ob_ratio_total": 9.1,
      "ob_ratio_credit": 64.0,
      "cash_ratio_total": 85.8,
      "competing_banks_str": "Sovcombank (11), VTB (2), TBank (2)",
      "top_competing_bank": "Sovcombank (11)"
    }
  ]
};

let currentBankingMode = 'share'; // 'share' or 'volume'
let topSberChart = null;
let antiTopChart = null;

function getBankingDataPayload() {
    const p = (window.dataPayload && window.dataPayload.banking_analytics)
           || (window.currentData && window.currentData.banking_analytics)
           || (window.bankingAnalyticsData);

    if (p && p.top10_sber_share && p.top10_sber_share.length > 0) {
        return p;
    }
    return DEFAULT_BANKING_PAYLOAD;
}

function renderBankingDashboard() {
    renderRankings();
}

function renderRankings() {
    const sberChartCanvas = document.getElementById('topSberChart');
    const antiChartCanvas = document.getElementById('antiTopChart');
    const sberTbody = document.getElementById('topSberTbody');
    const antiTbody = document.getElementById('antiTopTbody');

    if (!sberChartCanvas || !antiChartCanvas || !sberTbody || !antiTbody) {
        return;
    }

    const payload = getBankingDataPayload();
    const isShare = currentBankingMode === 'share';
    const topSberData = isShare ? payload.top10_sber_share : payload.top10_sber_volume;
    const antiTopData = isShare ? payload.antitop10_ob_share : payload.antitop10_ob_volume;

    const btnShare = document.getElementById('btnShare');
    const btnVolume = document.getElementById('btnVolume');
    if (btnShare) btnShare.className = 'tab-btn ' + (isShare ? 'active' : '');
    if (btnVolume) btnVolume.className = 'tab-btn ' + (!isShare ? 'active' : '');

    const subSber = document.getElementById('topSberSubtitle');
    if (subSber) {
        subSber.innerText = isShare ?
            'Рейтинг по доле кредитов Сбера от общего объема сделок ДЦ (%)' :
            'Рейтинг по абсолютному количеству сделок Сбера (шт.)';
    }

    const subAnti = document.getElementById('antiTopSubtitle');
    if (subAnti) {
        subAnti.innerText = isShare ?
            'Рейтинг по доле сторонних банков от общего объема сделок ДЦ (%)' :
            'Рейтинг по абсолютному количеству сделок сторонних банков (шт.)';
    }

    // 1. Render Top Sber Table
    sberTbody.innerHTML = (topSberData || []).map((p, idx) => `
        <tr>
            <td class="center"><span class="rank-badge">${idx + 1}</span></td>
            <td class="partner-cell">
                <div class="name">${p.partner}</div>
                <div class="loc">${p.city || ''} • ${p.macro || ''}</div>
            </td>
            <td class="num"><b>${(p.total_deals || 0).toLocaleString()}</b></td>
            <td class="num"><span class="badge badge-sber">${(p.sber_deals || 0).toLocaleString()}</span></td>
            <td class="num">
                <b>${p.sber_ratio_total != null ? p.sber_ratio_total : (p.sber_pct_total || 0)}%</b>
                <div class="progress-bar-container">
                    <div class="bar-sber" style="width: ${p.sber_ratio_total != null ? p.sber_ratio_total : (p.sber_pct_total || 0)}%;"></div>
                    <div class="bar-ob" style="width: ${p.ob_ratio_total != null ? p.ob_ratio_total : (p.ob_pct_total || 0)}%;"></div>
                    <div class="bar-cash" style="width: ${p.cash_ratio_total != null ? p.cash_ratio_total : (p.cash_pct_total || 0)}%;"></div>
                </div>
            </td>
        </tr>
    `).join('');

    // 2. Render Anti-Top Other Banks Table
    antiTbody.innerHTML = (antiTopData || []).map((p, idx) => `
        <tr>
            <td class="center"><span class="rank-badge">${idx + 1}</span></td>
            <td class="partner-cell">
                <div class="name">${p.partner}</div>
                <div class="loc">${p.city || ''} • ${p.macro || ''} | <i>Конкуренты: ${p.competing_banks_str || '—'}</i></div>
            </td>
            <td class="num"><b>${(p.total_deals || 0).toLocaleString()}</b></td>
            <td class="num"><span class="badge badge-risk">${(p.other_banks_deals || 0).toLocaleString()}</span></td>
            <td class="num">
                <b>${p.ob_ratio_total != null ? p.ob_ratio_total : (p.ob_pct_total || 0)}%</b>
                <div class="progress-bar-container">
                    <div class="bar-ob" style="width: ${p.ob_ratio_total != null ? p.ob_ratio_total : (p.ob_pct_total || 0)}%;"></div>
                    <div class="bar-sber" style="width: ${p.sber_ratio_total != null ? p.sber_ratio_total : (p.sber_pct_total || 0)}%;"></div>
                    <div class="bar-cash" style="width: ${p.cash_ratio_total != null ? p.cash_ratio_total : (p.cash_pct_total || 0)}%;"></div>
                </div>
            </td>
        </tr>
    `).join('');

    // 3. Render Top Sber Chart
    if (topSberChart) {
        topSberChart.destroy();
        topSberChart = null;
    }
    const ctxSber = sberChartCanvas.getContext('2d');
    topSberChart = new Chart(ctxSber, {
        type: 'bar',
        data: {
            labels: (topSberData || []).map(p => p.partner.length > 25 ? p.partner.substring(0, 23) + '...' : p.partner),
            datasets: [
                {
                    label: 'Сбербанк',
                    data: isShare ? (topSberData || []).map(p => p.sber_ratio_total != null ? p.sber_ratio_total : p.sber_pct_total) : (topSberData || []).map(p => p.sber_deals),
                    backgroundColor: '#21A038',
                    borderRadius: 4
                },
                {
                    label: 'Другие банки',
                    data: isShare ? (topSberData || []).map(p => p.ob_ratio_total != null ? p.ob_ratio_total : p.ob_pct_total) : (topSberData || []).map(p => p.other_banks_deals),
                    backgroundColor: '#E74C3C',
                    borderRadius: 4
                },
                {
                    label: 'Наличные',
                    data: isShare ? (topSberData || []).map(p => p.cash_ratio_total != null ? p.cash_ratio_total : p.cash_pct_total) : (topSberData || []).map(p => p.cash_deals),
                    backgroundColor: '#CBD5E1',
                    borderRadius: 4
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    max: isShare ? 100 : undefined,
                    title: { display: true, text: isShare ? 'Доля в сделках (%)' : 'Количество сделок (шт.)' }
                },
                y: { stacked: true }
            },
            plugins: {
                datalabels: { display: false },
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.parsed.x;
                            return context.dataset.label + ': ' + (isShare ? val + '%' : val + ' шт.');
                        }
                    }
                }
            }
        }
    });

    // 4. Render Anti-Top Chart
    if (antiTopChart) {
        antiTopChart.destroy();
        antiTopChart = null;
    }
    const ctxAnti = antiChartCanvas.getContext('2d');
    antiTopChart = new Chart(ctxAnti, {
        type: 'bar',
        data: {
            labels: (antiTopData || []).map(p => p.partner.length > 25 ? p.partner.substring(0, 23) + '...' : p.partner),
            datasets: [
                {
                    label: 'Другие банки',
                    data: isShare ? (antiTopData || []).map(p => p.ob_ratio_total != null ? p.ob_ratio_total : p.ob_pct_total) : (antiTopData || []).map(p => p.other_banks_deals),
                    backgroundColor: '#E74C3C',
                    borderRadius: 4
                },
                {
                    label: 'Сбербанк',
                    data: isShare ? (antiTopData || []).map(p => p.sber_ratio_total != null ? p.sber_ratio_total : p.sber_pct_total) : (antiTopData || []).map(p => p.sber_deals),
                    backgroundColor: '#21A038',
                    borderRadius: 4
                },
                {
                    label: 'Наличные',
                    data: isShare ? (antiTopData || []).map(p => p.cash_ratio_total != null ? p.cash_ratio_total : p.cash_pct_total) : (antiTopData || []).map(p => p.cash_deals),
                    backgroundColor: '#CBD5E1',
                    borderRadius: 4
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    max: isShare ? 100 : undefined,
                    title: { display: true, text: isShare ? 'Доля в сделках (%)' : 'Количество сделок (шт.)' }
                },
                y: { stacked: true }
            },
            plugins: {
                datalabels: { display: false },
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.parsed.x;
                            return context.dataset.label + ': ' + (isShare ? val + '%' : val + ' шт.');
                        }
                    }
                }
            }
        }
    });
}

function switchBankingMode(mode) {
    currentBankingMode = mode;
    renderRankings();
}

// Global exposure
window.renderBankingDashboard = renderBankingDashboard;
window.renderRankings = renderRankings;
window.switchBankingMode = switchBankingMode;
window.switchMode = switchBankingMode;

// Auto-render if tab becomes visible
document.addEventListener('DOMContentLoaded', () => {
    const tabEl = document.getElementById('tab-banking');
    if (tabEl && !tabEl.classList.contains('hidden')) {
        renderBankingDashboard();
    }
});
