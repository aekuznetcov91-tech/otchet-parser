# Spec: Dashboard Analytics Enhancements & KPI Synchronization

## 1. Overview & Objectives
This specification covers 16 targeted enhancements, audit resolutions, and metric synchronizations across all tabs of the B2C Analytics Dashboard (Динамика, Партнеры сквозной ID, КАМ, Лиды и регионы, Радар динамики, В ожидании).
The implementation is organized into 3 sequential delivery packages:
- **Package 1 (Quick Fixes & UI):** Items 1–5, 11, 12, 14.
- **Package 2 (Audit & Metric Synchronization):** Items 6–9, 13, 15, 16.
- **Package 3 (Role-Based Access for KAMs):** Item 10.

---

## 2. Requirements & Scope Breakdown

### Package 1: Quick Fixes & UI Enhancements
- **Item 1 (Brand Merging - JELAND):**
  - Merge `OMODA`, `JAECOO`, and `JELAND` into a unified brand **`JELAND`** across all dashboard tabs, charts, and tables for deals from September 2026 onwards (`deal_month >= '2026-09'`).
  - Historical data (Jan–Aug 2026) remains preserved as `OMODA & JAECOO`.
- **Item 2 (Monthly Dynamic Deltas in Tables):**
  - In `js/tables.js`, table "ТИП СДЕЛКИ (B2C) ПО МАРКАМ" (`#tableB2CBrands`): display absolute volume and change vs previous month (e.g. `38 ▲+12` or `14 ▼-5`).
  - In table "СТРУКТУРА СДЕЛОК B2C ВНУТРИ БРЕНДА (%)" (`#tableB2CStruct`): display share % and change in percentage points vs previous month (e.g. `45% ▲+3%` or `20% ▼-2%`).
- **Item 3 (Retire Redundant Code):**
  - Remove "Историческая помесячная Динамика" table (`#tableHistDyn`) from `index.html`, `js/tables.js`, and `site/js/tables.js` to streamline page performance and reduce code complexity.
- **Item 4 (Prepayments Column Sorting):**
  - In `tablePartners` ("Партнеры сквозной ID"), clicking numerical headers (Предоплаты, Сделки) must sort in descending order (`desc`) on initial click rather than ascending (`asc`), preventing non-zero values from being pushed to the bottom.
- **Item 5 (Agency Fee % in Deal Drilldown):**
  - In the expandable deal row on "Партнеры сквозной ID", display `% АВ от стоимости` calculated as `(AB_commission / Car_price) * 100`, formatted as e.g. `2.1%`.
- **Item 11 (CR Threshold Palette on KAM Tab):**
  - Update conversion rate coloring in `js/kam-dashboard.js`:
    - CR < 7%: Red (`#ef4444` / badge danger)
    - 7% <= CR <= 13%: Amber/Yellow (`#f59e0b` / badge warning)
    - CR > 13%: Green (`#10b981` / badge success)
- **Item 12 (Swap Columns on KAM Tab):**
  - Swap column positions in the KAM partners table: MTD deals should precede Total deals for intuitive operational monitoring.
- **Item 14 (Collapsed Region Accordions):**
  - In `js/lead-geo.js`, set all regional grouping accordions to collapsed (`closed`) by default on initial page render.

### Package 2: Audit & Metric Synchronization
- **Item 6 & 7 (Conversion Synchronization & Single Truth Source):**
  - Align conversion rate (CR) methodology on "Партнеры сквозной ID" with the KAM tab and AGENTS.md:
    $$\text{CR} = \frac{\text{leadDirectDeals}}{\text{trans\_leads}} \times 100\%$$
    using transferred leads strictly without double counting.
- **Item 8 (SberAuto Lead Breakdown by Email/Contact Queue):**
  - In `raw_data/data (44).xlsx` and lead pipelines, decompose "СберАвто" (1,287 leads) by queue name from `Название контакта` (`Почта БХ Чери МСК1`, `Почта Фреш Чери Воронеж`, etc.) into distinct partner rows.
- **Item 9 (Audit of 64 Unmatched Leads):**
  - Audit and remap 64 unallocated lead records from September 2026 that had empty/unmatched partner identifiers.
- **Item 13 (Lead Geographic Parsing Audit):**
  - Audit and improve address-to-region normalization in `lead-geo.js` and parser scripts to reduce the oversized "Другие регионы" bucket (currently 6,563) by resolving unstructured address strings.
- **Item 15 & 16 (Radar & Debtors Synchronization):**
  - Synchronize "Радар Динамики -> Авансы" and "В ожидании" to consume a single unified dataset `data.debtors`.
  - Fix any company filtering glitches to ensure all partners with active advances render reliably.

### Package 3: Role-Based Access for KAMs
- **Item 10 (KAM Role PIN / Authentication Modal):**
  - Implement a client-side PIN/role authentication layer for the KAM tab.
  - Each KAM enters their personal PIN to edit only their assigned portfolio rows/status comments.
  - Provide a master admin/ROP PIN with global editing permissions.

---

## 3. Verification & Compliance
- Maintain historical preservation of closed months (Jan–Aug 2026).
- Mirror all UI and logic modifications identically across root (`js/`, `index.html`) and `site/` (`site/js/`, `site/index.html`).
- All existing and new tests must pass (`python -m unittest discover tests`).
- Git sync to `origin main` with descriptive commit messages.
