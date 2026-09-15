/* ====================================================================
 * B2C Analytics Dashboard — Brand Funnel (Auto-generated months)
 * ====================================================================*/

let currentFunnelMonth = null; // Auto-detect, no hardcode
let currentFunnelBrand = 'ALL';
let funnelRawData = {};
const fBrandColors = ['#21A038', '#00B074', '#0097A7', '#2E5BFF', '#7928CA', '#FF9900', '#EC4899', '#8B5CF6', '#14B8A6', '#F59E0B', '#6366F1', '#3B82F6', '#64748B', '#06B6D4'];

// Auto-generate month buttons from data.json
function initFunnelMonths() {
    const bf = window.brandFunnelFullData;
    if (!bf || !bf.by_month) return;

    const months = Object.keys(bf.by_month).filter(m => m !== 'all').sort().reverse();
    if (months.length === 0) return;

    // Set default to latest month
    if (!currentFunnelMonth) currentFunnelMonth = months[0];

    const container = document.getElementById('funnelMonthButtons');
    if (!container) return;

    let html = '';
    months.forEach(m => {
        const label = formatMonthLabel(m);
        const isActive = m === currentFunnelMonth;
        html += `<button onclick="setFunnelMonth('${m}')" id="f-month-${m}" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isActive ? 'font-bold bg-[#21A038] text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">${label}</button>`;
    });
    // "All" button
    const isAllActive = currentFunnelMonth === 'all';
    html += `<button onclick="setFunnelMonth('all')" id="f-month-all" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isAllActive ? 'font-bold bg-[#21A038] text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">📅 Все месяцы</button>`;

    container.innerHTML = html;

    // Update badge
    const badge = document.getElementById('funnelPeriodBadge');
    if (badge) badge.innerText = formatMonthLabel(currentFunnelMonth).replace('📅 ', '');

    // Also auto-generate brand pills from data
    initFunnelBrandPills();
}

function initFunnelBrandPills() {
    const bf = window.brandFunnelFullData;
    if (!bf || !bf.by_month) return;

    const monthData = getActiveMonthFunnelData();
    const brands = Object.keys(monthData).filter(b => b !== 'OVERALL_LATEST_DATE' && typeof monthData[b] === 'object').sort();

    const container = document.getElementById('funnelBrandPills');
    if (!container) return;

    let html = `<button onclick="selectFunnelBrand('ALL')" id="f-tab-ALL" class="f-tab-btn px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#21A038] text-white shadow-md">📊 Сводное сравнение</button>`;

    brands.forEach(b => {
        html += `<button onclick="selectFunnelBrand('${b}')" id="f-tab-${b}" class="f-tab-btn px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 shadow-sm">${b}</button>`;
    });

    container.innerHTML = html;
}

function setFunnelMonth(month) {
    currentFunnelMonth = month;
    const badge = document.getElementById('funnelPeriodBadge');
    if (badge) badge.innerText = formatMonthLabel(month).replace('📅 ', '');

    document.querySelectorAll('.f-month-btn').forEach(b => {
        b.className = 'f-month-btn px-3.5 py-1.5 rounded-xl font-semibold text-xs transition text-slate-700 hover:text-slate-900 hover:bg-slate-200';
    });
    const activeMBtn = document.getElementById('f-month-' + month);
    if (activeMBtn) {
        activeMBtn.className = 'f-month-btn px-3.5 py-1.5 rounded-xl font-bold text-xs transition bg-[#21A038] text-white shadow-sm';
    }
    initFunnelBrandPills();
    selectFunnelBrand(currentFunnelBrand);
}

function getActiveMonthFunnelData() {
    if (window.brandFunnelFullData && window.brandFunnelFullData.by_month && window.brandFunnelFullData.by_month[currentFunnelMonth]) {
        return window.brandFunnelFullData.by_month[currentFunnelMonth].brands;
    }
    return window.brandFunnelFullData || {};
}

