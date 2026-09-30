/* ====================================================================
 * B2C Analytics Dashboard — Lead Geo & Dealers Module
 * Tracks qualified leads, transfers to dealers by region, and BFS client drilldown
 * ====================================================================*/

let currentLeadGeoFilter = {
    search: '',
    brand: 'all',
    status: 'all'
};

let currentModalClients = [];

/**
 * Returns currently selected month for Lead Geo tab ('2026-09', '2026-08', or 'all')
 */
function getActiveLeadGeoMonth() {
    if (window.currentFilterConfig) {
        if (window.currentFilterConfig.mode === 'all') return 'all';
        if (window.currentFilterConfig.month) return window.currentFilterConfig.month;
    }
    return '2026-09';
}

/**
 * Initializes and renders the Lead Geo & Dealers Tab
 */
function renderLeadGeoTab() {
    const activeMonth = getActiveLeadGeoMonth();
    const lgd = (window.dataPayload && window.dataPayload.lead_geo_dealers) || {};
    const monthData = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd))) || lgd;
    const summary = monthData.summary || lgd.summary || {
        total_clients: 0,
        qual_clients: 0,
        trans_clients: 0,
        trans_qual_clients: 0,
        trans_qual_pct: 0,
        deals_from_trans: 0,
        deals_cr_pct: 0
    };
    const regions = monthData.regions || lgd.regions || [];

    // Render KPI Cards
    const elQual = document.getElementById('kpiGeoQualClients');
    const elTrans = document.getElementById('kpiGeoTransClients');
    const elTransPct = document.getElementById('kpiGeoTransPct');
    const elDeals = document.getElementById('kpiGeoDeals');
    const elRegionsCount = document.getElementById('kpiGeoRegionsCount');

    if (elQual) elQual.innerText = fmtNum(summary.qual_clients);
    if (elTrans) elTrans.innerText = fmtNum(summary.trans_clients);
    if (elTransPct) elTransPct.innerText = `${summary.trans_qual_pct}%`;
    if (elDeals) elDeals.innerText = fmtNum(summary.deals_from_trans);
    if (elRegionsCount) elRegionsCount.innerText = fmtNum(regions.length);

    // Populate Brand Filter if empty
    const brandSel = document.getElementById('leadGeoBrandFilter');
    if (brandSel && brandSel.options.length <= 1) {
        const auxKeywords = ["КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ВНЕСЕНИЕ АВАНСА", "АВАНС"];
        const brandsSet = new Set();
        (lgd.regions || []).forEach(r => {
            (r.dealers || []).forEach(d => {
                (d.top_brands || []).forEach(b => {
                    if (b && !auxKeywords.some(kw => b.toUpperCase().includes(kw))) {
                        brandsSet.add(b);
                    }
                });
            });
        });
        Array.from(brandsSet).sort().forEach(b => {
            if (b && b !== 'Другие') {
                const opt = document.createElement('option');
                opt.value = b;
                opt.textContent = b;
                brandSel.appendChild(opt);
            }
        });
    }

    renderLeadGeoTable();
}

/**
 * Renders the interactive Region & Dealer Table
 */
