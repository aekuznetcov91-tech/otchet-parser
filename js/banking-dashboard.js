/**
 * banking-dashboard.js
 * ====================
 * Единый аналитический дашборд:
 * Лидогенерация, Сделки ДЦ и Банки (Секции 1, 2, 3 и База Сделок).
 * Оптимизирован: данные динамически подтягиваются из data.json.
 */

function getBankingDataPayload() {
    if (window.bankingAnalyticsData) return window.bankingAnalyticsData;
    if (window.dataPayload && window.dataPayload.banking_analytics) return window.dataPayload.banking_analytics;
    if (window.currentData && window.currentData.banking_analytics) return window.currentData.banking_analytics;
    return {};
}

// Proxy to dynamically resolve any dataPayload property from loaded data
const dataPayload = new Proxy({}, {
    get(target, prop) {
        const p = getBankingDataPayload();
        return p[prop];
    },
    has(target, prop) {
        const p = getBankingDataPayload();
        return prop in p;
    },
    ownKeys(target) {
        const p = getBankingDataPayload();
        return Reflect.ownKeys(p);
    },
    getOwnPropertyDescriptor(target, prop) {
        const p = getBankingDataPayload();
        return Object.getOwnPropertyDescriptor(p, prop) || {
            configurable: true,
            enumerable: true,
            value: p[prop]
        };
    }
});


let currentActiveDb = 'lead_deals';
let currentDbFilter = 'all';
let isTopSberExpanded = false;
let isAntiTopExpanded = false;
let funnelPaymentsChartInstance = null;
let funnelBanksChartInstance = null;

// 1. Navigation Switcher
function switchSection(secId) {
    document.querySelectorAll('#tab-banking .section-view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('#tab-banking .nav-tab-btn').forEach(el => el.classList.remove('active'));
    
    const target = document.getElementById('section-' + secId);
    if (target) target.classList.add('active');
    
    // Mark matching nav tab button active
    const btns = document.querySelectorAll('#tab-banking .nav-tab-btn');
    btns.forEach(b => {
        if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(secId)) {
            b.classList.add('active');
        }
    });

    if (secId === 'rankings') {
        renderRankings();
    }
}

function switchBankingSection(secId, btn) {
    switchSection(secId);
    if (btn) {
        document.querySelectorAll('#tab-banking .nav-tab-btn').forEach(el => el.classList.remove('active'));
        btn.classList.add('active');
    }
}

// 2. Render Top / Anti-Top Rankings (Strict Disjoint Partition)
function renderRankings() {
    const topSberTbody = document.getElementById('topSberTbody');
    const antiTopTbody = document.getElementById('antiTopTbody');
    if (!topSberTbody || !antiTopTbody) return;

    const topSberData = isTopSberExpanded ? dataPayload.left_group_all : dataPayload.left_group_top10;
    const antiTopData = isAntiTopExpanded ? dataPayload.right_group_all : dataPayload.right_group_top10;

    const subSber = document.getElementById('topSberHeaderSubtitle');
    if (subSber) {
        subSber.innerText = isTopSberExpanded ? 
            `Все ДЦ с долей Сбера ≥ 50% (${dataPayload.left_group_all.length} партнеров)` : 
            `ТОП-10 (сделок от 10) • Доля Сбера ≥ 50%`;
    }

    const subAnti = document.getElementById('antiTopHeaderSubtitle');
    if (subAnti) {
        subAnti.innerText = isAntiTopExpanded ? 
            `Все ДЦ с долей Др.Банков > 50% (${dataPayload.right_group_all.length} партнеров)` : 
            `АНТИТОП-10 (сделок от 10) • Доля Др.Банков > 50%`;
    }

    topSberTbody.innerHTML = (topSberData || []).map((p, idx) => `
        <tr>
            <td class="center"><span class="badge badge-sber">${idx + 1}</span></td>
            <td>
                <div style="font-weight: 600; font-size: 13px;">${p.partner}</div>
                <div style="font-size: 11px; color: var(--text-muted);">${p.city} • ${p.macro}</div>
            </td>
            <td class="num"><b>${p.total_deals}</b></td>
            <td class="num"><span class="badge badge-sber">${p.sber_deals}</span></td>
            <td class="num"><span class="badge badge-cash">${p.other_banks_deals}</span></td>
            <td class="num">
                <b>${p.sber_pct_credit}%</b>
                <div class="progress-bar-wrap">
                    <div class="prog-sber" style="width: ${p.sber_pct_credit}%;"></div>
                    <div class="prog-ob" style="width: ${p.ob_pct_credit}%;"></div>
                </div>
            </td>
        </tr>
    `).join('');

    antiTopTbody.innerHTML = (antiTopData || []).map((p, idx) => `
        <tr>
            <td class="center"><span class="badge badge-risk">${idx + 1}</span></td>
            <td>
                <div style="font-weight: 600; font-size: 13px;">${p.partner}</div>
                <div style="font-size: 11px; color: var(--text-muted);">${p.city} • ${p.macro} | <i>${p.competing_banks_str}</i></div>
            </td>
            <td class="num"><b>${p.total_deals}</b></td>
            <td class="num"><span class="badge badge-risk">${p.other_banks_deals}</span></td>
            <td class="num"><span class="badge badge-sber">${p.sber_deals}</span></td>
            <td class="num">
                <b>${p.ob_pct_credit}%</b>
                <div class="progress-bar-wrap">
                    <div class="prog-ob" style="width: ${p.ob_pct_credit}%;"></div>
                    <div class="prog-sber" style="width: ${p.sber_pct_credit}%;"></div>
                </div>
            </td>
        </tr>
    `).join('');
}

