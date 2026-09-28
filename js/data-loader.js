/* ====================================================================
 * B2C Analytics Dashboard — Data Loading & Filtering
 * ====================================================================*/

let db = [], dbPartners = [], rawDebtorsList = [];

let currentFilterConfig = {
    mode: 'month',
    month: null, // will be set dynamically from data
    from: null,
    to: null
};

if (typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
}

async function loadData() {
    try {
        const res = await fetch('data.json?v=' + new Date().getTime());
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        const data = await res.json();
        db = data.sys_db || [];
        dbPartners = data.sys_db_partners || [];
        window.dataPayload = data;
        window.currentData = data;
        if (data.banking_analytics) {
            window.bankingAnalyticsData = data.banking_analytics;
        }
        rawDebtorsList = data.debtors || [];
        if (data.brand_funnel) {
            window.brandFunnelFullData = data.brand_funnel;
            if (typeof funnelRawData !== 'undefined') {
                Object.assign(funnelRawData, data.brand_funnel);
            }
        }
        updateDataFreshnessBadge(data.metadata);
        initDropdown();
        if (typeof initFunnelMonths === 'function') initFunnelMonths();
    } catch (error) {
        console.error("Ошибка загрузки data.json:", error);
        showToast("Ошибка загрузки data.json: " + error.message, 'error', 5000);
    }
}

function updateDataFreshnessBadge(meta) {
    const badge = document.getElementById('dataFreshnessBadge');
    const txt = document.getElementById('dataFreshnessText');
    const sub = document.getElementById('dataFreshnessSub');
    if (!badge || !txt) return;

    if (!meta || !meta.updated_at) {
        txt.innerText = 'Данные загружены';
        if (sub) sub.innerText = 'База сделок и воронки активна';
        return;
    }

    const updatedAt = meta.updated_at;
    const dealsCnt = meta.total_sales ? fmtNum(meta.total_sales) : '0';
    const revM = meta.total_revenue ? (meta.total_revenue / 1000000).toFixed(1) + 'M ₽' : '';
    const file = meta.latest_deal_file || '';

    txt.innerText = `Актуально на ${updatedAt}`;
    if (sub) {
        sub.innerText = `База: ${dealsCnt} сделок • ${revM} выручки • Источник: ${file}`;
    }
}

function initDropdown() {
    let months = new Set();
    db.forEach(r => {
        if (r.SaleMonth) months.add(r.SaleMonth.replace("'", ""));
        if (r.PrepayMonth) months.add(r.PrepayMonth.replace("'", ""));
    });
    let sorted = Array.from(months).filter(m => m).sort().reverse();
    let sel = document.getElementById('monthFilter');
    if (sel) {
        sel.innerHTML = '<option value="all">Весь период</option>';
        sorted.forEach(m => {
            sel.innerHTML += `<option value="${m}">${formatMonthLabel(m).replace('📅 ','')}</option>`;
        });
        sel.innerHTML += '<option value="custom">🗓️ Выбрать даты (календарь)...</option>';
        // Auto-select latest month (no hardcode)
        let def = sorted[0] || "all";
        sel.value = def;
        currentFilterConfig.month = def;
        onPeriodSelectChange(def);
        sel.onchange = (e) => onPeriodSelectChange(e.target.value);
    } else {
        currentFilterConfig.month = sorted[0] || null;
        updateAllTabs();
    }
}

function onPeriodSelectChange(val) {
    const customCont = document.getElementById('customDateContainer');
    if (val === 'custom') {
        if (customCont) customCont.classList.remove('hidden');
        let dFrom = document.getElementById('dateFrom')?.value;
        let dTo = document.getElementById('dateTo')?.value;
        if (!dFrom || !dTo) {
            let now = new Date();
            let y = now.getFullYear();
            let m = (now.getMonth() + 1).toString().padStart(2, '0');
            dFrom = `${y}-${m}-01`;
            dTo = `${y}-${m}-${now.getDate().toString().padStart(2, '0')}`;
            if (document.getElementById('dateFrom')) document.getElementById('dateFrom').value = dFrom;
            if (document.getElementById('dateTo')) document.getElementById('dateTo').value = dTo;
        }
        applyCustomDateFilter();
        return;
    }

    if (customCont) customCont.classList.add('hidden');
    if (val === 'all') {
        currentFilterConfig = { mode: 'all', month: null, from: null, to: null };
    } else {
        currentFilterConfig = { mode: 'month', month: val, from: null, to: null };
    }
    updateAllTabs();
}

