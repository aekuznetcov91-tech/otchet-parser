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
        rawDebtorsList = data.debtors || [];
        if (data.brand_funnel) {
            window.brandFunnelFullData = data.brand_funnel;
            if (typeof funnelRawData !== 'undefined') {
                Object.assign(funnelRawData, data.brand_funnel);
            }
        }
        initDropdown();
        if (typeof initFunnelMonths === 'function') initFunnelMonths();
    } catch (error) {
        console.error("Ошибка загрузки data.json:", error);
        showToast("Ошибка загрузки data.json: " + error.message, 'error', 5000);
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

    // Plan vs Fact KPI
    updatePlanVsFact(tS, revTotal, pTot);

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

    // Regional heatmap
    if (typeof updateHeatmap === 'function') updateHeatmap(sDb);

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

function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    const targetEl = document.getElementById(tabId);
    if (targetEl) targetEl.classList.remove('hidden');
    if (btn) btn.classList.add('active');
    if (tabId === 'tab-funnel' && typeof selectFunnelBrand === 'function') selectFunnelBrand('ALL');
    if (typeof lucide !== 'undefined') lucide.createIcons();
}
