/* ====================================================================
 * B2C Analytics Dashboard — Charts & Dashboard Visualizations
 * ====================================================================*/

/**
 * Renders brand split table and B2C split table into #tableDashBrands and #tableDashB2C
 * @param {Array} sDb - Filtered sales database
 */
function renderDashTables(sDb) {
    let br = {}, b2c = {};
    sDb.forEach(r => { br[r.Brand] = (br[r.Brand]||0)+1; b2c[r.B2C||"(пусто)"] = (b2c[r.B2C||"(пусто)"]||0)+1; });
    const makeHtml = (dict, t1, t2) => {
        let sorted = Object.entries(dict).sort((a,b)=>b[1]-a[1]);
        let tot = sorted.reduce((s,x)=>s+x[1],0);
        let h = `<table><thead><tr><th>${t1}</th><th>${t2}</th></tr></thead><tbody>`;
        sorted.forEach(x => h+=`<tr><td class="font-bold">${x[0]}</td><td>${fmtNum(x[1])}</td></tr>`);
        return h + `<tr><td class="table-subtotal">Общий итог</td><td class="table-subtotal">${fmtNum(tot)}</td></tr></tbody></table>`;
    };
    const elDashBrands = document.getElementById('tableDashBrands');
    if (elDashBrands) elDashBrands.innerHTML = makeHtml(br, "Марка авто", "Количество");
    const elDashB2C = document.getElementById('tableDashB2C');
    if (elDashB2C) elDashB2C.innerHTML = makeHtml(b2c, "Тип сделки B2C", "Количество");
}

/**
 * Returns top 7 brands + 'Прочие'
 * @param {Array} salesDb - Sales records array
 * @returns {Array<[string, number]>}
 */
function getTopBrands(salesDb) {
    const aux = ["ВНЕСЕНИЕ", "АВАНС", "КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП", "СЕРВИС", "ФИНАНС", "ДОГОВОР", "ОФОРМЛЕН", "КОМИСС", "УСЛУГ", "НЕИЗВЕСТН", "ДРУГИЕ", "NULL", "UNDEFINED"];
    let counts = {};
    salesDb.forEach(r => {
        let b = r.Brand;
        if (!b || b === 'null' || b === 'undefined' || b === 'Другие' || aux.some(k => String(b).toUpperCase().includes(k))) return;
        counts[b] = (counts[b] || 0) + 1;
    });
    let sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
    let top = sorted.slice(0,7), others = sorted.slice(7).reduce((sum,item)=>sum+item[1],0);
    if (others > 0) top.push(["Прочие", others]);
    return top;
}

/**
 * Returns top 7 B2C types + 'Прочие'
 * @param {Array} salesDb - Sales records array
 * @returns {Array<[string, number]>}
 */
function getB2CSplit(salesDb) {
    let counts = {};
    salesDb.forEach(r => counts[r.B2C||"(пусто)"] = (counts[r.B2C||"(пусто)"]||0)+1);
    let sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
    let top = sorted.slice(0,7), others = sorted.slice(7).reduce((sum,item)=>sum+item[1],0);
    if (others > 0) top.push(["Прочие", others]);
    return top;
}

/**
 * Creates/updates Chart.js pie chart with custom HTML legend
 * @param {string} canvasId - HTML canvas element ID
 * @param {object} chartInst - Unused/legacy chart reference
 * @param {Array<[string, number]>} dataEntries - Key/value pairs for the chart
 * @param {string} titleText - Title text
 */
