/**
 * executive-dashboard.js
 * =======================
 * Управленческая аналитическая панель (Executive Analytics):
 * 1. Темп месяца (Pace / Run-Rate Tracker) — с динамической адаптацией к выбранному фильтру
 * 2. Радар критических отклонений (Alerts Radar) — просадки брендов, отвал ДЦ и зависшие авансы
 * 3. Доходность и юнит-экономика каналов (Margin & ARPU) — честная классификация по d.B2C
 * 4. Матрица эффективности дилерской сети (Partner Health Score) — 4 квадранта, фильтры по КАМ, детальный модал и экспорт в Excel
 */

let activeAlertTab = 'growth_brands'; // 'growth_brands' | 'brands' | 'growth_dealers' | 'dealers' | 'prepays'
let activeAlertChannel = 'all'; // 'all' | 'opt' | 'retail'
let activeHealthQuadrant = 'all'; // 'all' | 'stars' | 'growth' | 'niche' | 'risk'

const ALERT_CHANNELS = [
    { key: 'all', label: 'Все каналы' },
    { key: 'opt', label: 'Опт МП2' },
    { key: 'retail', label: 'Розница (ФДЦ, B2C, Online, Прочие)' }
];

function getAlertDealChannelKey(b2c) {
    const raw = (b2c || '').toString().trim().toLowerCase();
    if (raw.includes('мп2') || raw === 'мп 2') return 'opt';
    return 'retail';
}

function canonicalPartnerName(name) {
    if (!name) return 'Неизвестный партнер';
    let s = name.trim();
    const low = s.toLowerCase();
    
    // Диалог Авто (Казань, Альметьевск, Набережные Челны)
    if (low.includes('диалог')) return 'Диалог Авто';
    
    // Башавтоком / Чанган Центр
    if (low.includes('башавтоком') || low.includes('чанган центр') || low.includes('changan центр')) return 'Башавтоком / Чанган Центр';
    
    // ГК Арконт Холдинг
    if (low.includes('арконт')) return 'ГК Арконт Холдинг';
    
    // Планета Авто
    if (low.includes('планета авто') || low.includes('планета-авто') || low.includes('чери центр планета авто восток')) return 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК';

    // ГК Сильвер
    if (low.includes('сильвер')) return 'ГК Сильвер';
    
    // АвтоМаркет Jetour
    if (low.includes('автомаркет')) return 'АвтоМаркет Jetour';
    
    // Автомир Симферополь vs Автомир
    if (low.includes('автомир') && (low.includes('симферополь') || low.includes('крым'))) return 'Автомир (Симферополь)';
    
    // Олимп (Темп Авто Кубань)
    if (low.includes('олимп')) return 'Олимп (Кубань)';
    
    // ФДЦ Автосеть АМК РФ
    if ((low.includes('автосеть') && (low.includes('амк') || low.includes('пилот'))) || (low.includes('амк') && !low.includes('амкапитал') && !low.includes('ам капитал') && !low.includes('автомир'))) return 'ФДЦ Автосеть АМК РФ';

    // Автосеть РФ / Апельсин
    if (low.includes('апельсин')) return 'Апельсин (Автосеть РФ)';
    
    // Дебрянск Авто (БН-Моторс)
    if (low.includes('дебрянск') || low.includes('бн-моторс') || low.includes('бн моторс') || low.includes('бнм')) return 'Дебрянск Авто';

    // Юг-Авто (Краснодар) vs АвтоЮг (Ставрополь)
    if (low.includes('юг-авто') || low.includes('юг авто') || low.includes('ак «юг-авто»') || low.includes('дц юг-авто')) return 'Юг-Авто';
    if (low.includes('автоюг')) return 'АвтоЮг';

    // ААА Моторс (Ростов-на-Дону) vs Артекс
    if (low.includes('ааа моторс') || low.includes('ааа-моторс') || low.includes('формула-н') || low.includes('формула н')) return 'ААА Моторс';
    if (low.includes('артекс')) return 'Артекс';
    
    // Восток Моторс
    if (low.includes('восток моторс') || low.includes('восток-моторс')) return 'ООО "ВОСТОК МОТОРС" ONLINE';
    
    // Эксперт Авто (Новосибирск vs Оренбург vs Самара)
    if (low.includes('эксперт') && (low.includes('новосибирск') || low.includes('нск'))) return 'Эксперт Авто (Новосибирск)';
    if (low.includes('эксперт') && (low.includes('оренбург') || low.includes('эксперт св'))) return 'Эксперт Авто (Оренбург)';
    
    // Автопрестиж
    if (low.includes('автопрестиж')) return 'ГК Автопрестиж';

    // Нижегородец
    if (low.includes('нижегородец')) return 'Нижегородец';

    return s;
}

function isAutomotiveBrand(b) {
    if (!b) return false;
    const bNorm = b.trim();
    if (!bNorm || bNorm === 'Другие' || bNorm === 'NONE' || bNorm === '—') return false;
    const lower = bNorm.toLowerCase();
    if (lower.includes('бронир') || lower.includes('бронь') || lower.includes('услуг') || 
        lower.includes('страх') || lower.includes('доп') || lower.includes('аванс') || 
        lower.includes('комисс') || lower.includes('кредит') || lower.includes('каско') || 
        lower.includes('осаго') || lower.includes('договор')) {
        return false;
    }
    return true;
}

/**
 * Main render function called from data-loader.js updateAllTabs()
 */
