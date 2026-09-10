/**
 * executive-dashboard.js
 * =======================
 * Управленческая панель (Executive Analytics):
 * 1. Темп месяца (Pace / Run-Rate Tracker)
 * 2. Радар критических отклонений (Alerts Radar)
 * 3. Доходность и юнит-экономика каналов (Margin & ARPU)
 * 4. Матрица эффективности дилерской сети (Partner Health Score)
 */

let activeAlertTab = 'brands'; // 'brands' | 'dealers' | 'prepays'
let activeHealthQuadrant = 'all'; // 'all' | 'stars' | 'growth' | 'niche' | 'risk'

/**
 * Main render function called from data-loader.js updateAllTabs()
 */
function renderExecutiveDashboard(sDb, pDb, allDb, allPartners, filterConfig) {
    const container = document.getElementById('executiveDashboardContainer');
    if (!container) return;

    const activeMonth = (filterConfig && filterConfig.month) || 'all';

    // 1. Calculate Pace / Run-rate metrics
    const paceData = calculatePaceMetrics(sDb, allDb, activeMonth);

    // 2. Calculate Alerts Radar
    const alertData = calculateAlertsRadar(allDb, pDb);

    // 3. Calculate Margin & ARPU by Channel
    const marginData = calculateChannelUnitEconomics(sDb);

    // 4. Calculate Partner Health Score Matrix
    const healthData = calculatePartnerHealthScore(sDb, allPartners || []);

    // Render HTML structure
    container.innerHTML = `
        <div class="mb-6 space-y-6">
            <!-- Executive Section Header -->
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-5 md:p-6 rounded-3xl shadow-lg border border-slate-800">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shrink-0 font-black text-xl shadow-inner">
                        🎯
                    </div>
                    <div>
                        <div class="flex items-center gap-2.5 flex-wrap">
                            <h2 class="text-xl font-black tracking-tight text-white flex items-center gap-2">
                                Управленческий радар & Темп месяца
                            </h2>
                            <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold flex items-center gap-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                Executive Analytics
                            </span>
                        </div>
                        <p class="text-xs text-slate-300 mt-1">
                            Ключевые сигналы для принятия решений: суточный темп run-rate, просадки брендов, риск отвала ДЦ и маржинальность каналов
                        </p>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <div class="text-right hidden sm:block">
                        <div class="text-xs text-slate-400">Срез актуальности</div>
                        <div class="text-sm font-bold text-slate-200">${paceData.asOfDateStr}</div>
                    </div>
                </div>
            </div>

            <!-- 4 Executive Grid Cards -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Block 1: Pace / Run-Rate Tracker -->
                ${renderPaceCardHTML(paceData)}

                <!-- Block 2: Alerts Radar -->
                ${renderAlertsRadarCardHTML(alertData)}

                <!-- Block 3: Margin & ARPU Unit Economics -->
                ${renderMarginCardHTML(marginData)}

                <!-- Block 4: Partner Health Score Matrix -->
                ${renderHealthScoreCardHTML(healthData)}
            </div>
        </div>
    `;

    // Initialize Lucide icons if available
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
}

/**
 * =========================================================================
 * BLOCK 1: PACE & RUN-RATE TRACKER
 * =========================================================================
 */