function renderLeadGeoTable() {
    const container = document.getElementById('leadGeoTableContainer');
    if (!container) return;

    const activeMonth = getActiveLeadGeoMonth();
    const lgd = (window.dataPayload && window.dataPayload.lead_geo_dealers) || {};
    const monthData = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd))) || lgd;
    const rawRegions = monthData.regions || lgd.regions || [];

    const q = (currentLeadGeoFilter.search || '').toLowerCase().trim();
    const selBrand = currentLeadGeoFilter.brand;
    const selStatus = currentLeadGeoFilter.status;

    let totalQualFiltered = 0;
    let totalTransFiltered = 0;
    let totalDealsFiltered = 0;
    let matchingDealersCount = 0;

    let html = `<table id="tableLeadGeo" class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50 text-slate-700 text-xs font-bold uppercase tracking-wider">
            <tr>
                <th style="min-width: 260px;">Регион / Дилерский Центр</th>
                <th style="text-align: center; width: 140px;">Квалифицировано</th>
                <th style="text-align: center; width: 140px;">Передано в ДЦ</th>
                <th style="text-align: center; width: 160px;">Доля передачи (% квал.)</th>
                <th style="text-align: center; width: 120px;">Сделки</th>
                <th style="text-align: center; width: 120px;">Конверсия</th>
                <th style="text-align: right; width: 170px;">База клиентов БФС</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 bg-white">`;

    rawRegions.forEach((reg, rIdx) => {
        // Filter dealers within region
        let filteredDealers = (reg.dealers || []).filter(d => {
            if (q) {
                const matchName = d.dealer_name.toLowerCase().includes(q);
                const matchReg = reg.region_name.toLowerCase().includes(q);
                const matchBrand = (d.top_brands || []).some(b => b.toLowerCase().includes(q));
                if (!matchName && !matchReg && !matchBrand) return false;
            }
            if (selBrand !== 'all') {
                if (!(d.top_brands || []).includes(selBrand)) return false;
            }
            if (selStatus === 'qual' && d.qual_clients === 0) return false;
            if (selStatus === 'trans' && d.trans_clients === 0) return false;
            if (selStatus === 'deals' && d.deals === 0) return false;
            return true;
        });

        if (filteredDealers.length === 0) return;

        let regQual = filteredDealers.reduce((s, d) => s + d.qual_clients, 0);
        let regTrans = filteredDealers.reduce((s, d) => s + d.trans_clients, 0);
        let regTransQual = filteredDealers.reduce((s, d) => s + d.trans_qual_clients, 0);
        let regDeals = filteredDealers.reduce((s, d) => s + d.deals, 0);
        let regTransPct = regQual > 0 ? ((regTransQual / regQual) * 100).toFixed(1) : '0.0';
        let regCr = regTrans > 0 ? ((regDeals / regTrans) * 100).toFixed(1) : '0.0';

        totalQualFiltered += regQual;
        totalTransFiltered += regTrans;
        totalDealsFiltered += regDeals;
        matchingDealersCount += filteredDealers.length;

        // Group Header (Region Row)
        const safeRegName = encodeURIComponent(reg.region_name);
        html += `
        <tr class="region-group-row bg-slate-50/90 hover:bg-emerald-50/60 font-bold cursor-pointer group border-b border-slate-200 transition select-none" onclick="toggleRegionRows('${rIdx}')">
            <td class="py-3 px-4 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span id="regionArrow_${rIdx}" class="text-xs transition-transform transform text-slate-400 group-hover:text-emerald-600 font-bold">▶</span>
                    <span class="text-sm font-black text-slate-900">${reg.region_name}</span>
                    <span class="px-2 py-0.5 text-[10px] rounded-full bg-slate-200 text-slate-700 font-bold border border-slate-300">
                        ${filteredDealers.length} ДЦ
                    </span>
                </div>
            </td>
            <td class="text-center font-black text-emerald-700">
                <span class="cursor-pointer underline decoration-dotted hover:text-emerald-800" onclick="event.stopPropagation(); openRegionClientDrilldown('${safeRegName}', 'qual')" title="Показать всех квалифицированных клиентов региона">
                    ${fmtNum(regQual)}
                </span>
            </td>
            <td class="text-center font-black text-blue-700">
                <span class="cursor-pointer underline decoration-dotted hover:text-blue-800" onclick="event.stopPropagation(); openRegionClientDrilldown('${safeRegName}', 'trans')" title="Показать всех переданных клиентов региона">
                    ${fmtNum(regTrans)}
                </span>
            </td>
            <td class="text-center">
                <div class="flex items-center justify-center gap-1.5 text-xs font-bold text-slate-700">
                    <span>${regTransPct}%</span>
                    <div class="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden shrink-0">
                        <div class="h-full bg-emerald-500 rounded-full" style="width: ${Math.min(100, parseFloat(regTransPct))}%"></div>
                    </div>
                </div>
            </td>
            <td class="text-center font-black text-purple-700">
                <span class="cursor-pointer underline decoration-dotted hover:text-purple-800" onclick="event.stopPropagation(); openRegionClientDrilldown('${safeRegName}', 'deals')" title="Показать все сделки региона">
                    ${fmtNum(regDeals)}
                </span>
            </td>
            <td class="text-center text-xs text-slate-800 font-black">${regCr}%</td>
            <td class="text-right">
                <button onclick="event.stopPropagation(); openRegionClientDrilldown('${safeRegName}', 'all')" class="px-3 py-1 bg-white hover:bg-emerald-50 text-emerald-700 border border-emerald-300 rounded-lg text-xs font-bold transition shadow-sm inline-flex items-center gap-1 cursor-pointer">
                    <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    Клиенты региона
                </button>
            </td>
        </tr>`;

        // Dealer Sub-rows
        filteredDealers.forEach((d, dIdx) => {
            const safeDealerName = encodeURIComponent(d.dealer_name);
            const rowBg = dIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50/70';
            const brandsBadge = (d.top_brands || []).map(b => `<span class="px-1.5 py-0.2 bg-gray-100 text-gray-700 rounded text-[10px] font-semibold border border-gray-200">${b}</span>`).join(' ');

            html += `
            <tr class="dealer-subrow region-subrow-${rIdx} ${rowBg} hover:bg-blue-50/40 border-b border-slate-100 transition" style="display: none;">
                <td class="pl-8 py-2.5">
                    <div class="font-bold text-slate-900 text-xs">${d.dealer_name}</div>
                    <div class="text-[11px] text-gray-500 flex items-center gap-1 mt-0.5">
                        ${brandsBadge || '<span class="text-gray-400">Мультибренд</span>'}
                    </div>
                </td>
                <td class="text-center font-bold text-emerald-700">
                    <button onclick="openDealerClientDrilldown('${safeRegName}', '${safeDealerName}', 'qual')" class="px-2 py-0.5 rounded hover:bg-emerald-100 transition cursor-pointer font-bold text-emerald-700" title="Нажмите, чтобы открыть ${d.qual_clients} квалифицированных клиентов с ссылками на БФС">
                        ${fmtNum(d.qual_clients)}
                    </button>
                </td>
                <td class="text-center font-bold text-blue-700">
                    <button onclick="openDealerClientDrilldown('${safeRegName}', '${safeDealerName}', 'trans')" class="px-2 py-0.5 rounded hover:bg-blue-100 transition cursor-pointer font-bold text-blue-700" title="Нажмите, чтобы открыть ${d.trans_clients} переданных клиентов с ссылками на БФС">
                        ${fmtNum(d.trans_clients)}
                    </button>
                </td>
                <td class="text-center">
                    <div class="flex items-center justify-center gap-1.5 text-xs font-semibold text-gray-700">
                        <span>${d.trans_qual_pct}%</span>
                        <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden shrink-0">
                            <div class="h-full bg-blue-500 rounded-full" style="width: ${Math.min(100, d.trans_qual_pct)}%"></div>
                        </div>
                    </div>
                </td>
                <td class="text-center font-bold text-purple-800">
                    <button onclick="openDealerClientDrilldown('${safeRegName}', '${safeDealerName}', 'deals')" class="px-2 py-0.5 rounded hover:bg-purple-100 transition cursor-pointer font-bold text-purple-800" title="Нажмите, чтобы открыть ${d.deals} клиентов со сделками с ссылками на БФС">
                        ${fmtNum(d.deals)}
                    </button>
                </td>
                <td class="text-center text-xs font-semibold ${d.deals_cr_pct > 0 ? 'text-emerald-700 font-bold' : 'text-gray-400'}">
                    ${d.deals_cr_pct}%
                </td>
                <td class="text-right">
                    <button onclick="openDealerClientDrilldown('${safeRegName}', '${safeDealerName}', 'all')" class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-xs font-bold transition inline-flex items-center gap-1 cursor-pointer shadow-sm">
                        <span>🔗 БФС (${d.total_clients || (d.clients ? d.clients.length : 0)})</span>
                    </button>
                </td>
            </tr>`;
        });
    });

    // Grand Total Row
    let totalTransPct = totalQualFiltered > 0 ? ((totalTransFiltered / totalQualFiltered) * 100).toFixed(1) : '0.0';
    let totalCr = totalTransFiltered > 0 ? ((totalDealsFiltered / totalTransFiltered) * 100).toFixed(1) : '0.0';

    html += `
    <tr class="table-total bg-slate-900 text-white font-bold">
        <td class="py-3 px-4 font-black">ИТОГО ПО ВЫБОРКЕ (${matchingDealersCount} ДЦ)</td>
        <td class="text-center font-black text-emerald-400">${fmtNum(totalQualFiltered)}</td>
        <td class="text-center font-black text-blue-400">${fmtNum(totalTransFiltered)}</td>
        <td class="text-center font-black text-white">${totalTransPct}%</td>
        <td class="text-center font-black text-amber-300">${fmtNum(totalDealsFiltered)}</td>
        <td class="text-center font-black text-emerald-400">${totalCr}%</td>
        <td></td>
    </tr>
    </tbody></table>`;

    container.innerHTML = html;
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Toggle expanding/collapsing sub-rows for a region
 */
