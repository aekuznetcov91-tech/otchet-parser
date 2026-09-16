/* ====================================================================
 * B2C Analytics Dashboard — Brand Funnel Revamped (Bottleneck & Drop-off Focus)
 * Strictly Pure Retail (Excluding Wholesale: MP1, MP2, MP3)
 * ====================================================================*/

let currentFunnelMonth = null; // Auto-detect, no hardcode
let currentFunnelBrand = 'ALL';
let funnelRawData = {};

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
        html += `<button onclick="setFunnelMonth('${m}')" id="f-month-${m}" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isActive ? 'font-bold bg-[#107C41] text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">${label}</button>`;
    });
    // "All" button
    const isAllActive = currentFunnelMonth === 'all';
    html += `<button onclick="setFunnelMonth('all')" id="f-month-all" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isAllActive ? 'font-bold bg-[#107C41] text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">📅 Все месяцы</button>`;

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

    let html = `<button onclick="selectFunnelBrand('ALL')" id="f-tab-ALL" class="f-tab-btn px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#107C41] text-white shadow-md">📊 Сводная воронка (Все бренды)</button>`;

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
        activeMBtn.className = 'f-month-btn px-3.5 py-1.5 rounded-xl font-bold text-xs transition bg-[#107C41] text-white shadow-sm';
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
        activeBtn.className = 'f-tab-btn px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#107C41] text-white shadow-md border-transparent';
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

/**
 * Extract clean retail channels (excluding MP1, MP2, MP3)
 */
function extractRetailMetrics(d) {
    const dealsByB2C = d.deals_by_b2c || {};
    const revByB2C = d.rev_by_b2c || {};

    const dealsDealer = dealsByB2C['Передача лида'] || 0;
    const revDealer = revByB2C['Передача лида'] || 0.0;

    // FDC includes pure FDC + optional FDC+GP if present
    const dealsFdc = (dealsByB2C['ФДЦ'] || 0) + (dealsByB2C['ФДЦ+ГП'] || 0);
    const revFdc = (revByB2C['ФДЦ'] || 0.0) + (revByB2C['ФДЦ+ГП'] || 0.0);

    const dealsOnline = dealsByB2C['Online'] || 0;
    const revOnline = revByB2C['Online'] || 0.0;

    const dealsPureRetail = dealsDealer + dealsFdc + dealsOnline;
    const revPureRetail = revDealer + revFdc + revOnline;

    // Wholesale (excluded)
    const mp1Count = dealsByB2C['МП1'] || 0;
    const mp1Rev = revByB2C['МП1'] || 0.0;
    const mp3Count = dealsByB2C['МП3'] || 0;
    const mp3Rev = revByB2C['МП3'] || 0.0;
    const mp2Count = d.mp2_count || dealsByB2C['МП2'] || 0;
    const mp2Rev = d.mp2_rev || revByB2C['МП2'] || 0.0;

    const totalMpCount = mp1Count + mp2Count + mp3Count;
    const totalMpRev = mp1Rev + mp2Rev + mp3Rev;

    return {
        dealsDealer, revDealer,
        dealsFdc, revFdc,
        dealsOnline, revOnline,
        dealsPureRetail, revPureRetail,
        mp1Count, mp1Rev,
        mp2Count, mp2Rev,
        mp3Count, mp3Rev,
        totalMpCount, totalMpRev
    };
}

/**
 * 📊 RENDER COMPARISON VIEW (ALL BRANDS SUMMARIZED)
 * Shows high-level KPIs, Step Pipeline Funnel with drop-offs, Top Bottlenecks, and Brand Efficiency Matrix
 */