function renderExecutiveDashboard(sDb, pDb, allDb, allPartners, filterConfig, debtorsList) {
    const container = document.getElementById('executiveDashboardContainer');
    if (!container) return;

    const actualDebtors = debtorsList || window.rawDebtorsList || (window.currentData && window.currentData.debtors) || [];

    // 1. Calculate Pace / Run-rate metrics with dynamic filter support
    const paceData = calculatePaceMetrics(sDb, allDb, filterConfig);

    // 2. Calculate Alerts Radar
    const alertData = calculateAlertsRadar(allDb, pDb, allPartners || [], filterConfig, actualDebtors);

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
                        <div class="text-xs text-slate-400">Срез аналитики</div>
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

    // Ensure Health Matrix modal exists in the DOM
    ensureHealthModalExists();

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
function calculatePaceMetrics(sDb, allDb, filterConfig) {
    const deals = allDb || [];
    const salesOnly = deals.filter(d => (d.SaleQty > 0) || (d.SaleMonth && d.SaleMonth.length > 0));

    // Find the latest sale date in dataset
    let globalMaxSaleDate = null;
    salesOnly.forEach(d => {
        const sDate = d.SaleDate || d.DealDate;
        if (sDate) {
            const dt = excelToJSDate(sDate);
            if (dt && (!globalMaxSaleDate || dt > globalMaxSaleDate)) {
                globalMaxSaleDate = dt;
            }
        }
    });

    const latestYear = globalMaxSaleDate ? globalMaxSaleDate.getFullYear() : 2026;
    const latestMonthIdx = globalMaxSaleDate ? globalMaxSaleDate.getMonth() : 8;
    const latestDay = globalMaxSaleDate ? globalMaxSaleDate.getDate() : 10;

    let targetYear = latestYear;
    let targetMonthIdx = latestMonthIdx;

    if (filterConfig && filterConfig.mode === 'month' && filterConfig.month) {
        const parts = filterConfig.month.split('-');
        targetYear = parseInt(parts[0]);
        targetMonthIdx = parseInt(parts[1]) - 1;
    }

    const monthNames = ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"];
    const curMonthName = monthNames[targetMonthIdx];
    const totalDaysInMonth = new Date(targetYear, targetMonthIdx + 1, 0).getDate();
    const isLatestActiveMonth = (targetYear === latestYear && targetMonthIdx === latestMonthIdx);

    const daysElapsed = isLatestActiveMonth ? Math.min(latestDay, totalDaysInMonth) : totalDaysInMonth;
    const isClosedMonth = !isLatestActiveMonth;
    const monthProgressPct = Math.round((daysElapsed / totalDaysInMonth) * 100);

    const curMonthPrefix = `${targetYear}-${String(targetMonthIdx + 1).padStart(2, '0')}`;
    const curMonthDeals = salesOnly.filter(d => (d.SaleMonth || '').replace(/'/g, '') === curMonthPrefix);
    const mtdSalesCount = curMonthDeals.length;
    const mtdRevenue = curMonthDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    const dailyRate = daysElapsed > 0 ? (mtdSalesCount / daysElapsed) : 0;
    const projectedSales = isClosedMonth ? mtdSalesCount : Math.round(dailyRate * totalDaysInMonth);
    const projectedRevenue = isClosedMonth ? mtdRevenue : (daysElapsed > 0 ? Math.round((mtdRevenue / daysElapsed) * totalDaysInMonth) : 0);

    // Benchmark comparison (previous month)
    const prevMonthIdx = targetMonthIdx === 0 ? 11 : targetMonthIdx - 1;
    const prevYear = targetMonthIdx === 0 ? targetYear - 1 : targetYear;
    const prevMonthPrefix = `${prevYear}-${String(prevMonthIdx + 1).padStart(2, '0')}`;
    const prevMonthName = monthNames[prevMonthIdx];

    const prevMonthAllDeals = salesOnly.filter(d => (d.SaleMonth || '').replace(/'/g, '') === prevMonthPrefix);
    const prevMonthTotalSales = prevMonthAllDeals.length;
    const prevMonthTotalRevenue = prevMonthAllDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    const prevMtdDeals = prevMonthAllDeals.filter(d => {
        if (isClosedMonth) return true;
        const sDate = d.SaleDate || d.DealDate;
        if (!sDate) return false;
        const dt = excelToJSDate(sDate);
        return dt && dt.getDate() <= daysElapsed;
    });

    const prevMtdSalesCount = prevMtdDeals.length;
    const prevMtdRevenue = prevMtdDeals.reduce((sum, d) => sum + (d.Revenue || 0), 0);

    const paceSalesDiff = mtdSalesCount - prevMtdSalesCount;
    const paceSalesPct = prevMtdSalesCount > 0 ? Math.round((paceSalesDiff / prevMtdSalesCount) * 100) : 0;
    const paceRevDiff = mtdRevenue - prevMtdRevenue;
    const paceRevPct = prevMtdRevenue > 0 ? Math.round((paceRevDiff / prevMtdRevenue) * 100) : 0;

    return {
        curMonthName,
        curMonthPrefix,
        prevMonthName,
        targetYear,
        daysElapsed,
        totalDaysInMonth,
        monthProgressPct,
        isClosedMonth,
        isLatestActiveMonth,
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
        asOfDateStr: isClosedMonth ? `Итоги за ${curMonthName} ${targetYear}` : `${daysElapsed} ${curMonthName.toLowerCase()} ${targetYear}`
    };
}

function renderPaceCardHTML(p) {
    const isAhead = p.paceSalesPct >= 0;
    const deltaColor = isAhead ? 'text-emerald-600' : 'text-rose-600';
    const deltaBg = isAhead ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200';
    const deltaIcon = isAhead ? '▲ +' : '▼ ';

    const benchmarkLabel = p.isClosedMonth ? `к ${p.prevMonthName}` : `к MTD ${p.prevMonthName}`;
    const cardSubtitle = p.isClosedMonth 
        ? `Итоги закрытия за ${p.curMonthName} и сравнение с ${p.prevMonthName}`
        : `Прогноз закрытия ${p.curMonthName} на базе суточного темпа`;

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
                            <p class="text-xs text-slate-400">${cardSubtitle}</p>
                        </div>
                    </div>
                    <span class="text-xs px-2.5 py-1 rounded-full font-black border ${deltaBg} ${deltaColor}">
                        ${deltaIcon}${Math.abs(p.paceSalesPct)}% ${benchmarkLabel}
                    </span>
                </div>

                <!-- Calendar Progress Bar -->
                <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-100 mb-4">
                    <div class="flex justify-between items-center text-xs mb-1.5 font-bold">
                        <span class="text-slate-600">
                            ${p.isClosedMonth ? `Месяц завершен (${p.totalDaysInMonth} дней)` : `День ${p.daysElapsed} из ${p.totalDaysInMonth} (${p.curMonthName})`}
                        </span>
                        <span class="text-indigo-600">${p.monthProgressPct}% ${p.isClosedMonth ? 'итог' : 'месяца позади'}</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-500" style="width: ${p.monthProgressPct}%"></div>
                    </div>
                </div>

                <!-- 4 KPI Metrics Grid -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                    <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-center">
                        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                            ${p.isClosedMonth ? 'Факт месяца' : 'Факт MTD'}
                        </div>
                        <div class="text-2xl font-black text-slate-800 mt-1">${fmtNum(p.mtdSalesCount)}</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">${fmtRub(p.mtdRevenue)}</div>
                    </div>
                    <div class="bg-blue-50/60 p-3 rounded-2xl border border-blue-100 text-center">
                        <div class="text-[11px] font-bold text-blue-600 uppercase tracking-wider">
                            ${p.isClosedMonth ? 'Среднесут.' : 'Темп / день'}
                        </div>
                        <div class="text-2xl font-black text-blue-700 mt-1">${p.dailyRate}</div>
                        <div class="text-[10px] text-blue-500 mt-0.5">сделок/сут.</div>
                    </div>
                    <div class="bg-indigo-50/60 p-3 rounded-2xl border border-indigo-100 text-center">
                        <div class="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                            ${p.isClosedMonth ? 'Итог факта' : 'Прогноз Run-Rate'}
                        </div>
                        <div class="text-2xl font-black text-indigo-700 mt-1">${fmtNum(p.projectedSales)}</div>
                        <div class="text-[10px] text-indigo-500 mt-0.5">${fmtRub(p.projectedRevenue)}</div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-center">
                        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                            ${p.isClosedMonth ? 'Прошлый месяц' : 'Бенчмарк MTD'}
                        </div>
                        <div class="text-2xl font-black text-slate-700 mt-1">${fmtNum(p.prevMtdSalesCount)}</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">${p.prevMonthName}</div>
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
                    ${p.projectedSales >= p.prevMonthTotalSales ? '🎯 Выше прошлого месяца' : '⚠️ Отстаем от прошлого месяца'}
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
function calculateAlertsRadar(allDb, pDb, allPartners, filterConfig, debtorsList) {
    const deals = allDb || [];
    const salesOnly = deals.filter(d => (d.SaleQty > 0) || (d.SaleMonth && d.SaleMonth.length > 0));

    // Global max sale date
    let globalMaxSaleDate = null;
    salesOnly.forEach(d => {
        const sDate = d.SaleDate || d.DealDate;
        if (sDate) {
            const dt = excelToJSDate(sDate);
            if (dt && (!globalMaxSaleDate || dt > globalMaxSaleDate)) globalMaxSaleDate = dt;
        }
    });

    const latestYear = globalMaxSaleDate ? globalMaxSaleDate.getFullYear() : 2026;
    const latestMonthIdx = globalMaxSaleDate ? globalMaxSaleDate.getMonth() : 8;
    const latestDay = globalMaxSaleDate ? globalMaxSaleDate.getDate() : 10;

    let targetYear = latestYear;
    let targetMonthIdx = latestMonthIdx;

    if (filterConfig && filterConfig.mode === 'month' && filterConfig.month) {
        const parts = filterConfig.month.split('-');
        targetYear = parseInt(parts[0]);
        targetMonthIdx = parseInt(parts[1]) - 1;
    }

    const monthNames = ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"];
    const curMonthName = monthNames[targetMonthIdx];
    const isLatestActiveMonth = (targetYear === latestYear && targetMonthIdx === latestMonthIdx);

    const prevMonthIdx = targetMonthIdx === 0 ? 11 : targetMonthIdx - 1;
    const prevYear = targetMonthIdx === 0 ? targetYear - 1 : targetYear;
    const prevMonthPrefix = `${prevYear}-${String(prevMonthIdx + 1).padStart(2, '0')}`;
    const prevMonthName = monthNames[prevMonthIdx];
    const curMonthPrefix = `${targetYear}-${String(targetMonthIdx + 1).padStart(2, '0')}`;

    const periodLabel = isLatestActiveMonth 
        ? `${curMonthName} (MTD ${latestDay} дн.) vs ${prevMonthName}`
        : `${curMonthName} vs ${prevMonthName}`;

    // Verified Stuck Prepayments from Debtors registry (excludes delivered cars & replaced VINs)
    const actualDebtors = debtorsList || window.rawDebtorsList || (window.currentData && window.currentData.debtors) || [];
    const allStuckPrepays = [];
    actualDebtors.forEach(d => {
        // Month filter check: include active unclosed advances up to selected period
        if (filterConfig && filterConfig.mode === 'month' && filterConfig.month) {
            let m = d.prepay_date ? d.prepay_date.split('.').reverse().slice(0, 2).join('-') : "";
            if (m && m > filterConfig.month) return;
        } else if (filterConfig && filterConfig.mode === 'custom' && filterConfig.to) {
            const tTime = filterConfig.to.getTime();
            if (d.prepay_serial && d.prepay_serial > 0) {
                const jsD = excelToJSDate(d.prepay_serial);
                if (jsD && jsD.getTime() > tTime) return;
            }
        }
        const days = (typeof d.aging_days === 'number') ? d.aging_days : (typeof getDebtorAgeDays === 'function' ? getDebtorAgeDays(d) : 0);
        if (days >= 7) {
            allStuckPrepays.push({
                partner: canonicalPartnerName(d.company || d.raw_company),
                rawPartner: d.raw_company || d.company || '',
                kam: d.kam || '—',
                brand: d.brand || '',
                model: d.model || '',
                vin: d.vin || '',
                clientId: d.client_id || '',
                dealId: d.deal_id || '',
                days: days,
                dateStr: d.prepay_date || '',
                b2c: d.b2c || '',
                channelKey: getAlertDealChannelKey(d.b2c)
            });
        }
    });
    allStuckPrepays.sort((a, b) => b.days - a.days);

    // Deals for cur and prev period
    const curMonthDeals = salesOnly.filter(d => (d.SaleMonth || '').replace(/'/g, '') === curMonthPrefix);
    const prevMonthDeals = salesOnly.filter(d => {
        if ((d.SaleMonth || '').replace(/'/g, '') !== prevMonthPrefix) return false;
        if (isLatestActiveMonth) {
            const sDate = d.SaleDate || d.DealDate;
            if (!sDate) return false;
            const dt = excelToJSDate(sDate);
            return dt && dt.getDate() <= latestDay;
        }
        return true;
    });

    const prevPartnersDeals = (allPartners || []).filter(r => {
        if (r.Type !== 'Сделка' || r.Month !== prevMonthPrefix) return false;
        if (isLatestActiveMonth && r.Date) {
            const dt = excelToJSDate(r.Date);
            return dt && dt.getDate() <= latestDay;
        }
        return true;
    });
    const curPartnersDeals = (allPartners || []).filter(r => r.Type === 'Сделка' && r.Month === curMonthPrefix);

    const channelsData = {};

    ALERT_CHANNELS.forEach(ch => {
        // 1. BRAND DYNAMICS (GROWTH & DROPS) - strictly automotive brands only
        const cCur = ch.key === 'all' ? curMonthDeals : curMonthDeals.filter(d => getAlertDealChannelKey(d.B2C) === ch.key);
        const cPrev = ch.key === 'all' ? prevMonthDeals : prevMonthDeals.filter(d => getAlertDealChannelKey(d.B2C) === ch.key);

        const bCur = {}, bPrev = {};
        cCur.forEach(d => {
            let b = (d.Brand || '').trim();
            if (b === 'SOUEAS') b = 'SOUEAST';
            if (!isAutomotiveBrand(b)) return;
            bCur[b] = (bCur[b] || 0) + 1;
        });
        cPrev.forEach(d => {
            let b = (d.Brand || '').trim();
            if (b === 'SOUEAS') b = 'SOUEAST';
            if (!isAutomotiveBrand(b)) return;
            bPrev[b] = (bPrev[b] || 0) + 1;
        });

        const allBrandKeys = new Set([...Object.keys(bCur), ...Object.keys(bPrev)]);
        const brandAlerts = [];
        const brandGrowth = [];

        allBrandKeys.forEach(b => {
            const prevCnt = bPrev[b] || 0;
            const curCnt = bCur[b] || 0;
            const diff = curCnt - prevCnt;
            const pct = prevCnt > 0 ? Math.round((diff / prevCnt) * 100) : (curCnt > 0 ? 100 : 0);

            if (diff < 0) {
                brandAlerts.push({
                    brand: b,
                    prevCnt,
                    curCnt,
                    diff,
                    pct,
                    severity: Math.abs(diff) >= 15 || pct <= -50 || curCnt === 0 ? 'critical' : 'warning'
                });
            } else if (diff > 0) {
                brandGrowth.push({
                    brand: b,
                    prevCnt,
                    curCnt,
                    diff,
                    pct,
                    isNew: prevCnt === 0,
                    significance: diff >= 10 || pct >= 50 ? 'leader' : 'normal'
                });
            }
        });
        brandAlerts.sort((a, b) => a.diff - b.diff); // largest drops first (-172, -19...)
        brandGrowth.sort((a, b) => b.diff - a.diff); // largest growth first (+44, +21...)

        // 2. DEALER DYNAMICS (CHURN RISK & GROWTH) - matching via canonicalPartnerName
        const pPrev = ch.key === 'all' ? prevPartnersDeals : prevPartnersDeals.filter(r => getAlertDealChannelKey(r.B2C) === ch.key);
        const pCur = ch.key === 'all' ? curPartnersDeals : curPartnersDeals.filter(r => getAlertDealChannelKey(r.B2C) === ch.key);

        const dPrevMap = {}, dCurMap = {};
        pPrev.forEach(r => {
            const rawName = r.Partner || 'Неизвестный партнер';
            const p = canonicalPartnerName(rawName);
            if (!dPrevMap[p]) {
                dPrevMap[p] = { partner: p, prevDeals: 0, kam: r.KAM || '—', rawPartner: r.RawPartner || rawName };
            }
            dPrevMap[p].prevDeals += (r.Qty || 1);
            if (r.KAM && dPrevMap[p].kam === '—') dPrevMap[p].kam = r.KAM;
        });

        pCur.forEach(r => {
            const rawName = r.Partner || 'Неизвестный партнер';
            const p = canonicalPartnerName(rawName);
            if (!dCurMap[p]) {
                dCurMap[p] = { partner: p, curDeals: 0, kam: r.KAM || '—', rawPartner: r.RawPartner || rawName };
            }
            dCurMap[p].curDeals += (r.Qty || 1);
            if (r.KAM && dCurMap[p].kam === '—') dCurMap[p].kam = r.KAM;
        });

        const allDealerKeys = new Set([...Object.keys(dCurMap), ...Object.keys(dPrevMap)]);
        const thresh = (ch.key === 'all' || ch.key === 'opt') ? 3 : 2;
        const dealerAlerts = [];
        const dealerGrowth = [];

        allDealerKeys.forEach(p => {
            const prevInfo = dPrevMap[p];
            const curInfo = dCurMap[p];
            const prevDeals = prevInfo ? prevInfo.prevDeals : 0;
            const curDeals = curInfo ? curInfo.curDeals : 0;
            const kam = (curInfo && curInfo.kam !== '—') ? curInfo.kam : (prevInfo ? prevInfo.kam : '—');
            const rawPartner = (curInfo && curInfo.rawPartner) ? curInfo.rawPartner : (prevInfo ? prevInfo.rawPartner : '');
            const diff = curDeals - prevDeals;

            // Churn alert: had deals >= thresh before, now 0
            if (prevDeals >= thresh && curDeals === 0) {
                dealerAlerts.push({
                    partner: p,
                    prevDeals,
                    curDeals: 0,
                    kam,
                    rawPartner,
                    severity: prevDeals >= 10 ? 'critical' : 'warning'
                });
            }

            // Dealer growth / activation
            if (diff > 0) {
                const pct = prevDeals > 0 ? Math.round((diff / prevDeals) * 100) : 100;
                dealerGrowth.push({
                    partner: p,
                    prevDeals,
                    curDeals,
                    diff,
                    pct,
                    kam,
                    rawPartner,
                    isNew: (prevDeals === 0),
                    significance: diff >= 5 || pct >= 100 ? 'leader' : 'normal'
                });
            }
        });
        dealerAlerts.sort((a, b) => b.prevDeals - a.prevDeals);
        dealerGrowth.sort((a, b) => b.diff - a.diff);

        // 3. STUCK PREPAYMENTS for this channel from verified debtors
        let channelStuckPrepays = allStuckPrepays;
        if (ch.key !== 'all') {
            channelStuckPrepays = allStuckPrepays.filter(p => p.channelKey === ch.key);
        }

        channelsData[ch.key] = {
            brandGrowth,
            brandAlerts,
            dealerGrowth,
            dealerAlerts,
            stuckPrepays: channelStuckPrepays,
            totalCriticalCount: brandAlerts.filter(b => b.severity === 'critical').length + 
                                dealerAlerts.filter(d => d.severity === 'critical').length,
            totalGrowthCount: brandGrowth.length + dealerGrowth.length
        };
    });

    window._alertsRadarChannels = channelsData;
    window._alertsRadarMeta = {
        periodLabel,
        curMonthName,
        prevMonthName
    };

    const currentChannel = channelsData[activeAlertChannel] || channelsData['all'];

    return {
        periodLabel,
        curMonthName,
        prevMonthName,
        activeChannel: activeAlertChannel,
        channelsData,
        brandGrowth: currentChannel.brandGrowth,
        brandAlerts: currentChannel.brandAlerts,
        dealerGrowth: currentChannel.dealerGrowth,
        dealerAlerts: currentChannel.dealerAlerts,
        stuckPrepays: currentChannel.stuckPrepays,
        totalCriticalCount: currentChannel.totalCriticalCount,
        totalGrowthCount: currentChannel.totalGrowthCount
    };
}

function renderBrandGrowthItemsHTML(brandGrowth, prevMonthName) {
    if (!brandGrowth || brandGrowth.length === 0) {
        return `
            <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100 text-center text-slate-600 text-xs font-bold">
                В выбранном канале прироста марок относительно ${prevMonthName} не зафиксировано
            </div>
        `;
    }
    return brandGrowth.map(b => `
        <div class="flex items-center justify-between p-2.5 rounded-2xl ${b.significance === 'leader' ? 'bg-emerald-50/90 border border-emerald-200' : 'bg-teal-50/60 border border-teal-100'}">
            <div class="flex items-center gap-2.5">
                <div class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">
                    🚀
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-black text-slate-900">${b.brand}</span>
                        ${b.isNew ? '<span class="text-[10px] px-1.5 py-0.2 bg-emerald-200 text-emerald-900 font-bold rounded">NEW</span>' : ''}
                    </div>
                    <div class="text-[11px] text-slate-500">
                        Факт: <b>${b.curCnt}</b> шт. (было ${b.prevCnt} в ${prevMonthName})
                    </div>
                </div>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-black bg-emerald-200 text-emerald-900 whitespace-nowrap flex items-center gap-1">
                +${b.diff} шт. <span class="text-[10px] font-bold opacity-80">(+${b.pct}%)</span>
            </span>
        </div>
    `).join('');
}

function renderDealerGrowthItemsHTML(dealerGrowth, prevMonthName) {
    if (!dealerGrowth || dealerGrowth.length === 0) {
        return `
            <div class="p-4 bg-slate-50 rounded-2xl border border-slate-100 text-center text-slate-600 text-xs font-bold">
                В выбранном канале прироста дилеров относительно ${prevMonthName} не зафиксировано
            </div>
        `;
    }
    return dealerGrowth.map(d => `
        <div class="flex items-center justify-between p-2.5 rounded-2xl ${d.significance === 'leader' ? 'bg-emerald-50/90 border border-emerald-200' : 'bg-slate-50 border border-slate-200/70'}">
            <div class="min-w-0 pr-2">
                <div class="flex items-center gap-1.5">
                    <span class="text-xs font-black text-slate-900 truncate">${d.partner}</span>
                    ${d.isNew ? '<span class="text-[10px] px-1.5 py-0.2 bg-indigo-100 text-indigo-800 font-bold rounded shrink-0">Активация</span>' : ''}
                </div>
                <div class="text-[11px] text-slate-500 mt-0.5">
                    Сделок: <b>${d.curDeals} шт.</b> (было ${d.prevDeals} в ${prevMonthName}) • КАМ: <span class="font-medium text-slate-700">${d.kam}</span>
                </div>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-black bg-emerald-200 text-emerald-900 whitespace-nowrap">
                +${d.diff} шт. <span class="text-[10px] font-bold opacity-80">(+${d.pct}%)</span>
            </span>
        </div>
    `).join('');
}

function renderBrandAlertItemsHTML(brandAlerts, prevMonthName) {
    if (!brandAlerts || brandAlerts.length === 0) {
        return `
            <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                🟢 Критических просадок по маркам в выбранном канале не зафиксировано
            </div>
        `;
    }
    return brandAlerts.map(b => `
        <div class="flex items-center justify-between p-2.5 rounded-2xl ${b.severity === 'critical' ? 'bg-rose-50/80 border border-rose-100' : 'bg-amber-50/80 border border-amber-100'}">
            <div class="flex items-center gap-2.5">
                <span class="text-xs font-black ${b.severity === 'critical' ? 'text-rose-700' : 'text-amber-800'}">${b.brand}</span>
                <span class="text-[11px] text-slate-500">Факт: <b>${b.curCnt}</b> шт. (было ${b.prevCnt} в ${prevMonthName})</span>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-black ${b.severity === 'critical' ? 'bg-rose-200 text-rose-800' : 'bg-amber-200 text-amber-800'} whitespace-nowrap">
                ${b.diff} шт. <span class="text-[10px] font-bold opacity-75">(${b.pct}%)</span>
            </span>
        </div>
    `).join('');
}

function renderDealerAlertItemsHTML(dealerAlerts, prevMonthName) {
    if (!dealerAlerts || dealerAlerts.length === 0) {
        return `
            <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                🟢 Все ключевые партнеры проявляют активность в этом канале
            </div>
        `;
    }
    return dealerAlerts.map(d => `
        <div class="flex items-center justify-between p-2.5 rounded-2xl ${d.severity === 'critical' ? 'bg-rose-50/80 border border-rose-200/80' : 'bg-slate-50 border border-slate-200/70'}">
            <div class="min-w-0 pr-2">
                <div class="text-xs font-black text-slate-800 truncate">${d.partner}</div>
                <div class="text-[11px] text-slate-500 mt-0.5">
                    Было в ${prevMonthName}: <b>${d.prevDeals} шт.</b> • КАМ: <span class="font-medium text-slate-700">${d.kam}</span>
                </div>
            </div>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-black ${d.severity === 'critical' ? 'bg-rose-600 text-white' : 'bg-rose-100 text-rose-700 border border-rose-200'} whitespace-nowrap">
                0 сделок ⚠️
            </span>
        </div>
    `).join('');
}

function renderPrepayAlertItemsHTML(stuckPrepays) {
    if (!stuckPrepays || stuckPrepays.length === 0) {
        return `
            <div class="p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-center text-emerald-800 text-xs font-bold">
                🟢 Зависших авансов (>7 дней) не обнаружено
            </div>
        `;
    }
    return stuckPrepays.map(p => {
        const severityClass = p.days >= 30 ? 'bg-rose-50/80 border-rose-200 text-rose-950' : 
                             (p.days >= 14 ? 'bg-amber-50/80 border-amber-200 text-amber-950' : 'bg-slate-50 border-slate-200/80 text-slate-800');
        const badgeClass = p.days >= 30 ? 'bg-rose-600 text-white' : 
                          (p.days >= 14 ? 'bg-amber-200 text-amber-900 border border-amber-300' : 'bg-amber-100 text-amber-800 border border-amber-200');
        const carInfo = [p.brand, p.model].filter(Boolean).join(' ');
        const vinInfo = p.vin && p.vin !== p.dealId ? `VIN: ${p.vin}` : (p.dealId ? `Сделка #${p.dealId}` : '');
        const chBadge = p.b2c ? `<span class="text-[10px] px-1.5 py-0.2 rounded font-bold bg-indigo-100 text-indigo-800">${p.b2c}</span>` : '';

        return `
            <div class="flex items-center justify-between p-2.5 rounded-2xl border ${severityClass}">
                <div class="min-w-0 pr-2">
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span class="text-xs font-black truncate">${p.partner}</span>
                        ${chBadge}
                        ${carInfo ? `<span class="text-[11px] font-semibold text-slate-700 truncate">• ${carInfo}</span>` : ''}
                    </div>
                    <div class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-2 flex-wrap">
                        <span>Аванс от <b>${p.dateStr}</b></span>
                        ${vinInfo ? `<span class="font-mono text-[10px] bg-slate-200/70 text-slate-700 px-1.5 py-0.2 rounded">${vinInfo}</span>` : ''}
                        <span>• КАМ: <span class="font-medium text-slate-700">${p.kam}</span></span>
                    </div>
                </div>
                <span class="text-xs px-2.5 py-0.5 rounded-full font-black ${badgeClass} whitespace-nowrap shrink-0">
                    ${p.days} дн. завис
                </span>
            </div>
        `;
    }).join('');
}

function updateAlertFooter(tabName) {
    const footerInfo = document.getElementById('alertFooterInfo');
    if (!footerInfo) return;

    const channelsData = window._alertsRadarChannels || {};
    const curData = channelsData[activeAlertChannel] || channelsData['all'] || {
        brandGrowth: [], brandAlerts: [], dealerGrowth: [], dealerAlerts: [], stuckPrepays: []
    };

    if (tabName === 'growth_brands') {
        const topBrand = (curData.brandGrowth && curData.brandGrowth[0]) ? `${curData.brandGrowth[0].brand} (+${curData.brandGrowth[0].diff} шт.)` : '—';
        footerInfo.innerHTML = `
            <span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            Брендов с приростом: <b>${(curData.brandGrowth || []).length}</b> • Лидер: <b>${topBrand}</b>
        `;
    } else if (tabName === 'growth_dealers') {
        const topDealer = (curData.dealerGrowth && curData.dealerGrowth[0]) ? `${curData.dealerGrowth[0].partner} (+${curData.dealerGrowth[0].diff} шт.)` : '—';
        footerInfo.innerHTML = `
            <span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            Выросших ДЦ: <b>${(curData.dealerGrowth || []).length}</b> • Лидер: <b>${topDealer}</b>
        `;
    } else if (tabName === 'brands') {
        const topDrop = (curData.brandAlerts && curData.brandAlerts[0]) ? `${curData.brandAlerts[0].brand} (${curData.brandAlerts[0].diff} шт.)` : '—';
        footerInfo.innerHTML = `
            <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-500"></i>
            Просадок по маркам: <b>${(curData.brandAlerts || []).length}</b> • Наибольшая: <b>${topDrop}</b>
        `;
    } else if (tabName === 'dealers') {
        const critDealers = (curData.dealerAlerts || []).filter(d => d.severity === 'critical').length;
        footerInfo.innerHTML = `
            <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-500"></i>
            Партнеров с риском отвала: <b>${(curData.dealerAlerts || []).length}</b> (Критических: <b>${critDealers}</b>)
        `;
    } else if (tabName === 'prepays') {
        footerInfo.innerHTML = `
            <i data-lucide="clock" class="w-3.5 h-3.5 text-amber-500"></i>
            Зависших авансов (>7 дней): <b>${(curData.stuckPrepays || []).length}</b> шт.
        `;
    }

    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
}

function switchAlertTab(tabName) {
    activeAlertTab = tabName;
    const tabList = [
        { key: 'growth_brands', contentId: 'alertContent_growth_brands', btnId: 'alertTabBtn_growth_brands', activeClass: 'bg-emerald-700 text-white shadow-sm' },
        { key: 'brands', contentId: 'alertContent_brands', btnId: 'alertTabBtn_brands', activeClass: 'bg-rose-700 text-white shadow-sm' },
        { key: 'growth_dealers', contentId: 'alertContent_growth_dealers', btnId: 'alertTabBtn_growth_dealers', activeClass: 'bg-emerald-700 text-white shadow-sm' },
        { key: 'dealers', contentId: 'alertContent_dealers', btnId: 'alertTabBtn_dealers', activeClass: 'bg-rose-700 text-white shadow-sm' },
        { key: 'prepays', contentId: 'alertContent_prepays', btnId: 'alertTabBtn_prepays', activeClass: 'bg-amber-600 text-white shadow-sm' }
    ];

    const inactiveClass = 'bg-white/90 text-slate-600 hover:bg-white hover:text-slate-900 border border-slate-200/70';

    tabList.forEach(item => {
        const content = document.getElementById(item.contentId);
        const btn = document.getElementById(item.btnId);
        const isActive = (item.key === tabName);
        if (content) content.classList.toggle('hidden', !isActive);
        if (btn) {
            btn.className = `px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${isActive ? item.activeClass : inactiveClass}`;
        }
    });

    updateAlertFooter(tabName);
}

function switchAlertChannel(channelKey) {
    activeAlertChannel = channelKey;
    const channelsData = window._alertsRadarChannels || {};
    const meta = window._alertsRadarMeta || { prevMonthName: 'прошлом месяце' };
    const curData = channelsData[channelKey] || channelsData['all'] || {
        brandGrowth: [], brandAlerts: [], dealerGrowth: [], dealerAlerts: [], stuckPrepays: [], totalCriticalCount: 0
    };

    // 1. Update channel selector buttons
    ALERT_CHANNELS.forEach(ch => {
        const btn = document.getElementById(`alertChanBtn_${ch.key}`);
        if (btn) {
            if (ch.key === channelKey) {
                btn.className = 'px-2.5 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap bg-slate-900 text-white shadow-sm';
            } else {
                btn.className = 'px-2.5 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap bg-white/70 text-slate-600 hover:bg-white hover:text-slate-900';
            }
        }
    });

    // 2. Update tab buttons text with counts
    const bgBtn = document.getElementById('alertTabBtn_growth_brands');
    const bBtn = document.getElementById('alertTabBtn_brands');
    const dgBtn = document.getElementById('alertTabBtn_growth_dealers');
    const dBtn = document.getElementById('alertTabBtn_dealers');
    const pBtn = document.getElementById('alertTabBtn_prepays');

    if (bgBtn) bgBtn.textContent = `🚀 Рост марок (${(curData.brandGrowth || []).length})`;
    if (bBtn) bBtn.textContent = `🔻 Просадки (${(curData.brandAlerts || []).length})`;
    if (dgBtn) dgBtn.textContent = `🌟 Рост ДЦ (${(curData.dealerGrowth || []).length})`;
    if (dBtn) dBtn.textContent = `⚠️ Отвал ДЦ (${(curData.dealerAlerts || []).length})`;
    if (pBtn) pBtn.textContent = `⏳ Авансы (${(curData.stuckPrepays || []).length})`;

    // 3. Update tab contents
    const bgContent = document.getElementById('alertContent_growth_brands');
    const bContent = document.getElementById('alertContent_brands');
    const dgContent = document.getElementById('alertContent_growth_dealers');
    const dContent = document.getElementById('alertContent_dealers');
    const pContent = document.getElementById('alertContent_prepays');

    if (bgContent) bgContent.innerHTML = renderBrandGrowthItemsHTML(curData.brandGrowth || [], meta.prevMonthName);
    if (bContent) bContent.innerHTML = renderBrandAlertItemsHTML(curData.brandAlerts || [], meta.prevMonthName);
    if (dgContent) dgContent.innerHTML = renderDealerGrowthItemsHTML(curData.dealerGrowth || [], meta.prevMonthName);
    if (dContent) dContent.innerHTML = renderDealerAlertItemsHTML(curData.dealerAlerts || [], meta.prevMonthName);
    if (pContent) pContent.innerHTML = renderPrepayAlertItemsHTML(curData.stuckPrepays || []);

    // 4. Update header quick badges
    const badgePlus = document.getElementById('alertHeaderBadgePlus');
    const badgeMinus = document.getElementById('alertHeaderBadgeMinus');
    if (badgePlus) {
        badgePlus.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span>${(curData.brandGrowth || []).length} в плюсе`;
    }
    if (badgeMinus) {
        badgeMinus.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span>${(curData.brandAlerts || []).length} просадок`;
    }

    // 5. Update footer
    updateAlertFooter(activeAlertTab);
}

// Attach functions to window for global access
window.switchAlertTab = switchAlertTab;
window.switchAlertChannel = switchAlertChannel;
window.updateAlertFooter = updateAlertFooter;

function renderAlertsRadarCardHTML(a) {
    const currentChannel = (a.channelsData && a.channelsData[activeAlertChannel]) ? a.channelsData[activeAlertChannel] : a;
    const bGrowth = currentChannel.brandGrowth || [];
    const bAlerts = currentChannel.brandAlerts || [];
    const dGrowth = currentChannel.dealerGrowth || [];
    const dAlerts = currentChannel.dealerAlerts || [];
    const sPrepays = currentChannel.stuckPrepays || [];

    const activeGrowthBrandsClass = 'bg-emerald-700 text-white shadow-sm';
    const activeBrandsClass = 'bg-rose-700 text-white shadow-sm';
    const activeGrowthDealersClass = 'bg-emerald-700 text-white shadow-sm';
    const activeDealersClass = 'bg-rose-700 text-white shadow-sm';
    const activePrepaysClass = 'bg-amber-600 text-white shadow-sm';
    const inactiveClass = 'bg-white/90 text-slate-600 hover:bg-white hover:text-slate-900 border border-slate-200/70';

    let initialFooterHTML = '';
    if (activeAlertTab === 'growth_brands') {
        const topB = bGrowth[0] ? `${bGrowth[0].brand} (+${bGrowth[0].diff} шт.)` : '—';
        initialFooterHTML = `<span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>Брендов с приростом: <b>${bGrowth.length}</b> • Лидер: <b>${topB}</b>`;
    } else if (activeAlertTab === 'growth_dealers') {
        const topD = dGrowth[0] ? `${dGrowth[0].partner} (+${dGrowth[0].diff} шт.)` : '—';
        initialFooterHTML = `<span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>Выросших ДЦ: <b>${dGrowth.length}</b> • Лидер: <b>${topD}</b>`;
    } else if (activeAlertTab === 'brands') {
        const topDrop = bAlerts[0] ? `${bAlerts[0].brand} (${bAlerts[0].diff} шт.)` : '—';
        initialFooterHTML = `<i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-500"></i>Просадок по маркам: <b>${bAlerts.length}</b> • Наибольшая: <b>${topDrop}</b>`;
    } else if (activeAlertTab === 'dealers') {
        const critD = dAlerts.filter(d => d.severity === 'critical').length;
        initialFooterHTML = `<i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-500"></i>Партнеров с риском отвала: <b>${dAlerts.length}</b> (Критических: <b>${critD}</b>)`;
    } else {
        initialFooterHTML = `<i data-lucide="clock" class="w-3.5 h-3.5 text-amber-500"></i>Зависших авансов (>7 дней): <b>${sPrepays.length}</b> шт.`;
    }

    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title & Summary Badges -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-lg">
                            📡
                        </div>
                        <div>
                            <h3 class="font-black text-slate-800 text-base">Радар динамики & отклонений</h3>
                            <p class="text-xs text-slate-400">Сравнение: ${a.periodLabel}</p>
                        </div>
                    </div>
                    <!-- Quick Badges: Growth vs Drops -->
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span id="alertHeaderBadgePlus" class="text-[11px] px-2.5 py-1 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                            ${bGrowth.length} в плюсе
                        </span>
                        <span id="alertHeaderBadgeMinus" class="text-[11px] px-2.5 py-1 rounded-xl bg-rose-50 text-rose-800 border border-rose-200 font-bold flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
                            ${bAlerts.length} просадок
                        </span>
                    </div>
                </div>

                <!-- Tabs Row: 5 direct filters (Рост марок, Просадки, Рост ДЦ, Отвал ДЦ, Авансы) -->
                <div class="flex items-center gap-1.5 p-1 bg-slate-100/90 rounded-2xl mb-2.5 overflow-x-auto no-scrollbar">
                    <button id="alertTabBtn_growth_brands" onclick="switchAlertTab('growth_brands')" class="px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${activeAlertTab === 'growth_brands' ? activeGrowthBrandsClass : inactiveClass}">
                        🚀 Рост марок (${bGrowth.length})
                    </button>
                    <button id="alertTabBtn_brands" onclick="switchAlertTab('brands')" class="px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${activeAlertTab === 'brands' ? activeBrandsClass : inactiveClass}">
                        🔻 Просадки (${bAlerts.length})
                    </button>
                    <button id="alertTabBtn_growth_dealers" onclick="switchAlertTab('growth_dealers')" class="px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${activeAlertTab === 'growth_dealers' ? activeGrowthDealersClass : inactiveClass}">
                        🌟 Рост ДЦ (${dGrowth.length})
                    </button>
                    <button id="alertTabBtn_dealers" onclick="switchAlertTab('dealers')" class="px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${activeAlertTab === 'dealers' ? activeDealersClass : inactiveClass}">
                        ⚠️ Отвал ДЦ (${dAlerts.length})
                    </button>
                    <button id="alertTabBtn_prepays" onclick="switchAlertTab('prepays')" class="px-2.5 sm:px-3 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${activeAlertTab === 'prepays' ? activePrepaysClass : inactiveClass}">
                        ⏳ Авансы (${sPrepays.length})
                    </button>
                </div>

                <!-- Channel Filter Buttons -->
                <div class="flex items-center gap-1.5 p-1 bg-slate-50 border border-slate-100 rounded-2xl mb-3 overflow-x-auto no-scrollbar" id="alertChannelFilterRow">
                    ${ALERT_CHANNELS.map(ch => {
                        const isActive = ch.key === activeAlertChannel;
                        return `
                            <button onclick="switchAlertChannel('${ch.key}')" 
                                    id="alertChanBtn_${ch.key}"
                                    class="px-2.5 py-1 text-xs font-bold rounded-xl transition whitespace-nowrap ${isActive ? 'bg-slate-900 text-white shadow-sm' : 'bg-white/70 text-slate-600 hover:bg-white hover:text-slate-900'}">
                                ${ch.label}
                            </button>
                        `;
                    }).join('')}
                </div>

                <!-- TAB 1: BRAND GROWTH (Positive Dynamics) -->
                <div id="alertContent_growth_brands" class="${activeAlertTab === 'growth_brands' ? '' : 'hidden'} space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
                    ${renderBrandGrowthItemsHTML(bGrowth, a.prevMonthName)}
                </div>

                <!-- TAB 2: BRAND DROPS (Alerts) -->
                <div id="alertContent_brands" class="${activeAlertTab === 'brands' ? '' : 'hidden'} space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
                    ${renderBrandAlertItemsHTML(bAlerts, a.prevMonthName)}
                </div>

                <!-- TAB 3: DEALER GROWTH (Positive Dynamics) -->
                <div id="alertContent_growth_dealers" class="${activeAlertTab === 'growth_dealers' ? '' : 'hidden'} space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
                    ${renderDealerGrowthItemsHTML(dGrowth, a.prevMonthName)}
                </div>

                <!-- TAB 4: DEALERS CHURN RISK -->
                <div id="alertContent_dealers" class="${activeAlertTab === 'dealers' ? '' : 'hidden'} space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
                    ${renderDealerAlertItemsHTML(dAlerts, a.prevMonthName)}
                </div>

                <!-- TAB 5: STUCK PREPAYMENTS -->
                <div id="alertContent_prepays" class="${activeAlertTab === 'prepays' ? '' : 'hidden'} space-y-2 mb-4 max-h-72 overflow-y-auto pr-1">
                    ${renderPrepayAlertItemsHTML(sPrepays)}
                </div>
            </div>

            <!-- Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5" id="alertFooterInfo">
                    ${initialFooterHTML}
                </span>
                <span class="text-slate-400">Прокрутите список для просмотра всех</span>
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
        'opt': { key: 'opt', name: 'Опт МП2', deals: 0, revenue: 0, totalPrice: 0, color: 'bg-blue-500' },
        'fdc': { key: 'fdc', name: 'ФДЦ (ФДЦ / ГП)', deals: 0, revenue: 0, totalPrice: 0, color: 'bg-purple-500' },
        'retail': { key: 'retail', name: 'Розница (B2C / Лиды)', deals: 0, revenue: 0, totalPrice: 0, color: 'bg-emerald-500' },
        'online': { key: 'online', name: 'Online продажи', deals: 0, revenue: 0, totalPrice: 0, color: 'bg-cyan-500' },
        'other': { key: 'other', name: 'Прочие (МП1 / МП3)', deals: 0, revenue: 0, totalPrice: 0, color: 'bg-slate-400' }
    };

    deals.forEach(d => {
        const rawB2C = (d.B2C || '').toString().trim().toLowerCase();
        const rev = d.Revenue || 0;
        const pr = d.Price || 0;

        let key = 'other';
        if (rawB2C.includes('мп2') || rawB2C === 'мп 2') {
            key = 'opt';
        } else if (rawB2C.includes('фдц') || rawB2C.includes('гп')) {
            key = 'fdc';
        } else if (rawB2C.includes('лид') || rawB2C.includes('b2c') || rawB2C.includes('розниц')) {
            key = 'retail';
        } else if (rawB2C.includes('online') || rawB2C.includes('онлайн')) {
            key = 'online';
        } else if (rawB2C.includes('мп1') || rawB2C.includes('мп3')) {
            key = 'other';
        } else {
            key = 'opt';
        }

        channels[key].deals += 1;
        channels[key].revenue += rev;
        channels[key].totalPrice += pr;
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
                            <p class="text-xs text-slate-400">Сравнение комиссионных доходов и чека по 5 каналам продаж</p>
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
                                <th class="text-left py-2">Канал продаж</th>
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
                                        <span class="w-2 h-2 rounded-full ${r.color}"></span>
                                        ${r.name}
                                    </td>
                                    <td class="py-2.5 text-right text-slate-700">
                                        <b>${fmtNum(r.deals)}</b> <span class="text-slate-400 text-[11px]">(${r.shareDeals}%)</span>
                                    </td>
                                    <td class="py-2.5 text-right text-slate-800">
                                        <b>${fmtRub(r.revenue)}</b> <span class="text-slate-400 text-[11px]">(${r.shareRev}%)</span>
                                    </td>
                                    <td class="py-2.5 text-right font-black ${r.arpu >= m.overallArpu ? 'text-emerald-700' : 'text-slate-700'}">
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
                    <b>Online</b> дает макс. ARPU (48.3к ₽), а <b>Опт МП2</b> обеспечивает 77.5% объема
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

    // Build DealId -> Partner info lookup from allPartners
    const pLookup = new Map();
    if (allPartners && allPartners.length > 0) {
        allPartners.forEach(p => {
            if (p.DealId && (p.Type === 'Сделка' || p.Type === 'Предоплата' || !pLookup.has(String(p.DealId)))) {
                pLookup.set(String(p.DealId), p);
            }
        });
    }

    deals.forEach(d => {
        const pInfo = d.DealId ? pLookup.get(String(d.DealId)) : null;
        const pName = (pInfo && pInfo.Partner) ? pInfo.Partner : (d.LegalPartner || d.Partner || 'Неизвестный партнер');
        const kam = (pInfo && pInfo.KAM) ? pInfo.KAM : (d.KAM || '—');
        const rawPartner = (pInfo && pInfo.RawPartner) ? pInfo.RawPartner : '';

        if (!partnersMap[pName]) {
            partnersMap[pName] = {
                partner: pName,
                kam: kam,
                rawPartners: new Set(),
                deals: 0,
                revenue: 0,
                totalPrice: 0
            };
        }
        if (kam && kam !== '—' && (!partnersMap[pName].kam || partnersMap[pName].kam === '—')) {
            partnersMap[pName].kam = kam;
        }
        if (rawPartner) {
            partnersMap[pName].rawPartners.add(rawPartner);
        }
        partnersMap[pName].deals += 1;
        partnersMap[pName].revenue += (d.Revenue || 0);
        partnersMap[pName].totalPrice += (d.Price || 0);
    });

    const list = Object.values(partnersMap).map(p => {
        const arpu = p.deals > 0 ? Math.round(p.revenue / p.deals) : 0;
        const avgCheck = p.deals > 0 ? Math.round(p.totalPrice / p.deals) : 0;
        const takeRate = p.totalPrice > 0 ? ((p.revenue / p.totalPrice) * 100).toFixed(2) : '0.00';
        return {
            ...p,
            rawPartnersList: Array.from(p.rawPartners),
            arpu,
            avgCheck,
            takeRate
        };
    });

    if (list.length === 0) {
        window._partnerHealthCache = { allList: [], stars: [], growth: [], niche: [], risk: [], overallArpu: 0, volThreshold: 3 };
        return { stars: [], growth: [], niche: [], risk: [], totalPartners: 0, overallArpu: 0, volThreshold: 3, allList: [] };
    }

    // Benchmark ARPU & Dynamic Volume Threshold (Median volume, min 3)
    const totalRev = list.reduce((s, p) => s + p.revenue, 0);
    const totalDeals = list.reduce((s, p) => s + p.deals, 0);
    const overallArpu = totalDeals > 0 ? Math.round(totalRev / totalDeals) : 40000;

    const sortedDeals = list.map(p => p.deals).sort((a, b) => a - b);
    const medianDeals = sortedDeals[Math.floor(sortedDeals.length / 2)] || 2;
    const volThreshold = Math.max(3, medianDeals);

    const stars = [];
    const growth = [];
    const niche = [];
    const risk = [];

    list.forEach(p => {
        const isHighVolume = p.deals >= volThreshold;
        const isHighYield = p.arpu >= overallArpu;

        if (isHighVolume && isHighYield) {
            p.quadrant = 'stars';
            p.quadrantName = 'Локомотив';
            p.action = 'Удерживать приоритет, развивать совместные промо';
            stars.push(p);
        } else if (isHighVolume && !isHighYield) {
            p.quadrant = 'growth';
            p.quadrantName = 'Точка роста';
            p.action = 'Повысить маржинальность: допуслуги, пересмотр условий';
            growth.push(p);
        } else if (!isHighVolume && isHighYield) {
            p.quadrant = 'niche';
            p.quadrantName = 'Нишевый';
            p.action = 'Масштабировать объем продаж без потери чека';
            niche.push(p);
        } else {
            p.quadrant = 'risk';
            p.quadrantName = 'Зона риска';
            p.action = 'Ревизия условий сотрудничества и активности КАМ';
            risk.push(p);
        }
    });

    stars.sort((a, b) => b.revenue - a.revenue);
    growth.sort((a, b) => b.deals - a.deals);
    niche.sort((a, b) => b.revenue - a.revenue);
    risk.sort((a, b) => b.deals - a.deals);

    // Save in global cache for modal view
    window._partnerHealthCache = {
        allList: list.sort((a, b) => b.revenue - a.revenue),
        stars,
        growth,
        niche,
        risk,
        overallArpu,
        volThreshold
    };

    return {
        stars,
        growth,
        niche,
        risk,
        totalPartners: list.length,
        overallArpu,
        volThreshold,
        allList: list
    };
}

function renderHealthScoreCardHTML(h) {
    const starTop = h.stars.slice(0, 3).map(p => `${p.partner} (${p.deals})`).join(', ') || '—';
    const growthTop = h.growth.slice(0, 3).map(p => `${p.partner} (${p.deals})`).join(', ') || '—';
    const nicheTop = h.niche.slice(0, 3).map(p => `${p.partner} (${p.deals})`).join(', ') || '—';
    const riskTop = h.risk.slice(0, 3).map(p => `${p.partner} (${p.deals})`).join(', ') || '—';

    return `
        <div class="card !p-5 bg-white rounded-3xl shadow-sm border border-gray-200 flex flex-col justify-between">
            <div>
                <!-- Title & Badge -->
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
                    <button onclick="openHealthDetailsModal('all')" class="text-xs px-3 py-1 rounded-full font-black bg-purple-100 hover:bg-purple-200 text-purple-800 transition flex items-center gap-1 shadow-sm">
                        <span>Все ${h.totalPartners} ДЦ ➔</span>
                    </button>
                </div>

                <!-- 4 Quadrants Grid (Clickable) -->
                <div class="grid grid-cols-2 gap-3 mb-3">
                    <!-- Quadrant 1: Stars -->
                    <div onclick="openHealthDetailsModal('stars')" class="p-3.5 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200/80 hover:border-emerald-400 cursor-pointer transition-all hover:shadow-md transform hover:-translate-y-0.5">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-emerald-800 flex items-center gap-1">🌟 Локомотивы</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900">${h.stars.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-emerald-700 mt-1">Высокий объем + высокий ARPU</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate" title="${starTop}">
                            Топ: ${starTop}
                        </div>
                    </div>

                    <!-- Quadrant 2: Growth Potential -->
                    <div onclick="openHealthDetailsModal('growth')" class="p-3.5 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200/80 hover:border-blue-400 cursor-pointer transition-all hover:shadow-md transform hover:-translate-y-0.5">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-blue-800 flex items-center gap-1">🚀 Точки роста</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-blue-200 text-blue-900">${h.growth.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-blue-700 mt-1">Высокий объем, резерв по ARPU</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate" title="${growthTop}">
                            Топ: ${growthTop}
                        </div>
                    </div>

                    <!-- Quadrant 3: Specialized / Niche -->
                    <div onclick="openHealthDetailsModal('niche')" class="p-3.5 rounded-2xl bg-gradient-to-br from-purple-50 to-fuchsia-50 border border-purple-200/80 hover:border-purple-400 cursor-pointer transition-all hover:shadow-md transform hover:-translate-y-0.5">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-purple-800 flex items-center gap-1">💼 Нишевые</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-purple-200 text-purple-900">${h.niche.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-purple-700 mt-1">Штучные сделки с высоким чеком</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate" title="${nicheTop}">
                            Топ: ${nicheTop}
                        </div>
                    </div>

                    <!-- Quadrant 4: At Risk -->
                    <div onclick="openHealthDetailsModal('risk')" class="p-3.5 rounded-2xl bg-gradient-to-br from-amber-50 to-rose-50 border border-amber-200/80 hover:border-rose-300 cursor-pointer transition-all hover:shadow-md transform hover:-translate-y-0.5">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black text-amber-800 flex items-center gap-1">⚠️ Зона риска</span>
                            <span class="text-xs font-black px-2 py-0.5 rounded-full bg-amber-200 text-amber-900">${h.risk.length} ДЦ</span>
                        </div>
                        <div class="text-[11px] text-amber-700 mt-1">Мало сделок и низкая маржинальность</div>
                        <div class="text-xs text-slate-600 font-bold mt-2 truncate" title="${riskTop}">
                            Топ: ${riskTop}
                        </div>
                    </div>
                </div>

                <!-- Interactive CTA Button -->
                <button onclick="openHealthDetailsModal('all')" class="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-2xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-sm">
                    <i data-lucide="table" class="w-3.5 h-3.5"></i>
                    <span>Открыть реестр всех ${h.totalPartners} партнеров с фильтром по КАМ ➔</span>
                </button>
            </div>

            <!-- Footer -->
            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="flex items-center gap-1.5">
                    <i data-lucide="users" class="w-3.5 h-3.5 text-purple-600"></i>
                    Фокус внимания КАМ: <b>«Точки роста»</b> (допродажи) и <b>«Зона риска»</b>
                </span>
                <span class="text-slate-400">Порог: ≥${h.volThreshold} сд. • ARPU ${fmtNum(h.overallArpu)} ₽</span>
            </div>
        </div>
    `;
}

/**
 * =========================================================================
 * MODAL WINDOW: PARTNER HEALTH SCORE DETAILS, FILTERS & EXCEL EXPORT
 * =========================================================================
 */
function ensureHealthModalExists() {
    if (document.getElementById('modalPartnerHealth')) return;

    const modalHTML = `
        <div id="modalPartnerHealth" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-3 sm:p-4 animate-fade-in" onclick="handleHealthModalBackdrop(event)">
            <div class="bg-white w-full max-w-5xl max-h-[90vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-slate-200" onclick="event.stopPropagation()">
                <!-- Header -->
                <div class="p-5 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between border-b border-slate-800">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-2xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-purple-300 font-black text-lg">
                            📊
                        </div>
                        <div>
                            <h3 class="text-lg font-black text-white flex items-center gap-2">
                                Аудит эффективности партнерской сети (Partner Health Score)
                            </h3>
                            <p id="modalHealthSubtitle" class="text-xs text-slate-300 mt-0.5">
                                Детальный реестр активных дилеров: объемы, выручка, ARPU и рекомендации для КАМ
                            </p>
                        </div>
                    </div>
                    <button onclick="closeHealthDetailsModal()" class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center text-lg transition font-bold">
                        &times;
                    </button>
                </div>

                <!-- Toolbar & Filters -->
                <div class="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <!-- Quadrant Tabs -->
                    <div class="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0" id="healthModalTabs">
                        <button onclick="switchHealthModalTab('all')" id="healthTabBtn_all" class="px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-900 text-white shadow-sm">
                            Все (<span id="healthTabCount_all">0</span>)
                        </button>
                        <button onclick="switchHealthModalTab('stars')" id="healthTabBtn_stars" class="px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-700 hover:bg-slate-200">
                            🌟 Локомотивы (<span id="healthTabCount_stars">0</span>)
                        </button>
                        <button onclick="switchHealthModalTab('growth')" id="healthTabBtn_growth" class="px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-700 hover:bg-slate-200">
                            🚀 Точки роста (<span id="healthTabCount_growth">0</span>)
                        </button>
                        <button onclick="switchHealthModalTab('niche')" id="healthTabBtn_niche" class="px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-700 hover:bg-slate-200">
                            💼 Нишевые (<span id="healthTabCount_niche">0</span>)
                        </button>
                        <button onclick="switchHealthModalTab('risk')" id="healthTabBtn_risk" class="px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-700 hover:bg-slate-200">
                            ⚠️ Зона риска (<span id="healthTabCount_risk">0</span>)
                        </button>
                    </div>

                    <!-- Search Input & Excel Export -->
                    <div class="flex items-center gap-2 w-full sm:w-auto">
                        <div class="relative w-full sm:w-64">
                            <input id="healthModalSearch" type="text" oninput="filterHealthModalTable()" placeholder="Поиск по партнеру или КАМу..." class="w-full bg-white border border-slate-300 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-purple-500 outline-none">
                            <span class="absolute left-2.5 top-2 text-slate-400 text-xs">🔍</span>
                        </div>
                        <button onclick="exportPartnerHealthToExcel()" title="Скачать таблицу в Excel (.xlsx)" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 shadow-sm">
                            <span>📥 Excel</span>
                        </button>
                    </div>
                </div>

                <!-- Table Content -->
                <div class="flex-1 overflow-y-auto max-h-[60vh] p-4">
                    <table class="min-w-full text-xs" id="tablePartnerHealthModal">
                        <thead class="sticky top-0 bg-white shadow-sm z-10">
                            <tr class="border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                                <th class="text-left py-2.5 px-3">Партнер (ДЦ)</th>
                                <th class="text-left py-2.5 px-3">Квадрант</th>
                                <th class="text-left py-2.5 px-3">Закрепленный КАМ</th>
                                <th class="text-right py-2.5 px-3">Сделки (шт)</th>
                                <th class="text-right py-2.5 px-3">Выручка (₽)</th>
                                <th class="text-right py-2.5 px-3">ARPU (₽/шт)</th>
                                <th class="text-right py-2.5 px-3">Take-rate</th>
                                <th class="text-left py-2.5 px-3">Рекомендация КАМ</th>
                            </tr>
                        </thead>
                        <tbody id="modalHealthTableBody" class="divide-y divide-slate-100 font-medium text-slate-700">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>

                <!-- Footer Summary -->
                <div class="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-600 font-medium">
                    <div class="flex items-center gap-3">
                        <span>Показано: <b id="healthModalShowingCount" class="text-slate-900">0</b> ДЦ</span>
                        <span>•</span>
                        <span>Сделок: <b id="healthModalTotalDeals" class="text-slate-900">0</b> шт.</span>
                        <span>•</span>
                        <span>Выручка: <b id="healthModalTotalRev" class="text-slate-900">0 ₽</b></span>
                        <span>•</span>
                        <span>Средний ARPU: <b id="healthModalAvgArpu" class="text-purple-700">0 ₽</b></span>
                    </div>
                    <button onclick="closeHealthDetailsModal()" class="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl font-bold transition">
                        Закрыть
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Escape key listener
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeHealthDetailsModal();
        }
    });
}

function handleHealthModalBackdrop(event) {
    if (event.target.id === 'modalPartnerHealth') {
        closeHealthDetailsModal();
    }
}

function openHealthDetailsModal(quadrantKey = 'all') {
    ensureHealthModalExists();
    activeHealthQuadrant = quadrantKey;

    const modal = document.getElementById('modalPartnerHealth');
    if (!modal) return;

    // Reset search
    const searchInput = document.getElementById('healthModalSearch');
    if (searchInput) searchInput.value = '';

    // Update tab counts
    const cache = window._partnerHealthCache || { allList: [], stars: [], growth: [], niche: [], risk: [] };
    const setTabCount = (id, count) => {
        const el = document.getElementById(`healthTabCount_${id}`);
        if (el) el.textContent = count;
    };
    setTabCount('all', cache.allList.length);
    setTabCount('stars', cache.stars.length);
    setTabCount('growth', cache.growth.length);
    setTabCount('niche', cache.niche.length);
    setTabCount('risk', cache.risk.length);

    // Update subtitle
    const subTitle = document.getElementById('modalHealthSubtitle');
    if (subTitle) {
        subTitle.textContent = `Детальный реестр ${cache.allList.length} дилеров: объемы, выручка, ARPU и рекомендации для КАМ`;
    }

    switchHealthModalTab(quadrantKey);

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeHealthDetailsModal() {
    const modal = document.getElementById('modalPartnerHealth');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = '';
}

function switchHealthModalTab(tabKey) {
    activeHealthQuadrant = tabKey;

    const tabs = ['all', 'stars', 'growth', 'niche', 'risk'];
    tabs.forEach(t => {
        const btn = document.getElementById(`healthTabBtn_${t}`);
        if (btn) {
            if (t === tabKey) {
                btn.className = 'px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-900 text-white shadow-sm';
            } else {
                btn.className = 'px-3 py-1.5 text-xs font-bold rounded-xl transition bg-slate-100 text-slate-700 hover:bg-slate-200';
            }
        }
    });

    filterHealthModalTable();
}

function filterHealthModalTable() {
    const cache = window._partnerHealthCache || { allList: [], stars: [], growth: [], niche: [], risk: [] };
    let list = [];

    if (activeHealthQuadrant === 'stars') list = cache.stars;
    else if (activeHealthQuadrant === 'growth') list = cache.growth;
    else if (activeHealthQuadrant === 'niche') list = cache.niche;
    else if (activeHealthQuadrant === 'risk') list = cache.risk;
    else list = cache.allList;

    const searchInput = document.getElementById('healthModalSearch');
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();

    if (query) {
        list = list.filter(p => {
            const nameMatch = p.partner.toLowerCase().includes(query);
            const rawMatch = (p.rawPartnersList || []).some(r => r.toLowerCase().includes(query));
            const kamMatch = (p.kam || '').toLowerCase().includes(query);
            return nameMatch || rawMatch || kamMatch;
        });
    }

    const tbody = document.getElementById('modalHealthTableBody');
    if (!tbody) return;

    if (list.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-8 text-slate-400 font-bold">
                    🔍 По вашему запросу партнеры не найдены
                </td>
            </tr>
        `;
    } else {
        const quadrantBadges = {
            stars: '<span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-emerald-100 text-emerald-800 border border-emerald-200">🌟 Локомотив</span>',
            growth: '<span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-blue-100 text-blue-800 border border-blue-200">🚀 Точка роста</span>',
            niche: '<span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-purple-100 text-purple-800 border border-purple-200">💼 Нишевый</span>',
            risk: '<span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-rose-100 text-rose-800 border border-rose-200">⚠️ Зона риска</span>'
        };

        tbody.innerHTML = list.map(p => `
            <tr class="hover:bg-slate-50 transition">
                <td class="py-2.5 px-3 text-slate-800 font-black">
                    <div class="truncate max-w-xs font-bold text-slate-900">${p.partner}</div>
                    ${p.rawPartnersList && p.rawPartnersList.length > 0 ? `
                        <div class="text-[10px] text-slate-400 truncate max-w-xs font-normal">
                            ${p.rawPartnersList.join(' • ')}
                        </div>
                    ` : ''}
                </td>
                <td class="py-2.5 px-3 whitespace-nowrap">
                    ${quadrantBadges[p.quadrant] || '<span class="text-slate-400">—</span>'}
                </td>
                <td class="py-2.5 px-3 text-slate-700 whitespace-nowrap">
                    <span class="font-bold">${p.kam || '—'}</span>
                </td>
                <td class="py-2.5 px-3 text-right font-black text-slate-800">
                    ${fmtNum(p.deals)}
                </td>
                <td class="py-2.5 px-3 text-right font-bold text-slate-800">
                    ${fmtRub(p.revenue)}
                </td>
                <td class="py-2.5 px-3 text-right font-black ${p.arpu >= (cache.overallArpu || 0) ? 'text-emerald-700' : 'text-slate-700'}">
                    ${fmtNum(p.arpu)} ₽
                </td>
                <td class="py-2.5 px-3 text-right font-bold text-slate-600">
                    ${p.takeRate}%
                </td>
                <td class="py-2.5 px-3 text-slate-600 text-[11px]">
                    ${p.action}
                </td>
            </tr>
        `).join('');
    }

    // Update footer stats
    const totalDeals = list.reduce((s, p) => s + p.deals, 0);
    const totalRev = list.reduce((s, p) => s + p.revenue, 0);
    const avgArpu = totalDeals > 0 ? Math.round(totalRev / totalDeals) : 0;

    const setFooterVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    setFooterVal('healthModalShowingCount', list.length);
    setFooterVal('healthModalTotalDeals', fmtNum(totalDeals));
    setFooterVal('healthModalTotalRev', fmtRub(totalRev));
    setFooterVal('healthModalAvgArpu', `${fmtNum(avgArpu)} ₽`);
}

function exportPartnerHealthToExcel() {
    if (typeof XLSX === 'undefined') {
        alert('Библиотека XLSX не загружена на странице');
        return;
    }
    const cache = window._partnerHealthCache || { allList: [] };
    let list = [];

    if (activeHealthQuadrant === 'stars') list = cache.stars;
    else if (activeHealthQuadrant === 'growth') list = cache.growth;
    else if (activeHealthQuadrant === 'niche') list = cache.niche;
    else if (activeHealthQuadrant === 'risk') list = cache.risk;
    else list = cache.allList;

    const searchInput = document.getElementById('healthModalSearch');
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();

    if (query) {
        list = list.filter(p => {
            const nameMatch = p.partner.toLowerCase().includes(query);
            const rawMatch = (p.rawPartnersList || []).some(r => r.toLowerCase().includes(query));
            const kamMatch = (p.kam || '').toLowerCase().includes(query);
            return nameMatch || rawMatch || kamMatch;
        });
    }

    if (list.length === 0) {
        alert('Нет данных для выгрузки');
        return;
    }

    const rows = list.map(p => ({
        'Партнер (ДЦ)': p.partner,
        'Юридические лица': (p.rawPartnersList || []).join('; '),
        'Квадрант': p.quadrantName,
        'Закрепленный КАМ': p.kam || '—',
        'Сделки (шт)': p.deals,
        'Выручка (руб)': p.revenue,
        'ARPU (руб/шт)': p.arpu,
        'Take-rate (%)': p.takeRate + '%',
        'Рекомендация для КАМ': p.action
    }));

    const ws = XLSX.utils.json_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Partner Health Audit');

    const fileName = `Partner_Health_Score_${activeHealthQuadrant}_${new Date().toISOString().slice(0, 10)}.xlsx`;
    XLSX.writeFile(wb, fileName);
}