function toggleExpand(type) {
    if (type === 'topSber') {
        isTopSberExpanded = !isTopSberExpanded;
        const btn = document.getElementById('btnExpandTopSber');
        if (btn) {
            btn.innerText = isTopSberExpanded ? 
                '▲ Свернуть до ТОП-10' : 
                `▼ Раскрыть всех партнеров с долей Сбера ≥ 50% (${dataPayload.left_group_all.length} ДЦ)`;
        }
    } else {
        isAntiTopExpanded = !isAntiTopExpanded;
        const btn = document.getElementById('btnExpandAntiTop');
        if (btn) {
            btn.innerText = isAntiTopExpanded ? 
                '▲ Свернуть до АНТИТОП-10' : 
                `▼ Раскрыть всех партнеров с долей Др.Банков > 50% (${dataPayload.right_group_all.length} ДЦ)`;
        }
    }
    renderRankings();
}

// 3. Database Modal View Logic
function openDatabase(type) {
    currentActiveDb = type;
    currentDbFilter = 'all';
    const sInput = document.getElementById('dbSearchInput');
    if (sInput) sInput.value = '';
    
    document.querySelectorAll('#dbFilterChips .filter-chip').forEach((chip, i) => {
        chip.className = 'filter-chip ' + (i === 0 ? 'active' : '');
    });

    const mTitle = document.getElementById('modalTitle');
    if (mTitle) {
        if (type === 'lead_deals') {
            mTitle.innerHTML = '📂 Датабейс: Сделки по переданным лидам СберАвто (331 сделка)';
        } else {
            mTitle.innerHTML = '📂 Датабейс: Другие сделки ДЦ без передачи лида СА (3 606 сделок)';
        }
    }

    renderDatabaseRows();
    const modal = document.getElementById('databaseModal');
    if (modal) modal.classList.add('active');
}

function closeDatabase() {
    const modal = document.getElementById('databaseModal');
    if (modal) modal.classList.remove('active');
}

function handleModalOverlayClick(e) {
    if (e.target && e.target.id === 'databaseModal') closeDatabase();
}

function setDbFilter(cat, btn) {
    currentDbFilter = cat;
    document.querySelectorAll('#dbFilterChips .filter-chip').forEach(chip => chip.classList.remove('active'));
    if (btn) {
        btn.classList.add('active');
    } else if (window.event && window.event.target) {
        window.event.target.classList.add('active');
    }
    renderDatabaseRows();
}