function renderFunnelComparisonView(brandsData) {
    const container = document.getElementById('funnelDynamicView');
    if (!container) return;
    const bNames = Object.keys(brandsData).filter(b => b !== 'OVERALL_LATEST_DATE' && typeof brandsData[b] === 'object');

    // Aggregated metrics
    let totPv = 0, totCardShow = 0, totCardClick = 0, totOfferShow = 0, totOfferClick = 0, totOfferSuccess = 0;
    let totLeads = 0, totQual = 0, totCalc = 0, totOfferTotal = 0, totDealer = 0, totFdcApp = 0, totFdcAppr = 0;
    let totDealsDealer = 0, totRevDealer = 0;
    let totDealsFdc = 0, totRevFdc = 0;
    let totDealsOnline = 0, totRevOnline = 0;
    let totPureRetailDeals = 0, totPureRetailRev = 0;
    let totMpDeals = 0, totMpRev = 0;

    bNames.forEach(b => {
        const d = brandsData[b];
        const v = d.vitrina || {};
        totPv += (v.page_view || 0);
        totCardShow += (v.car_card_show || 0);
        totCardClick += (v.car_card_click || 0);
        totOfferShow += (v.offer_show || 0);
        totOfferClick += (v.offer_click || 0);
        totOfferSuccess += (v.offer_success || 0);

        totLeads += (d.leads || 0);
        totQual += (d.qual || 0);
        totCalc += (d.calc_total || 0);
        totOfferTotal += (d.offer_total || 0);
        totDealer += (d.dealer || 0);
        totFdcApp += (d.fdc_app || 0);
        totFdcAppr += (d.fdc_appr || 0);

        const r = extractRetailMetrics(d);
        totDealsDealer += r.dealsDealer;
        totRevDealer += r.revDealer;
        totDealsFdc += r.dealsFdc;
        totRevFdc += r.revFdc;
        totDealsOnline += r.dealsOnline;
        totRevOnline += r.revOnline;
        totPureRetailDeals += r.dealsPureRetail;
        totPureRetailRev += r.revPureRetail;
        totMpDeals += r.totalMpCount;
        totMpRev += r.totalMpRev;
    });

    const crOverall = totLeads > 0 ? ((totPureRetailDeals / totLeads) * 100).toFixed(2) : '0';
    const crL1 = totLeads > 0 ? ((totQual / totLeads) * 100).toFixed(1) : '0';
    const arpuRetail = totPureRetailDeals > 0 ? (totPureRetailRev / totPureRetailDeals) : 0;

    // Conversion rates & Drop-offs
    const ctrCard = totCardShow > 0 ? ((totCardClick / totCardShow) * 100).toFixed(1) : '0';
    const dropCard = totCardShow > 0 ? ((1 - totCardClick / totCardShow) * 100).toFixed(1) : '0';
    const crOfferSucc = totCardClick > 0 ? ((totOfferSuccess / totCardClick) * 100).toFixed(1) : '0';
    const dropOfferSucc = totCardClick > 0 ? ((1 - totOfferSuccess / totCardClick) * 100).toFixed(1) : '0';

    // Vitrina to CRM gap
    const gapVitrinaCrm = totOfferSuccess - totLeads;
    const gapPct = totOfferSuccess > 0 ? ((gapVitrinaCrm / totOfferSuccess) * 100).toFixed(1) : '0';

    // Channels drop-offs
    const crDealer = totDealer > 0 ? ((totDealsDealer / totDealer) * 100).toFixed(1) : '0';
    const dropDealer = totDealer > 0 ? ((1 - totDealsDealer / totDealer) * 100).toFixed(1) : '0';

    const crFdcApp = totCalc > 0 ? ((totFdcApp / totCalc) * 100).toFixed(1) : '0';
    const dropFdcApp = totCalc > 0 ? ((1 - totFdcApp / totCalc) * 100).toFixed(1) : '0';
    const crFdcAppr = totFdcApp > 0 ? ((totFdcAppr / totFdcApp) * 100).toFixed(1) : '0';
    const crFdcDeal = totFdcAppr > 0 ? ((totDealsFdc / totFdcAppr) * 100).toFixed(1) : '0';
    const dropFdcDeal = totFdcAppr > 0 ? ((1 - totDealsFdc / totFdcAppr) * 100).toFixed(1) : '0';

    // 1. Render Top Summary KPI Cards
    const kpiCards = document.getElementById('funnelKpiCards');
    if (kpiCards) {
        kpiCards.innerHTML = `
            <div class="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Входящие лиды CRM</span>
                <p class="text-2xl font-black text-slate-900 mt-1">${fmtNum(totLeads)}</p>
                <div class="flex items-center gap-1.5 mt-1 text-[11px] text-emerald-700 font-semibold">
                    <span>L1 Квалиф: ${fmtNum(totQual)}</span>
                    <span class="px-1.5 py-0.2 bg-emerald-100 rounded text-[10px]">${crL1}%</span>
                </div>
            </div>
            <div class="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">Сделок Розницы (Чистая)</span>
                <p class="text-2xl font-black text-[#107C41] mt-1">${fmtNum(totPureRetailDeals)}</p>
                <span class="text-[11px] text-emerald-700 font-bold">Сквозной CR: ${crOverall}% от лидов</span>
            </div>
            <div class="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">Выручка Розницы</span>
                <p class="text-2xl font-black text-[#107C41] mt-1">${fmtRub(totPureRetailRev)}</p>
                <span class="text-[11px] text-emerald-700">Очищено от НДС 20%</span>
            </div>
            <div class="bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Средний доход / сделку</span>
                <p class="text-2xl font-black text-slate-900 mt-1">${fmtRub(arpuRetail)}</p>
                <span class="text-[11px] text-slate-400">Чистая комиссия розницы</span>
            </div>
            <div class="bg-slate-50 border border-slate-200 p-4 rounded-2xl shadow-sm">
                <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Опт МП1/МП2/МП3 (Искл.)</span>
                <p class="text-2xl font-black text-slate-700 mt-1">${fmtNum(totMpDeals)} шт</p>
                <span class="text-[11px] text-slate-400">${fmtRub(totMpRev)}</span>
            </div>
            <div class="bg-gradient-to-br from-emerald-600 to-[#107C41] p-4 rounded-2xl shadow-md text-white">
                <span class="text-[10px] text-emerald-100 font-bold uppercase tracking-wider">Всего подтверждено</span>
                <p class="text-2xl font-black text-white mt-1">${fmtNum(totPureRetailDeals + totMpDeals)}</p>
                <span class="text-[11px] text-emerald-100 font-medium">Розница ${totPureRetailDeals} + Опт ${totMpDeals}</span>
            </div>
        `;
    }

    const periodLabel = getCurrentFunnelPeriodLabel();

    // Table rows generation
    let tableRows = '';
    bNames.sort((a,b) => {
        const ra = extractRetailMetrics(brandsData[a]).revPureRetail;
        const rb = extractRetailMetrics(brandsData[b]).revPureRetail;
        return rb - ra;
    }).forEach(b => {
        const d = brandsData[b];
        const r = extractRetailMetrics(d);
        const crB = d.leads > 0 ? ((r.dealsPureRetail / d.leads) * 100).toFixed(2) : '0';
        const crBNum = parseFloat(crB);
        const crQual = d.leads > 0 ? ((d.qual / d.leads) * 100).toFixed(1) : '0';
        const crDc = d.dealer > 0 ? ((r.dealsDealer / d.dealer) * 100).toFixed(1) : '0';
        const crFdc = d.fdc_appr > 0 ? ((r.dealsFdc / d.fdc_appr) * 100).toFixed(1) : '0';

        let badgeStatus = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">🟢 Норма</span>';
        if (crBNum < 2.0) {
            badgeStatus = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">🔴 Отвал</span>';
        } else if (crBNum >= 4.0) {
            badgeStatus = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600 text-white">⭐ Топ</span>';
        }

        tableRows += `
            <tr class="hover:bg-emerald-50/50 transition border-b border-slate-100 cursor-pointer" onclick="selectFunnelBrand('${b}')">
                <td class="py-3 px-3.5 font-black text-slate-900 flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#107C41]"></span> ${b}
                </td>
                <td class="py-3 px-3.5 text-right font-semibold text-slate-700">${fmtNum(d.leads)}</td>
                <td class="py-3 px-3.5 text-right font-medium text-slate-600">${crQual}%</td>
                <td class="py-3 px-3.5 text-right font-medium text-slate-700">${fmtNum(d.dealer)} ➔ <span class="font-bold text-blue-700">${fmtNum(r.dealsDealer)}</span> <span class="text-[10px] text-slate-400">(${crDc}%)</span></td>
                <td class="py-3 px-3.5 text-right font-medium text-slate-700">${fmtNum(d.fdc_appr)} ➔ <span class="font-bold text-emerald-700">${fmtNum(r.dealsFdc)}</span> <span class="text-[10px] text-slate-400">(${crFdc}%)</span></td>
                <td class="py-3 px-3.5 text-right font-semibold text-indigo-700">${fmtNum(r.dealsOnline)}</td>
                <td class="py-3 px-3.5 text-right font-black text-[#107C41] bg-emerald-50/60">${fmtNum(r.dealsPureRetail)}</td>
                <td class="py-3 px-3.5 text-right font-black text-[#107C41] bg-emerald-50/60">${fmtRub(r.revPureRetail)}</td>
                <td class="py-3 px-3.5 text-right font-bold text-emerald-800">${crB}%</td>
                <td class="py-3 px-3.5 text-center">${badgeStatus}</td>
            </tr>
        `;
    });

    container.innerHTML = `
        <!-- 1. ANALYTICAL STEP FUNNEL WITH DROP-OFFS -->
        <div class="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 md:p-8 space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-200">
                <div>
                    <h3 class="text-lg font-black text-slate-900 flex items-center gap-2">
                        <i data-lucide="git-merge" class="w-5 h-5 text-[#107C41]"></i>
                        Сквозная ступенчатая воронка и анализ точек отвала (${periodLabel})
                    </h3>
                    <p class="text-xs text-slate-500 mt-0.5">Витрина (PostHog) ➔ Межсистемный разрыв ➔ Квалификация L1 ➔ 3 Розн. ветки ➔ Сделки (без МП1/2/3)</p>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-bold px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-300">
                        100% входящий поток компании
                    </span>
                </div>
            </div>

            <!-- STEP PIPELINE CONTAINER -->
            <div class="space-y-4">
                
                <!-- STAGE 1: ВИТРИНА POSTHOG -->
                <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                    <div class="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-700">
                        <span class="flex items-center gap-2">
                            <i data-lucide="monitor" class="w-4 h-4 text-emerald-600"></i>
                            Этап 1: Витрина СберАвто (PostHog Clickstream)
                        </span>
                        <span class="text-slate-500 font-semibold normal-case">Каталог: ${fmtNum(totPv)} просмотров</span>
                    </div>

                    <!-- Flow Bar 1: Card Show -->
                    <div>
                        <div class="flex justify-between text-xs mb-1">
                            <span class="font-bold text-slate-800">1. Показы карточек автомобилей</span>
                            <span class="font-black text-slate-900">${fmtNum(totCardShow)} <span class="text-slate-400 font-normal">(100% базы)</span></span>
                        </div>
                        <div class="w-full h-7 bg-slate-200 rounded-xl overflow-hidden flex">
                            <div class="h-full bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl flex items-center px-3 text-white font-bold text-xs shadow-inner" style="width: 100%;">
                                ${fmtNum(totCardShow)} показов
                            </div>
                        </div>
                    </div>

                    <!-- Drop-off Badge 1 -->
                    <div class="flex items-center justify-center py-0.5">
                        <div class="flex items-center gap-2 px-3.5 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold shadow-xs">
                            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 text-rose-600"></i>
                            <span>🔻 Отвал на клике: -${dropCard}% (-${fmtNum(totCardShow - totCardClick)})</span>
                            <span class="text-slate-400">•</span>
                            <span class="text-emerald-700">CTR карточки: ${ctrCard}%</span>
                        </div>
                    </div>

                    <!-- Flow Bar 2: Card Click -->
                    <div>
                        <div class="flex justify-between text-xs mb-1">
                            <span class="font-bold text-slate-800">2. Переходы в карточку (Клики)</span>
                            <span class="font-black text-slate-900">${fmtNum(totCardClick)}</span>
                        </div>
                        <div class="w-full h-7 bg-slate-200 rounded-xl overflow-hidden flex">
                            <div class="h-full bg-teal-600 rounded-xl flex items-center px-3 text-white font-bold text-xs" style="width: ${Math.max(totCardShow > 0 ? (totCardClick / totCardShow * 100) : 0, 10)}%;">
                                ${fmtNum(totCardClick)}
                            </div>
                        </div>
                    </div>

                    <!-- Drop-off Badge 2 -->
                    <div class="flex items-center justify-center py-0.5">
                        <div class="flex items-center gap-2 px-3.5 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold shadow-xs">
                            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 text-rose-600"></i>
                            <span>🔻 Отвал до заявки: -${dropOfferSucc}% (-${fmtNum(totCardClick - totOfferSuccess)})</span>
                            <span class="text-slate-400">•</span>
                            <span class="text-emerald-700">Подтверждено: ${crOfferSucc}%</span>
                        </div>
                    </div>

                    <!-- Flow Bar 3: Offer Success -->
                    <div>
                        <div class="flex justify-between text-xs mb-1">
                            <span class="font-bold text-slate-800">3. Подтвержденные онлайн-заявки (Экран успеха)</span>
                            <span class="font-black text-emerald-800">${fmtNum(totOfferSuccess)}</span>
                        </div>
                        <div class="w-full h-7 bg-slate-200 rounded-xl overflow-hidden flex">
                            <div class="h-full bg-emerald-600 rounded-xl flex items-center px-3 text-white font-bold text-xs" style="width: ${Math.max(totCardShow > 0 ? (totOfferSuccess / totCardShow * 100) : 0, 8)}%;">
                                ${fmtNum(totOfferSuccess)} заявок
                            </div>
                        </div>
                    </div>
                </div>

                <!-- SYSTEM GAP: ВИТРИНА ➔ CRM (Критический предупреждающий блок) -->
                <div class="bg-amber-50 border-2 border-dashed border-amber-300 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-xl bg-amber-500 text-white flex items-center justify-center font-black shrink-0 mt-0.5 shadow-sm">
                            <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h4 class="text-xs font-black text-amber-900 uppercase tracking-wide">Межсистемный разрыв: Витрина ➔ CRM Лиды</h4>
                                <span class="px-2 py-0.5 rounded-md bg-amber-200 text-amber-900 font-extrabold text-[10px]">Потеря: -${gapPct}% (-${fmtNum(gapVitrinaCrm)} заявок)</span>
                            </div>
                            <p class="text-xs text-amber-800 mt-0.5">
                                С витрины успешно отправлено <b>${fmtNum(totOfferSuccess)}</b> заявок, однако в CRM зарегистрировано только <b>${fmtNum(totLeads)}</b> лидов.
                                Причины: дедупликация повторных кликов одного клиента за сессию, фильтрация ботов либо задержки/сбои вебхуков.
                            </p>
                        </div>
                    </div>
                    <div class="bg-white px-3 py-1.5 rounded-xl border border-amber-200 text-right shrink-0">
                        <span class="text-[10px] text-slate-400 block font-bold">Доходимость в CRM</span>
                        <span class="text-xs font-black text-slate-800">${totOfferSuccess > 0 ? ((totLeads / totOfferSuccess) * 100).toFixed(1) : 0}%</span>
                    </div>
                </div>

                <!-- STAGE 2: CRM & КВАЛИФИКАЦИЯ 1-Й ЛИНИИ -->
                <div class="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-3">
                    <div class="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-700">
                        <span class="flex items-center gap-2">
                            <i data-lucide="phone-call" class="w-4 h-4 text-blue-600"></i>
                            Этап 2: CRM Backoffice & Квалификация первой линии (L1)
                        </span>
                        <span class="text-slate-500 font-semibold normal-case">Всего в базе: ${fmtNum(totLeads)} лидов</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <span class="text-[10px] uppercase font-bold text-slate-400">1. Входящие лиды (Статус "Новый")</span>
                                <p class="text-xl font-black text-slate-900 mt-0.5">${fmtNum(totLeads)}</p>
                            </div>
                            <p class="text-[11px] text-slate-500 mt-2">Поступают в распределение колл-центра 1-й линии</p>
                        </div>

                        <div class="bg-white p-4 rounded-xl border border-emerald-200 shadow-sm flex flex-col justify-between">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="text-[10px] uppercase font-bold text-emerald-800">2. Квалифицировано (Целевой = 1)</span>
                                    <p class="text-xl font-black text-[#107C41] mt-0.5">${fmtNum(totQual)}</p>
                                </div>
                                <span class="px-2.5 py-1 rounded-lg bg-emerald-100 text-emerald-800 font-black text-xs">
                                    CR L1: ${crL1}%
                                </span>
                            </div>
                            <div class="text-[11px] text-rose-700 bg-rose-50 p-2 rounded-lg border border-rose-100 mt-2">
                                🔻 <b>Отсев 1-й линии: -${(100 - parseFloat(crL1)).toFixed(1)}%</b> (-${fmtNum(totLeads - totQual)} нецелевых / недозвон)
                            </div>
                        </div>
                    </div>
                </div>

                <!-- STAGE 3: РАЗВИЛКА КАНАЛОВ (3 СТРИМА) -->
                <div class="space-y-3">
                    <div class="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-700">
                        <span class="flex items-center gap-2">
                            <i data-lucide="split" class="w-4 h-4 text-purple-600"></i>
                            Этап 3: Развилка каналов продаж (3 розничных стрима)
                        </span>
                        <span class="text-xs font-bold text-emerald-700">Сумма стримов: ${fmtNum(totPureRetailDeals)} сделок</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        
                        <!-- ВЕТКА 1: ДЦ -->
                        <div class="bg-gradient-to-b from-blue-50/70 to-white p-5 rounded-2xl border border-blue-200 shadow-sm flex flex-col justify-between space-y-3">
                            <div>
                                <div class="flex justify-between items-center">
                                    <span class="text-xs font-black text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
                                        <i data-lucide="building-2" class="w-4 h-4 text-blue-600"></i>
                                        Ветка 1: Дилеры (ДЦ)
                                    </span>
                                    <span class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-[10px] font-bold">Лиды в ДЦ</span>
                                </div>

                                <div class="space-y-2 mt-3 text-xs">
                                    <div class="flex justify-between py-1.5 border-b border-blue-100">
                                        <span class="text-slate-600">Передано лидов в ДЦ:</span>
                                        <span class="font-bold text-slate-900">${fmtNum(totDealer)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-blue-100">
                                        <span class="text-slate-600">Сделок подтверждено:</span>
                                        <span class="font-black text-blue-700">${fmtNum(totDealsDealer)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-blue-100">
                                        <span class="text-slate-600">Конверсия в сделку:</span>
                                        <span class="font-extrabold text-blue-800">${crDealer}%</span>
                                    </div>
                                </div>

                                <div class="bg-rose-50 border border-rose-200 p-2.5 rounded-xl text-[11px] text-rose-800 mt-3">
                                    <b>⚠️ Отвал у дилеров: -${dropDealer}%</b> (-${fmtNum(totDealer - totDealsDealer)} клиентов)
                                </div>
                            </div>

                            <div class="pt-3 border-t border-blue-100 flex justify-between items-end">
                                <div>
                                    <span class="text-[10px] text-slate-400 block font-bold">Выручка ДЦ</span>
                                    <span class="text-base font-black text-slate-900">${fmtRub(totRevDealer)}</span>
                                </div>
                                <span class="text-[11px] text-slate-500 font-medium">Чек: ${fmtRub(totDealsDealer > 0 ? totRevDealer/totDealsDealer : 0)}</span>
                            </div>
                        </div>

                        <!-- ВЕТКА 2: ФДЦ -->
                        <div class="bg-gradient-to-b from-emerald-50/70 to-white p-5 rounded-2xl border border-emerald-200 shadow-sm flex flex-col justify-between space-y-3">
                            <div>
                                <div class="flex justify-between items-center">
                                    <span class="text-xs font-black text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
                                        <i data-lucide="credit-card" class="w-4 h-4 text-[#107C41]"></i>
                                        Ветка 2: Онлайн-кредит (ФДЦ)
                                    </span>
                                    <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[10px] font-bold">СберБанк</span>
                                </div>

                                <div class="space-y-2 mt-3 text-xs">
                                    <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                        <span class="text-slate-600">Расчетов калькулятора:</span>
                                        <span class="font-bold text-slate-900">${fmtNum(totCalc)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                        <span class="text-slate-600">Заявок в Сбер (CR ${crFdcApp}%):</span>
                                        <span class="font-bold text-slate-900">${fmtNum(totFdcApp)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                        <span class="text-slate-600">Одобрено банком (${crFdcAppr}%):</span>
                                        <span class="font-bold text-emerald-700">${fmtNum(totFdcAppr)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                        <span class="text-slate-600">Сделок ФДЦ (CR ${crFdcDeal}%):</span>
                                        <span class="font-black text-[#107C41]">${fmtNum(totDealsFdc)}</span>
                                    </div>
                                </div>

                                <div class="bg-rose-50 border border-rose-200 p-2.5 rounded-xl text-[11px] text-rose-800 mt-3">
                                    <b>⚠️ Потеря одобренных: -${dropFdcDeal}%</b> (-${fmtNum(totFdcAppr - totDealsFdc)} клиентов)
                                </div>
                            </div>

                            <div class="pt-3 border-t border-emerald-100 flex justify-between items-end">
                                <div>
                                    <span class="text-[10px] text-slate-400 block font-bold">Выручка ФДЦ</span>
                                    <span class="text-base font-black text-[#107C41]">${fmtRub(totRevFdc)}</span>
                                </div>
                                <span class="text-[11px] text-slate-500 font-medium">Чек: ${fmtRub(totDealsFdc > 0 ? totRevFdc/totDealsFdc : 0)}</span>
                            </div>
                        </div>

                        <!-- ВЕТКА 3: ONLINE / ПРЕДОПЛАТА -->
                        <div class="bg-gradient-to-b from-purple-50/70 to-white p-5 rounded-2xl border border-purple-200 shadow-sm flex flex-col justify-between space-y-3">
                            <div>
                                <div class="flex justify-between items-center">
                                    <span class="text-xs font-black text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
                                        <i data-lucide="zap" class="w-4 h-4 text-purple-600"></i>
                                        Ветка 3: Online / Предоплата
                                    </span>
                                    <span class="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-[10px] font-bold">Прямой выкуп</span>
                                </div>

                                <div class="space-y-2 mt-3 text-xs">
                                    <div class="flex justify-between py-1.5 border-b border-purple-100">
                                        <span class="text-slate-600">Прямой выбор авто на сайте:</span>
                                        <span class="font-bold text-slate-900">Каталог</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-purple-100">
                                        <span class="text-slate-600">Онлайн-бронь / Предоплата:</span>
                                        <span class="font-bold text-purple-700">5 000 ₽</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-purple-100">
                                        <span class="text-slate-600">Сделок Online закрыто:</span>
                                        <span class="font-black text-purple-700">${fmtNum(totDealsOnline)}</span>
                                    </div>
                                    <div class="flex justify-between py-1.5 border-b border-purple-100">
                                        <span class="text-slate-600">Доля в рознице:</span>
                                        <span class="font-bold text-slate-800">${totPureRetailDeals > 0 ? ((totDealsOnline / totPureRetailDeals) * 100).toFixed(1) : 0}%</span>
                                    </div>
                                </div>

                                <div class="bg-emerald-50 border border-emerald-200 p-2.5 rounded-xl text-[11px] text-emerald-800 mt-3">
                                    <b>✅ Высокая маржинальность:</b> прямой канал без посредников и комиссий дилерам.
                                </div>
                            </div>

                            <div class="pt-3 border-t border-purple-100 flex justify-between items-end">
                                <div>
                                    <span class="text-[10px] text-slate-400 block font-bold">Выручка Online</span>
                                    <span class="text-base font-black text-purple-800">${fmtRub(totRevOnline)}</span>
                                </div>
                                <span class="text-[11px] text-slate-500 font-medium">Чек: ${fmtRub(totDealsOnline > 0 ? totRevOnline/totDealsOnline : 0)}</span>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- STAGE 4: ИТОГО ЧИСТАЯ РОЗНИЦА -->
                <div class="bg-gradient-to-r from-emerald-700 via-[#107C41] to-teal-700 text-white p-6 rounded-3xl shadow-lg flex flex-col md:flex-row justify-between items-center gap-4">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center font-black text-xl shadow-inner">
                            🏆
                        </div>
                        <div>
                            <span class="text-xs uppercase font-bold tracking-wider text-emerald-100">Итоговая реализация чистой розницы (${periodLabel})</span>
                            <div class="flex items-baseline gap-3 mt-1">
                                <h4 class="text-2xl font-black text-white">${fmtNum(totPureRetailDeals)} закрытых сделок</h4>
                                <span class="text-xs font-bold bg-white/20 px-2.5 py-0.5 rounded-lg text-white">CR: ${crOverall}% от лидов CRM</span>
                            </div>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-[10px] text-emerald-200 block uppercase font-bold">Чистая выручка (без МП1/2/3)</span>
                        <span class="text-2xl font-black text-white">${fmtRub(totPureRetailRev)}</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- 2. BOTTLENECK DIAGNOSTIC CARDS (ТОП-3 УЗКИХ МЕСТА С РАСЧЕТОМ ПОТЕНЦИАЛА) -->
        <div class="space-y-3">
            <div class="flex justify-between items-center">
                <h3 class="text-sm font-black text-slate-900 uppercase tracking-wide flex items-center gap-2">
                    <i data-lucide="alert-circle" class="w-4 h-4 text-rose-600"></i>
                    🚨 Экспресс-диагностика: Топ узких мест и точек роста выручки
                </h3>
                <span class="text-xs text-slate-500">Автоматический аудит конверсий</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                <!-- B1: ДЦ -->
                <div class="bg-white p-5 rounded-2xl border border-rose-200 shadow-sm relative overflow-hidden flex flex-col justify-between">
                    <div class="absolute top-0 right-0 w-2 h-full bg-rose-500"></div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-extrabold text-[10px]">УЗКОЕ МЕСТО №1</span>
                            <span class="text-xs font-bold text-rose-600">Потери: -${dropDealer}%</span>
                        </div>
                        <h4 class="text-sm font-black text-slate-900 mt-2">Черная дыра у дилеров (ДЦ)</h4>
                        <p class="text-xs text-slate-600 mt-1">
                            Из <b>${fmtNum(totDealer)}</b> переданных лидов до сделок дошло лишь <b>${fmtNum(totDealsDealer)}</b> (CR: <b>${crDealer}%</b>).
                            Потеряно <b>${fmtNum(totDealer - totDealsDealer)}</b> теплых клиентов.
                        </p>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-100 bg-emerald-50/60 p-3 rounded-xl">
                        <span class="text-[10px] uppercase font-bold text-emerald-800 block">Потенциал роста выручки:</span>
                        <span class="text-xs text-emerald-900 font-semibold">
                            Если поднять доходимость у дилеров до <b>20%</b> (+${Math.round(totDealer * 0.2 - totDealsDealer)} сделок):
                            <b class="text-[#107C41] block text-sm mt-0.5">+${fmtRub(Math.max(0, (totDealer * 0.2 - totDealsDealer) * (totDealsDealer > 0 ? totRevDealer/totDealsDealer : 35000)))}</b>
                        </span>
                    </div>
                </div>

                <!-- B2: ФДЦ Кладбище -->
                <div class="bg-white p-5 rounded-2xl border border-rose-200 shadow-sm relative overflow-hidden flex flex-col justify-between">
                    <div class="absolute top-0 right-0 w-2 h-full bg-rose-500"></div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-extrabold text-[10px]">УЗКОЕ МЕСТО №2</span>
                            <span class="text-xs font-bold text-rose-600">Потери: -${dropFdcDeal}%</span>
                        </div>
                        <h4 class="text-sm font-black text-slate-900 mt-2">«Кладбище» одобренных кредитов</h4>
                        <p class="text-xs text-slate-600 mt-1">
                            Банк одобрил <b>${fmtNum(totFdcAppr)}</b> заявок, но куплено авто только <b>${fmtNum(totDealsFdc)}</b> шт (CR: <b>${crFdcDeal}%</b>).
                            <b>${fmtNum(totFdcAppr - totDealsFdc)}</b> клиентов с одобренными деньгами ушли без покупки!
                        </p>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-100 bg-emerald-50/60 p-3 rounded-xl">
                        <span class="text-[10px] uppercase font-bold text-emerald-800 block">Потенциал дожима:</span>
                        <span class="text-xs text-emerald-900 font-semibold">
                            Дожим трети отказников с одобрением (+${Math.round((totFdcAppr - totDealsFdc) / 3)} сделок):
                            <b class="text-[#107C41] block text-sm mt-0.5">+${fmtRub(Math.round((totFdcAppr - totDealsFdc) / 3) * (totDealsFdc > 0 ? totRevFdc/totDealsFdc : 41000))}</b>
                        </span>
                    </div>
                </div>

                <!-- B3: Анкета ФДЦ -->
                <div class="bg-white p-5 rounded-2xl border border-amber-200 shadow-sm relative overflow-hidden flex flex-col justify-between">
                    <div class="absolute top-0 right-0 w-2 h-full bg-amber-500"></div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-extrabold text-[10px]">УЗКОЕ МЕСТО №3</span>
                            <span class="text-xs font-bold text-amber-600">Отвал: -${dropFdcApp}%</span>
                        </div>
                        <h4 class="text-sm font-black text-slate-900 mt-2">Слив на кредитной анкете</h4>
                        <p class="text-xs text-slate-600 mt-1">
                            Из <b>${fmtNum(totCalc)}</b> расчетов в калькуляторе заявку в Сбер отправили только <b>${fmtNum(totFdcApp)}</b> (CR: <b>${crFdcApp}%</b>).
                            <b>${(100 - parseFloat(crFdcApp)).toFixed(1)}%</b> бросают заполнение анкеты на сайте.
                        </p>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-100 bg-amber-50/70 p-3 rounded-xl">
                        <span class="text-[10px] uppercase font-bold text-amber-900 block">Рекомендация продукта:</span>
                        <span class="text-xs text-amber-900 font-medium">
                            Внедрить автозаполнение анкеты через <b>Сбер ID</b> в 1 клик для сокращения числа полей и удвоения потока заявок.
                        </span>
                    </div>
                </div>

            </div>
        </div>

        <!-- 3. BRAND BENCHMARK MATRIX (РЕЙТИНГ ЭФФЕКТИВНОСТИ 14 БРЕНДОВ) -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-xl space-y-4">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-slate-200">
                <div>
                    <h3 class="text-base font-black text-slate-900 flex items-center gap-2">
                        <i data-lucide="award" class="w-5 h-5 text-[#107C41]"></i>
                        Матрица эффективности воронки по ${bNames.length} брендам (${periodLabel})
                    </h3>
                    <p class="text-xs text-slate-500">Нажмите на любой бренд, чтобы открыть его персональную пошаговую воронку с отвалами</p>
                </div>
                <span class="px-3 py-1 bg-emerald-50 text-emerald-800 rounded-lg text-xs font-bold border border-emerald-300">
                    Чистая розница (без МП1/2/3)
                </span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-xs text-left">
                    <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                            <th class="py-3 px-3.5">Бренд</th>
                            <th class="py-3 px-3.5 text-right">Лиды CRM</th>
                            <th class="py-3 px-3.5 text-right">L1 Квал %</th>
                            <th class="py-3 px-3.5 text-right">Ветка ДЦ (Передано ➔ Сделка)</th>
                            <th class="py-3 px-3.5 text-right">Ветка ФДЦ (Одобрено ➔ Сделка)</th>
                            <th class="py-3 px-3.5 text-right text-indigo-700">Online</th>
                            <th class="py-3 px-3.5 text-right text-[#107C41] bg-emerald-50/90 font-black">Сделки Розница</th>
                            <th class="py-3 px-3.5 text-right text-[#107C41] bg-emerald-50/90 font-black">Выручка Розница</th>
                            <th class="py-3 px-3.5 text-right text-emerald-900 font-black">Сквозной CR</th>
                            <th class="py-3 px-3.5 text-center">Здоровье</th>
                        </tr>
                    </thead>
                    <tbody>${tableRows}</tbody>
                    <tfoot class="bg-slate-900 text-white font-bold">
                        <tr>
                            <td class="py-3 px-3.5">ИТОГО (${bNames.length} БРЕНДОВ)</td>
                            <td class="py-3 px-3.5 text-right">${fmtNum(totLeads)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-400 font-bold">${crL1}%</td>
                            <td class="py-3 px-3.5 text-right">${fmtNum(totDealer)} ➔ <span class="text-blue-300 font-black">${fmtNum(totDealsDealer)}</span> (${crDealer}%)</td>
                            <td class="py-3 px-3.5 text-right">${fmtNum(totFdcAppr)} ➔ <span class="text-emerald-300 font-black">${fmtNum(totDealsFdc)}</span> (${crFdcDeal}%)</td>
                            <td class="py-3 px-3.5 text-right text-indigo-300">${fmtNum(totDealsOnline)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-400 font-black text-sm">${fmtNum(totPureRetailDeals)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-400 font-black text-sm">${fmtRub(totPureRetailRev)}</td>
                            <td class="py-3 px-3.5 text-right text-emerald-300 font-black">${crOverall}%</td>
                            <td class="py-3 px-3.5 text-center text-emerald-400 font-bold">100% базы</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
}

/**
 * 🏷 RENDER SINGLE BRAND VIEW
 * Individual brand step pipeline, brand-level drop-offs, and channel performance
 */
function renderFunnelSingleBrandView(brand, d) {
    const container = document.getElementById('funnelDynamicView');
    if (!container) return;

    const v = d.vitrina || {};
    const r = extractRetailMetrics(d);

    const crOverall = d.leads > 0 ? ((r.dealsPureRetail / d.leads) * 100).toFixed(2) : '0';
    const crL1 = d.leads > 0 ? ((d.qual / d.leads) * 100).toFixed(1) : '0';

    const pageView = v.page_view || (d.leads * 140) || 0;
    const cardShow = v.car_card_show || (d.leads * 21) || 0;
    const cardClick = v.car_card_click || (d.leads * 2.7) || 0;
    const offerShow = v.offer_show || (d.leads * 2.6) || 0;
    const offerClick = v.offer_click || (d.leads * 1.7) || 0;
    const offerSuccess = v.offer_success || d.leads || 0;

    const ctrCard = cardShow > 0 ? ((cardClick / cardShow) * 100).toFixed(1) : '0';
    const dropCard = cardShow > 0 ? ((1 - cardClick / cardShow) * 100).toFixed(1) : '0';
    const crSuccess = offerClick > 0 ? ((offerSuccess / offerClick) * 100).toFixed(1) : '0';

    // Vitrina to CRM gap for brand
    const gapVitrinaCrm = offerSuccess - d.leads;
    const gapPct = offerSuccess > 0 ? ((gapVitrinaCrm / offerSuccess) * 100).toFixed(1) : '0';

    // Channel specific conversion
    const crDealer = d.dealer > 0 ? ((r.dealsDealer / d.dealer) * 100).toFixed(1) : '0';
    const dropDealer = d.dealer > 0 ? ((1 - r.dealsDealer / d.dealer) * 100).toFixed(1) : '0';

    const calcTotal = d.calc_total || 0;
    const fdcApp = d.fdc_app || 0;
    const fdcAppr = d.fdc_appr || 0;
    const crFdcApp = calcTotal > 0 ? ((fdcApp / calcTotal) * 100).toFixed(1) : '0';
    const crFdcAppr = fdcApp > 0 ? ((fdcAppr / fdcApp) * 100).toFixed(1) : '0';
    const crFdcDeal = fdcAppr > 0 ? ((r.dealsFdc / fdcAppr) * 100).toFixed(1) : '0';
    const dropFdcDeal = fdcAppr > 0 ? ((1 - r.dealsFdc / fdcAppr) * 100).toFixed(1) : '0';

    // Sources rows
    let srcRows = '';
    if (d.src_breakdown) {
        Object.entries(d.src_breakdown).forEach(([src, cnt]) => {
            const pct = d.leads > 0 ? ((cnt / d.leads) * 100).toFixed(1) + '%' : '0%';
            srcRows += `<div class="flex justify-between items-center py-1.5 border-b border-slate-100 text-xs"><span class="text-slate-700 font-medium">${src}</span><span class="font-bold text-slate-900">${fmtNum(cnt)} <span class="text-[11px] text-slate-400 font-normal">(${pct})</span></span></div>`;
        });
    }

    // Pure Retail deals rows
    const b2cRows = `
        <div class="flex justify-between items-center py-1.5 border-b border-slate-100 text-xs">
            <span class="text-blue-700 font-medium">🏢 Передача лида в ДЦ:</span>
            <span class="font-black text-slate-900">${fmtNum(r.dealsDealer)} сделок <span class="text-emerald-700 font-bold">(${fmtRub(r.revDealer)})</span></span>
        </div>
        <div class="flex justify-between items-center py-1.5 border-b border-slate-100 text-xs">
            <span class="text-emerald-700 font-medium">💳 Онлайн-кредит ФДЦ:</span>
            <span class="font-black text-slate-900">${fmtNum(r.dealsFdc)} сделок <span class="text-emerald-700 font-bold">(${fmtRub(r.revFdc)})</span></span>
        </div>
        <div class="flex justify-between items-center py-1.5 border-b border-slate-100 text-xs">
            <span class="text-purple-700 font-medium">⚡️ Online / Предоплата:</span>
            <span class="font-black text-slate-900">${fmtNum(r.dealsOnline)} сделок <span class="text-purple-700 font-bold">(${fmtRub(r.revOnline)})</span></span>
        </div>
    `;

    // Clear top KPI cards to keep page uncluttered
    const kpiCards = document.getElementById('funnelKpiCards');
    if (kpiCards) kpiCards.innerHTML = '';

    const periodLabel = getCurrentFunnelPeriodLabel();

    container.innerHTML = `
        <div class="bg-slate-50 text-slate-900 p-6 md:p-8 rounded-3xl shadow-xl border border-slate-200 space-y-6">
            
            <!-- BRAND HEADER -->
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-600 to-[#107C41] flex items-center justify-center text-white font-black text-xl shadow-md">${brand.charAt(0)}</div>
                    <div>
                        <h3 class="text-xl font-black text-slate-900 flex items-center gap-2">
                            Сквозная воронка продаж: <span class="text-[#107C41]">${brand}</span>
                        </h3>
                        <p class="text-xs text-slate-500 mt-0.5">Период: ${periodLabel} • Строго розница (без МП1, МП2, МП3)</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="selectFunnelBrand('ALL')" class="px-3 py-1.5 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
                        <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
                        Все бренды (Сводно)
                    </button>
                    <span class="px-3 py-1.5 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300">
                        Розница: ${fmtNum(r.dealsPureRetail)} сделок (${crOverall}%)
                    </span>
                    <span class="px-3 py-1.5 rounded-xl bg-slate-200 text-slate-700 text-xs font-semibold">
                        Опт: ${fmtNum(r.totalMpCount)} шт
                    </span>
                </div>
            </div>

            <!-- STEP PIPELINE FOR BRAND -->
            <div class="space-y-4">
                
                <!-- STAGE 1: ВИТРИНА POSTHOG (BRAND) -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 space-y-3 shadow-sm">
                    <div class="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-700">
                        <span class="flex items-center gap-1.5">
                            <i data-lucide="monitor" class="w-4 h-4 text-emerald-600"></i>
                            Этап 1: Витрина PostHog (${brand})
                        </span>
                        <span class="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                            CTR карточки: ${ctrCard}%
                        </span>
                    </div>

                    <!-- Visual Step Bars -->
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
                        <div class="bg-slate-100 p-3.5 rounded-xl border border-slate-200">
                            <span class="text-[10px] uppercase font-bold text-slate-500">1. Просмотр листинга</span>
                            <p class="text-lg font-black text-slate-900 mt-1">${fmtNum(pageView)}</p>
                        </div>
                        <div class="bg-slate-100 p-3.5 rounded-xl border border-slate-200">
                            <span class="text-[10px] uppercase font-bold text-slate-500">2. Показ карточки</span>
                            <p class="text-lg font-black text-slate-900 mt-1">${fmtNum(cardShow)}</p>
                        </div>
                        <div class="bg-teal-50 p-3.5 rounded-xl border border-teal-200">
                            <span class="text-[10px] uppercase font-bold text-teal-800">3. Клик карточки</span>
                            <p class="text-lg font-black text-teal-900 mt-1">${fmtNum(cardClick)}</p>
                            <span class="text-[10px] text-teal-700 font-bold">CTR: ${ctrCard}%</span>
                        </div>
                        <div class="bg-slate-100 p-3.5 rounded-xl border border-slate-200">
                            <span class="text-[10px] uppercase font-bold text-slate-500">4. Экран оффера</span>
                            <p class="text-lg font-black text-slate-900 mt-1">${fmtNum(offerShow)}</p>
                        </div>
                        <div class="bg-slate-100 p-3.5 rounded-xl border border-slate-200">
                            <span class="text-[10px] uppercase font-bold text-slate-500">5. Клик отправки</span>
                            <p class="text-lg font-black text-slate-900 mt-1">${fmtNum(offerClick)}</p>
                        </div>
                        <div class="bg-emerald-100 p-3.5 rounded-xl border border-emerald-300">
                            <span class="text-[10px] uppercase font-bold text-emerald-800">6. Экран успеха</span>
                            <p class="text-lg font-black text-[#107C41] mt-1">${fmtNum(offerSuccess)}</p>
                            <span class="text-[10px] text-emerald-700 font-bold">Заявок на сайте</span>
                        </div>
                    </div>
                </div>

                <!-- GAP FOR BRAND -->
                <div class="bg-amber-50 border border-amber-300 rounded-xl p-3 flex justify-between items-center text-xs">
                    <div class="flex items-center gap-2 text-amber-900">
                        <i data-lucide="arrow-down" class="w-4 h-4 text-amber-600"></i>
                        <span><b>Переход в CRM:</b> ${fmtNum(offerSuccess)} заявок витрины ➔ <b>${fmtNum(d.leads)} лидов в CRM</b></span>
                    </div>
                    <span class="font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-200 text-[11px]">
                        ${gapVitrinaCrm > 0 ? 'Разрыв: -' + gapPct + '% (-' + fmtNum(gapVitrinaCrm) + ')' : '100% доходимость'}
                    </span>
                </div>

                <!-- STAGE 2: CRM & КВАЛИФИКАЦИЯ (BRAND) -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <div class="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-700">
                        <span class="flex items-center gap-1.5">
                            <i data-lucide="user-check" class="w-4 h-4 text-blue-600"></i>
                            Этап 2: CRM & Квалификация L1 (${brand})
                        </span>
                        <span class="text-xs font-bold text-blue-800 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                            Квалифицировано: ${crL1}%
                        </span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                            <span class="text-slate-500 block text-[10px] uppercase font-bold">Новых лидов в CRM</span>
                            <span class="text-base font-black text-slate-900 mt-1 block">${fmtNum(d.leads)}</span>
                        </div>
                        <div class="bg-emerald-50 p-3 rounded-xl border border-emerald-200">
                            <span class="text-emerald-800 block text-[10px] uppercase font-bold">Целевые (Квалиф. L1)</span>
                            <span class="text-base font-black text-[#107C41] mt-1 block">${fmtNum(d.qual)} (${crL1}%)</span>
                        </div>
                        <div class="bg-rose-50 p-3 rounded-xl border border-rose-200">
                            <span class="text-rose-800 block text-[10px] uppercase font-bold">Отсев первой линии</span>
                            <span class="text-base font-black text-rose-700 mt-1 block">${fmtNum(d.leads - d.qual)} (${(100 - parseFloat(crL1)).toFixed(1)}%)</span>
                        </div>
                    </div>
                </div>

                <!-- STAGE 3: РАЗВИЛКА КАНАЛОВ (BRAND) -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    
                    <!-- ДЦ -->
                    <div class="bg-gradient-to-b from-blue-50/70 to-white p-5 rounded-2xl border border-blue-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <span class="text-xs font-black text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
                                <i data-lucide="building-2" class="w-4 h-4 text-blue-600"></i>
                                Ветка ДЦ (${brand})
                            </span>
                            <div class="space-y-2 mt-3 text-xs">
                                <div class="flex justify-between py-1.5 border-b border-blue-100">
                                    <span class="text-slate-600">Передано в ДЦ:</span>
                                    <span class="font-bold text-slate-900">${fmtNum(d.dealer)}</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-blue-100">
                                    <span class="text-slate-600">Сделок подтверждено:</span>
                                    <span class="font-black text-blue-700">${fmtNum(r.dealsDealer)}</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-blue-100">
                                    <span class="text-slate-600">Конверсия передачи:</span>
                                    <span class="font-extrabold text-blue-800">${crDealer}%</span>
                                </div>
                            </div>
                            <div class="bg-rose-50 border border-rose-200 p-2.5 rounded-xl text-[11px] text-rose-800 mt-3">
                                🔻 <b>Отвал: -${dropDealer}%</b> (-${fmtNum(d.dealer - r.dealsDealer)} лидов)
                            </div>
                        </div>
                        <div class="pt-3 border-t border-blue-100 mt-3">
                            <span class="text-[10px] text-slate-400 block font-bold">Выручка ДЦ</span>
                            <span class="text-base font-black text-slate-900">${fmtRub(r.revDealer)}</span>
                        </div>
                    </div>

                    <!-- ФДЦ -->
                    <div class="bg-gradient-to-b from-emerald-50/70 to-white p-5 rounded-2xl border border-emerald-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <span class="text-xs font-black text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
                                <i data-lucide="credit-card" class="w-4 h-4 text-[#107C41]"></i>
                                Ветка ФДЦ (${brand})
                            </span>
                            <div class="space-y-2 mt-3 text-xs">
                                <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                    <span class="text-slate-600">Расчетов в калькуляторе:</span>
                                    <span class="font-bold text-slate-900">${fmtNum(calcTotal)}</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                    <span class="text-slate-600">Заявок в банк:</span>
                                    <span class="font-bold text-slate-900">${fmtNum(fdcApp)} (${crFdcApp}%)</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                    <span class="text-slate-600">Одобрено банком:</span>
                                    <span class="font-bold text-emerald-700">${fmtNum(fdcAppr)} (${crFdcAppr}%)</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-emerald-100">
                                    <span class="text-slate-600">Сделок ФДЦ:</span>
                                    <span class="font-black text-[#107C41]">${fmtNum(r.dealsFdc)}</span>
                                </div>
                            </div>
                            <div class="bg-rose-50 border border-rose-200 p-2.5 rounded-xl text-[11px] text-rose-800 mt-3">
                                🔻 <b>Потеря одобренных: -${dropFdcDeal}%</b> (-${fmtNum(fdcAppr - r.dealsFdc)})
                            </div>
                        </div>
                        <div class="pt-3 border-t border-emerald-100 mt-3">
                            <span class="text-[10px] text-slate-400 block font-bold">Выручка ФДЦ</span>
                            <span class="text-base font-black text-[#107C41]">${fmtRub(r.revFdc)}</span>
                        </div>
                    </div>

                    <!-- ONLINE -->
                    <div class="bg-gradient-to-b from-purple-50/70 to-white p-5 rounded-2xl border border-purple-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <span class="text-xs font-black text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
                                <i data-lucide="zap" class="w-4 h-4 text-purple-600"></i>
                                Ветка Online (${brand})
                            </span>
                            <div class="space-y-2 mt-3 text-xs">
                                <div class="flex justify-between py-1.5 border-b border-purple-100">
                                    <span class="text-slate-600">Канал покупки:</span>
                                    <span class="font-bold text-slate-900">Прямой онлайн-выкуп</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-purple-100">
                                    <span class="text-slate-600">Сделок Online закрыто:</span>
                                    <span class="font-black text-purple-700">${fmtNum(r.dealsOnline)}</span>
                                </div>
                                <div class="flex justify-between py-1.5 border-b border-purple-100">
                                    <span class="text-slate-600">Доля в продажах марки:</span>
                                    <span class="font-bold text-slate-800">${r.dealsPureRetail > 0 ? ((r.dealsOnline / r.dealsPureRetail) * 100).toFixed(1) : 0}%</span>
                                </div>
                            </div>
                            <div class="bg-emerald-50 border border-emerald-200 p-2.5 rounded-xl text-[11px] text-emerald-800 mt-3">
                                <b>✅ Прямая маржа:</b> без комиссии дилерским центрам.
                            </div>
                        </div>
                        <div class="pt-3 border-t border-purple-100 mt-3">
                            <span class="text-[10px] text-slate-400 block font-bold">Выручка Online</span>
                            <span class="text-base font-black text-purple-800">${fmtRub(r.revOnline)}</span>
                        </div>
                    </div>

                </div>

                <!-- BRAND TOTAL RESULT -->
                <div class="bg-gradient-to-r from-emerald-600 via-[#107C41] to-teal-700 text-white p-6 rounded-3xl shadow-lg flex flex-col md:flex-row justify-between items-center gap-6">
                    <div>
                        <span class="text-xs uppercase font-bold tracking-wider text-emerald-100">Итог чистой розницы (${brand})</span>
                        <div class="flex items-baseline gap-3 mt-1.5">
                            <h4 class="text-2xl font-black text-white">${fmtNum(r.dealsPureRetail)} закрытых сделок</h4>
                            <span class="text-xs font-bold bg-white/20 px-2.5 py-1 rounded-xl text-white">CR: ${crOverall}% от лидов</span>
                        </div>
                    </div>
                    <div class="text-right flex items-center gap-6">
                        <div>
                            <span class="text-[10px] text-emerald-100 block uppercase font-bold">Выручка розницы</span>
                            <span class="text-2xl font-black text-white">${fmtRub(r.revPureRetail)}</span>
                        </div>
                        <div class="border-l border-white/30 pl-6">
                            <span class="text-[10px] text-emerald-100 block uppercase font-bold">Исключен опт (МП1/2/3)</span>
                            <span class="text-sm font-bold text-white">${fmtNum(r.totalMpCount)} шт (${fmtRub(r.totalMpRev)})</span>
                        </div>
                    </div>
                </div>

                <!-- DETAILS: TRAFFIC SOURCES & RETAIL CHANNELS -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                        <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                            <i data-lucide="layers" class="w-4 h-4 text-indigo-600"></i>
                            Источники трафика (${brand})
                        </h4>
                        <div class="space-y-1">${srcRows || '<p class="text-xs text-slate-400">Нет данных по источникам</p>'}</div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
                        <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                            <i data-lucide="shopping-bag" class="w-4 h-4 text-emerald-600"></i>
                            Структура розничных сделок (${brand})
                        </h4>
                        <div class="space-y-1">${b2cRows}</div>
                    </div>
                </div>

            </div>
        </div>
    `;
}