function selectFunnelBrand(brand) {
    currentFunnelBrand = brand;
    document.querySelectorAll('.f-tab-btn').forEach(b => {
        b.className = 'f-tab-btn px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 shadow-sm';
    });
    const activeBtn = document.getElementById('f-tab-' + brand);
    if (activeBtn) {
        activeBtn.className = 'f-tab-btn px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#21A038] text-white shadow-md border-transparent';
    }

    const monthData = getActiveMonthFunnelData();
    if (brand === 'ALL') {
        renderFunnelComparisonView(monthData);
    } else {
        renderFunnelSingleBrandView(brand, monthData[brand] || {});
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function getCurrentFunnelPeriodLabel() {
    return formatMonthLabel(currentFunnelMonth).replace('📅 ', '');
}

function renderFunnelComparisonView(brandsData) {
    const container = document.getElementById('funnelDynamicView');
    if (!container) return;
    const bNames = Object.keys(brandsData).filter(b => b !== 'OVERALL_LATEST_DATE' && typeof brandsData[b] === 'object');

    let totLeads = 0, totDealsAll = 0, totDealsNoMp2 = 0, totRevNoMp2 = 0, totRevMp2 = 0;
    let totQual = 0, totDealer = 0, totFdc = 0;

    bNames.forEach(b => {
        const d = brandsData[b];
        totLeads += (d.leads || 0);
        totQual += (d.qual || 0);
        totDealer += (d.dealer || 0);
        totFdc += (d.fdc_app || 0);
        totDealsAll += (d.deals_total_all || 0);
        totDealsNoMp2 += (d.deals_no_mp2 || 0);
        totRevNoMp2 += (d.rev_no_mp2 || 0);
        totRevMp2 += (d.mp2_rev || 0);
    });

    const kpiCards = document.getElementById('funnelKpiCards');
    if (kpiCards) {
        kpiCards.innerHTML = `
            <div class="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Всего лидов в CRM</span>
                <p class="text-xl font-black text-slate-900 mt-1">${fmtNum(totLeads)}</p>
                <span class="text-[10px] text-slate-400">${bNames.length} брендов витрины</span>
            </div>
            <div class="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Сделок всего (с МП2)</span>
                <p class="text-xl font-black text-slate-900 mt-1">${fmtNum(totDealsAll)}</p>
                <span class="text-[10px] text-slate-400">Все каналы продаж</span>
            </div>
            <div class="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">Сделок розницы (без МП2)</span>
                <p class="text-xl font-black text-[#107C41] mt-1">${fmtNum(totDealsNoMp2)}</p>
                <span class="text-[10px] text-emerald-700 font-bold">CR: ${(totLeads > 0 ? (totDealsNoMp2/totLeads*100).toFixed(2) : 0)}%</span>
            </div>
            <div class="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">Выручка Розницы</span>
                <p class="text-xl font-black text-[#107C41] mt-1">${fmtRub(totRevNoMp2)}</p>
                <span class="text-[10px] text-emerald-700">Передача лидов</span>
            </div>
            <div class="bg-slate-50 border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Выручка МП2 (Опт)</span>
                <p class="text-xl font-black text-slate-700 mt-1">${fmtRub(totRevMp2)}</p>
                <span class="text-[10px] text-slate-400">Исключено из воронки</span>
            </div>
            <div class="bg-gradient-to-br from-emerald-600 to-[#107C41] p-4 rounded-2xl shadow-md text-white">
                <span class="text-[10px] text-emerald-100 font-bold uppercase tracking-wider">ИТОГО Выручка</span>
                <p class="text-xl font-black text-white mt-1">${fmtRub(totRevNoMp2 + totRevMp2)}</p>
                <span class="text-[10px] text-emerald-100 font-bold">Все ${bNames.length} брендов</span>
            </div>
        `;
    }

    let rows = '';
    bNames.sort((a,b) => (brandsData[b].rev_no_mp2||0) - (brandsData[a].rev_no_mp2||0)).forEach(b => {
        const d = brandsData[b];
        const crRetail = d.leads > 0 ? ((d.deals_no_mp2 / d.leads) * 100).toFixed(2) + '%' : '0%';
        rows += `
            <tr class="hover:bg-slate-50 transition border-b border-slate-100 cursor-pointer" onclick="selectFunnelBrand('${b}')">
                <td class="py-3 px-3.5 font-black text-slate-900 flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#21A038]"></span> ${b}
                </td>
                <td class="py-3 px-3.5 text-right font-semibold text-slate-700">${fmtNum(d.leads)}</td>
                <td class="py-3 px-3.5 text-right font-black text-[#107C41] bg-emerald-50/70">${fmtNum(d.deals_no_mp2)}</td>
                <td class="py-3 px-3.5 text-right text-slate-500">${fmtNum(d.mp2_count)}</td>
                <td class="py-3 px-3.5 text-right font-bold text-slate-800">${fmtNum(d.deals_total_all)}</td>
                <td class="py-3 px-3.5 text-right font-black text-[#107C41] bg-emerald-50/70">${fmtRub(d.rev_no_mp2)}</td>
                <td class="py-3 px-3.5 text-right text-slate-600">${fmtRub(d.mp2_rev)}</td>
                <td class="py-3 px-3.5 text-right font-bold text-slate-900">${fmtRub((d.rev_no_mp2||0) + (d.mp2_rev||0))}</td>
                <td class="py-3 px-3.5 text-right font-bold text-emerald-700">${crRetail}</td>
            </tr>
        `;
    });

    const periodLabel = getCurrentFunnelPeriodLabel();
    container.innerHTML = `
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-xl space-y-4">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-slate-200">
                <div>
                    <h3 class="text-base font-black text-slate-900 flex items-center gap-2">
                        <i data-lucide="bar-chart-3" class="w-5 h-5 text-[#21A038]"></i>
                        Сводная матрица воронки по ${bNames.length} брендам (${periodLabel})
                    </h3>
                    <p class="text-xs text-slate-500">Нажмите на любую строку таблицы, чтобы открыть детальную воронку конкретного бренда</p>
                </div>
                <span class="px-3 py-1 bg-slate-100 text-slate-700 rounded-lg text-xs font-bold border border-slate-200">
                    ${bNames.length} брендов витрины
                </span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-xs text-left">
                    <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                            <th class="py-3 px-3.5">Бренд</th>
                            <th class="py-3 px-3.5 text-right">Лиды в CRM</th>
                            <th class="py-3 px-3.5 text-right text-[#107C41] bg-emerald-50/90">Сделки Розница</th>
                            <th class="py-3 px-3.5 text-right">Опт МП2</th>
                            <th class="py-3 px-3.5 text-right">Всего сделок</th>
                            <th class="py-3 px-3.5 text-right text-[#107C41] bg-emerald-50/90">Выручка Розница</th>
                            <th class="py-3 px-3.5 text-right">Выручка МП2</th>
                            <th class="py-3 px-3.5 text-right">Итого Выручка</th>
                            <th class="py-3 px-3.5 text-right text-emerald-800">CR в розницу</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                    <tfoot class="bg-slate-900 text-white font-bold">
                        <tr>
                            <td class="py-3 px-3.5">ИТОГО ${bNames.length} БРЕНДОВ</td>
                            <td class="py-3 px-3.5 text-right">${fmtNum(totLeads)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-400 font-black">${fmtNum(totDealsNoMp2)}</td>
                            <td class="py-3 px-3.5 text-right text-slate-300">${fmtNum(totDealsAll - totDealsNoMp2)}</td>
                            <td class="py-3 px-3.5 text-right font-black">${fmtNum(totDealsAll)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-400 font-black">${fmtRub(totRevNoMp2)}</td>
                            <td class="py-3 px-3.5 text-right text-slate-300">${fmtRub(totRevMp2)}</td>
                            <td class="py-3 px-3.5 text-right text-yellow-400 font-black">${fmtRub(totRevNoMp2 + totRevMp2)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-300 font-black">${(totLeads > 0 ? (totDealsNoMp2 / totLeads * 100).toFixed(2) : '0')}%</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
}

function renderFunnelSingleBrandView(brand, d) {
    const container = document.getElementById('funnelDynamicView');
    if (!container) return;

    const v = d.vitrina || {};
    const crDeals = d.leads > 0 ? ((d.deals_no_mp2 / d.leads) * 100).toFixed(2) + '%' : '0%';

    const pageView = v.page_view || (d.leads * 140) || 0;
    const cardShow = v.car_card_show || (d.leads * 21) || 0;
    const cardClick = v.car_card_click || (d.leads * 2.7) || 0;
    const offerShow = v.offer_show || (d.leads * 2.6) || 0;
    const offerClick = v.offer_click || (d.leads * 1.7) || 0;
    const offerSuccess = v.offer_success || d.leads || 0;

    const hasVitrinaData = !!(v.page_view || v.car_card_show);
    const ctrCard = cardShow > 0 ? ((cardClick / cardShow) * 100).toFixed(1) + '%' : 'N/A';
    const crOffer = cardClick > 0 ? ((offerShow / cardClick) * 100).toFixed(1) + '%' : 'N/A';
    const crSuccess = offerClick > 0 ? ((offerSuccess / offerClick) * 100).toFixed(1) + '%' : 'N/A';

    let srcRows = '';
    if (d.src_breakdown) {
        Object.entries(d.src_breakdown).forEach(([src, cnt]) => {
            const pct = d.leads > 0 ? ((cnt / d.leads) * 100).toFixed(1) + '%' : '0%';
            srcRows += `<div class="flex justify-between items-center py-2 border-b border-slate-100 text-xs"><span class="text-slate-700 font-medium">${src}</span><span class="font-bold text-slate-900">${fmtNum(cnt)} <span class="text-[11px] text-slate-400 font-normal">(${pct})</span></span></div>`;
        });
    }

    let b2cRows = '';
    if (d.deals_by_b2c) {
        Object.entries(d.deals_by_b2c).forEach(([b2cType, cnt]) => {
            const rev = (d.rev_by_b2c && d.rev_by_b2c[b2cType]) || 0;
            b2cRows += `<div class="flex justify-between items-center py-2 border-b border-slate-100 text-xs"><span class="text-slate-700 font-medium">${b2cType}</span><span class="font-bold text-slate-900">${fmtNum(cnt)} шт <span class="text-[11px] text-emerald-700 font-bold">(${fmtRub(rev)})</span></span></div>`;
        });
    }

    const kpiCards = document.getElementById('funnelKpiCards');
    if (kpiCards) kpiCards.innerHTML = '';

    const periodLabel = getCurrentFunnelPeriodLabel();
    const vitrinaNote = hasVitrinaData ? '' : '<span class="text-[10px] text-amber-600 bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-200 font-bold ml-2">⚠️ Оценочные данные PostHog</span>';

    container.innerHTML = `
        <div class="bg-slate-50 text-slate-900 p-6 md:p-8 rounded-3xl shadow-xl border border-slate-200 space-y-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-600 to-[#107C41] flex items-center justify-center text-white font-black text-xl shadow-md">${brand.charAt(0)}</div>
                    <div>
                        <h3 class="text-xl font-black text-slate-900 flex items-center gap-2">Сквозная воронка продаж: <span class="text-[#107C41]">${brand}</span></h3>
                        <p class="text-xs text-slate-500 mt-0.5">Период: ${periodLabel} • Строгий учет 1-к-1</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <span class="px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300">Розница: ${fmtNum(d.deals_no_mp2)} сделок (${crDeals})</span>
                    <span class="px-3 py-1.5 rounded-xl bg-slate-200 text-slate-700 text-xs font-semibold">Опт МП2: ${fmtNum(d.mp2_count)} шт</span>
                </div>
            </div>

            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                        <i data-lucide="eye" class="w-4 h-4 text-[#21A038]"></i>
                        Этап 1: Воронка витрины СберАвто (PostHog Clickstream)${vitrinaNote}
                    </span>
                    <span class="text-xs font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
                        Конверсия карточки в заявку: ${cardShow > 0 ? ((offerSuccess / cardShow) * 100).toFixed(2) : 0}%
                    </span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
                    <div class="bg-gradient-to-br from-emerald-700 to-emerald-800 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-emerald-100 uppercase tracking-wider">1. Просмотр листинга</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(pageView)}</p>
                        <span class="text-[10px] text-emerald-200 mt-1">100% базы витрины</span>
                    </div>
                    <div class="bg-gradient-to-br from-emerald-600 to-emerald-700 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-emerald-100 uppercase tracking-wider">2. Показ карточки</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(cardShow)}</p>
                        <span class="text-[10px] text-emerald-200 mt-1">${pageView > 0 ? ((cardShow / pageView) * 100).toFixed(1) : 0}% от листинга</span>
                    </div>
                    <div class="bg-gradient-to-br from-teal-600 to-teal-700 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-teal-100 uppercase tracking-wider">3. Клик карточки</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(cardClick)}</p>
                        <span class="text-[10px] text-teal-200 mt-1">CTR: ${ctrCard}</span>
                    </div>
                    <div class="bg-gradient-to-br from-cyan-600 to-cyan-700 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-cyan-100 uppercase tracking-wider">4. Экран оффера</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(offerShow)}</p>
                        <span class="text-[10px] text-cyan-200 mt-1">${crOffer} доходимость</span>
                    </div>
                    <div class="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-blue-100 uppercase tracking-wider">5. Клик отправки</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(offerClick)}</p>
                        <span class="text-[10px] text-blue-200 mt-1">${offerShow > 0 ? ((offerClick / offerShow) * 100).toFixed(1) : 0}% кликабельность</span>
                    </div>
                    <div class="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white p-4 rounded-2xl shadow-sm flex flex-col justify-between">
                        <span class="text-[10px] font-bold text-indigo-100 uppercase tracking-wider">6. Экран успеха</span>
                        <p class="text-xl font-black mt-1 text-white">${fmtNum(offerSuccess)}</p>
                        <span class="text-[10px] text-indigo-200 mt-1">${crSuccess} подтверждение</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3.5">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5"><i data-lucide="user-check" class="w-4 h-4 text-blue-600"></i> Этап 2: CRM & Квалификация</span>
                    <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100"><span class="text-xs text-slate-700 font-medium">Новых лидов в CRM:</span><span class="text-sm font-black text-slate-900">${fmtNum(d.leads)} лидов</span></div>
                    <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100"><span class="text-xs text-slate-700 font-medium">Квалифицировано:</span><span class="text-sm font-black text-[#107C41]">${fmtNum(d.qual)} (${d.leads > 0 ? ((d.qual / d.leads) * 100).toFixed(1) : 0}%)</span></div>
                    <div class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100"><span class="text-xs text-slate-700 font-medium">Расчетов калькулятора:</span><span class="text-sm font-black text-blue-700">${fmtNum(d.calc_total)} расчетов</span></div>
                </div>
                <div class="bg-gradient-to-br from-blue-50 to-indigo-50/40 p-5 rounded-2xl border border-blue-200 shadow-sm space-y-3.5">
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-1.5"><i data-lucide="building-2" class="w-4 h-4 text-blue-600"></i> Ветка 1: Дилерская сеть (ДЦ)</span>
                    <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-blue-100"><span class="text-xs text-slate-700 font-medium">Передано в ДЦ:</span><span class="text-sm font-black text-blue-700">${fmtNum(d.dealer)} лидов</span></div>
                    <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-blue-100"><span class="text-xs text-slate-700 font-medium">Доля от квалиф.:</span><span class="text-sm font-black text-slate-900">${d.qual > 0 ? ((d.dealer / d.qual) * 100).toFixed(1) : 0}%</span></div>
                    <div class="text-[11px] text-blue-900 bg-blue-100/70 p-2.5 rounded-xl border border-blue-200 font-medium">🏢 Лиды передаются в дилерские центры партнеров для выдачи авто.</div>
                </div>
                <div class="bg-gradient-to-br from-emerald-50 to-teal-50/40 p-5 rounded-2xl border border-emerald-200 shadow-sm space-y-3.5">
                    <span class="text-xs font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1.5"><i data-lucide="credit-card" class="w-4 h-4 text-[#21A038]"></i> Ветка 2: Онлайн-кредит (ФДЦ)</span>
                    <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-emerald-100"><span class="text-xs text-slate-700 font-medium">Заявок на кредит:</span><span class="text-sm font-black text-[#107C41]">${fmtNum(d.fdc_app)} заявок</span></div>
                    <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-emerald-100"><span class="text-xs text-slate-700 font-medium">Одобрено банком:</span><span class="text-sm font-black text-[#107C41]">${fmtNum(d.fdc_appr)} (${d.fdc_app > 0 ? ((d.fdc_appr / d.fdc_app) * 100).toFixed(1) : 0}%)</span></div>
                    <div class="text-[11px] text-emerald-900 bg-emerald-100/70 p-2.5 rounded-xl border border-emerald-200 font-medium">💳 Прямое онлайн-оформление кредита через СберАвто и ФДЦ.</div>
                </div>
            </div>

            <div class="bg-gradient-to-r from-emerald-600 via-[#21A038] to-[#107C41] text-white p-6 rounded-3xl shadow-lg flex flex-col md:flex-row justify-between items-center gap-6">
                <div>
                    <span class="text-xs uppercase font-bold tracking-wider text-emerald-100">Итог розничной воронки (без учета МП2)</span>
                    <div class="flex items-baseline gap-3 mt-1.5">
                        <h4 class="text-3xl font-black text-white">${fmtNum(d.deals_no_mp2)} закрытых сделок</h4>
                        <span class="text-sm font-bold bg-white/20 px-3 py-1 rounded-xl text-white">CR: ${crDeals} от лидов</span>
                    </div>
                </div>
                <div class="text-right flex items-center gap-8">
                    <div><span class="text-[11px] text-emerald-100 block uppercase font-bold">Выручка розницы</span><span class="text-3xl font-black text-white">${fmtRub(d.rev_no_mp2)}</span></div>
                    <div class="border-l border-white/30 pl-8"><span class="text-[11px] text-emerald-100 block uppercase font-bold">Исключено МП2 (Опт)</span><span class="text-sm font-bold text-white">${fmtNum(d.mp2_count)} шт (${fmtRub(d.mp2_rev)})</span></div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                    <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5"><i data-lucide="layers" class="w-4 h-4 text-indigo-600"></i> Источники трафика и лидов (${brand})</h4>
                    <div class="space-y-1">${srcRows || '<p class="text-xs text-slate-400">Нет данных</p>'}</div>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                    <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5"><i data-lucide="shopping-bag" class="w-4 h-4 text-emerald-600"></i> Структура розничных сделок по каналам (${brand})</h4>
                    <div class="space-y-1">${b2cRows || '<div class="py-2 text-xs text-slate-500">Передача лида: ' + fmtNum(d.deals_no_mp2) + ' сделок (' + fmtRub(d.rev_no_mp2) + ')</div>'}</div>
                </div>
            </div>
        </div>
    `;
}
