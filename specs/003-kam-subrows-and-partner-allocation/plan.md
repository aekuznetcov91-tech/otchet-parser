# Technical Plan: Fix KAM Partner Hierarchy Subrows and "Авто Премиум Тверь" Allocation

## 1. Architecture & Root Cause Analysis

### 1.1 "Авто Премиум Тверь" False Hijacking
- **File:** `partners_registry.json`, `data/partners_registry.json`, `site/partners_registry.json`, `data.json`, `site/data.json`
- **Root Cause:**
  Partner `ID 1040` had `"holding": "ONLIN"`, `"bitrix_aliases": ["ONLINE ООО \"СОЮЗ-Т\"", "ONLIN Авто Премиум Тверь"]`, `"bi_aliases": ["ONLIN Авто Премиум Тверь"]`.
  When `js/kam-dashboard.js` seeded `partnerListForMatching`:
  `const cleanAliases = Array.from(new Set(aliases.map(a => (a || '').toLowerCase().trim()).filter(a => a.length > 0)));`
  The string `"onlin"` was stored as an alias.
  Then in `matchDealerToPartner(dealerName)`:
  ```javascript
  for (let p of partnerListForMatching) {
      for (let a of p.aliases) {
          if (a.length >= 4 && (a.includes(dn) || dn.includes(a))) {
              return p;
          }
      }
  }
  ```
  Since `a` was `"onlin"` (length 5 >= 4), any dealer with `"online"` in its name (e.g. `Online ООО "АВТОЛИГА"`) satisfied `dn.includes(a)`, causing `matchDealerToPartner` to return `ID 1040`.
  Because `Online ООО "АВТОЛИГА"` had KAM = "Светлана Дариенко", a phantom entry `RAW_Online ООО "АВТОЛИГА"__Светлана Дариенко` was created with `p.id = 1040` and `p.name = 'Авто Премиум Тверь'`.
- **Solution:**
  1. Correct partner ID 1040:
     - `canonical_name: "Авто Премиум Тверь"`
     - `holding: "Авто Премиум"`
     - `kam: "Алексей Чихарев"`
     - `bitrix_aliases: ["Авто Премиум Тверь", "ООО \"СОЮЗ-Т\"", "ONLINE ООО \"СОЮЗ-Т\""]`
     - `bi_aliases: ["Авто Премиум Тверь"]`
  2. Implement strict generic stop-words filtering in `js/kam-dashboard.js` and `site/js/kam-dashboard.js`:
     ```javascript
     const GENERIC_STOP_WORDS = new Set([
         'ооо', 'зао', 'пао', 'ао', 'ип', 'online', 'онлайн', 'onlin', 
         'авто', 'auto', 'холдинг', 'holding', 'группа', 'group', 'моторс', 'motors',
         'центр', 'дилер', 'сервис', 'плюс', 'трейд', 'компания', 'россия', 'russia'
     ]);
     ```
     Exclude any alias from `cleanAliases` that matches `GENERIC_STOP_WORDS`.
     In substring matching, do not allow matching if `a` is a generic word or if `a.length < 5`.

---

### 1.2 Missing Accordion Subrows on Dealer Click
- **File:** `js/kam-dashboard.js`, `site/js/kam-dashboard.js`
- **Root Cause:**
  In `getKamAggregatedData()`, `oemGeo` is only present for partners with OEM directory records. For 71+ partners, `oemGeo` is empty (`[]`).
  In transaction loop (`fPartners.forEach`):
  ```javascript
  const recordCityMatch = () => {
      for (let cName in ps.cities) {
          if (ps.cities[cName].brands && ps.cities[cName].brands[brand]) return ps.cities[cName].brands[brand];
      }
      const firstCity = Object.values(ps.cities)[0];
      if (firstCity) { ... return firstCity.brands[brand]; }
      return null;
  };
  ```
  When `ps.cities` is `{}`:
  `recordCityMatch()` returned `null`.
  `ps.brands[brand]` was populated, but `ps.cities` remained `{}`.
  Then in `renderKamTable()`:
  ```javascript
  const citiesList = Object.keys(p.cities || {});
  const citiesCount = citiesList.length;
  const brandsCount = Object.keys(p.brands || {}).length;
  const hasSubrows = citiesCount > 0 || brandsCount > 0;
  ```
  `hasSubrows` was `true` (because `brandsCount > 0`), which rendered the arrow `▶`.
  However, the subrow rendering loop only iterated over `p.cities`:
  ```javascript
  if (hasSubrows) {
      Object.entries(p.cities || {}).forEach(([cityName, cityData]) => { ... });
  }
  ```
  Because `p.cities` was empty, `Object.entries(p.cities)` had 0 items. Zero `<tr class="kam-subrow-...">` elements were created in the DOM.
  When the user clicked the row, `toggleKamPartnerRows()` ran:
  - Rotated the arrow `▶` to `▼`.
  - Found 0 matching `.kam-subrow-...` elements.
  - Nothing expanded.
- **Solution:**
  1. During aggregation in `getKamAggregatedData()`:
     If `recordCityMatch()` finds no existing city in `ps.cities`:
     Derive city from transaction `r.City` (or `p.oem_data[0].city` or `"Город не указан"`).
     Initialize `ps.cities[cityName] = { name: cityName, brands: {} };`.
     Populate `ps.cities[cityName].brands[brand]`.
  2. Fallback normalization before rendering:
     Ensure that any partner with brands in `p.brands` has at least one city in `p.cities`. If `Object.keys(p.cities).length === 0`:
     Create `p.cities['Город не указан'] = { name: 'Город не указан', brands: { ...p.brands } }`.
  3. In `renderKamTable()`:
     If `Object.keys(p.cities || {}).length === 0` and `brandsCount > 0`:
     Render the brand subrows under `"Город не указан"`.
  4. Ensure `safeKey` uses a reliable prefix (`kam_row_${idx}_...`) so DOM selectors always match uniquely.

---

## 2. File Modification Blueprint
1. `scripts/merge_partner_splits.py`:
   - Add sanitization for ID 1040 and clean bad holdings/aliases across all registry files.
2. `partners_registry.json`, `data/partners_registry.json`, `site/partners_registry.json`:
   - Update ID 1040 to clean holding and aliases.
3. `js/kam-dashboard.js` & `site/js/kam-dashboard.js`:
   - Update `cleanAliases` to filter `GENERIC_STOP_WORDS`.
   - Update `recordCityMatch` to dynamically create city entries for non-OEM partners.
   - Update `getKamAggregatedData` to ensure all partners with brands have city entries.
   - Update `renderKamTable` to guarantee subrow generation and reliable toggle behavior.
4. `tests/test_kam_subrows.py`:
   - Create comprehensive unit tests verifying 100% subrow generation and correct KAM assignment.