function calculatePaceMetrics(sDb, allDb, activeMonth) {
    const deals = allDb || sDb || [];
    
    // Find latest sale date across all deals
    let maxSaleDate = null;
    deals.forEach(d => {
        const sDate = d.SaleDate || d.DealDate;
        if (sDate) {
            const dt = excelToJSDate(sDate);
            if (dt && (!maxSaleDate || dt > maxSaleDate)) {
                maxSaleDate = dt;
            }
        }
    });

    const refDate = maxSaleDate || new Date();
    const curYear = refDate.getFullYear();
    const curMonthIdx = refDate.getMonth(); // 0-based
    const curDay = refDate.getDate(); // e.g. 9

    const monthNames = ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"];
    const curMonthName = monthNames[curMonthIdx];
    const totalDaysInMonth = new Date(curYear, curMonthIdx + 1, 0).getDate(); // 30 for Sept
    const daysElapsed = Math.min(curDay, totalDaysInMonth);
    const monthProgressPct = Math.round((daysElapsed / totalDaysInMonth) * 100);

    // Current month deals MTD
    const curMonthPrefix = `${curYear}-${String(curMonthIdx + 1).padStart(2, '0')}`;
    const curMonthDeals = deals.filter(d => {
        const m = (d.SaleMonth || '').replace(/'/g, '');
        return m === curMonthPrefix;
    });

    const mtdSalesCount = curMonthDeals.length;
    const mtdRevenue = curMonthDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    // Daily run rate
    const dailyRate = daysElapsed > 0 ? (mtdSalesCount / daysElapsed) : 0;
    const projectedSales = Math.round(dailyRate * totalDaysInMonth);
    const projectedRevenue = daysElapsed > 0 ? Math.round((mtdRevenue / daysElapsed) * totalDaysInMonth) : 0;

    // Previous month comparison (MTD same days)
    const prevMonthIdx = curMonthIdx === 0 ? 11 : curMonthIdx - 1;
    const prevYear = curMonthIdx === 0 ? curYear - 1 : curYear;
    const prevMonthPrefix = `${prevYear}-${String(prevMonthIdx + 1).padStart(2, '0')}`;
    const prevMonthName = monthNames[prevMonthIdx];

    const prevMonthAllDeals = deals.filter(d => (d.SaleMonth || '').replace(/'/g, '') === prevMonthPrefix);
    const prevMonthTotalSales = prevMonthAllDeals.length;
    const prevMonthTotalRevenue = prevMonthAllDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    // Prev month MTD (same day cutoff)
    const prevMonthMtdDeals = prevMonthAllDeals.filter(d => {
        const sDate = d.SaleDate || d.DealDate;
        if (!sDate) return false;
        const dt = excelToJSDate(sDate);
        return dt && dt.getDate() <= daysElapsed;
    });
    const prevMtdSalesCount = prevMonthMtdDeals.length;
    const prevMtdRevenue = prevMonthMtdDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    // Pace delta vs Prev MTD
    const paceSalesDiff = mtdSalesCount - prevMtdSalesCount;
    const paceSalesPct = prevMtdSalesCount > 0 ? Math.round((paceSalesDiff / prevMtdSalesCount) * 100) : 0;
    const paceRevDiff = mtdRevenue - prevMtdRevenue;
    const paceRevPct = prevMtdRevenue > 0 ? Math.round((paceRevDiff / prevMtdRevenue) * 100) : 0;

    return {
        curMonthName,
        curMonthPrefix,
        prevMonthName,
        curDay,
        totalDaysInMonth,
        daysElapsed,
        monthProgressPct,
        mtdSalesCount,
        mtdRevenue,
        dailyRate: dailyRate.toFixed(1),
        projectedSales,
        projectedRevenue,
        prevMtdSalesCount,
        prevMtdRevenue,
        prevMonthTotalSales,
        prevMonthTotalRevenue,
        paceSalesDiff,
        paceSalesPct,
        paceRevDiff,
        paceRevPct,
        asOfDateStr: `${daysElapsed} ${curMonthName.toLowerCase()} ${curYear}`
    };
}

function renderPaceCardHTML(p) {
    const isAhead = p.paceSalesPct >= 0;
    const deltaColor = isAhead ? 'text-emerald-600' : 'text-rose-600';
    const deltaBg = isAhead ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200';
    const deltaIcon = isAhead ? '▲ +' : '▼ ';

    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title & Badge -->
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg">
                            ⏱️
                        </div>
                        <div>
                            <h3 class="font-black text-slate-800 text-base">Темп месяца (Pace / Run-Rate)</h3>
                            <p class="text-xs text-slate-400">Прогноз закрытия ${p.curMonthName} на базе суточного темпа</p>
                        </div>
                    </div>
                    <span class="text-xs px-2.5 py-1 rounded-full font-black border ${deltaBg} ${deltaColor}">
                        ${deltaIcon}${Math.abs(p.paceSalesPct)}% к MTD ${p.prevMonthName}
                    </span>
                </div>

                <!-- Calendar Progress Bar -->
                <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-100 mb-4">
                    <div class="flex justify-between items-center text-xs mb-1.5 font-bold">
                        <span class="text-slate-600">День ${p.daysElapsed} из ${p.totalDaysInMonth} (${p.curMonthName})</span>
                        <span class="text-indigo-600">${p.monthProgressPct}% месяца позади</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-500" style="width: ${p.monthProgressPct}%"></div>
                    </div>
                </div>

                <!-- 4 KPI Metrics Grid -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                    <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-center">
                        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Факт MTD</div>
                        <div class="text-2xl font-black text-slate-800 mt-1">${fmtNum(p.mtdSalesCount)}</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">${fmtRub(p.mtdRevenue)}</div>
                    </div>
                    <div class="bg-blue-50/60 p-3 rounded-2xl border border-blue-100 text-center">
                        <div class="text-[11px] font-bold text-blue-600 uppercase tracking-wider">Темп / день</div>
                        <div class="text-2xl font-black text-blue-700 mt-1">${p.dailyRate}</div>
                        <div class="text-[10px] text-blue-500 mt-0.5">сделок/сут.</div>
                    </div>
                    <div class="bg-indigo-50/60 p-3 rounded-2xl border border-indigo-100 text-center">
                        <div class="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">Прогноз Run-Rate</div>
                        <div class="text-2xl font-black text-indigo-700 mt-1">${fmtNum(p.projectedSales)}</div>
                        <div class="text-[10px] text-indigo-500 mt-0.5">${fmtRub(p.projectedRevenue)}</div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-center">
                        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Бенчмарк MTD</div>
                        <div class="text-2xl font-black text-slate-700 mt-1">${fmtNum(p.prevMtdSalesCount)}</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">MTD ${p.prevMonthName}</div>
                    </div>
                </div>
            </div>

            <!-- Insight Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5">
                    <i data-lucide="info" class="w-3.5 h-3.5 text-slate-400"></i>
                    Весь ${p.prevMonthName}: <b>${fmtNum(p.prevMonthTotalSales)} сделок</b> (${fmtRub(p.prevMonthTotalRevenue)})
                </span>
                <span class="font-bold ${p.projectedSales >= p.prevMonthTotalSales ? 'text-emerald-600' : 'text-amber-600'}">
                    ${p.projectedSales >= p.prevMonthTotalSales ? '🎯 Идем выше прошлого месяца' : '⚠️ Отстаем от итога прошлого месяца'}
                </span>
            </div>
        </div>
    `;
}

/**
 * =========================================================================
 * BLOCK 2: ALERTS RADAR (РАДАР КРИТИЧЕСКИХ ОТКЛОНЕНИЙ)
 * =========================================================================
 */
function calculateAlertsRadar(allDb, pDb) {
    const deals = allDb || [];

    // Find latest month and prev month
    let maxSaleDate = null;
    deals.forEach(d => {
        const sDate = d.SaleDate || d.DealDate;
        if (sDate) {
            const dt = excelToJSDate(sDate);
            if (dt && (!maxSaleDate || dt > maxSaleDate)) maxSaleDate = dt;
        }
    });

    const refDate = maxSaleDate || new Date();
    const curYear = refDate.getFullYear();
    const curMonthIdx = refDate.getMonth();
    const curDay = refDate.getDate();

    const curMonthPrefix = `${curYear}-${String(curMonthIdx + 1).padStart(2, '0')}`;
    const prevMonthIdx = curMonthIdx === 0 ? 11 : curMonthIdx - 1;
    const prevYear = curMonthIdx === 0 ? curYear - 1 : curYear;
    const prevMonthPrefix = `${prevYear}-${String(prevMonthIdx + 1).padStart(2, '0')}`;

    // 1. BRAND CRITICAL DROPS (Aug MTD vs Sept MTD)
    const curMonthDeals = deals.filter(d => (d.SaleMonth || '').replace(/'/g, '') === curMonthPrefix);
    const prevMonthMtdDeals = deals.filter(d => {
        if ((d.SaleMonth || '').replace(/'/g, '') !== prevMonthPrefix) return false;
        const sDate = d.SaleDate || d.DealDate;
        if (!sDate) return false;
        const dt = excelToJSDate(sDate);
        return dt && dt.getDate() <= curDay;
    });

    const brandCur = {}, brandPrev = {};
    curMonthDeals.forEach(d => {
        const b = d.Brand || 'Другие';
        brandCur[b] = (brandCur[b] || 0) + 1;
    });
    prevMonthMtdDeals.forEach(d => {
        const b = d.Brand || 'Другие';
        brandPrev[b] = (brandPrev[b] || 0) + 1;
    });

    const brandAlerts = [];
    Object.keys(brandPrev).forEach(b => {
        const prevCnt = brandPrev[b];
        if (prevCnt >= 3) {
            const curCnt = brandCur[b] || 0;
            const diff = curCnt - prevCnt;
            const pct = Math.round((diff / prevCnt) * 100);
            if (pct <= -15) {
                brandAlerts.push({
                    brand: b,
                    prevCnt,
                    curCnt,
                    diff,
                    pct,
                    severity: curCnt === 0 ? 'critical' : 'warning'
                });
            }
        }
    });
    brandAlerts.sort((a, b) => a.pct - b.pct);

    // 2. DEALERS CHURN RISK (Active in prev month >= 3 deals, but 0 in cur month)
    const prevMonthAllDeals = deals.filter(d => (d.SaleMonth || '').replace(/'/g, '') === prevMonthPrefix);
    const dealerPrevFull = {}, dealerCurFull = {};

    prevMonthAllDeals.forEach(d => {
        const p = d.LegalPartner || d.Partner || 'Неизвестный партнер';
        dealerPrevFull[p] = (dealerPrevFull[p] || 0) + 1;
    });
    curMonthDeals.forEach(d => {
        const p = d.LegalPartner || d.Partner || 'Неизвестный партнер';
        dealerCurFull[p] = (dealerCurFull[p] || 0) + 1;
    });

    const dealerAlerts = [];
    Object.keys(dealerPrevFull).forEach(p => {
        const prevDeals = dealerPrevFull[p];
        const curDeals = dealerCurFull[p] || 0;
        if (prevDeals >= 3 && curDeals === 0) {
            dealerAlerts.push({
                partner: p,
                prevDeals,
                curDeals: 0,
                status: '0 сделок в сентябре'
            });
        }
    });
    dealerAlerts.sort((a, b) => b.prevDeals - a.prevDeals);

    // 3. STUCK PREPAYMENTS (> 14 days without sale)
    const prepays = pDb || deals.filter(d => d.Status === 'Внесение аванса' || d.Status === 'Аванс');
    const stuckPrepays = [];
    prepays.forEach(p => {
        const sDate = p.SaleDate || p.DealDate;
        if (p.PrepayDate && (!sDate || p.Status !== 'Сделка закрыта')) {
            const dt = excelToJSDate(p.PrepayDate);
            if (dt) {
                const diffDays = Math.round((refDate - dt) / (1000 * 60 * 60 * 24));
                if (diffDays > 14) {
                    stuckPrepays.push({
                        partner: p.LegalPartner || p.Partner || 'Неизвестный партнер',
                        brand: p.Brand || '—',
                        days: diffDays,
                        price: p.Price || 0,
                        dateStr: dt.toLocaleDateString('ru-RU')
                    });
                }
            }
        }
    });
    stuckPrepays.sort((a, b) => b.days - a.days);

    return {
        brandAlerts,
        dealerAlerts,
        stuckPrepays,
        totalCriticalCount: brandAlerts.length + dealerAlerts.length + (stuckPrepays.length > 0 ? 1 : 0)
    };
}

function switchAlertTab(tabName) {
    activeAlertTab = tabName;
    const brandContent = document.getElementById('alertContentBrands');
    const dealerContent = document.getElementById('alertContentDealers');
    const prepayContent = document.getElementById('alertContentPrepays');

    const bBtn = document.getElementById('alertTabBtnBrands');
    const dBtn = document.getElementById('alertTabBtnDealers');
    const pBtn = document.getElementById('alertTabBtnPrepays');

    if (brandContent) brandContent.classList.toggle('hidden', tabName !== 'brands');
    if (dealerContent) dealerContent.classList.toggle('hidden', tabName !== 'dealers');
    if (prepayContent) prepayContent.classList.toggle('hidden', tabName !== 'prepays');

    const activeClass = 'bg-slate-900 text-white shadow-sm';
    const inactiveClass = 'bg-slate-100 text-slate-600 hover:bg-slate-200';

    if (bBtn) bBtn.className = `px-3 py-1 text-xs font-bold rounded-xl transition ${tabName === 'brands' ? activeClass : inactiveClass}`;
    if (dBtn) dBtn.className = `px-3 py-1 text-xs font-bold rounded-xl transition ${tabName === 'dealers' ? activeClass : inactiveClass}`;
    if (pBtn) pBtn.className = `px-3 py-1 text-xs font-bold rounded-xl transition ${tabName === 'prepays' ? activeClass : inactiveClass}`;
}

function renderAlertsRadarCardHTML(a) {
    const hasCrit = a.totalCriticalCount > 0;

    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title & Tabs -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg">
                            🚨
                        </div>
                        <div>
                            <h3 class="font-black text-slate-800 text-base">Радар отклонений (Alerts Radar)</h3>
                            <p class="text-xs text-slate-400">Автоматический мониторинг сигналов риска</p>
                        </div>
                    </div>
                    <!-- Pill Buttons -->
                    <div class="flex items-center gap-1.5 p-1 bg-slate-50 rounded-2xl border border-slate-100">
                        <button id="alertTabBtnBrands" onclick="switchAlertTab('brands')" class="px-3 py-1 text-xs font-bold rounded-xl transition bg-slate-900 text-white shadow-sm">
                            Бренды (${a.brandAlerts.length})
                        </button>
                        <button id="alertTabBtnDealers" onclick="switchAlertTab('dealers')" class="px-3 py-1 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-600 hover:bg-slate-200">
                            Отвал ДЦ (${a.dealerAlerts.length})
                        </button>
                        <button id="alertTabBtnPrepays" onclick="switchAlertTab('prepays')" class="px-3 py-1 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-600 hover:bg-slate-200">
                            Авансы (${a.stuckPrepays.length})
                        </button>
                    </div>
                </div>

                <!-- TAB 1: BRANDS DROP -->
                <div id="alertContentBrands" class="space-y-2 mb-4">
                    ${a.brandAlerts.length === 0 ? `
                        <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                            🟢 Критических просадок по маркам не зафиксировано
                        </div>
                    ` : a.brandAlerts.slice(0, 4).map(b => `
                        <div class="flex items-center justify-between p-2.5 rounded-2xl ${b.severity === 'critical' ? 'bg-rose-50 border border-rose-100' : 'bg-amber-50 border border-amber-100'}">
                            <div class="flex items-center gap-2.5">
                                <span class="text-xs font-black ${b.severity === 'critical' ? 'text-rose-700' : 'text-amber-800'}">${b.brand}</span>
                                <span class="text-[11px] text-slate-500">Факт: <b>${b.curCnt}</b> шт. (было ${b.prevCnt} в авг. MTD)</span>
                            </div>
                            <span class="text-xs px-2 py-0.5 rounded-full font-black ${b.severity === 'critical' ? 'bg-rose-200 text-rose-800' : 'bg-amber-200 text-amber-800'}">
                                ${b.pct}%
                            </span>
                        </div>
                    `).join('')}
                </div>

                <!-- TAB 2: DEALERS CHURN RISK -->
                <div id="alertContentDealers" class="hidden space-y-2 mb-4">
                    ${a.dealerAlerts.length === 0 ? `
                        <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                            🟢 Все ключевые партнеры проявляют активность
                        </div>
                    ` : a.dealerAlerts.slice(0, 4).map(d => `
                        <div class="flex items-center justify-between p-2.5 rounded-2xl bg-slate-50 border border-slate-200/70">
                            <div class="min-w-0 pr-2">
                                <div class="text-xs font-black text-slate-800 truncate">${d.partner}</div>
                                <div class="text-[11px] text-slate-500 mt-0.5">В августе: <b>${d.prevDeals} сделок</b></div>
                            </div>
                            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-rose-100 text-rose-700 border border-rose-200 whitespace-nowrap">
                                0 в сентябре ⚠️
                            </span>
                        </div>
                    `).join('')}
                </div>

                <!-- TAB 3: STUCK PREPAYMENTS -->
                <div id="alertContentPrepays" class="hidden space-y-2 mb-4">
                    ${a.stuckPrepays.length === 0 ? `
                        <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                            🟢 Зависших авансов (>14 дней) не обнаружено
                        </div>
                    ` : a.stuckPrepays.slice(0, 4).map(p => `
                        <div class="flex items-center justify-between p-2.5 rounded-2xl bg-amber-50/70 border border-amber-200/70">
                            <div class="min-w-0 pr-2">
                                <div class="text-xs font-black text-slate-800 truncate">${p.partner} • ${p.brand}</div>
                                <div class="text-[11px] text-slate-500 mt-0.5">Аванс от ${p.dateStr} (${p.days} дней назад)</div>
                            </div>
                            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-200 text-amber-900 whitespace-nowrap">
                                ${p.days} дн. завис
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5">
                    <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-500"></i>
                    Всего сигналов риска: <b>${a.totalCriticalCount}</b>
                </span>
                <span class="text-slate-400">Требуется реакция КАМ-менеджеров</span>
            </div>
        </div>
    `;
}

/**
 * =========================================================================
 * BLOCK 3: MARGIN & ARPU UNIT ECONOMICS
 * =========================================================================
 */
function calculateChannelUnitEconomics(sDb) {
    const deals = sDb || [];
    const totalDeals = deals.length;
    const totalRev = deals.reduce((s, d) => s + (d.Revenue || 0), 0);

    const channels = {
        'Опт МП2': { name: 'Опт МП2', deals: 0, revenue: 0, totalPrice: 0 },
        'Розница': { name: 'Розница (B2C)', deals: 0, revenue: 0, totalPrice: 0 },
        'Online': { name: 'Online продажи', deals: 0, revenue: 0, totalPrice: 0 },
        'Прочие': { name: 'Прочие каналы', deals: 0, revenue: 0, totalPrice: 0 }
    };

    deals.forEach(d => {
        const type = (d.DealType || '').toLowerCase();
        const pName = (d.Partner || d.LegalPartner || '').toLowerCase();
        const rev = d.Revenue || 0;
        const pr = d.Price || 0;

        let ch = 'Прочие';
        if (type.includes('мп2') || type.includes('маркетплейс 2') || type.includes('b2b')) {
            ch = 'Опт МП2';
        } else if (type.includes('онлайн') || type.includes('online') || pName.includes('online')) {
            ch = 'Online';
        } else if (type.includes('розниц') || type.includes('b2c') || type.includes('договор')) {
            ch = 'Розница';
        } else {
            ch = 'Опт МП2'; // Majority of non-retail in this dataset is wholesale MP2
        }

        channels[ch].deals += 1;
        channels[ch].revenue += rev;
        channels[ch].totalPrice += pr;
    });

    const rows = Object.values(channels).map(c => {
        const shareDeals = totalDeals > 0 ? Math.round((c.deals / totalDeals) * 100) : 0;
        const shareRev = totalRev > 0 ? Math.round((c.revenue / totalRev) * 100) : 0;
        const arpu = c.deals > 0 ? Math.round(c.revenue / c.deals) : 0;
        const avgCheck = c.deals > 0 ? Math.round(c.totalPrice / c.deals) : 0;
        const takeRate = c.totalPrice > 0 ? ((c.revenue / c.totalPrice) * 100).toFixed(2) : '0.00';

        return {
            ...c,
            shareDeals,
            shareRev,
            arpu,
            avgCheck,
            takeRate
        };
    }).sort((a, b) => b.revenue - a.revenue);

    return {
        rows,
        totalDeals,
        totalRev,
        overallArpu: totalDeals > 0 ? Math.round(totalRev / totalDeals) : 0
    };
}

function renderMarginCardHTML(m) {
    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title & ARPU Badge -->
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">
                            💰
                        </div>
                        <div>
                            <h3 class="font-black text-slate-800 text-base">Доходность и юнит-экономика (ARPU)</h3>
                            <p class="text-xs text-slate-400">Сравнение комиссионных доходов и чека по каналам</p>
                        </div>
                    </div>
                    <span class="text-xs px-2.5 py-1 rounded-full font-black bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Средний ARPU: ${fmtNum(m.overallArpu)} ₽
                    </span>
                </div>

                <!-- Channels Table -->
                <div class="overflow-x-auto mb-4">
                    <table class="min-w-full text-xs">
                        <thead>
                            <tr class="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                                <th class="text-left py-2">Канал</th>
                                <th class="text-right py-2">Сделки (% шт)</th>
                                <th class="text-right py-2">Выручка (% денег)</th>
                                <th class="text-right py-2">ARPU (доход/шт)</th>
                                <th class="text-right py-2">Take-rate</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 font-medium">
                            ${m.rows.map(r => `
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="py-2.5 text-slate-800 font-black flex items-center gap-1.5">
                                        <span class="w-2 h-2 rounded-full ${r.name.includes('Опт') ? 'bg-blue-500' : r.name.includes('Розница') ? 'bg-emerald-500' : 'bg-indigo-500'}"></span>
                                        ${r.name}
                                    </td>
                                    <td class="py-2.5 text-right text-slate-700">
                                        <b>${fmtNum(r.deals)}</b> <span class="text-slate-400 text-[11px]">(${r.shareDeals}%)</span>
                                    </td>
                                    <td class="py-2.5 text-right text-slate-800">
                                        <b>${fmtRub(r.revenue)}</b> <span class="text-slate-400 text-[11px]">(${r.shareRev}%)</span>
                                    </td>
                                    <td class="py-2.5 text-right font-black text-emerald-700">
                                        ${fmtNum(r.arpu)} ₽
                                    </td>
                                    <td class="py-2.5 text-right font-bold text-slate-600">
                                        ${r.takeRate}%
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Insight Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5">
                    <i data-lucide="trending-up" class="w-3.5 h-3.5 text-emerald-600"></i>
                    Розница дает максимальный ARPU, а Опт МП2 обеспечивает базовый объем
                </span>
                <span class="font-bold text-indigo-600">Комиссия без НДС</span>
            </div>
        </div>
    `;
}

/**
 * =========================================================================
 * BLOCK 4: PARTNER HEALTH SCORE MATRIX (МАТРИЦА ЭФФЕКТИВНОСТИ СЕТИ)
 * =========================================================================
 */
function calculatePartnerHealthScore(sDb, allPartners) {
    const deals = sDb || [];
    const partnersMap = {};

    deals.forEach(d => {
        const p = d.LegalPartner || d.Partner || 'Неизвестный партнер';
        if (!partnersMap[p]) {
            partnersMap[p] = {
                partner: p,
                deals: 0,
                revenue: 0,
                totalPrice: 0,
                leads: 0,
                transfers: 0
            };
        }
        partnersMap[p].deals += 1;
        partnersMap[p].revenue += (d.Revenue || 0);
        partnersMap[p].totalPrice += (d.Price || 0);
    });

    const list = Object.values(partnersMap);
    if (list.length === 0) {
        return {
            stars: [],
            growth: [],
            niche: [],
            risk: [],
            totalPartners: 0
        };
    }

    // Compute medians
    const sortedDeals = list.map(p => p.deals).sort((a, b) => a - b);
    const medianDeals = sortedDeals[Math.floor(sortedDeals.length / 2)] || 1;
    const avgArpu = list.reduce((s, p) => s + (p.revenue / (p.deals || 1)), 0) / list.length;

    const stars = [];
    const growth = [];
    const niche = [];
    const risk = [];

    list.forEach(p => {
        const arpu = p.deals > 0 ? (p.revenue / p.deals) : 0;
        const isHighVolume = p.deals >= Math.max(3, medianDeals);
        const isHighYield = arpu >= avgArpu;

        if (isHighVolume && isHighYield) {
            stars.push(p);
        } else if (isHighVolume && !isHighYield) {
            growth.push(p);
        } else if (!isHighVolume && isHighYield) {
            niche.push(p);
        } else {
            risk.push(p);
        }
    });

    stars.sort((a, b) => b.revenue - a.revenue);
    growth.sort((a, b) => b.deals - a.deals);
    niche.sort((a, b) => b.revenue - a.revenue);
    risk.sort((a, b) => b.deals - a.deals);

    return {
        stars,
        growth,
        niche,
        risk,
        totalPartners: list.length
    };
}

function renderHealthScoreCardHTML(h) {
    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title -->
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-lg">
                            📊
                        </div>
                        <div>
                            <h3 class="font-black text-slate-800 text-base">Матрица дилеров (Partner Health Score)</h3>
                            <p class="text-xs text-slate-400">Сегментация ${h.totalPartners} активных ДЦ по объему и доходности</p>
                        </div>
                    </div>
                    <span class="text-xs px-2.5 py-1 rounded-full font-black bg-purple-50 text-purple-700 border border-purple-200">
                        4 квадранта КАМ
                    </span>
                </div>

                <!-- 4 Quadrants Grid -->
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <!-- Quadrant 1: Stars -->
                    <div class="p-3.5 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200/80">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-emerald-800 flex items-center gap-1">🌟 Локомотивы</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900">${h.stars.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-emerald-700 mt-1">Высокий объем + высокий ARPU</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate">
                            Топ: ${h.stars[0] ? h.stars[0].partner : '—'}
                        </div>
                    </div>

                    <!-- Quadrant 2: Growth Potential -->
                    <div class="p-3.5 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200/80">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-blue-800 flex items-center gap-1">🚀 Точки роста</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-blue-200 text-blue-900">${h.growth.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-blue-700 mt-1">Высокий объем, резерв по ARPU</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate">
                            Топ: ${h.growth[0] ? h.growth[0].partner : '—'}
                        </div>
                    </div>

                    <!-- Quadrant 3: Specialized / Niche -->
                    <div class="p-3.5 rounded-2xl bg-gradient-to-br from-purple-50 to-fuchsia-50 border border-purple-200/80">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-purple-800 flex items-center gap-1">💼 Нишевые</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-purple-200 text-purple-900">${h.niche.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-purple-700 mt-1">Штучные сделки с высоким чеком</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate">
                            Топ: ${h.niche[0] ? h.niche[0].partner : '—'}
                        </div>
                    </div>

                    <!-- Quadrant 4: At Risk -->
                    <div class="p-3.5 rounded-2xl bg-gradient-to-br from-amber-50 to-rose-50 border border-amber-200/80">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-amber-800 flex items-center gap-1">⚠️ Зона риска</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-amber-200 text-amber-900">${h.risk.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-amber-700 mt-1">Мало сделок и низкая маржинальность</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate">
                            ${h.risk.length} ДЦ требуют ревизии условий
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5">
                    <i data-lucide="users" class="w-3.5 h-3.5 text-purple-600"></i>
                    Фокус внимания КАМ: <b>«Точки роста»</b> для допродажи услуг
                </span>
                <span class="text-slate-400">Автоматическая матрица</span>
            </div>
        </div>
    `;
}
