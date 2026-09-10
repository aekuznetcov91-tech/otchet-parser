/* ====================================================================
 * B2C Analytics Dashboard — Charts & Dashboard Visualizations
 * ====================================================================*/

/**
 * Renders brand split table and B2C split table into #tableDashBrands and #tableDashB2C
 * @param {Array} sDb - Filtered sales database
 */
function renderDashTables(sDb) {
    const safeStr = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    function getChannelKey(b2c) {
        const raw = (b2c || '').toString().trim().toLowerCase();
        if (raw.includes('мп2') || raw === 'мп 2') return 'opt';
        if (raw.includes('фдц') || raw.includes('гп')) return 'fdc';
        if (raw.includes('лид') || raw.includes('b2c') || raw.includes('розниц')) return 'retail';
        if (raw.includes('online') || raw.includes('онлайн')) return 'online';
        if (raw.includes('мп1') || raw.includes('мп3')) return 'other';
        return 'opt';
    }

    const brandMap = {};
    const totChannels = { opt: 0, fdc: 0, retail: 0, online: 0, other: 0, total: 0 };
    const b2cMap = {};

    sDb.forEach(r => {
        let b = (r.Brand || 'Другие').trim();
        if (b === 'SOUEAS') b = 'SOUEAST';
        const ch = getChannelKey(r.B2C);

        if (!brandMap[b]) {
            brandMap[b] = { brand: b, total: 0, opt: 0, fdc: 0, retail: 0, online: 0, other: 0 };
        }
        brandMap[b].total++;
        brandMap[b][ch]++;
        totChannels.total++;
        totChannels[ch]++;

        const b2cLabel = r.B2C || '(пусто)';
        b2cMap[b2cLabel] = (b2cMap[b2cLabel] || 0) + 1;
    });

    const sortedBrands = Object.values(brandMap).sort((a, b) => b.total - a.total);

    let brHtml = `
        <div class="overflow-x-auto max-h-[300px] overflow-y-auto">
            <table class="min-w-full text-xs" style="font-size: 11px;">
                <thead class="sticky top-0 bg-white z-10 shadow-sm">
                    <tr class="border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                        <th class="text-left py-2 px-2">Марка авто</th>
                        <th class="text-right py-2 px-2 font-black text-slate-800">Всего</th>
                        <th class="text-right py-2 px-1.5 text-blue-700 bg-blue-50/50" title="Опт МП2">Опт</th>
                        <th class="text-right py-2 px-1.5 text-purple-700 bg-purple-50/50" title="Фронт-ДЦ / Гарантия платежа">ФДЦ</th>
                        <th class="text-right py-2 px-1.5 text-emerald-700 bg-emerald-50/50" title="Розница (B2C / Лиды)">B2C</th>
                        <th class="text-right py-2 px-1.5 text-cyan-700 bg-cyan-50/50" title="Online продажи">Online</th>
                        <th class="text-right py-2 px-1.5 text-slate-500 bg-slate-50/50" title="Прочие (МП1/3)">Проч.</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    ${sortedBrands.map(x => `
                        <tr class="hover:bg-slate-50 transition">
                            <td class="font-bold py-1 px-2 text-slate-800 whitespace-nowrap">${safeStr(x.brand)}</td>
                            <td class="text-right py-1 px-2 font-black text-slate-900">${fmtNum(x.total)}</td>
                            <td class="text-right py-1 px-1.5 ${x.opt > 0 ? 'font-bold text-blue-700' : 'text-slate-300'}">${x.opt > 0 ? fmtNum(x.opt) : '·'}</td>
                            <td class="text-right py-1 px-1.5 ${x.fdc > 0 ? 'font-bold text-purple-700' : 'text-slate-300'}">${x.fdc > 0 ? fmtNum(x.fdc) : '·'}</td>
                            <td class="text-right py-1 px-1.5 ${x.retail > 0 ? 'font-bold text-emerald-700' : 'text-slate-300'}">${x.retail > 0 ? fmtNum(x.retail) : '·'}</td>
                            <td class="text-right py-1 px-1.5 ${x.online > 0 ? 'font-bold text-cyan-700' : 'text-slate-300'}">${x.online > 0 ? fmtNum(x.online) : '·'}</td>
                            <td class="text-right py-1 px-1.5 ${x.other > 0 ? 'font-bold text-slate-600' : 'text-slate-300'}">${x.other > 0 ? fmtNum(x.other) : '·'}</td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot class="sticky bottom-0 bg-slate-100 font-bold border-t-2 border-slate-300 text-[11px]">
                    <tr>
                        <td class="py-1.5 px-2 text-slate-900 font-black">Общий итог</td>
                        <td class="text-right py-1.5 px-2 font-black text-slate-900">${fmtNum(totChannels.total)}</td>
                        <td class="text-right py-1.5 px-1.5 font-black text-blue-800">${fmtNum(totChannels.opt)}</td>
                        <td class="text-right py-1.5 px-1.5 font-black text-purple-800">${fmtNum(totChannels.fdc)}</td>
                        <td class="text-right py-1.5 px-1.5 font-black text-emerald-800">${fmtNum(totChannels.retail)}</td>
                        <td class="text-right py-1.5 px-1.5 font-black text-cyan-800">${fmtNum(totChannels.online)}</td>
                        <td class="text-right py-1.5 px-1.5 font-black text-slate-700">${fmtNum(totChannels.other)}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;

    const elDashBrands = document.getElementById('tableDashBrands');
    if (elDashBrands) elDashBrands.innerHTML = brHtml;

    // B2C table with share percentages
    let sortedB2C = Object.entries(b2cMap).sort((a, b) => b[1] - a[1]);
    let totB2C = sortedB2C.reduce((s, x) => s + x[1], 0);
    let b2cHtml = `
        <div class="overflow-x-auto max-h-[300px] overflow-y-auto">
            <table class="min-w-full text-xs" style="font-size: 11px;">
                <thead class="sticky top-0 bg-white z-10 shadow-sm">
                    <tr class="border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                        <th class="text-left py-2 px-2">Тип сделки B2C</th>
                        <th class="text-right py-2 px-2 font-black text-slate-800">Количество</th>
                        <th class="text-right py-2 px-2 text-slate-500">Доля (%)</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    ${sortedB2C.map(x => `
                        <tr class="hover:bg-slate-50 transition">
                            <td class="font-bold py-1 px-2 text-slate-800">${safeStr(x[0])}</td>
                            <td class="text-right py-1 px-2 font-black text-slate-900">${fmtNum(x[1])}</td>
                            <td class="text-right py-1 px-2 text-slate-600 font-medium">${totB2C > 0 ? fmtPct(x[1] / totB2C) : '0%'}</td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot class="sticky bottom-0 bg-slate-100 font-bold border-t-2 border-slate-300 text-[11px]">
                    <tr>
                        <td class="py-1.5 px-2 text-slate-900 font-black">Общий итог</td>
                        <td class="text-right py-1.5 px-2 font-black text-slate-900">${fmtNum(totB2C)}</td>
                        <td class="text-right py-1.5 px-2 font-black text-slate-900">100%</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;

    const elDashB2C = document.getElementById('tableDashB2C');
    if (elDashB2C) elDashB2C.innerHTML = b2cHtml;
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
    const ctx = canvas.getContext('2d');
    if (window[canvasId + 'Inst']) window[canvasId + 'Inst'].destroy();

    const labels = dataEntries.map(e => e[0]);
    const dataValues = dataEntries.map(e => e[1]);
    const total = dataValues.reduce((a, b) => a + b, 0);

    const colors = MODERN_PALETTE.slice(0, dataEntries.length);
    while (colors.length < dataEntries.length) {
        colors.push('#' + Math.floor(Math.random()*16777215).toString(16));
    }

    window[canvasId + 'Inst'] = new Chart(ctx, {
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

    let ctx = canvas.getContext('2d');
    if (canvas._chartInstance) canvas._chartInstance.destroy();

    canvas._chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                { label: 'Выходные', data: sW, type: 'bar', backgroundColor: 'rgba(200, 200, 200, 0.25)', barPercentage: 1.0, categoryPercentage: 1.0, order: 3, datalabels: { display: false } },
                { label: 'Сделки', data: dataSales, borderColor: '#2563eb', backgroundColor: '#2563eb', tension: 0.1, fill: false, order: 1, datalabels: { align: 'top', font: { weight: 'bold', size: 10 } } },
                { label: 'Предоплаты', data: dataPrepays, borderColor: '#f97316', backgroundColor: '#f97316', tension: 0.1, fill: false, order: 2, datalabels: { align: 'bottom', font: { weight: 'bold', size: 10 } } }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' }, tooltip: { mode: 'index', intersect: false } },
            scales: { y: { beginAtZero: true, max: wH } }
        }
    });
}
