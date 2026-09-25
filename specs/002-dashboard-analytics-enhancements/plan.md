# Implementation Plan: Dashboard Analytics Enhancements

## Phase 1: Package 1 Implementation (Quick Fixes & UI)
- [ ] **Task 1.1: Brand Merging - JELAND (Item 1)**
  - Modify `scripts/parser_engine.py` (and any brand mapping dictionary): if `deal_month >= '2026-09'` and brand in `['OMODA', 'JAECOO', 'JELAND', 'OMODA & JAECOO', 'OMODA & JAECOO (СБЕР)']`, map to `JELAND`.
  - In frontend brand helpers (`js/tables.js`, `site/js/tables.js`, `js/executive-dashboard.js`, `site/js/executive-dashboard.js`), apply the same mapping for September+ dates.
  - Historical data (< '2026-09') remains `OMODA & JAECOO`.
- [ ] **Task 1.2: Dynamic Table Monthly Deltas (Item 2)**
  - In `js/tables.js` and `site/js/tables.js`:
    - For `#tableB2CBrands`: compute `delta = current_month_count - prev_month_count`. Render badge: `▲+N` (green) if delta > 0, `▼-N` (red) if delta < 0, `0` if equal.
    - For `#tableB2CStruct`: compute `delta_pp = current_month_share - prev_month_share`. Render badge: `▲+N%` (green) if delta > 0, `▼-N%` (red) if delta < 0.
- [ ] **Task 1.3: Remove "Историческая помесячная Динамика" (Item 3)**
  - Remove HTML element `#tableHistDyn` and its card container from `index.html` and `site/index.html`.
  - Remove rendering function and event listeners for `#tableHistDyn` in `js/tables.js` and `site/js/tables.js`.
- [ ] **Task 1.4: Prepayments Sorting Fix (Item 4)**
  - In `js/tables.js` (around line 848) and `site/js/tables.js`, update column sorting: if column is numerical (Prepayments, Deals, etc.) or when clicking a new column, default to `descending` order on first click.
- [ ] **Task 1.5: Deal Drilldown AB % (Item 5)**
  - In `renderPartnersTable` deal drilldown in `js/tables.js` and `site/js/tables.js`, calculate and render `% АВ от стоимости` as `(comm / price * 100).toFixed(1) + '%'`.
- [ ] **Task 1.6: KAM Tab CR Colors & Column Swap (Items 11 & 12)**
  - In `js/kam-dashboard.js` and `site/js/kam-dashboard.js`:
    - Update CR badge class: `< 7%` -> red, `7%–13%` -> amber/yellow, `> 13%` -> green.
    - Swap columns: place MTD deals column before Total deals column in header and body.
- [ ] **Task 1.7: Lead Geo Accordions Collapsed (Item 14)**
  - In `js/lead-geo.js` and `site/js/lead-geo.js`: ensure region group containers are initialized with `display: none` / collapsed accordion state.
- [ ] **Task 1.8: Verification & Unit Tests**
  - Add/update unit test in `tests/` verifying `JELAND` mapping from September 2026.
  - Run `python -m unittest discover tests`.
  - Commit Package 1 changes to Git.

---

## Phase 2: Package 2 Implementation (Audit & Metric Synchronization)
- [ ] **Task 2.1: Conversion Formula Synchronization (Items 6 & 7)**
  - In `js/tables.js` and `site/js/tables.js` for "Партнеры сквозной ID", ensure CR = `leadDirectDeals / trans_leads * 100%`, eliminating any double counting.
- [ ] **Task 2.2: SberAuto Queue Breakdown (Item 8)**
  - In `scripts/parser_engine.py`, parse `Название контакта` for SberAuto leads in `raw_data/data (44).xlsx` and generate partner entries per email/queue.
- [ ] **Task 2.3: Audit 64 Unmatched Leads (Item 9)**
  - Investigate the 64 unallocated lead records in September 2026 and establish explicit partner matching rules.
- [ ] **Task 2.4: Geographic Normalization Audit (Item 13)**
  - Refine city/region regex in parser and `lead-geo.js` to map address strings to federal regions, decreasing "Другие регионы".
- [ ] **Task 2.5: Advances & Debtors Synchronization (Items 15 & 16)**
  - Synchronize radar prepayments and "В ожидании" with single source `data.debtors`.
  - Fix any company filtering bottlenecks.

---

## Phase 3: Package 3 Implementation (KAM Role Authentication)
- [ ] **Task 3.1: KAM Modal & Role Verification (Item 10)**
  - Add PIN prompt modal when switching KAM or editing notes/statuses.
  - Restrict row editing to authenticated KAM or ROP/Admin PIN.
