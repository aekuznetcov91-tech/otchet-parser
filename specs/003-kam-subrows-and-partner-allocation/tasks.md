# Tasks: Fix KAM Partner Hierarchy Subrows and "Авто Премиум Тверь" Allocation

## Phase 1: Registry & Alias Sanitization
- [x] **T001**: Sanitize ID 1040 in `partners_registry.json`, `data/partners_registry.json`, and `site/partners_registry.json` (`holding = "Авто Премиум"`, remove `"ONLIN"` aliases, `kam = "Алексей Чихарев"`).
- [x] **T002**: Clean any remaining partners having generic holdings (`"ONLIN"`, `"ONLINE"`, `"ООО"`) in `scripts/merge_partner_splits.py`.

## Phase 2: Core Matching & Geo Aggregation Fixes
- [x] **T003**: In `js/kam-dashboard.js` and `site/js/kam-dashboard.js`, implement `GENERIC_STOP_WORDS` filtering on partner aliases in `getKamAggregatedData()`.
- [x] **T004**: In `js/kam-dashboard.js` and `site/js/kam-dashboard.js`, fix `recordCityMatch()` to dynamically create a city entry (from `r.City` or `"Город не указан"`) when a partner has no OEM cities.
- [x] **T005**: In `js/kam-dashboard.js` and `site/js/kam-dashboard.js`, ensure all partners with `brandsCount > 0` have at least one city in `p.cities` before passing to the table renderer.

## Phase 3: Table Rendering & Accordion Robustness
- [x] **T006**: In `js/kam-dashboard.js` and `site/js/kam-dashboard.js`, update `renderKamTable()`:
  - Generate unique `safeKey` (`krow_${idx}_${p.id || 'raw'}_...`).
  - Guarantee that subrows (`<tr class="kam-subrow-${safeKey}">`) are rendered for every city and brand whenever `hasSubrows` is true.
  - Add fallback rendering for brands if `p.cities` is unexpectedly empty.

## Phase 4: Verification, Data Synchronization & Deployment
- [x] **T007**: Apply registry updates to `data.json` and `site/data.json`.
- [x] **T008**: Create automated unit tests in `tests/test_kam_subrows.py` verifying that all partners with brands have rendered subrows and that ID 1040 does not appear under Дариенко.
- [x] **T009**: Run the complete test suite (`python -m unittest discover tests`).
- [x] **T010**: Deploy to Cloudflare Pages and synchronize to Git `origin main` using `deploy_to_cloudflare.py`.
