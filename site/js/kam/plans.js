function getPartnerPlanCellHtml(p) {
    const partnerKam = p.kam || '';
    const canEdit = canUserEditPartnerPlan(partnerKam);
    const user = getKamActiveUser();

    if (canEdit) {
        return `
            <input type="number" min="0" step="1"
                value="${p.plan || ''}"
                placeholder="—"
                class="w-16 text-center text-xs font-bold text-blue-700 bg-gray-50 border border-gray-300 rounded px-1.5 py-0.5 outline-none focus:bg-white focus:border-blue-500 transition"
                onchange="onPartnerPlanChange('${p.key}', this.value, '${partnerKam}')"
                onkeyup="if(event.key==='Enter') this.blur();"
                title="Введите план сделок для «${p.name}» (сохраняется автоматически)">
        `;
    } else {
        const lockHint = user
            ? `План закреплен за КАМом: ${partnerKam || 'Не назначен'}. Редактирование доступно только ему или Руководителю.`
            : `План закреплен за КАМом: ${partnerKam || 'Не назначен'}. Войдите в профиль для редактирования.`;
        return `
            <div class="flex items-center justify-center gap-1 cursor-pointer group" onclick="openKamLoginModal('${partnerKam}')" title="${lockHint} (нажмите для входа)">
                <span class="text-xs font-bold ${p.plan > 0 ? 'text-gray-700' : 'text-gray-400'}">${p.plan > 0 ? p.plan : '—'}</span>
                <span class="text-[10px] text-gray-400 group-hover:text-blue-600 transition">🔒</span>
            </div>
        `;
    }
}

/**
 * Retrieves KAM plans from localStorage/sessionStorage or defaults.
 */
const PLANS_MIGRATION_VERSION = '2026-09-29-darienko-329-v1';

function getKamPlansStore() {
    try {
        let raw = localStorage.getItem(STORAGE_KEY_KAM_PLANS);
        if (!raw) {
            raw = sessionStorage.getItem(STORAGE_KEY_KAM_PLANS);
        }
        let store = null;
        if (raw) {
            const parsed = JSON.parse(raw);
            const mergedKam = Object.assign({}, DEFAULT_KAM_PLANS.kam_plans, parsed.kam_plans || {});
            const mergedPartners = Object.assign({}, DEFAULT_KAM_PLANS.partner_plans);
            if (parsed.partner_plans) {
                for (let k in parsed.partner_plans) {
                    const val = parsed.partner_plans[k];
                    // Keep positive customized plans; don't let empty/0 wipe out configured defaults
                    if (val > 0 || !(k in DEFAULT_KAM_PLANS.partner_plans)) {
                        mergedPartners[k] = val;
                    }
                }
            }
            store = {
                kam_plans: mergedKam,
                partner_plans: mergedPartners
            };
        } else {
            store = JSON.parse(JSON.stringify(DEFAULT_KAM_PLANS));
        }

        // Auto-migrate authoritative September plans if not yet stamped
        try {
            if (typeof localStorage !== 'undefined' && localStorage.getItem(PLANS_MIGRATION_VERSION) !== 'applied') {
                Object.assign(store.partner_plans, CHIKHAREV_OFFICIAL_PLANS, DARIENKO_OFFICIAL_PLANS);
                store.kam_plans["Алексей Чихарев"] = 550;
                store.kam_plans["Светлана Дариенко"] = 329;
                localStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store));
                localStorage.setItem(PLANS_MIGRATION_VERSION, 'applied');
            }
        } catch(e) {}

        return store;
    } catch (e) {
        console.warn('Error reading KAM plans from localStorage:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_KAM_PLANS));
}

/**
 * Saves KAM plans store to both localStorage and sessionStorage, and auto-syncs to Cloudflare KV.
 */
function saveKamPlansStore(store, pushToCloud = true) {
    try {
        localStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store));
    } catch (e) {
        console.warn('Ошибка сохранения sberauto_kam_plans в localStorage:', e);
    }
    try {
        sessionStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store));
    } catch (e) {}

    // Auto-sync to Cloudflare KV in background
    if (pushToCloud) {
        clearTimeout(planSaveDebounceTimer);
        planSaveDebounceTimer = setTimeout(async () => {
            try {
                await fetch(CLOUD_PLANS_API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json; charset=utf-8' },
                    body: JSON.stringify(store)
                });
                console.log('☁️ Plans auto-synced to Cloudflare KV database');
            } catch (err) {
                console.warn('Notice: Background cloud sync unavailable:', err);
            }
        }, 800);
    }
}