function toggleRegionRows(rIdx) {
    const rows = document.querySelectorAll(`.region-subrow-${rIdx}`);
    const arrow = document.getElementById(`regionArrow_${rIdx}`);
    if (rows.length === 0) return;
    const isCurrentlyHidden = rows[0].style.display === 'none';
    rows.forEach(r => {
        r.style.display = isCurrentlyHidden ? '' : 'none';
    });
    if (arrow) {
        arrow.style.transform = isCurrentlyHidden ? 'rotate(90deg)' : 'rotate(0deg)';
    }
}

/**
 * Opens Client Drilldown Modal for a specific Dealer
 * Lazy-loads geo_clients.json on first invocation for performance
 */
let _geoClientsCache = null;
async function _ensureGeoClients() {
    if (_geoClientsCache) return _geoClientsCache;
    try {
        const cacheKey = window._dataVersion || Date.now();
        const res = await fetch('geo_clients.json?v=' + cacheKey);
        if (res.ok) {
            _geoClientsCache = await res.json();
        }
    } catch (e) {
        console.warn('Failed to load geo_clients.json, falling back to main payload', e);
    }
    // Fallback: use main payload if separate file not available
    if (!_geoClientsCache) {
        _geoClientsCache = (window.dataPayload && window.dataPayload.lead_geo_dealers) || {};
    }
    return _geoClientsCache;
}