let _bankingDealsCache = null;
async function _ensureBankingDeals() {
    if (_bankingDealsCache) return _bankingDealsCache;
    try {
        const cacheKey = window._dataVersion || Date.now();
        const res = await fetch('banking_deals.json?v=' + cacheKey);
        if (res.ok) {
            _bankingDealsCache = await res.json();
            return _bankingDealsCache;
        }
    } catch (e) {
        console.warn('Failed to load banking_deals.json, falling back to payload', e);
    }
    // Fallback: use main payload if separate file not available
    _bankingDealsCache = dataPayload.other_deals_db || [];
    return _bankingDealsCache;
}

async function renderDatabaseRows() {
    let rawData;
    if (currentActiveDb === 'lead_deals') {
        rawData = dataPayload.lead_deals_db;
    } else {
        rawData = await _ensureBankingDeals();
    }
    if (!rawData) return;

    const sInput = document.getElementById('dbSearchInput');
    const search = sInput ? sInput.value.toLowerCase() : '';

    let filtered = rawData.filter(d => {
        if (currentDbFilter === 'sber' && d.bank_cat !== 'Сбер') return false;
        if (currentDbFilter === 'other_banks' && d.bank_cat !== 'Другие банки') return false;
        if (currentDbFilter === 'cash' && d.bank_cat !== 'Наличные') return false;

        if (search) {
            const matchStr = `${d.cid} ${d.partner} ${d.comp} ${d.product} ${d.vin} ${d.bank} ${d.city} ${d.macro} ${d.fdc}`.toLowerCase();
            if (!matchStr.includes(search)) return false;
        }
        return true;
    });

    const cntEl = document.getElementById('dbRecordCount');
    if (cntEl) {
        cntEl.innerText = `Найдено записей: ${filtered.length.toLocaleString()} из ${rawData.length.toLocaleString()}`;
    }

    const displayData = filtered.slice(0, 500);
    const tbody = document.getElementById('modalDataTbody');
    if (tbody) {
        tbody.innerHTML = displayData.map((d, i) => `
            <tr>
                <td class="center">${i + 1}</td>
                <td class="center"><b>${d.cid}</b></td>
                <td><b>${d.partner || d.comp}</b></td>
                <td>${d.brand} ${d.model}</td>
                <td><span style="font-family: monospace; font-size: 11px;">${d.vin}</span></td>
                <td>
                    ${d.bank_cat === 'Сбер' ? `<span class="badge badge-sber">${d.bank}</span>` : 
                       d.bank_cat === 'Другие банки' ? `<span class="badge badge-risk">${d.bank}</span>` : 
                       `<span class="badge badge-cash">Наличные</span>`}
                </td>
                <td class="center">${d.bank_cat}</td>
                <td>${d.city}</td>
                <td>${d.macro}</td>
                <td class="center">${d.date}</td>
                <td class="center"><span style="font-family: monospace; font-size: 11px;">${d.fdc}</span></td>
            </tr>
        `).join('');
    }

    const footInfo = document.getElementById('modalFooterInfo');
    if (footInfo) {
        if (filtered.length > 500) {
            footInfo.innerText = `Показаны первые 500 записей из ${filtered.length}. Уточните поиск для точной выборки.`;
        } else {
            footInfo.innerText = `Отображено записей: ${filtered.length}`;
        }
    }
}

function filterDatabaseTable() {
    renderDatabaseRows();
}

function filterPartnerTable() {
    const sInput = document.getElementById('partnerFilterInput');
    if (!sInput) return;
    const search = sInput.value.toLowerCase();
    const tableEl = document.getElementById('allPartnersTable');
    if (!tableEl) return;
    const rows = tableEl.getElementsByTagName('tbody')[0]?.getElementsByTagName('tr') || [];
    for (let i = 0; i < rows.length; i++) {
        const text = rows[i].innerText.toLowerCase();
        rows[i].style.display = text.includes(search) ? '' : 'none';
    }
}