/**
 * Automatically loads the latest plans from Cloudflare KV database and updates the dashboard.
 */
async function syncKamPlansFromCloud() {
    if (isSyncingPlansWithCloud) return;
    isSyncingPlansWithCloud = true;
    try {
        const res = await fetch(CLOUD_PLANS_API, { cache: 'no-store' });
        if (res.ok) {
            const cloudData = await res.json();
            if (cloudData && (cloudData.kam_plans || cloudData.partner_plans)) {
                const localStore = getKamPlansStore();
                const mergedKam = Object.assign({}, DEFAULT_KAM_PLANS.kam_plans, localStore.kam_plans || {}, cloudData.kam_plans || {});
                const mergedPartners = Object.assign({}, DEFAULT_KAM_PLANS.partner_plans, localStore.partner_plans || {}, cloudData.partner_plans || {});

                const updated = {
                    kam_plans: mergedKam,
                    partner_plans: mergedPartners
                };
                saveKamPlansStore(updated, false); // save locally without echo

                // Refresh KAM tab if visible
                const kamTab = document.getElementById('tab-kam');
                if (kamTab && !kamTab.classList.contains('hidden')) {
                    if (typeof renderKamTab === 'function') {
                        renderKamTab(currentFilterConfig, true);
                    }
                }
            }
        }
    } catch (e) {
        console.warn('Notice: Cloud plans fetch skipped or offline:', e);
    } finally {
        isSyncingPlansWithCloud = false;
    }
}

// Initial background sync from Cloudflare KV on page load
if (typeof window !== 'undefined') {
    setTimeout(() => {
        syncKamPlansFromCloud();
    }, 200);
}

/**
 * Updates overall plan for a KAM manager and auto-refreshes KPI/bars.
 */
function onKamOverallPlanChange(kamName, val) {
    if (!canUserEditOverallPlan(kamName)) {
        const displayName = kamName === 'all' ? 'Все КАМы (Сеть)' : kamName;
        if (typeof showToast === 'function') {
            showToast(`🔒 Редактирование плана «${displayName}» доступно только закрепленному сотруднику или Руководителю`, 'warning', 3500);
        }
        openKamLoginModal(kamName);
        const agg = getKamAggregatedData(currentFilterConfig);
        renderKamPlanHeader(agg.summary);
        return;
    }
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.kam_plans[kamName] = num;
    saveKamPlansStore(store);

    // In-place refresh header KPI and progress bar without losing DOM focus
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamPlanHeader(agg.summary);

    if (typeof showToast === 'function') {
        showToast(`План для «${kamName === 'all' ? 'Все КАМы' : kamName}» сохранен: ${fmtNum(num)} сделок`, 'success', 2000);
    }
}

/**
 * Updates individual partner plan with multi-key redundancy and auto-refreshes row progress.
 */
