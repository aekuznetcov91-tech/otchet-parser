# Tasks: Dashboard Analytics Enhancements

## Package 1: Quick Fixes & UI Enhancements
- [x] **TASK-101**: [Item 1] Unify Omoda, Jaecoo, Jeland -> `JELAND` starting from `2026-09` in `scripts/parser_engine.py` and frontend tables.
- [x] **TASK-102**: [Item 2] Add MoM dynamic delta badges to `#tableB2CBrands` (volume) and `#tableB2CStruct` (share %) in `js/tables.js` and `site/js/tables.js`.
- [x] **TASK-103**: [Item 3] Remove "Историческая помесячная Динамика" table (`#tableHistDyn`) from `index.html`, `site/index.html`, `js/tables.js`, and `site/js/tables.js`.
- [x] **TASK-104**: [Item 4] Fix header sort in `tablePartners` (`js/tables.js` & `site/js/tables.js`): numerical columns sort descending first.
- [x] **TASK-105**: [Item 5] Add `% АВ от стоимости` column to partner deal drilldown in `js/tables.js` & `site/js/tables.js`.
- [x] **TASK-106**: [Item 11] Set CR color thresholds (<7% red, 7-13% yellow, >13% green) in `js/kam-dashboard.js` & `site/js/kam-dashboard.js`.
- [x] **TASK-107**: [Item 12] Swap MTD and Total deals columns on KAM tab in `js/kam-dashboard.js` & `site/js/kam-dashboard.js`.
- [x] **TASK-108**: [Item 14] Make region accordions collapsed by default in `js/lead-geo.js` & `site/js/lead-geo.js`.
- [x] **TASK-109**: Run automated tests, verify changes, and sync Git commit.

## Package 2: Audit & Metric Synchronization
- [ ] **TASK-201**: [Item 6 & 7] Synchronize CR on "Партнеры сквозной ID" to use strictly direct deals / transferred leads.
- [ ] **TASK-202**: [Item 8] Break down SberAuto leads by email/contact queue in `scripts/parser_engine.py`.
- [ ] **TASK-203**: [Item 9] Audit and remap 64 unmatched September leads.
- [ ] **TASK-204**: [Item 13] Geographic parsing audit and address resolution to reduce "Другие регионы".
- [ ] **TASK-205**: [Item 15 & 16] Synchronize radar prepayments with `data.debtors` and verify partner advance rendering.

## Package 3: Role-Based Access for KAMs
- [ ] **TASK-301**: [Item 10] Implement KAM PIN authentication modal and role-based editing restrictions.
