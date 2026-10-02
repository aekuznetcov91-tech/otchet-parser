function exportKamReportToExcel() {
    try {
        const table = document.getElementById('tableKamPartners');
        if (!table) {
            if (typeof showToast === 'function') showToast('Таблица не найдена для экспорта', 'error');
            return;
        }
        const wb = XLSX.utils.table_to_book(table, { sheet: "Отчет_КАМ" });
        const kamNameClean = (currentKamFilter === 'all' ? 'Все_КАМ' : currentKamFilter).replace(/\s+/g, '_');
        const fileName = `Отчет_КАМ_${kamNameClean}_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);
        if (typeof showToast === 'function') showToast(`Отчет успешно экспортирован в ${fileName}`, 'success', 3000);
    } catch (e) {
        console.error('Ошибка экспорта в Excel:', e);
        if (typeof showToast === 'function') showToast('Ошибка при выгрузке Excel: ' + e.message, 'error');
    }
}

// ================= ITEM 4: LEGAL ENTITIES MODAL =================
let currentKamLegalEntities = [];
let currentKamRooftops = [];
let kamModalActiveTab = 'rooftops'; // 'rooftops' | 'legal_entities'
let kamModalStatusFilter = 'all'; // 'all' | 'active' | 'sleeping'
let kamLegalEntitiesSearchQuery = '';

function openKamLegalEntitiesModal(defaultTab = 'rooftops') {
    kamModalActiveTab = defaultTab;
    kamModalStatusFilter = 'all';
    kamLegalEntitiesSearchQuery = '';

    const agg = getKamAggregatedData(currentFilterConfig);
    currentKamLegalEntities = agg.summary.legal_entities || [];
    currentKamRooftops = agg.summary.rooftops || [];

    let modal = document.getElementById('kamLegalEntitiesModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'kamLegalEntitiesModal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-3 sm:p-4';
        document.body.appendChild(modal);
    }
    modal.classList.remove('hidden');
    renderKamLegalEntitiesModalContent();
}

function closeKamLegalEntitiesModal() {
    const modal = document.getElementById('kamLegalEntitiesModal');
    if (modal) modal.classList.add('hidden');
}

function setKamModalTab(tab) {
    kamModalActiveTab = tab;
    renderKamLegalEntitiesModalContent();
}

function setKamModalStatusFilter(status) {
    kamModalStatusFilter = status;
    renderKamLegalEntitiesModalTable();
}

function onKamLegalEntitiesSearch(val) {
    kamLegalEntitiesSearchQuery = (val || '').toLowerCase().trim();
    renderKamLegalEntitiesModalTable();
}

function renderKamLegalEntitiesModalContent() {
    const modal = document.getElementById('kamLegalEntitiesModal');
    if (!modal) return;

    const kamName = currentKamFilter === 'all' ? 'Все КАМ-менеджеры' : currentKamFilter;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    const totalDeals = currentKamRooftops.reduce((s, x) => s + (x.deals_count || 0), 0);
    const activeRooftopsCount = currentKamRooftops.filter(r => r.deals_count > 0).length;
    const activeLeCount = currentKamLegalEntities.filter(l => l.total_deals > 0).length;

    modal.innerHTML = `
    <div class="bg-white rounded-2xl shadow-2xl border border-gray-200 w-full max-w-6xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="p-4 sm:p-5 border-b border-gray-200 bg-slate-900 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-md shrink-0">
                    🏢
                </div>
                <div>
                    <h3 class="text-base font-bold flex items-center gap-2">
                        <span>Детализация: Юр. лица и Крыши</span>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-400/30 text-indigo-200 border border-indigo-400/40">
                            ${kamName}
                        </span>
                    </h3>
                    <p class="text-xs text-slate-300 mt-0.5">
                        Юр. лиц: <b>${activeLeCount} из ${currentKamLegalEntities.length}</b> |
                        Крыш (Город+Бренд): <b>${activeRooftopsCount} из ${currentKamRooftops.length}</b> |
                        Сделок: <b class="text-emerald-300">${fmt(totalDeals)}</b>
                    </p>
                </div>
            </div>
            <button onclick="closeKamLegalEntitiesModal()" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center text-lg font-bold transition self-end sm:self-auto">
                ✕
            </button>
        </div>

        <!-- Mode Tabs & Controls Bar -->
        <div class="p-3 sm:px-5 bg-slate-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3">
            <!-- Mode Switcher -->
            <div class="flex items-center bg-gray-200/80 p-1 rounded-xl shadow-inner gap-1">
                <button onclick="setKamModalTab('rooftops')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${kamModalActiveTab === 'rooftops' ? 'bg-white text-indigo-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}">
                    <span>🏷️ Крыши (Город + Бренд)</span>
                    <span class="px-1.5 py-0.2 rounded-full text-[10px] ${kamModalActiveTab === 'rooftops' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-300/80 text-gray-700'}">${currentKamRooftops.length}</span>
                </button>
                <button onclick="setKamModalTab('legal_entities')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${kamModalActiveTab === 'legal_entities' ? 'bg-white text-indigo-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}">
                    <span>🏢 Юридические лица</span>
                    <span class="px-1.5 py-0.2 rounded-full text-[10px] ${kamModalActiveTab === 'legal_entities' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-300/80 text-gray-700'}">${currentKamLegalEntities.length}</span>
                </button>
            </div>

            <!-- Status Filter Pills -->
            <div class="flex items-center gap-1 text-xs">
                <button onclick="setKamModalStatusFilter('all')" class="px-2.5 py-1 rounded-lg font-semibold border transition ${kamModalStatusFilter === 'all' ? 'bg-slate-800 text-white border-slate-800' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-100'}">
                    Все
                </button>
                <button onclick="setKamModalStatusFilter('active')" class="px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1 ${kamModalStatusFilter === 'active' ? 'bg-emerald-700 text-white border-emerald-700' : 'bg-white text-emerald-700 border-emerald-300 hover:bg-emerald-50'}">
                    <span>🟢 Со сделками</span>
                </button>
                <button onclick="setKamModalStatusFilter('sleeping')" class="px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1 ${kamModalStatusFilter === 'sleeping' ? 'bg-amber-700 text-white border-amber-700' : 'bg-white text-amber-700 border-amber-300 hover:bg-amber-50'}">
                    <span>💤 Спящие (0 сделок)</span>
                </button>
            </div>
        </div>

        <!-- Search Bar -->
        <div class="px-4 py-2.5 bg-white border-b border-gray-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div class="relative flex-1">
                <input type="text"
                    id="searchKamLegalEntitiesInput"
                    placeholder="${kamModalActiveTab === 'rooftops' ? 'Поиск по партнеру, городу или бренду крыши...' : 'Поиск по юрлицу, ИНН, Master Partner, городу или бренду...'}"
                    value="${kamLegalEntitiesSearchQuery}"
                    class="w-full bg-slate-50 border border-gray-200 rounded-xl pl-9 pr-4 py-1.5 text-xs font-semibold text-gray-800 placeholder-gray-400 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition shadow-sm"
                    oninput="onKamLegalEntitiesSearch(this.value)">
                <span class="absolute left-3 top-2 text-gray-400 text-xs">🔍</span>
            </div>
            <div class="text-[11px] font-semibold text-gray-500 text-right shrink-0">
                Период: <b>${(window.currentFilterConfig && window.currentFilterConfig.month) === 'all' ? 'Все месяцы' : (window.currentFilterConfig && window.currentFilterConfig.month) || 'Август 2026'}</b>
            </div>
        </div>

        <!-- Table Container -->
        <div class="flex-1 overflow-y-auto p-4" id="kamLegalEntitiesTableContainer">
            <!-- Rendered by renderKamLegalEntitiesModalTable() -->
        </div>

        <!-- Footer -->
        <div class="p-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
            <span>💡 1 крыша = 1 бренд в 1 городе (Rooftop). Показывает фактическое распределение продаж и утилизацию дилерской сети.</span>
            <button onclick="closeKamLegalEntitiesModal()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold transition shadow-sm">
                Закрыть
            </button>
        </div>
    </div>
    `;

    renderKamLegalEntitiesModalTable();
}

function renderKamLegalEntitiesModalTable() {
    const cont = document.getElementById('kamLegalEntitiesTableContainer');
    if (!cont) return;

    const q = kamLegalEntitiesSearchQuery;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    if (kamModalActiveTab === 'rooftops') {
        // Render Rooftops Table
        let filtered = currentKamRooftops.filter(rt => {
            if (kamModalStatusFilter === 'active' && rt.deals_count === 0) return false;
            if (kamModalStatusFilter === 'sleeping' && rt.deals_count > 0) return false;

            if (!q) return true;
            const mPartner = (rt.partner_name || '').toLowerCase().includes(q);
            const mCity = (rt.city || '').toLowerCase().includes(q);
            const mBrand = (rt.brand || '').toLowerCase().includes(q);
            const mAddress = (rt.address || '').toLowerCase().includes(q);
            return mPartner || mCity || mBrand || mAddress;
        });

        if (filtered.length === 0) {
            cont.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">🏷️</div>
                <p class="font-bold text-sm">Крыши не найдены</p>
                <p class="text-xs text-gray-400 mt-1">Попробуйте изменить поисковый запрос или фильтр статуса</p>
            </div>`;
            return;
        }

        let html = `
        <table class="min-w-full text-xs">
            <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200 shadow-sm">
                <tr>
                    <th class="py-2.5 px-3 text-left w-10">#</th>
                    <th class="py-2.5 px-3 text-left min-w-[200px]">Партнер / Холдинг</th>
                    <th class="py-2.5 px-3 text-left min-w-[140px]">Город</th>
                    <th class="py-2.5 px-3 text-left min-w-[150px]">Бренд (Крыша)</th>
                    <th class="py-2.5 px-3 text-center w-28">Статус крыши</th>
                    <th class="py-2.5 px-3 text-center w-20">Сделки МП</th>
                    <th class="py-2.5 px-3 text-center w-24">ФДЦ / Онлайн</th>
                    <th class="py-2.5 px-3 text-center w-24">Всего сделок</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
        `;

        filtered.forEach((rt, idx) => {
            const isActive = rt.deals_count > 0;
            html += `
            <tr class="hover:bg-indigo-50/40 transition font-medium ${isActive ? 'bg-white' : 'bg-gray-50/50 text-gray-400'}">
                <td class="py-2 px-3 text-gray-400 font-mono">${idx + 1}</td>
                <td class="py-2 px-3 font-bold text-gray-900">
                    <div class="flex items-center gap-1.5">
                        ${rt.partner_id ? `<span class="px-1.5 py-0.2 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">ID:${rt.partner_id}</span>` : ''}
                        <span class="truncate max-w-[240px]" title="${rt.partner_name}">${rt.partner_name}</span>
                    </div>
                </td>
                <td class="py-2 px-3 font-semibold text-gray-700">
                    <div class="flex items-center gap-1">
                        <span class="text-xs">📍</span>
                        <span class="truncate max-w-[150px]" title="${rt.city}">${rt.city}</span>
                    </div>
                </td>
                <td class="py-2 px-3">
                    <span class="px-2 py-0.5 rounded font-bold text-[11px] bg-slate-100 text-slate-800 border border-slate-200">
                        🏷️ ${rt.brand}
                    </span>
                </td>
                <td class="py-2 px-3 text-center">
                    ${isActive
                        ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 Активна</span>'
                        : '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">💤 Спит (0)</span>'}
                </td>
                <td class="py-2 px-3 text-center font-bold ${isActive ? 'text-amber-700' : 'text-gray-300'}">${fmt(rt.mp_deals)}</td>
                <td class="py-2 px-3 text-center font-bold ${isActive ? 'text-sky-700' : 'text-gray-300'}">${fmt(rt.fdc_online_deals)}</td>
                <td class="py-2 px-3 text-center font-black ${isActive ? 'text-indigo-900 bg-indigo-50/60 text-sm' : 'text-gray-300'}">${fmt(rt.deals_count)}</td>
            </tr>
            `;
        });

        html += `</tbody></table>`;
        cont.innerHTML = html;

    } else {
        // Render Legal Entities Table
        let filtered = currentKamLegalEntities.filter(le => {
            if (kamModalStatusFilter === 'active' && le.total_deals === 0) return false;
            if (kamModalStatusFilter === 'sleeping' && le.total_deals > 0) return false;

            if (!q) return true;
            const mName = (le.name || '').toLowerCase().includes(q);
            const mPartner = (le.canonical_partner || '').toLowerCase().includes(q);
            const mInn = (le.inn || '').toLowerCase().includes(q);
            const mKam = (le.kam || '').toLowerCase().includes(q);
            const mCity = Array.from(le.cities || []).some(c => c.toLowerCase().includes(q));
            const mBrand = Array.from(le.brands || []).some(b => b.toLowerCase().includes(q));
            return mName || mPartner || mInn || mKam || mCity || mBrand;
        });

        if (filtered.length === 0) {
            cont.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">🔍</div>
                <p class="font-bold text-sm">Юридические лица не найдены</p>
                <p class="text-xs text-gray-400 mt-1">Попробуйте изменить поисковый запрос</p>
            </div>`;
            return;
        }

        let html = `
        <table class="min-w-full text-xs">
            <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200">
                <tr>
                    <th class="py-2.5 px-3 text-left w-10">#</th>
                    <th class="py-2.5 px-3 text-left min-w-[220px]">Юридическое лицо / Название</th>
                    <th class="py-2.5 px-3 text-center w-28">ИНН</th>
                    <th class="py-2.5 px-3 text-left min-w-[180px]">Master Partner</th>
                    <th class="py-2.5 px-3 text-center w-32">КАМ</th>
                    <th class="py-2.5 px-3 text-center w-20">Сделки МП</th>
                    <th class="py-2.5 px-3 text-center w-24">ФДЦ/Онлайн</th>
                    <th class="py-2.5 px-3 text-center w-24">Всего сделок</th>
                    <th class="py-2.5 px-3 text-left min-w-[160px]">Города / Бренды</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
        `;

        filtered.forEach((le, idx) => {
            const citiesStr = Array.from(le.cities || []).slice(0, 2).join(', ') + (le.cities.size > 2 ? ` (+${le.cities.size - 2})` : '');
            const brandsStr = Array.from(le.brands || []).slice(0, 3).join(', ') + (le.brands.size > 3 ? ` (+${le.brands.size - 3})` : '');

            html += `
            <tr class="hover:bg-indigo-50/40 transition font-medium">
                <td class="py-2 px-3 text-gray-400 font-mono">${idx + 1}</td>
                <td class="py-2 px-3 font-bold text-gray-900">
                    <div class="truncate max-w-[280px]" title="${le.name}">${le.name}</div>
                </td>
                <td class="py-2 px-3 text-center font-mono font-semibold text-gray-600">
                    ${le.inn ? `<span class="px-2 py-0.5 bg-gray-100 rounded text-[11px] border border-gray-200 font-mono font-bold">${le.inn}</span>` : '<span class="text-gray-300">—</span>'}
                </td>
                <td class="py-2 px-3 text-gray-800">
                    <div class="flex items-center gap-1">
                        ${le.partner_id ? `<span class="px-1.5 py-0.2 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">ID:${le.partner_id}</span>` : ''}
                        <span class="font-semibold truncate max-w-[200px]" title="${le.canonical_partner}">${le.canonical_partner}</span>
                    </div>
                </td>
                <td class="py-2 px-3 text-center text-gray-600 font-medium">${le.kam || '—'}</td>
                <td class="py-2 px-3 text-center font-bold text-amber-700">${fmt(le.mp_deals)}</td>
                <td class="py-2 px-3 text-center font-bold text-sky-700">${fmt(le.fdc_online_deals)}</td>
                <td class="py-2 px-3 text-center font-black text-blue-700 bg-blue-50/50 text-sm">${fmt(le.total_deals)}</td>
                <td class="py-2 px-3 text-gray-500">
                    <div class="truncate max-w-[180px]" title="${citiesStr}">${citiesStr || '—'}</div>
                    <div class="text-[10px] text-gray-400 truncate max-w-[180px]" title="${brandsStr}">${brandsStr || '—'}</div>
                </td>
            </tr>
            `;
        });

        html += `</tbody></table>`;
        cont.innerHTML = html;
    }
}

/* ====================================================================
 * Transferred Leads Modal & Excel Export Functionality
 * ====================================================================*/
let currentTransferredLeadsList = [];

function handleTransLeadsButtonClick(btn) {
    if (!btn) return;
    const pidStr = btn.getAttribute('data-pid');
    const pid = pidStr ? parseInt(pidStr, 10) : null;
    const pname = btn.getAttribute('data-pname') || '';
    const brand = btn.getAttribute('data-brand') || null;
    openTransferredLeadsModal(pid, pname, brand);
}

function openTransferredLeadsModal(pid, partnerName, brandFilter) {
    const modal = document.getElementById('modalTransferredLeads');
    if (!modal) return;

    const titleEl = document.getElementById('transLeadsModalPartnerName');
    const badgeEl = document.getElementById('transLeadsModalCountBadge');
    const subEl = document.getElementById('transLeadsModalSubtitle');
    const searchInput = document.getElementById('searchTransLeadsInput');
    if (searchInput) searchInput.value = '';

    const safePName = partnerName || 'Партнер';
    let displayName = safePName;
    if (brandFilter) displayName += ` (${brandFilter})`;
    if (titleEl) titleEl.innerText = displayName;

    // Get active filter config and current month
    const cfg = (typeof currentFilterConfig !== 'undefined') ? currentFilterConfig : { mode: 'month', month: '2026-09' };
    let curMonth = '2026-09';
    if (cfg.mode === 'month' && cfg.month) {
        curMonth = cfg.month;
    } else if (cfg.mode === 'all') {
        curMonth = 'all';
    }

    if (subEl) {
        subEl.innerText = curMonth === 'all'
            ? 'Реестр отправленных лидов дилеру из CRM за все время'
            : `Реестр отправленных лидов дилеру из CRM за период: ${curMonth}`;
    }

    const payload = window.dataPayload || (typeof payload !== 'undefined' ? payload : {});
    const regList = (payload && payload.partners_registry) || (typeof masterRegistry !== 'undefined' ? masterRegistry : []);

    // Registry lookup for emails & aliases
    let regPartner = null;
    if (pid) {
        regPartner = regList.find(p => p.partner_id == pid);
    }
    if (!regPartner && safePName) {
        const low = safePName.toLowerCase().trim();
        regPartner = regList.find(p =>
            (p.canonical_name && p.canonical_name.toLowerCase().trim() === low) ||
            (p.bitrix_aliases && p.bitrix_aliases.some(a => (a || '').toLowerCase().trim() === low)) ||
            (p.bi_aliases && p.bi_aliases.some(a => (a || '').toLowerCase().trim() === low))
        );
    }

    // Build client-to-deal map for models
    const clientDealMap = {};
    if (payload.sys_db && Array.isArray(payload.sys_db)) {
        payload.sys_db.forEach(d => {
            if (d.ClientId) clientDealMap[String(d.ClientId).trim()] = d;
            if (d.LeadId) clientDealMap[String(d.LeadId).trim()] = d;
        });
    }

    // Filter leads from payload.sys_db_partners
    const allLeads = (payload && payload.sys_db_partners && Array.isArray(payload.sys_db_partners)) ? payload.sys_db_partners : [];
    const matchedLeads = [];

    const normPName = safePName.toLowerCase().trim();
    const normBrand = brandFilter ? normalizeBrandName(brandFilter) : null;
    const targetPid = pid ? parseInt(pid, 10) : (regPartner ? regPartner.partner_id : null);

    allLeads.forEach(r => {
        if (r.Type !== 'Лид') return;
        const rMonth = (r.Month || '').replace("'", "");

        // Month / date filter
        if (cfg.mode === 'month') {
            if (curMonth !== 'all' && rMonth !== curMonth) return;
        } else if (cfg.mode === 'custom') {
            const fTime = cfg.from ? new Date(cfg.from).getTime() : -Infinity;
            const tTime = cfg.to ? new Date(cfg.to).getTime() : Infinity;
            const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
            if (d) {
                const t = d.getTime();
                if (t < fTime || t > tTime) return;
            }
        }

        // Transferred leads are clean leads without prepay
        if (r.HasPrepay && r.HasPrepay !== 0) return;

        // Match partner
        let match = false;
        if (targetPid && r.PartnerId && parseInt(r.PartnerId, 10) === targetPid) match = true;
        else if (r.Partner && r.Partner.toLowerCase().trim() === normPName) match = true;
        else if (r.RawPartner && r.RawPartner.toLowerCase().includes(normPName)) match = true;
        else if (regPartner && r.PartnerId && parseInt(r.PartnerId, 10) === regPartner.partner_id) match = true;
        else if (normPName && r.Partner && normPName.includes(r.Partner.toLowerCase().trim())) match = true;

        if (!match && regPartner) {
            const rName = (r.Partner || r.RawPartner || '').toLowerCase().trim();
            if (rName) {
                if (regPartner.canonical_name && regPartner.canonical_name.toLowerCase().trim() === rName) match = true;
                else if (regPartner.bitrix_aliases && regPartner.bitrix_aliases.some(a => (a || '').toLowerCase().trim() === rName)) match = true;
                else if (regPartner.bi_aliases && regPartner.bi_aliases.some(a => (a || '').toLowerCase().trim() === rName)) match = true;
            }
        }

        if (!match) return;

        // Match brand if provided
        if (normBrand) {
            const b = normalizeBrandName(r.Brand);
            if (b !== normBrand) return;
        }

        // Resolve model from deals if not present in lead
        let model = r.Model || '';
        const deal = (r.ClientId && clientDealMap[String(r.ClientId).trim()]) || (r.LeadId && clientDealMap[String(r.LeadId).trim()]);
        if (deal && deal.Model) {
            model = deal.Model;
        }

        // Resolve recipient email from OEM data or pochta_aliases
        let recipientEmail = '';
        if (regPartner) {
            if (regPartner.oem_data && regPartner.oem_data.length > 0) {
                const leadBrand = normalizeBrandName(r.Brand);
                const matchingOem = regPartner.oem_data.find(o => normalizeBrandName(o.brand) === leadBrand && o.email) || regPartner.oem_data.find(o => o.email);
                if (matchingOem && matchingOem.email) {
                    recipientEmail = matchingOem.email;
                }
            }
            if (!recipientEmail && regPartner.pochta_aliases && regPartner.pochta_aliases.length > 0) {
                recipientEmail = regPartner.pochta_aliases.join(', ');
            }
        }

        matchedLeads.push({
            lead_id: r.LeadId || '',
            client_id: r.ClientId || '',
            date_serial: r.Date,
            brand: r.Brand || '—',
            model: model || '—',
            partner_name: r.Partner || safePName,
            recipient_email: recipientEmail || '—',
            has_prepay: r.HasPrepay || 0
        });
    });

    // Sort by date descending
    matchedLeads.sort((a, b) => (b.date_serial || 0) - (a.date_serial || 0));

    currentTransferredLeadsList = matchedLeads;

    if (badgeEl) badgeEl.innerText = `${matchedLeads.length} шт.`;

    renderTransferredLeadsModalTable(matchedLeads);

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.style.display = 'flex';
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function closeTransferredLeadsModal() {
    const modal = document.getElementById('modalTransferredLeads');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        modal.style.display = 'none';
    }
}

function renderTransferredLeadsModalTable(leads) {
    const container = document.getElementById('transLeadsTableContainer');
    const counterEl = document.getElementById('transLeadsRowsCounter');
    if (!container) return;

    if (counterEl) {
        counterEl.innerText = `Отображено: ${leads.length} из ${currentTransferredLeadsList.length}`;
    }

    if (leads.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">📭</div>
                <p class="font-bold text-gray-700">Лиды не найдены</p>
                <p class="text-xs text-gray-400 mt-1">По данному партнеру отсутствуют переданные лиды за указанный период</p>
            </div>
        `;
        return;
    }

    let html = `
    <table class="min-w-full text-xs">
        <thead class="bg-slate-800 text-white font-bold sticky top-0 z-10">
            <tr>
                <th class="py-2.5 px-3 text-center w-12">№</th>
                <th class="py-2.5 px-3 text-left w-24">Дата</th>
                <th class="py-2.5 px-3 text-left w-36">ID Лида (CRM)</th>
                <th class="py-2.5 px-3 text-left w-32">Client ID</th>
                <th class="py-2.5 px-3 text-left w-32">Марка</th>
                <th class="py-2.5 px-3 text-left">Модель</th>
                <th class="py-2.5 px-3 text-left">Email получателя (ДЦ)</th>
                <th class="py-2.5 px-3 text-center w-28">Статус аванса</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
    `;

    leads.forEach((l, idx) => {
        const rowBg = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/60';

        let dateStr = '—';
        if (l.date_serial && typeof excelToJSDate === 'function') {
            const d = excelToJSDate(l.date_serial);
            if (d) dateStr = d.toLocaleDateString('ru-RU');
        }

        const leadLink = l.lead_id
            ? `<a href="https://back.sberauto.com/crm/leads/${l.lead_id}" target="_blank" class="inline-flex items-center gap-1 font-bold text-blue-600 hover:text-blue-800 hover:underline">
                ${l.lead_id}
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
               </a>`
            : '<span class="text-gray-400">—</span>';

        const clientLink = l.client_id
            ? `<a href="https://back.sberauto.com/crm/clients/${l.client_id}" target="_blank" class="font-mono text-slate-700 hover:text-blue-600 font-semibold">
                ${l.client_id}
               </a>`
            : '<span class="text-gray-400">—</span>';

        const prepayBadge = l.has_prepay === 1
            ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">Есть аванс</span>`
            : `<span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-600">Без аванса</span>`;

        html += `
        <tr class="${rowBg} hover:bg-blue-50/50 transition">
            <td class="py-2 px-3 text-center text-gray-400 font-medium">${idx + 1}</td>
            <td class="py-2 px-3 text-gray-700 whitespace-nowrap">${dateStr}</td>
            <td class="py-2 px-3 whitespace-nowrap">${leadLink}</td>
            <td class="py-2 px-3 whitespace-nowrap">${clientLink}</td>
            <td class="py-2 px-3 font-bold text-gray-900">${l.brand}</td>
            <td class="py-2 px-3 text-gray-700 font-medium">${l.model}</td>
            <td class="py-2 px-3 text-gray-600 font-mono text-[11px] truncate max-w-xs" title="${l.recipient_email}">${l.recipient_email}</td>
            <td class="py-2 px-3 text-center">${prepayBadge}</td>
        </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function filterTransferredLeadsModalTable(q) {
    const query = (q || '').toLowerCase().trim();
    if (!query) {
        renderTransferredLeadsModalTable(currentTransferredLeadsList);
        return;
    }
    const filtered = currentTransferredLeadsList.filter(l => {
        return (l.lead_id && l.lead_id.toLowerCase().includes(query)) ||
               (l.client_id && l.client_id.toLowerCase().includes(query)) ||
               (l.brand && l.brand.toLowerCase().includes(query)) ||
               (l.model && l.model.toLowerCase().includes(query)) ||
               (l.recipient_email && l.recipient_email.toLowerCase().includes(query));
    });
    renderTransferredLeadsModalTable(filtered);
}

function exportTransferredLeadsToExcel() {
    if (typeof XLSX === 'undefined') {
        alert("Библиотека экспорта в Excel еще загружается. Повторите попытку через секунду.");
        return;
    }
    if (!currentTransferredLeadsList || currentTransferredLeadsList.length === 0) {
        alert("Нет лидов для экспорта.");
        return;
    }

    const wsData = [
        ["№", "ID Лида", "Client ID", "Партнер", "Дата передачи", "Марка", "Модель", "Email получателя (ДЦ)", "Статус аванса", "Ссылка на CRM BackOffice"]
    ];

    currentTransferredLeadsList.forEach((l, idx) => {
        let dateStr = '—';
        if (l.date_serial && typeof excelToJSDate === 'function') {
            const d = excelToJSDate(l.date_serial);
            if (d) dateStr = d.toLocaleDateString('ru-RU');
        }
        const backofficeUrl = l.lead_id ? `https://back.sberauto.com/crm/leads/${l.lead_id}` : (l.client_id ? `https://back.sberauto.com/crm/clients/${l.client_id}` : '—');

        wsData.push([
            idx + 1,
            l.lead_id || '—',
            l.client_id || '—',
            l.partner_name || '—',
            dateStr,
            l.brand || '—',
            l.model || '—',
            l.recipient_email || '—',
            l.has_prepay === 1 ? 'Есть аванс' : 'Без аванса',
            backofficeUrl
        ]);
    });

    const ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 6 },
        { wch: 14 },
        { wch: 16 },
        { wch: 28 },
        { wch: 14 },
        { wch: 16 },
        { wch: 20 },
        { wch: 35 },
        { wch: 15 },
        { wch: 45 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Переданные_лиды");

    const pName = (currentTransferredLeadsList[0] && currentTransferredLeadsList[0].partner_name) || 'Партнер';
    const cleanName = pName.replace(/["*\\/?:<>|]/g, '').replace(/\s+/g, '_').slice(0, 30);
    const todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    const fileName = `Переданные_лиды_${cleanName}_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
}