function onPartnerPlanChange(partnerKey, val, partnerKam = '') {
    if (!canUserEditPartnerPlan(partnerKam)) {
        if (typeof showToast === 'function') {
            showToast(`🔒 Редактирование плана партнера доступно только КАМу (${partnerKam || '—'}) или Руководителю`, 'warning', 3500);
        }
        openKamLoginModal(partnerKam);
        renderKamTableOnly();
        return;
    }
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.partner_plans[partnerKey] = num;

    // Multi-key redundancy so plan is resilient against filter changes, reassignment, or ID lookup
    const m = partnerKey.match(/ID_([a-zA-Z0-9_-]+)/);
    if (m && m[1]) {
        const pid = m[1];
        store.partner_plans[`ID_${pid}`] = num;
        store.partner_plans[pid] = num;
    }
    const safeKey = partnerKey.replace(/[^a-zA-Z0-9_-]/g, '_');
    const row = document.querySelector(`tr[onclick*="${safeKey}"]`);
    if (row) {
        const nameEl = row.querySelector('.font-bold.text-xs');
        if (nameEl && nameEl.textContent) {
            const pName = nameEl.textContent.trim();
            store.partner_plans[pName] = num;
            store.partner_plans[pName.toLowerCase()] = num;
        }
    }
    saveKamPlansStore(store);

    // In-place DOM update for row % and plan badge
    if (row) {
        const planPctCell = row.querySelector('.kam-plan-pct') || row.querySelectorAll('td')[3];
        let totalDeals = 0;
        if (row.dataset && row.dataset.totalDeals !== undefined) {
            totalDeals = parseInt(row.dataset.totalDeals, 10) || 0;
        } else {
            const totalDealsEl = row.querySelector('.kam-total-deals');
            const totalDealsText = totalDealsEl ? totalDealsEl.textContent.trim() : (row.querySelectorAll('td')[10] ? row.querySelectorAll('td')[10].textContent.trim() : '0');
            totalDeals = parseInt(totalDealsText.replace(/\D/g, ''), 10) || 0;
        }
        if (planPctCell) {
            const pct = num > 0 ? (totalDeals / num * 100) : 0;
            let planBadge = 'text-gray-400';
            if (num > 0) {
                planBadge = pct >= 100 ? 'text-emerald-700 font-black' : (pct >= 70 ? 'text-blue-600 font-bold' : 'text-amber-600 font-bold');
            }
            planPctCell.className = `text-center ${planBadge} kam-plan-pct`;
            planPctCell.textContent = num > 0 ? `${pct.toFixed(0)}%` : '—';
        }
    }

    // Refresh summary in header
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamPlanHeader(agg.summary);

    if (typeof showToast === 'function') {
        showToast(`План партнера сохранен: ${fmtNum(num)} сделок`, 'success', 1500);
    }
}

/**
 * Exports all current plans to JSON string / clipboard.
 */
function exportKamPlansJson() {
    const store = getKamPlansStore();
    const str = JSON.stringify(store, null, 2);
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(str).then(() => {
            if (typeof showToast === 'function') showToast('Планы скопированы в буфер обмена (JSON)!', 'success', 3000);
            else alert('Планы скопированы в буфер обмена!');
        }).catch(() => {
            prompt('Скопируйте конфигурацию планов (JSON):', str);
        });
    } else {
        prompt('Скопируйте конфигурацию планов (JSON):', str);
    }
}

/**
 * Imports plans from JSON string (Requires Supervisor/Admin role).
 */
function importKamPlansPrompt() {
    const user = getKamActiveUser();
    if (!user || !user.isAdmin) {
        if (typeof showToast === 'function') {
            showToast('🔒 Импорт планов из JSON доступен только Руководителю / Администратору', 'warning', 3500);
        } else {
            alert('Импорт планов доступен только Руководителю / Администратору.');
        }
        openKamLoginModal('admin');
        return;
    }
    const input = prompt('Вставьте JSON с планами КАМ и партнеров:');
    if (!input) return;
    try {
        const parsed = JSON.parse(input);
        if (parsed && (parsed.kam_plans || parsed.partner_plans)) {
            const current = getKamPlansStore();
            const updated = {
                kam_plans: Object.assign({}, current.kam_plans, parsed.kam_plans || {}),
                partner_plans: Object.assign({}, current.partner_plans, parsed.partner_plans || {})
            };
            saveKamPlansStore(updated);
            renderKamTab(currentFilterConfig);
            if (typeof showToast === 'function') showToast('Планы успешно импортированы и сохранены!', 'success', 3000);
            else alert('Планы успешно импортированы!');
        } else {
            alert('Некорректный формат JSON: отсутствуют kam_plans или partner_plans.');
        }
    } catch (e) {
        alert('Ошибка парсинга JSON: ' + e.message);
    }
}