async function openDealerClientDrilldown(encodedReg, encodedDealer, filterType) {
    const regName = decodeURIComponent(encodedReg);
    const dealerName = decodeURIComponent(encodedDealer);

    const activeMonth = getActiveLeadGeoMonth();
    const lgd = await _ensureGeoClients();
    const monthData = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd))) || lgd;

    const reg = (monthData.regions || []).find(r => r.region_name === regName) || (lgd.regions || []).find(r => r.region_name === regName);
    if (!reg) return;

    let dealer = (reg.dealers || []).find(d => d.dealer_name === dealerName);
    if (!dealer || !dealer.clients || dealer.clients.length === 0) {
        const rootReg = (lgd.regions || []).find(r => r.region_name === regName);
        if (rootReg) {
            const rootDealer = (rootReg.dealers || []).find(d => d.dealer_name === dealerName);
            if (rootDealer && rootDealer.clients && rootDealer.clients.length > 0) {
                dealer = rootDealer;
            }
        }
    }
    if (!dealer) return;

    let clients = (dealer.clients || []).slice();
    if (activeMonth !== 'all') {
        clients = clients.filter(c => c.month === activeMonth);
    }
    if (filterType === 'qual') clients = clients.filter(c => c.is_qual);
    if (filterType === 'trans') clients = clients.filter(c => c.is_trans);
    if (filterType === 'deals') clients = clients.filter(c => c.has_deal);

    const typeLabels = {
        'all': 'Все клиенты',
        'qual': 'Квалифицированные клиенты (Целевой = 1)',
        'trans': 'Клиенты, переданные в ДЦ',
        'deals': 'Клиенты со сделками'
    };

    const periodLabel = activeMonth === 'all' ? 'Весь период' : formatMonthLabel(activeMonth).replace('📅 ', '');

    openClientDrilldownModal({
        title: `${dealer.dealer_name} — ${typeLabels[filterType] || 'База клиентов'}`,
        subtitle: `Период: ${periodLabel} | Регион: ${reg.region_name} | Всего клиентов в выборке: ${clients.length}`,
        clients: clients,
        fileName: `Клиенты_БФС_${dealer.dealer_name.replace(/["*\\/?:<>|]/g, '')}_${activeMonth}_${filterType}`
    });
}

/**
 * Opens Client Drilldown Modal for an entire Region
 */