function initFunnelCharts() {
    const elDonut = document.getElementById('funnelPaymentsChart');
    const elBar = document.getElementById('funnelBanksComparisonChart');
    if (!elDonut || !elBar) return;

    if (funnelPaymentsChartInstance) {
        funnelPaymentsChartInstance.destroy();
        funnelPaymentsChartInstance = null;
    }
    if (funnelBanksChartInstance) {
        funnelBanksChartInstance.destroy();
        funnelBanksChartInstance = null;
    }

    funnelPaymentsChartInstance = new Chart(elDonut, {
        type: 'doughnut',
        data: {
            labels: [
                `Наличные (${dataPayload.deals_total ? Math.round((dataPayload.deals_cash || 0) / dataPayload.deals_total * 100) : 67.2}%)`,
                `Кредит Сбербанк (${dataPayload.deals_total ? Math.round((dataPayload.deals_sber || 0) / dataPayload.deals_total * 100) : 20.1}%)`,
                `Кредит Другие банки (${dataPayload.deals_total ? Math.round((dataPayload.deals_other_banks || 0) / dataPayload.deals_total * 100) : 12.7}%)`
            ],
            datasets: [{
                data: [dataPayload.deals_cash || 2647, dataPayload.deals_sber || 792, dataPayload.deals_other_banks || 498],
                backgroundColor: ['#64748B', '#21A038', '#E74C3C'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                datalabels: { display: false },
                legend: { position: 'bottom' }
            }
        }
    });

    funnelBanksChartInstance = new Chart(elBar, {
        type: 'bar',
        data: {
            labels: [
                `Сделки по лидам СА (${dataPayload.lead_deals_total || 331})`,
                `Другие сделки ДЦ (${(dataPayload.other_deals_total || 3606).toLocaleString()})`
            ],
            datasets: [
                { label: 'Кредит Сбербанк', data: [dataPayload.lead_deals_sber || 151, dataPayload.other_deals_sber || 641], backgroundColor: '#21A038' },
                { label: 'Кредит Другие банки', data: [dataPayload.lead_deals_other_banks || 45, dataPayload.other_deals_other_banks || 453], backgroundColor: '#E74C3C' },
                { label: 'Наличные', data: [dataPayload.lead_deals_cash || 135, dataPayload.other_deals_cash || 2512], backgroundColor: '#CBD5E1' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { x: { stacked: true }, y: { stacked: true } },
            plugins: {
                datalabels: { display: false },
                legend: { position: 'bottom' }
            }
        }
    });
}



// -------------------------------------------------------------
// Dynamic Card & Table Renderers for Section 1, 2 & 3
// -------------------------------------------------------------

function renderFunnelCards() {
    const setInner = (sel, val) => {
        const el = document.querySelector(sel);
        if (el) el.innerText = val;
    };
    
    // Transfers
    setInner('.card-leads .main-val', (dataPayload.transfers_total || 0).toLocaleString());
    setInner('.card-leads .breakdown-item:nth-child(1) b', `${(dataPayload.transfers_new || 0).toLocaleString()} (100.0%)`);
    setInner('.card-leads .breakdown-item:nth-child(2) b', `${(dataPayload.transfers_used || 0).toLocaleString()} (0.0%)`);
    
    // Lead Deals
    setInner('.card-lead-deals .main-val', (dataPayload.lead_deals_total || 0).toLocaleString());
    setInner('.card-lead-deals .breakdown-item:nth-child(1) b', `${dataPayload.lead_cr || 0}%`);
    const ldTot = dataPayload.lead_deals_total || 1;
    setInner('.card-lead-deals .breakdown-item:nth-child(2) b', `${(dataPayload.lead_deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.lead_deals_credit || 0) / ldTot * 100)}%)`);
    setInner('.card-lead-deals .breakdown-item:nth-child(3) b', `${(dataPayload.lead_deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.lead_deals_cash || 0) / ldTot * 100)}%)`);
    
    // Other Deals
    setInner('.card-other-deals .main-val', (dataPayload.other_deals_total || 0).toLocaleString());
    const odTot = dataPayload.other_deals_total || 1;
    setInner('.card-other-deals .breakdown-item:nth-child(1) b', `${(dataPayload.other_deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.other_deals_credit || 0) / odTot * 100)}%)`);
    setInner('.card-other-deals .breakdown-item:nth-child(2) b', (dataPayload.other_deals_sber || 0).toLocaleString());
    setInner('.card-other-deals .breakdown-item:nth-child(3) b', `${(dataPayload.other_deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.other_deals_cash || 0) / odTot * 100)}%)`);
    
    // Total Deals
    setInner('.card-total-deals .main-val', (dataPayload.deals_total || 0).toLocaleString());
    const dTot = dataPayload.deals_total || 1;
    setInner('.card-total-deals .breakdown-item:nth-child(1) b', `${(dataPayload.deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.deals_credit || 0) / dTot * 100)}%)`);
    setInner('.card-total-deals .breakdown-item:nth-child(2) b', (dataPayload.deals_sber || 0).toLocaleString());
    setInner('.card-total-deals .breakdown-item:nth-child(3) b', `${(dataPayload.deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.deals_cash || 0) / dTot * 100)}%)`);
}

function renderMacroTable() {
    const tbody = document.getElementById('macroRegionsTbody');
    if (!tbody) return;
    const rows = dataPayload.macro_rows || [];
    if (!rows.length) return;
    
    tbody.innerHTML = rows.map((r, idx) => `
        <tr>
            <td class="center">${idx + 1}</td>
            <td><b>${r.macro}</b></td>
            <td class="num">${r.transfers || 0}</td>
            <td class="num"><span class="badge badge-lead">${r.lead_deals || 0}</span></td>
            <td class="num"><b>${r.cr != null ? r.cr + '%' : '0%'}</b></td>
            <td class="num">${(r.other_deals || 0).toLocaleString()}</td>
            <td class="num"><b>${(r.all_deals || r.total_deals || 0).toLocaleString()}</b></td>
            <td class="num"><span class="badge badge-sber">${(r.sber || r.sber_deals || 0).toLocaleString()}</span></td>
            <td class="num"><span class="badge badge-risk">${(r.other_banks || r.other_banks_deals || 0).toLocaleString()}</span></td>
            <td class="num"><b>${r.credit_share != null ? r.credit_share + '%' : '—'}</b></td>
            <td class="num"><b>${r.sber_share != null ? r.sber_share + '%' : '—'}</b></td>
        </tr>
    `).join('');
}

function renderAllPartnersTable() {
    const tbody = document.getElementById('allPartnersTbody');
    if (!tbody) return;
    const partners = dataPayload.all_partners || [];
    if (!partners.length) return;
    
    tbody.innerHTML = partners.map(p => `
        <tr>
            <td>${p.macro || '—'}</td>
            <td>${p.city || '—'}</td>
            <td><b>${p.partner || '—'}</b></td>
            <td class="num">${p.lead_deals || 0}</td>
            <td class="num">${p.lead_deals || 0}</td>
            <td class="num">${p.other_deals || 0}</td>
            <td class="num"><b>${p.total_deals || 0}</b></td>
            <td class="num"><span class="badge badge-sber">${p.sber_deals || 0}</span></td>
            <td class="num"><span class="badge badge-risk">${p.other_banks_deals || 0}</span></td>
            <td class="num"><b>${p.sber_pct_credit != null ? p.sber_pct_credit + '%' : '—'}</b></td>
            <td><span style="font-size: 11px; color: #64748B;">${p.competing_banks_str || '—'}</span></td>
        </tr>
    `).join('');
}

function renderBankingDashboard() {
    renderFunnelCards();
    renderRankings();
    renderMacroTable();
    renderAllPartnersTable();
    initFunnelCharts();
}

// Global exposure
window.renderBankingDashboard = renderBankingDashboard;
window.switchSection = switchSection;
window.switchBankingSection = switchBankingSection;
window.renderRankings = renderRankings;
window.toggleExpand = toggleExpand;
window.openDatabase = openDatabase;
window.closeDatabase = closeDatabase;
window.handleModalOverlayClick = handleModalOverlayClick;
window.setDbFilter = setDbFilter;
window.renderDatabaseRows = renderDatabaseRows;
window.filterDatabaseTable = filterDatabaseTable;
window.filterPartnerTable = filterPartnerTable;
window.renderFunnelCards = renderFunnelCards;
window.renderMacroTable = renderMacroTable;
window.renderAllPartnersTable = renderAllPartnersTable;

document.addEventListener('DOMContentLoaded', () => {
    const tabEl = document.getElementById('tab-banking');
    if (tabEl && !tabEl.classList.contains('hidden')) {
        renderBankingDashboard();
    }
});