function applyCustomDateFilter() {
    const dFromStr = document.getElementById('dateFrom')?.value;
    const dToStr = document.getElementById('dateTo')?.value;
    if (!dFromStr || !dToStr) return;

    const fromDate = new Date(dFromStr + 'T00:00:00');
    const toDate = new Date(dToStr + 'T23:59:59');

    if (fromDate > toDate) {
        showToast('Дата начала не может быть позже даты окончания!', 'warning');
        return;
    }

    currentFilterConfig = { mode: 'custom', month: null, from: fromDate, to: toDate };
    updateAllTabs();
}

function forceDataUpdate(btn) {
    if (btn) {
        btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4 animate-spin"></i> Обновление...';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    loadData().then(() => {
        if (btn) {
            btn.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-emerald-500"></i> Обновлено!';
            if (typeof lucide !== 'undefined') lucide.createIcons();
            setTimeout(() => {
                btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4"></i> Обновить';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }, 2000);
        }
        showToast('Данные обновлены', 'success');
    });
}

function getFilteredData() {
    let sDb = [], pDb = [];
    if (currentFilterConfig.mode === 'all') {
        sDb = db.filter(r => r.SaleQty > 0);
        pDb = db.filter(r => r.PrepayQty > 0);
    } else if (currentFilterConfig.mode === 'month') {
        const m = currentFilterConfig.month;
        sDb = db.filter(r => r.SaleQty > 0 && r.SaleMonth === m);
        pDb = db.filter(r => r.PrepayQty > 0 && r.PrepayMonth === m);
    } else if (currentFilterConfig.mode === 'custom') {
        const fTime = currentFilterConfig.from.getTime();
        const tTime = currentFilterConfig.to.getTime();
        sDb = db.filter(r => {
            if (r.SaleQty <= 0) return false;
            const d = excelToJSDate(r.DealDate);
            if (!d) return false;
            return d.getTime() >= fTime && d.getTime() <= tTime;
        });
        pDb = db.filter(r => {
            if (r.PrepayQty <= 0) return false;
            const d = excelToJSDate(r.PrepayDate);
            if (!d) return false;
            return d.getTime() >= fTime && d.getTime() <= tTime;
        });
    }
    return { sDb, pDb };
}

function updateAllTabs() {
    const { sDb, pDb } = getFilteredData();
    window.currentFilteredSales = sDb;
    window.currentFilteredPrepays = pDb;
    let tS = sDb.length, tP = pDb.length;
    const setVal = (id, v) => { const el = document.getElementById(id); if (el) el.innerText = v; };

    setVal('kpiSales', fmtNum(tS));
    setVal('kpiPrepays', fmtNum(tP));

    let revTotal = 0, revChina = 0, revLada = 0;
    sDb.forEach(r => {
        let rv = r.Revenue || 0;
        revTotal += rv;
        if (r.Brand === 'LADA') revLada += rv;
        else revChina += rv;
    });
    setVal('kpiRevTotal', fmtRub(revTotal));
    setVal('kpiRevChina', fmtRub(revChina));
    setVal('kpiRevLada', fmtRub(revLada));

    let cntCh = 0, cntLa = 0, pCh = 0, pLa = 0, pTot = 0;
    sDb.forEach(r => {
        pTot += r.Price;
        if (r.Brand === 'LADA') { cntLa++; pLa += r.Price; }
        else { cntCh++; pCh += r.Price; }
    });
    setVal('kpiArpu', tS > 0 ? fmtRub(revTotal / tS) : '0 ₽');
    setVal('kpiArpuChina', cntCh > 0 ? fmtNum(revChina / cntCh) : '0');
    setVal('kpiArpuLada', cntLa > 0 ? fmtNum(revLada / cntLa) : '0');
    setVal('kpiCheck', tS > 0 ? fmtRub(pTot / tS) : '0 ₽');
    setVal('kpiCheckChina', cntCh > 0 ? fmtNum(pCh / cntCh) : '0');
    setVal('kpiCheckLada', cntLa > 0 ? fmtNum(pLa / cntLa) : '0');

    // Top KPI Plan indicators & progress bars
    const curAvgCheck = tS > 0 ? (pTot / tS) : 0;
    const curArpu = tS > 0 ? (revTotal / tS) : 0;
    updateTopKpiPlans(tS, tP, curAvgCheck, curArpu, revTotal);

    // Plan vs Fact KPI
    updatePlanVsFact(tS, revTotal, pTot);

    // Linear Run Rate KPI
    updateRunRate(sDb, currentFilterConfig);

    // Executive Dashboard: Pace, Alerts, Margin & Partner Health Matrix
    if (typeof renderExecutiveDashboard === 'function') {
        renderExecutiveDashboard(sDb, pDb, db, dbPartners, currentFilterConfig, rawDebtorsList);
    }

    renderDashTables(sDb);
    let y, m;
    if (currentFilterConfig.mode === 'month') {
        let p = currentFilterConfig.month.split('-'); y = parseInt(p[0]); m = parseInt(p[1]) - 1;
    } else if (currentFilterConfig.mode === 'custom' && currentFilterConfig.from) {
        y = currentFilterConfig.from.getFullYear(); m = currentFilterConfig.from.getMonth();
    } else {
        let n = new Date(); y = n.getFullYear(); m = n.getMonth();
    }

    updateLineChart('chartPartners', null, 'Partners', sDb, pDb, y, m);
    updateLineChart('chartNewAuto', null, 'Новые авто', sDb, pDb, y, m);
    updatePieChart('pieBrands', null, getTopBrands(sDb), 'Сплит по брендам');
    updatePieChart('pieB2C', null, getB2CSplit(sDb), 'Тип сделки B2C');

    renderDynamicsTab(sDb, pDb, currentFilterConfig.mode === 'all');
    renderDynMonthsTab(sDb, currentFilterConfig.mode === 'all', currentFilterConfig.mode === 'month' ? currentFilterConfig.month : null);
    renderPartnersTable(currentFilterConfig);
    renderManagersTable(sDb, pDb);
    renderWaitingTable(currentFilterConfig);
    renderDebtorsTable(currentFilterConfig);

    // Regional heatmap & modules
    if (typeof updateHeatmap === 'function') updateHeatmap(sDb);
    if (typeof renderLeadGeoTab === 'function') renderLeadGeoTab();
    if (typeof renderKamTab === 'function') renderKamTab(currentFilterConfig);

    initTableSorting();
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ====================================================================
// Plan vs Fact KPI Progress Bars
// ====================================================================
function updatePlanVsFact(totalDeals, totalRevenue, totalPrice) {
    const container = document.getElementById('planVsFactRow');
    if (!container) return;

    const now = new Date();
    const daysLeft = Math.max(0, Math.ceil((Q3_TARGETS.q3End - now) / 86400000));
    const q3DaysPassed = Math.ceil((now - Q3_TARGETS.q3Start) / 86400000);
    const q3TotalDays = Math.ceil((Q3_TARGETS.q3End - Q3_TARGETS.q3Start) / 86400000);

    // ALL months data for Q3 cumulative
    const allQ3Sales = db.filter(r => {
        if (r.SaleQty <= 0) return false;
        const sm = r.SaleMonth;
        return sm === '2026-07' || sm === '2026-08' || sm === '2026-09';
    });
    const q3Deals = allQ3Sales.length;
    const q3Revenue = allQ3Sales.reduce((s, r) => s + (r.Revenue || 0), 0);
    const q3Price = allQ3Sales.reduce((s, r) => s + (r.Price || 0), 0);
    const q3TR = q3Price > 0 ? (q3Revenue / q3Price * 100) : 0;

    const dealsPct = Math.min(100, (q3Deals / Q3_TARGETS.deals * 100));
    const revPct = Math.min(100, (q3Revenue / Q3_TARGETS.revenue * 100));
    const trPct = Math.min(100, (q3TR / Q3_TARGETS.trPercent * 100));

    const dealsPerDay = q3DaysPassed > 0 ? (q3Deals / q3DaysPassed) : 0;
    const revPerDay = q3DaysPassed > 0 ? (q3Revenue / q3DaysPassed) : 0;
    const dealsNeeded = Q3_TARGETS.deals - q3Deals;
    const revNeeded = Q3_TARGETS.revenue - q3Revenue;

    const dealsColor = dealsPct >= 90 ? '#22c55e' : (dealsPct >= 60 ? '#f59e0b' : '#ef4444');
    const revColor = revPct >= 90 ? '#22c55e' : (revPct >= 60 ? '#f59e0b' : '#ef4444');
    const trColor = trPct >= 95 ? '#22c55e' : (trPct >= 80 ? '#f59e0b' : '#ef4444');

    container.innerHTML = `
        <div class="kpi-card border-l-4 bg-white !mb-0" style="border-color: ${dealsColor}">
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Сделки Q3 (Факт / План)</p>
            <p class="text-xl font-black text-gray-800 mt-0.5">${fmtNum(q3Deals)} <span class="text-sm font-semibold text-gray-400">/ ${fmtNum(Q3_TARGETS.deals)}</span></p>
            <div class="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div class="h-2.5 rounded-full transition-all duration-500" style="width: ${dealsPct}%; background: ${dealsColor}"></div>
            </div>
            <div class="flex justify-between items-center mt-1.5">
                <span class="text-[10px] font-bold" style="color: ${dealsColor}">${dealsPct.toFixed(1)}%</span>
                <span class="text-[10px] text-gray-400">🏁 ${daysLeft} дн. | ${dealsPerDay.toFixed(0)}/день</span>
            </div>
        </div>

        <div class="kpi-card border-l-4 bg-white !mb-0" style="border-color: ${revColor}">
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Выручка Q3 (Факт / План)</p>
            <p class="text-xl font-black text-gray-800 mt-0.5">${fmtMln(q3Revenue)} <span class="text-sm font-semibold text-gray-400">/ ${fmtMln(Q3_TARGETS.revenue)}</span></p>
            <div class="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div class="h-2.5 rounded-full transition-all duration-500" style="width: ${revPct}%; background: ${revColor}"></div>
            </div>
            <div class="flex justify-between items-center mt-1.5">
                <span class="text-[10px] font-bold" style="color: ${revColor}">${revPct.toFixed(1)}%</span>
                <span class="text-[10px] text-gray-400">🎯 +${fmtMln(revPerDay)}/день</span>
            </div>
        </div>

        <div class="kpi-card border-l-4 bg-white !mb-0" style="border-color: ${trColor}">
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Take Rate Q3 (Факт / Цель)</p>
            <p class="text-xl font-black text-gray-800 mt-0.5">${q3TR.toFixed(2)}% <span class="text-sm font-semibold text-gray-400">/ ${Q3_TARGETS.trPercent}%</span></p>
            <div class="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div class="h-2.5 rounded-full transition-all duration-500" style="width: ${trPct}%; background: ${trColor}"></div>
            </div>
            <div class="flex justify-between items-center mt-1.5">
                <span class="text-[10px] font-bold" style="color: ${trColor}">${trPct.toFixed(1)}%</span>
                <span class="text-[10px] text-gray-400">${q3TR >= Q3_TARGETS.trPercent ? '✅ В целевом коридоре' : '⚠️ Ниже цели'}</span>
            </div>
        </div>
    `;
}

// ====================================================================
// Top KPI Card Plans & Progress Bars
// ====================================================================
function updateTopKpiPlans(tS, tP, curAvgCheck, curArpu, revTotal) {
    let targetSales = 1592;
    let targetPrepays = 1592;
    let targetCheck = 2600000;
    let targetArpu = 37167;
    let targetRev = 59170000;

    if (currentFilterConfig.mode === 'month' && currentFilterConfig.month) {
        if (currentFilterConfig.month === '2026-08') {
            targetSales = 1592;
            targetPrepays = 1592;
            targetCheck = 2600000;
            targetArpu = 37167;
            targetRev = 59170000;
        } else if (currentFilterConfig.month === '2026-07') {
            targetSales = 1500;
            targetPrepays = 1500;
            targetCheck = 2600000;
            targetArpu = 35667;
            targetRev = 53500000;
        } else {
            targetSales = Math.round(Q3_TARGETS.deals / 3);
            targetPrepays = Math.round(Q3_TARGETS.deals / 3);
            targetCheck = Q3_TARGETS.avgCheck;
            targetArpu = Math.round(Q3_TARGETS.revenue / Q3_TARGETS.deals);
            targetRev = Math.round(Q3_TARGETS.revenue / 3);
        }
    } else if (currentFilterConfig.mode === 'all') {
        targetSales = Q3_TARGETS.deals; // 5000
        targetPrepays = Q3_TARGETS.deals; // 5000
        targetCheck = Q3_TARGETS.avgCheck; // 2.6M
        targetArpu = Math.round(Q3_TARGETS.revenue / Q3_TARGETS.deals); // 34 000
        targetRev = Q3_TARGETS.revenue; // 170M
    }

    // 1. Sales
    const salesPct = targetSales > 0 ? (tS / targetSales * 100) : 0;
    const salesColor = salesPct >= 90 ? '#22c55e' : (salesPct >= 60 ? '#3b82f6' : '#f59e0b');
    const elSalesPlan = document.getElementById('kpiSalesPlan');
    if (elSalesPlan) {
        elSalesPlan.innerHTML = `
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, salesPct)}%; background: ${salesColor}"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] mt-1 text-gray-400">
                <span>План: <b class="text-gray-600">${fmtNum(targetSales)}</b></span>
                <span class="font-bold" style="color: ${salesColor}">${salesPct.toFixed(1)}%</span>
            </div>
        `;
    }

    // 2. Prepays
    const prepaysPct = targetPrepays > 0 ? (tP / targetPrepays * 100) : 0;
    const prepaysColor = prepaysPct >= 90 ? '#22c55e' : (prepaysPct >= 60 ? '#f97316' : '#f59e0b');
    const elPrepaysPlan = document.getElementById('kpiPrepaysPlan');
    if (elPrepaysPlan) {
        elPrepaysPlan.innerHTML = `
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, prepaysPct)}%; background: ${prepaysColor}"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] mt-1 text-gray-400">
                <span>План: <b class="text-gray-600">${fmtNum(targetPrepays)}</b></span>
                <span class="font-bold" style="color: ${prepaysColor}">${prepaysPct.toFixed(1)}%</span>
            </div>
        `;
    }

    // 3. Avg Check
    const checkPct = targetCheck > 0 ? (curAvgCheck / targetCheck * 100) : 0;
    const checkColor = checkPct >= 100 ? '#22c55e' : (checkPct >= 90 ? '#8b5cf6' : '#f59e0b');
    const elCheckPlan = document.getElementById('kpiCheckPlan');
    if (elCheckPlan) {
        elCheckPlan.innerHTML = `
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, checkPct)}%; background: ${checkColor}"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] mt-1 text-gray-400">
                <span>План: <b class="text-gray-600">${fmtMln(targetCheck)}</b></span>
                <span class="font-bold" style="color: ${checkColor}">${checkPct.toFixed(1)}%</span>
            </div>
        `;
    }

    // 4. ARPU
    const arpuPct = targetArpu > 0 ? (curArpu / targetArpu * 100) : 0;
    const arpuColor = arpuPct >= 100 ? '#22c55e' : (arpuPct >= 90 ? '#10b981' : '#f59e0b');
    const elArpuPlan = document.getElementById('kpiArpuPlan');
    if (elArpuPlan) {
        elArpuPlan.innerHTML = `
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, arpuPct)}%; background: ${arpuColor}"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] mt-1 text-gray-400">
                <span>План: <b class="text-gray-600">${fmtNum(targetArpu)} ₽</b></span>
                <span class="font-bold" style="color: ${arpuColor}">${arpuPct.toFixed(1)}%</span>
            </div>
        `;
    }

    // 5. Total Revenue
    const revPct = targetRev > 0 ? (revTotal / targetRev * 100) : 0;
    const revColor = revPct >= 90 ? '#22c55e' : (revPct >= 60 ? '#10b981' : '#f59e0b');
    const elRevPlan = document.getElementById('kpiRevPlan');
    if (elRevPlan) {
        elRevPlan.innerHTML = `
            <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, revPct)}%; background: ${revColor}"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] mt-1 text-gray-400">
                <span>План: <b class="text-gray-600">${fmtMln(targetRev)}</b></span>
                <span class="font-bold" style="color: ${revColor}">${revPct.toFixed(1)}%</span>
            </div>
        `;
    }
}

// ====================================================================
// Linear Run Rate KPI Card (Deals & Revenue)
// ====================================================================
function updateRunRate(sDb, filterConfig) {
    const container = document.getElementById('runRateRow');
    if (!container) return;

    let year = 2026, monthNum = 8, monthStr = '2026-08', periodTitle = 'Август 2026';
    let daysInMonth = 31, daysPassed = 1;

    if (filterConfig.mode === 'month' && filterConfig.month) {
        monthStr = filterConfig.month;
        const parts = monthStr.split('-');
        year = parseInt(parts[0]);
        monthNum = parseInt(parts[1]);
        daysInMonth = new Date(year, monthNum, 0).getDate();
        periodTitle = formatMonthLabel(monthStr).replace('📅 ', '');
    } else if (filterConfig.mode === 'custom' && filterConfig.from && filterConfig.to) {
        const f = filterConfig.from;
        const t = filterConfig.to;
        const diffDays = Math.max(1, Math.round((t - f) / 86400000) + 1);
        daysInMonth = diffDays;
        daysPassed = diffDays;
        periodTitle = `${formatDateDMY(f.getTime())} — ${formatDateDMY(t.getTime())}`;
    } else {
        // Mode 'all': default to latest active month
        const months = Array.from(new Set(db.map(r => r.SaleMonth).filter(Boolean))).sort();
        monthStr = months[months.length - 1] || '2026-08';
        const parts = monthStr.split('-');
        year = parseInt(parts[0]);
        monthNum = parseInt(parts[1]);
        daysInMonth = new Date(year, monthNum, 0).getDate();
        periodTitle = `${formatMonthLabel(monthStr).replace('📅 ', '')} (Текущий месяц)`;
    }

    let targetSales = sDb;
    if (filterConfig.mode === 'all') {
        targetSales = db.filter(r => r.SaleQty > 0 && r.SaleMonth === monthStr);
    }

    // Determine max day with deals in dataset for this month
    let maxDayInMonth = 0;
    targetSales.forEach(r => {
        const d = excelToJSDate(r.DealDate);
        if (d && d.getFullYear() === year && (d.getMonth() + 1) === monthNum) {
            if (d.getDate() > maxDayInMonth) maxDayInMonth = d.getDate();
        }
    });

    const now = new Date();
    const isThisCurrentMonth = (now.getFullYear() === year && (now.getMonth() + 1) === monthNum);

    if (filterConfig.mode === 'custom') {
        daysPassed = daysInMonth;
    } else if (isThisCurrentMonth || maxDayInMonth < daysInMonth) {
        daysPassed = maxDayInMonth > 0 ? Math.min(daysInMonth, maxDayInMonth) : Math.min(daysInMonth, now.getDate());
    } else {
        daysPassed = daysInMonth;
    }

    const dealsFact = targetSales.length;
    const revFact = targetSales.reduce((sum, r) => sum + (r.Revenue || 0), 0);
    const priceFact = targetSales.reduce((sum, r) => sum + (r.Price || 0), 0);

    const dealsPace = daysPassed > 0 ? (dealsFact / daysPassed) : 0;
    const revPace = daysPassed > 0 ? (revFact / daysPassed) : 0;

    const dealsRunRate = Math.round(dealsPace * daysInMonth);
    const revRunRate = revPace * daysInMonth;

    const dealsRem = Math.max(0, dealsRunRate - dealsFact);
    const revRem = Math.max(0, revRunRate - revFact);

    const daysLeft = Math.max(0, daysInMonth - daysPassed);
    const pctPassed = Math.min(100, Math.max(0, (daysPassed / daysInMonth) * 100));

    const arpuFact = dealsFact > 0 ? (revFact / dealsFact) : 0;
    const arpuRunRate = dealsRunRate > 0 ? (revRunRate / dealsRunRate) : arpuFact;
    const avgCheckFact = dealsFact > 0 ? (priceFact / dealsFact) : 0;

    // Monthly Target (Budget 1592 deals, 59.17M for Aug / 1500 for Jul / Q3 target / 3)
    const targetMonthDeals = (monthStr === '2026-08') ? 1592 : ((monthStr === '2026-07') ? 1500 : Math.round(Q3_TARGETS.deals / 3));
    const targetMonthRev = (monthStr === '2026-08') ? 59170000 : ((monthStr === '2026-07') ? 53500000 : (Q3_TARGETS.revenue / 3));

    const dealsPlanPct = targetMonthDeals > 0 ? (dealsRunRate / targetMonthDeals * 100) : 100;
    const revPlanPct = targetMonthRev > 0 ? (revRunRate / targetMonthRev * 100) : 100;

    container.innerHTML = `
        <div class="card !p-4 bg-white rounded-2xl shadow-sm border border-gray-200 mb-5">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center pb-3 mb-3 border-b border-gray-100 gap-2">
                <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
                        <i data-lucide="trending-up" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <h2 class="text-base font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                            Линейный Run Rate: ${periodTitle}
                        </h2>
                    </div>
                </div>
                <div class="flex items-center gap-2 flex-wrap">
                    <span class="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold flex items-center gap-1">
                        <i data-lucide="calendar" class="w-3.5 h-3.5"></i> Прошло ${daysPassed} из ${daysInMonth} дн. (${pctPassed.toFixed(1)}%)
                    </span>
                    <span class="px-2.5 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-bold flex items-center gap-1">
                        <i data-lucide="clock" class="w-3.5 h-3.5"></i> ${daysLeft > 0 ? `Осталось ${daysLeft} дн.` : 'Период завершен'}
                    </span>
                </div>
            </div>

            <!-- 3 RUN RATE CARDS (Light Dashboard Theme) -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- CARD 1: DEALS RUN RATE -->
                <div class="bg-gray-50/80 border border-gray-200 rounded-xl p-3.5 flex flex-col justify-between hover:border-blue-300 transition">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] uppercase font-bold text-gray-400 tracking-wider flex items-center gap-1">
                                <i data-lucide="shopping-cart" class="w-3.5 h-3.5 text-blue-600"></i> Ранрейт Сделок (Прогноз)
                            </span>
                            <span class="text-xs font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                                ${dealsPlanPct.toFixed(1)}% плана
                            </span>
                        </div>
                        <div class="flex items-baseline gap-2 mt-1">
                            <span class="text-2xl font-black text-gray-800">${fmtNum(dealsRunRate)}</span>
                            <span class="text-xs text-gray-400 font-medium">шт. к концу месяца</span>
                        </div>
                    </div>

                    <div class="mt-3 pt-2.5 border-t border-gray-200/80 text-[11px] space-y-1.5">
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Текущий факт:</span>
                            <b class="text-gray-800">${fmtNum(dealsFact)} шт.</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Прогноз остатка:</span>
                            <b class="text-blue-600 font-bold">+${fmtNum(dealsRem)} шт.</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Текущий темп:</span>
                            <b class="text-amber-600 font-bold">${dealsPace.toFixed(1)} шт./день</b>
                        </div>
                        <!-- Progress bar -->
                        <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                            <div class="bg-blue-600 h-1.5 rounded-full" style="width: ${Math.min(100, (dealsFact / Math.max(1, dealsRunRate) * 100))}%;"></div>
                        </div>
                    </div>
                </div>

                <!-- CARD 2: REVENUE RUN RATE -->
                <div class="bg-gray-50/80 border border-gray-200 rounded-xl p-3.5 flex flex-col justify-between hover:border-emerald-300 transition">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] uppercase font-bold text-gray-400 tracking-wider flex items-center gap-1">
                                <i data-lucide="coins" class="w-3.5 h-3.5 text-emerald-600"></i> Ранрейт Выручки (Прогноз)
                            </span>
                            <span class="text-xs font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700">
                                ${revPlanPct.toFixed(1)}% плана
                            </span>
                        </div>
                        <div class="flex items-baseline gap-2 mt-1">
                            <span class="text-2xl font-black text-emerald-700">${fmtMln(revRunRate)}</span>
                            <span class="text-xs text-gray-400 font-medium">без НДС</span>
                        </div>
                    </div>

                    <div class="mt-3 pt-2.5 border-t border-gray-200/80 text-[11px] space-y-1.5">
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Текущий факт:</span>
                            <b class="text-gray-800">${fmtMln(revFact)}</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Прогноз остатка:</span>
                            <b class="text-emerald-600 font-bold">+${fmtMln(revRem)}</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Текущий темп:</span>
                            <b class="text-amber-600 font-bold">+${fmtMln(revPace)}/день</b>
                        </div>
                        <!-- Progress bar -->
                        <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                            <div class="bg-emerald-600 h-1.5 rounded-full" style="width: ${Math.min(100, (revFact / Math.max(1, revRunRate) * 100))}%;"></div>
                        </div>
                    </div>
                </div>

                <!-- CARD 3: ARPU & AVERAGE CHECK -->
                <div class="bg-gray-50/80 border border-gray-200 rounded-xl p-3.5 flex flex-col justify-between hover:border-purple-300 transition">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] uppercase font-bold text-gray-400 tracking-wider flex items-center gap-1">
                                <i data-lucide="receipt" class="w-3.5 h-3.5 text-purple-600"></i> Эффективность & Чек
                            </span>
                            <span class="text-xs font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">
                                Ориентир
                            </span>
                        </div>
                        <div class="flex items-baseline gap-2 mt-1">
                            <span class="text-2xl font-black text-purple-700">${fmtNum(arpuRunRate)} ₽</span>
                            <span class="text-xs text-gray-400 font-medium">ARPU прогноз</span>
                        </div>
                    </div>

                    <div class="mt-3 pt-2.5 border-t border-gray-200/80 text-[11px] space-y-1.5">
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">Средний чек сделки:</span>
                            <b class="text-gray-800">${fmtMln(avgCheckFact)}</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">План сделок месяца:</span>
                            <b class="text-gray-700 font-bold">${fmtNum(targetMonthDeals)} шт.</b>
                        </div>
                        <div class="flex justify-between text-gray-600">
                            <span class="text-gray-400">План выручки месяца:</span>
                            <b class="text-gray-700 font-bold">${fmtMln(targetMonthRev)}</b>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                            <div class="bg-purple-600 h-1.5 rounded-full" style="width: ${Math.min(100, pctPassed)}%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    const targetEl = document.getElementById(tabId);
    if (targetEl) targetEl.classList.remove('hidden');
    if (btn) btn.classList.add('active');
    if (tabId === 'tab-funnel' && typeof selectFunnelBrand === 'function') selectFunnelBrand('ALL');
    if (tabId === 'tab-lead-geo' && typeof renderLeadGeoTab === 'function') renderLeadGeoTab();
    if (tabId === 'tab-kam' && typeof renderKamTab === 'function') renderKamTab(currentFilterConfig);
    if (tabId === 'tab-banking' && typeof renderBankingDashboard === 'function') renderBankingDashboard();
    if (tabId === 'tab-details') {
        const sInput = document.getElementById('searchDebtors');
        if (sInput) {
            sInput.value = '';
            if (typeof filterDebtorsTable === 'function') filterDebtorsTable('');
        }
        if (typeof renderDebtorsTable === 'function') renderDebtorsTable(currentFilterConfig);
        if (typeof renderWaitingTable === 'function') renderWaitingTable(currentFilterConfig);
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
}