async function openRegionClientDrilldown(encodedReg, filterType) {
    const regName = decodeURIComponent(encodedReg);

    const activeMonth = getActiveLeadGeoMonth();
    const lgd = await _ensureGeoClients();
    const monthData = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd))) || lgd;

    const reg = (monthData.regions || []).find(r => r.region_name === regName) || (lgd.regions || []).find(r => r.region_name === regName);
    if (!reg) return;

    const rootReg = (lgd.regions || []).find(r => r.region_name === regName);
    const sourceDealers = (reg.dealers && reg.dealers.some(d => d.clients && d.clients.length > 0))
        ? reg.dealers
        : (rootReg ? rootReg.dealers : reg.dealers || []);

    let allClients = [];
    (sourceDealers || []).forEach(d => {
        (d.clients || []).forEach(c => {
            allClients.push({
                ...c,
                dealer_name: d.dealer_name
            });
        });
    });

    if (activeMonth !== 'all') {
        allClients = allClients.filter(c => c.month === activeMonth);
    }
    if (filterType === 'qual') allClients = allClients.filter(c => c.is_qual);
    if (filterType === 'trans') allClients = allClients.filter(c => c.is_trans);
    if (filterType === 'deals') allClients = allClients.filter(c => c.has_deal);

    const typeLabels = {
        'all': 'Все клиенты региона',
        'qual': 'Квалифицированные клиенты региона (Целевой = 1)',
        'trans': 'Клиенты региона, переданные в ДЦ',
        'deals': 'Клиенты со сделками региона'
    };

    const periodLabel = activeMonth === 'all' ? 'Весь период' : formatMonthLabel(activeMonth).replace('📅 ', '');
    const dealersCount = (reg.dealers || []).length || reg.dealers_count || 0;

    openClientDrilldownModal({
        title: `${reg.region_name} — ${typeLabels[filterType] || 'База клиентов'}`,
        subtitle: `Период: ${periodLabel} | Дилеров в регионе: ${dealersCount} | Всего клиентов в выборке: ${allClients.length}`,
        clients: allClients,
        fileName: `Клиенты_БФС_${reg.region_name.replace(/["*\\/?:<>|]/g, '')}_${activeMonth}_${filterType}`
    });
}

/**
 * Renders the Client Drilldown Modal window
 */