function updatePieChart(canvasId, chartInst, dataEntries, titleText) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Safely destroy existing chart instance if canvas is already bound
    const existing = (typeof Chart !== 'undefined' && Chart.getChart(canvas)) || window[canvasId + 'Inst'] || canvas._chartInstance;
    if (existing) {
        try { existing.destroy(); } catch (e) { console.warn('Error destroying chart on canvas ' + canvasId, e); }
    }

    if (!dataEntries || dataEntries.length === 0) {
        dataEntries = [["(нет данных)", 0]];
    }

    const labels = dataEntries.map(e => e[0]);
    const dataValues = dataEntries.map(e => e[1]);
    const total = dataValues.reduce((a, b) => a + b, 0);

    const colors = MODERN_PALETTE.slice(0, dataEntries.length);
    while (colors.length < dataEntries.length) {
        colors.push('#' + Math.floor(Math.random()*16777215).toString(16));
    }

    const ctx = canvas.getContext('2d');
    const newChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.parsed;
                            const pct = total > 0 ? ((val / total) * 100).toFixed(1) + '%' : '0%';
                            return ` ${context.label}: ${fmtNum(val)} шт (${pct})`;
                        }
                    }
                },
                datalabels: {
                    color: '#ffffff',
                    font: { weight: '900', size: 12 },
                    textShadowColor: 'rgba(0, 0, 0, 0.4)',
                    textShadowBlur: 4,
                    formatter: (value) => {
                        if (total === 0 || value === 0) return '';
                        const pct = (value / total) * 100;
                        return pct >= 3.5 ? pct.toFixed(0) + '%' : '';
                    }
                }
            }
        }
    });

    window[canvasId + 'Inst'] = newChart;
    canvas._chartInstance = newChart;

    // Render Custom Legend on the Right
    const legendContainerId = canvasId === 'pieBrands' ? 'legendPieBrands' : 'legendPieB2C';
    const legendEl = document.getElementById(legendContainerId);
    if (legendEl) {
        let legHtml = '<div class="space-y-1">';
        dataEntries.forEach((item, idx) => {
            const label = item[0];
            const val = item[1];
            const pct = total > 0 ? ((val / total) * 100).toFixed(1) + '%' : '0%';
            const color = colors[idx];
            legHtml += `
                <div class="chart-legend-item flex items-center justify-between text-xs py-0.5 px-1.5 rounded hover:bg-gray-100 transition-colors">
                    <div class="flex items-center gap-1.5">
                        <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${color}"></span>
                        <span class="font-medium text-gray-700 break-words" title="${label}">${label}</span>
                    </div>
                    <div class="flex items-center gap-2 shrink-0 ml-2">
                        <span class="font-bold text-gray-800">${fmtNum(val)}</span>
                        <span class="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded font-semibold min-w-[42px] text-right">${pct}</span>
                    </div>
                </div>`;
        });
        legHtml += '</div>';
        legendEl.innerHTML = legHtml;
    }
}

/**
 * Creates/updates daily line chart with weekend bars
 * @param {string} canvasId - HTML canvas element ID
 * @param {object} chartInst - Unused/legacy chart reference
 * @param {string} groupName - Group name filter ('Partners', 'Новые авто', etc.)
 * @param {Array} salesDb - Sales records
 * @param {Array} prepayDb - Prepayments records
 * @param {number} year - Full year (e.g. 2026)
 * @param {number} month - 0-indexed month (0 = Jan, 11 = Dec)
 */
function updateLineChart(canvasId, chartInst, groupName, salesDb, prepayDb, year, month) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const labels = [], dataSales = [], dataPrepays = [], dataWeekends = [];
    let maxVal = 0;
    for (let d = 1; d <= daysInMonth; d++) {
        labels.push(`${d.toString().padStart(2, '0')}.${(month + 1).toString().padStart(2, '0')}`);
        let sC = salesDb.filter(r => { let date = excelToJSDate(r.DealDate); return r.ChartGroup === groupName && date && date.getDate()===d && date.getMonth()===month && date.getFullYear()===year; }).length;
        let pC = prepayDb.filter(r => { let date = excelToJSDate(r.PrepayDate); return r.ChartGroup === groupName && date && date.getDate()===d && date.getMonth()===month && date.getFullYear()===year; }).length;
        dataSales.push(sC); dataPrepays.push(pC);
        if (sC > maxVal) maxVal = sC; if (pC > maxVal) maxVal = pC;
        let jsDate = new Date(year, month, d); dataWeekends.push((jsDate.getDay() === 0 || jsDate.getDay() === 6) ? 1 : 0);
    }
    const wH = maxVal > 0 ? maxVal * 1.2 : 10;
    const sW = dataWeekends.map(w => w === 1 ? wH : 0);

    // Safely destroy existing chart instance if canvas is already bound
    const existing = (typeof Chart !== 'undefined' && Chart.getChart(canvas)) || canvas._chartInstance || window[canvasId + 'Inst'];
    if (existing) {
        try { existing.destroy(); } catch (e) { console.warn('Error destroying chart on canvas ' + canvasId, e); }
    }

    const ctx = canvas.getContext('2d');
    const newChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                { label: 'Выходные', data: sW, type: 'bar', backgroundColor: 'rgba(200, 200, 200, 0.25)', barPercentage: 1.0, categoryPercentage: 1.0, order: 3, datalabels: { display: false } },
                { label: 'Сделки', data: dataSales, borderColor: '#2563eb', backgroundColor: '#2563eb', tension: 0.1, fill: false, order: 1, datalabels: { align: 'top', font: { weight: 'bold', size: 10 }, formatter: (v) => v > 0 ? v : '' } },
                { label: 'Предоплаты', data: dataPrepays, borderColor: '#f97316', backgroundColor: '#f97316', tension: 0.1, fill: false, order: 2, datalabels: { align: 'bottom', font: { weight: 'bold', size: 10 }, formatter: (v) => v > 0 ? v : '' } }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' }, tooltip: { mode: 'index', intersect: false } },
            scales: { y: { beginAtZero: true, max: wH } }
        }
    });

    canvas._chartInstance = newChart;
    window[canvasId + 'Inst'] = newChart;
}