function openClientDrilldownModal(config) {
    const modal = document.getElementById('modalClientDrilldown');
    if (!modal) return;

    document.getElementById('modalClientDrilldownTitle').innerText = config.title;
    document.getElementById('modalClientDrilldownSubtitle').innerText = config.subtitle;

    currentModalClients = config.clients || [];
    window._currentModalExportFileName = config.fileName || 'Клиенты_БФС_Выборка';

    renderModalClientRows(currentModalClients);

    modal.classList.remove('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function closeClientDrilldownModal() {
    const modal = document.getElementById('modalClientDrilldown');
    if (modal) modal.classList.add('hidden');
}

/**
 * Filter rows inside Client Drilldown Modal in real-time
 */
function filterModalClientsTable(q) {
    const query = (q || '').toLowerCase().trim();
    if (!query) {
        renderModalClientRows(currentModalClients);
        return;
    }
    const filtered = currentModalClients.filter(c => {
        const idMatch = (c.id || '').toLowerCase().includes(query);
        const brandMatch = (c.brand || '').toLowerCase().includes(query);
        const modelMatch = (c.model || '').toLowerCase().includes(query);
        const vinMatch = (c.vin || '').toLowerCase().includes(query);
        const dealerMatch = (c.dealer || c.dealer_name || '').toLowerCase().includes(query);
        return idMatch || brandMatch || modelMatch || vinMatch || dealerMatch;
    });
    renderModalClientRows(filtered);
}

function renderModalClientRows(clients) {
    const tbody = document.getElementById('modalClientDrilldownTbody');
    const counter = document.getElementById('modalClientCountBadge');
    if (counter) counter.innerText = `${clients.length} клиентов`;

    if (!tbody) return;

    if (clients.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-400 font-medium">Нет записей клиентов по выбранному фильтру</td></tr>`;
        return;
    }

    let html = '';
    clients.slice(0, 300).forEach((c, idx) => {
        const rowBg = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/70';
        const qualBadge = c.is_qual ? 
            `<span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px] border border-emerald-200">Целевой</span>` : 
            `<span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded font-semibold text-[10px]">Не целевой</span>`;

        const transBadge = c.is_trans ? 
            `<span class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-bold text-[10px] border border-blue-200">Передан в ДЦ</span>` : 
            `<span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-semibold text-[10px]">В пуле</span>`;

        const dealBadge = c.has_deal ? 
            `<span class="px-2 py-0.5 bg-purple-100 text-purple-900 rounded font-bold text-[10px] border border-purple-200">Сделка</span>` : 
            `<span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px]">В работе</span>`;

        html += `
        <tr class="${rowBg} hover:bg-blue-50/50 transition text-xs">
            <td class="py-2 px-3 font-mono font-bold text-slate-800">
                <a href="${c.bfs_url}" target="_blank" class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold transition inline-flex items-center gap-1.5 shadow-sm" title="Открыть карточку клиента в БФС (CRM Backoffice)">
                    <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    BFS #${c.id}
                </a>
            </td>
            <td class="py-2 px-3 font-semibold text-slate-900">
                ${c.brand || '—'} <span class="text-slate-500 font-normal">${c.model || ''}</span>
            </td>
            <td class="py-2 px-3 text-slate-700">${c.dealer || c.dealer_name || 'Пул СберАвто'}</td>
            <td class="py-2 px-3 text-center">${qualBadge}</td>
            <td class="py-2 px-3 text-center">${transBadge}</td>
            <td class="py-2 px-3 text-center">${dealBadge}</td>
            <td class="py-2 px-3 font-mono text-[11px] text-slate-600 select-all">${c.vin || '—'}</td>
        </tr>`;
    });

    if (clients.length > 300) {
        html += `<tr><td colspan="7" class="text-center py-3 bg-amber-50 text-amber-800 font-bold text-xs">Показаны первые 300 клиентов из ${clients.length}. Для полного списка нажмите «Экспорт в Excel».</td></tr>`;
    }

    tbody.innerHTML = html;
}

/**
 * Export modal clients list to Excel
 */
function exportModalClientsToExcel() {
    if (!currentModalClients || currentModalClients.length === 0) {
        alert("Нет данных для выгрузки.");
        return;
    }

    const wsData = [
        ["ID клиента", "Ссылка на БФС", "Марка", "Модель", "Дилер / Партнер", "Квалифицирован", "Передан в ДЦ", "Сделка", "ВИН", "Цена"]
    ];

    currentModalClients.forEach(c => {
        wsData.push([
            c.id || "—",
            c.bfs_url || `https://backoffice.x.sberauto.com/crm/manager/${c.id}`,
            c.brand || "—",
            c.model || "—",
            c.dealer || c.dealer_name || "—",
            c.is_qual ? "Да" : "Нет",
            c.is_trans ? "Да" : "Нет",
            c.has_deal ? "Да" : "Нет",
            c.vin || "—",
            c.price || 0
        ]);
    });

    const ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 15 },
        { wch: 45 },
        { wch: 18 },
        { wch: 20 },
        { wch: 35 },
        { wch: 16 },
        { wch: 16 },
        { wch: 14 },
        { wch: 25 },
        { wch: 15 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Клиенты_БФС");

    const todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    const fileName = `${window._currentModalExportFileName || 'Клиенты_БФС'}_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
    alert(`✅ Успешно выгружена база (${currentModalClients.length} клиентов) в файл «${fileName}»!`);
}

// Filter listeners
function onLeadGeoSearchInput(val) {
    currentLeadGeoFilter.search = val;
    renderLeadGeoTable();
}

function onLeadGeoBrandChange(val) {
    currentLeadGeoFilter.brand = val;
    renderLeadGeoTable();
}

function setLeadGeoStatusFilter(status) {
    currentLeadGeoFilter.status = status;
    document.querySelectorAll('.lead-geo-chip').forEach(btn => {
        btn.classList.remove('bg-emerald-600', 'text-white');
        btn.classList.add('bg-slate-100', 'text-slate-700');
    });
    const activeBtn = document.getElementById(`geoChip_${status}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-slate-100', 'text-slate-700');
        activeBtn.classList.add('bg-emerald-600', 'text-white');
    }
    renderLeadGeoTable();
}
