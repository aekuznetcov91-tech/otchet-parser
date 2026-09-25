/* ====================================================================
 * B2C Analytics Dashboard — Table Rendering & Interactions
 * ====================================================================*/

/**
 * Filters rows in a table container based on text query.
 * @param {HTMLInputElement} input
 * @param {string} targetId
 */
/**
 * Filters rows in a table container based on text query.
 * @param {HTMLInputElement} input
 * @param {string} targetId
 */
function filterTable(input, targetId) {
    let val = input.value.toLowerCase();
    let container = document.getElementById(targetId);
    if (!container) return;
    let table = container.querySelector('table') || container;
    if (table.tagName !== 'TABLE') { table = table.querySelector('table'); if (!table) return; }
    let rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        if (row.classList.contains('partner-deals-row')) return;
        let text = row.textContent.toLowerCase();
        let match = text.includes(val);
        row.style.display = match ? '' : 'none';
        let rowKey = row.dataset.partnerKey;
        if (rowKey) {
            let detailsRow = document.getElementById('pdeals_row_' + rowKey);
            if (detailsRow) {
                if (!match) {
                    detailsRow.style.display = 'none';
                } else if (!detailsRow.classList.contains('hidden')) {
                    detailsRow.style.display = '';
                }
            }
        }
    });
}

/**
 * Creates datalist autocomplete for search inputs based on table content.
 * @param {string} inputId
 * @param {string} targetContainerId
 */
function setupSmartSearch(inputId, targetContainerId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const container = document.getElementById(targetContainerId);
    if (!container) return;
    const table = container.querySelector('table') || (container.tagName === 'TABLE' ? container : null);
    if (!table) return;

    let listId = 'datalist_' + inputId;
    let dl = document.getElementById(listId);
    if (!dl) {
        dl = document.createElement('datalist');
        dl.id = listId;
        document.body.appendChild(dl);
    }
    input.setAttribute('list', listId);

    const uniqueValues = new Set();
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.querySelectorAll('td').forEach(td => {
            const text = td.textContent.trim();
            if (text && text.length > 1 && text.length < 50 && !/^[0-9\s₽%,.-]+$/.test(text)) {
                uniqueValues.add(text);
            }
        });
    });

    dl.innerHTML = '';
    Array.from(uniqueValues).sort().forEach(val => {
        const opt = document.createElement('option');
        opt.value = val;
        dl.appendChild(opt);
    });

    input.oninput = function() {
        filterTable(this, targetContainerId);
    };
}

/**
 * Renders Operational Dynamics and B2C Structure tables.
 * @param {Array} sDb Sales data
 * @param {Array} pDb Prepayment data
 * @param {boolean} isAll Whether all periods are selected
 */
function renderDynamicsTab(sDb, pDb, isAll) {
    const getNormalizedBrand = (r) => {
        let b = r.Brand || '';
        let m = (r.SaleMonth || r.PrepayMonth || '').replace("'", "");
        if (m >= '2026-09') {
            let ub = b.toUpperCase();
            if (ub === 'OMODA' || ub === 'JAECOO' || ub === 'OMODA & JAECOO') {
                return 'JELAND';
            }
        }
        return b;
    };

    let brands = Array.from(new Set(sDb.map(r => getNormalizedBrand(r)))).filter(b => b && b !== "ВНЕСЕНИЕ").sort();
    let b2cTypes = new Set(sDb.map(r => r.B2C || "(пусто)"));
    let b2cArr = Array.from(b2cTypes).sort();

    // Determine current and previous month for dynamics comparison
    let curMonthStr = (typeof currentFilterConfig !== 'undefined' && currentFilterConfig && currentFilterConfig.mode === 'month')
        ? currentFilterConfig.month
        : (sDb.length > 0 ? (sDb[0].SaleMonth || '').replace("'", "") : null);

    let prevMonthStr = null;
    if (curMonthStr && /^\d{4}-\d{2}$/.test(curMonthStr)) {
        let [y, m] = curMonthStr.split('-').map(Number);
        m--;
        if (m < 1) { m = 12; y--; }
        prevMonthStr = `${y}-${String(m).padStart(2, '0')}`;
    }

    // Determine if current month is in-progress (MTD: Month-To-Date comparison)
    let maxCurDay = 0;
    sDb.forEach(r => {
        let dt = typeof excelToJSDate === 'function' ? excelToJSDate(r.DealDate || r.SaleDate) : null;
        if (dt && dt.getDate() > maxCurDay) maxCurDay = dt.getDate();
    });

    let daysInCurMonth = 31;
    if (curMonthStr && /^\d{4}-\d{2}$/.test(curMonthStr)) {
        let [y, m] = curMonthStr.split('-').map(Number);
        daysInCurMonth = new Date(y, m, 0).getDate();
    }

    const isMtd = maxCurDay > 0 && maxCurDay < daysInCurMonth;

    let prevMonthKey = prevMonthStr ? prevMonthStr.split('-')[1] : '';
    let curMonthKey = curMonthStr ? curMonthStr.split('-')[1] : '';
    let prevMonthName = (typeof MONTH_NAMES_RU !== 'undefined' && MONTH_NAMES_RU[prevMonthKey]) || prevMonthStr || '';
    let curMonthName = (typeof MONTH_NAMES_RU !== 'undefined' && MONTH_NAMES_RU[curMonthKey]) || curMonthStr || '';

    const mtdTitleAttr = isMtd
        ? `title="MTD (с 1 по ${maxCurDay} число): сравнение с 1–${maxCurDay} ${prevMonthName}"`
        : `title="Сравнение с полным месяцем ${prevMonthName}"`;

    let prevSalesDb = [];
    if (prevMonthStr && typeof db !== 'undefined' && Array.isArray(db)) {
        prevSalesDb = db.filter(r => {
            if (r.SaleQty <= 0) return false;
            if ((r.SaleMonth || '').replace(/'/g, "") !== prevMonthStr) return false;
            if (isMtd) {
                let dt = typeof excelToJSDate === 'function' ? excelToJSDate(r.DealDate || r.SaleDate) : null;
                if (!dt) return false;
                return dt.getDate() <= maxCurDay;
            }
            return true;
        });
    }
    const hasPrev = prevMonthStr && prevSalesDb.length > 0;
    const prevGrandTotal = prevSalesDb.length;
    const prevBrandTotals = {};
    brands.forEach(b => prevBrandTotals[b] = prevSalesDb.filter(r => getNormalizedBrand(r) === b).length);

    // Update MTD indicators in card headers
    const badgeText = isMtd 
        ? `MTD: 1–${maxCurDay} ${curMonthName.toLowerCase().slice(0, 3)} vs 1–${maxCurDay} ${prevMonthName.toLowerCase().slice(0, 3)}`
        : (prevMonthName ? `vs ${prevMonthName}` : '');

    const elBadgeBrands = document.getElementById('mtdBadgeB2CBrands');
    if (elBadgeBrands) {
        if (hasPrev && badgeText) {
            elBadgeBrands.textContent = badgeText;
            elBadgeBrands.title = isMtd 
                ? `MTD (Month-To-Date): сравнение динамики за 1–${maxCurDay} число текущего месяца с аналогичным периодом (1–${maxCurDay}) ${prevMonthName}`
                : `Сравнение с полным месяцем ${prevMonthName}`;
            elBadgeBrands.classList.remove('hidden');
        } else {
            elBadgeBrands.classList.add('hidden');
        }
    }
    const elBadgeStruct = document.getElementById('mtdBadgeB2CStruct');
    if (elBadgeStruct) {
        if (hasPrev && badgeText) {
            elBadgeStruct.textContent = badgeText;
            elBadgeStruct.title = isMtd 
                ? `MTD (Month-To-Date): сравнение структуры за 1–${maxCurDay} число текущего месяца с аналогичным периодом (1–${maxCurDay}) ${prevMonthName}`
                : `Сравнение с полным месяцем ${prevMonthName}`;
            elBadgeStruct.classList.remove('hidden');
        } else {
            elBadgeStruct.classList.add('hidden');
        }
    }

    const calcMet = (sales, prepays, brand, idx) => {
        let filteredS = brand ? sales.filter(r => getNormalizedBrand(r) === brand) : sales;
        let filteredP = brand ? prepays.filter(r => getNormalizedBrand(r) === brand) : prepays;
        let t = filteredS.length, pr = filteredS.reduce((s,x)=>s+x.Price,0), rev = filteredS.reduce((s,x)=>s+x.Revenue,0);
        if (idx === 0) return t;
        if (idx === 1) return t > 0 ? pr / t : 0;
        if (idx === 2) return t > 0 ? rev / t : 0;
        if (idx === 3) return filteredP.length;
        return 0;
    };

    let h1 = `<table id="tableOpDyn"><thead><tr><th>Показатель</th><th>Период</th><th class="table-subtotal">ИТОГО</th>`;
    brands.forEach(b => h1 += `<th>${b}</th>`); h1 += `</tr></thead><tbody>`;
    let metrics = ["Кол-во продаж (шт.)", "Средний чек (руб.)", "ARPU (без НДС)", "Кол-во предоплат"];
    metrics.forEach((met, i) => {
        h1 += `<tr><td class="font-bold border-r">${met}</td><td>Текущий факт</td><td class="font-bold bg-gray-50">${fmtNum(calcMet(sDb, pDb, null, i))}</td>`;
        brands.forEach(b => h1 += `<td class="bg-gray-50">${fmtNum(calcMet(sDb, pDb, b, i))}</td>`); h1 += `</tr>`;
    });
    const elOpDyn = document.getElementById('tableOpDyn');
    if (elOpDyn) {
        elOpDyn.innerHTML = h1 + `</tbody></table>`;
        setupSmartSearch('searchOpDyn', 'tableOpDyn');
    }

    let h2 = `<table id="tableB2CBrands"><thead><tr><th>Тип сделки B2C</th><th class="table-subtotal">ИТОГО</th>`;
    let h3 = `<table id="tableB2CStruct"><thead><tr><th>Тип сделки B2C</th><th class="table-subtotal">ИТОГО</th>`;
    brands.forEach(b => { h2 += `<th>${b}</th>`; h3 += `<th>${b}</th>`; });
    h2 += `</tr></thead><tbody>`; h3 += `</tr></thead><tbody>`;

    let b2cTotals = {}, brandTotals = {};
    b2cArr.forEach(t => b2cTotals[t] = 0);
    brands.forEach(b => brandTotals[b] = sDb.filter(r => getNormalizedBrand(r) === b).length);
    let grandTotal = sDb.length;

    b2cArr.forEach(t => {
        let rowCount = sDb.filter(r => (r.B2C||"(пусто)") === t).length;
        b2cTotals[t] = rowCount;

        // Subtotal row delta (volume)
        let prevRowCount = hasPrev ? prevSalesDb.filter(r => (r.B2C||"(пусто)") === t).length : 0;
        let rowDiff = rowCount - prevRowCount;
        let rowBadge = '';
        if (hasPrev) {
            if (rowDiff > 0) rowBadge = `<span class="text-[11px] font-semibold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${rowDiff}</span>`;
            else if (rowDiff < 0) rowBadge = `<span class="text-[11px] font-semibold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${rowDiff}</span>`;
            else rowBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
        }

        // Subtotal row delta (share %)
        let curRowShare = grandTotal > 0 ? (rowCount / grandTotal) : 0;
        let prevRowShare = prevGrandTotal > 0 ? (prevRowCount / prevGrandTotal) : 0;
        let rowShareDiff = (curRowShare - prevRowShare) * 100;
        let rowShareBadge = '';
        if (hasPrev) {
            if (rowShareDiff >= 0.1) rowShareBadge = `<span class="text-[11px] font-semibold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${rowShareDiff.toFixed(1)}%</span>`;
            else if (rowShareDiff <= -0.1) rowShareBadge = `<span class="text-[11px] font-semibold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${rowShareDiff.toFixed(1)}%</span>`;
            else rowShareBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
        }

        h2 += `<tr><td class="font-bold">${t}</td><td class="font-bold bg-gray-50"><div class="flex items-center justify-between"><span>${fmtNum(rowCount)}</span>${rowBadge}</div></td>`;
        h3 += `<tr><td class="font-bold">${t}</td><td class="font-bold bg-gray-50"><div class="flex items-center justify-between"><span>${grandTotal > 0 ? fmtPct(curRowShare) : "0%"}</span>${rowShareBadge}</div></td>`;

        brands.forEach(b => {
            let cell = sDb.filter(r => (r.B2C||"(пусто)") === t && getNormalizedBrand(r) === b).length;
            let prevCell = hasPrev ? prevSalesDb.filter(r => (r.B2C||"(пусто)") === t && getNormalizedBrand(r) === b).length : 0;

            // Volume cell badge in tableB2CBrands
            let cellDiff = cell - prevCell;
            let cellBadge = '';
            if (hasPrev) {
                if (cellDiff > 0) cellBadge = `<span class="text-[11px] font-semibold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${cellDiff}</span>`;
                else if (cellDiff < 0) cellBadge = `<span class="text-[11px] font-semibold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${cellDiff}</span>`;
                else cellBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
            }

            // Share % cell badge in tableB2CStruct (share inside brand)
            let curPct = brandTotals[b] > 0 ? (cell / brandTotals[b]) : 0;
            let prevPct = (prevBrandTotals[b] && prevBrandTotals[b] > 0) ? (prevCell / prevBrandTotals[b]) : 0;
            let diffPct = (curPct - prevPct) * 100;
            let structBadge = '';
            if (hasPrev && (brandTotals[b] > 0 || (prevBrandTotals[b] || 0) > 0)) {
                if (diffPct >= 0.1) structBadge = `<span class="text-[11px] font-semibold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${diffPct.toFixed(1)}%</span>`;
                else if (diffPct <= -0.1) structBadge = `<span class="text-[11px] font-semibold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${diffPct.toFixed(1)}%</span>`;
                else structBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
            }

            h2 += `<td><div class="flex items-center justify-between"><span>${fmtNum(cell)}</span>${cellBadge}</div></td>`;
            h3 += `<td><div class="flex items-center justify-between"><span>${brandTotals[b] > 0 ? fmtPct(curPct) : "0%"}</span>${structBadge}</div></td>`;
        });
        h2 += `</tr>`; h3 += `</tr>`;
    });

    // Grand total footer volume badge
    let grandDiff = grandTotal - prevGrandTotal;
    let grandBadge = '';
    if (hasPrev) {
        if (grandDiff > 0) grandBadge = `<span class="text-[11px] font-bold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${grandDiff}</span>`;
        else if (grandDiff < 0) grandBadge = `<span class="text-[11px] font-bold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${grandDiff}</span>`;
        else grandBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
    }

    h2 += `<tr class="table-total"><td>ИТОГО (шт.)</td><td><div class="flex items-center justify-between"><span>${fmtNum(grandTotal)}</span>${grandBadge}</div></td>`;
    h3 += `<tr class="table-total"><td>ДОЛЯ БРЕНДА</td><td>100%</td>`;

    brands.forEach(b => {
        let bDiff = brandTotals[b] - (prevBrandTotals[b] || 0);
        let bBadge = '';
        if (hasPrev) {
            if (bDiff > 0) bBadge = `<span class="text-[11px] font-bold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${bDiff}</span>`;
            else if (bDiff < 0) bBadge = `<span class="text-[11px] font-bold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${bDiff}</span>`;
            else bBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
        }

        let curBrandShare = grandTotal > 0 ? brandTotals[b] / grandTotal : 0;
        let prevBrandShare = prevGrandTotal > 0 ? (prevBrandTotals[b] || 0) / prevGrandTotal : 0;
        let bShareDiff = (curBrandShare - prevBrandShare) * 100;
        let bShareBadge = '';
        if (hasPrev) {
            if (bShareDiff >= 0.1) bShareBadge = `<span class="text-[11px] font-bold text-emerald-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▲+${bShareDiff.toFixed(1)}%</span>`;
            else if (bShareDiff <= -0.1) bShareBadge = `<span class="text-[11px] font-bold text-rose-600 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>▼${bShareDiff.toFixed(1)}%</span>`;
            else bShareBadge = `<span class="text-[10px] text-gray-400 ml-1.5 whitespace-nowrap cursor-help" ${mtdTitleAttr}>=</span>`;
        }

        h2 += `<td><div class="flex items-center justify-between"><span>${fmtNum(brandTotals[b])}</span>${bBadge}</div></td>`;
        h3 += `<td><div class="flex items-center justify-between"><span>${fmtPct(curBrandShare)}</span>${bShareBadge}</div></td>`;
    });
    const elB2CBrands = document.getElementById('tableB2CBrands');
    if (elB2CBrands) {
        elB2CBrands.innerHTML = h2 + `</tr></tbody></table>`;
        setupSmartSearch('searchB2CBrands', 'tableB2CBrands');
    }
    const elB2CStruct = document.getElementById('tableB2CStruct');
    if (elB2CStruct) {
        elB2CStruct.innerHTML = h3 + `</tr></tbody></table>`;
    }
}

/**
 * Renders weekly comparison, weekly B2C, and historical dynamics tables.
 * @param {Array} sDb Sales data
 * @param {boolean} isAll Whether all periods are selected
 * @param {string|null} period Current period identifier
 */
function renderDynMonthsTab(sDb, isAll, period) {
    let dates = sDb.map(r => excelToJSDate(r.DealDate)).filter(d => d);
    if (dates.length === 0) return;

    let minD, maxD;
    if (isAll || !period || period === 'all' || period.includes('🗓️')) {
        minD = new Date(Math.min(...dates)); maxD = new Date(Math.max(...dates));
    } else {
        let [y, m] = period.split('-');
        minD = new Date(parseInt(y), parseInt(m)-1, 1);
        maxD = new Date(parseInt(y), parseInt(m), 0);
    }

    let weeks = [], cur = new Date(minD), wNum = 1;
    while (cur <= maxD) {
        let ws = new Date(cur);
        let dayOfWeek = cur.getDay();
        let monday = cur.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
        ws = new Date(cur); ws.setDate(monday);
        if (ws < minD) ws = new Date(minD);
        let we = new Date(ws); we.setDate(ws.getDate() + 6);
        if (we > maxD) we = new Date(maxD);

        let sStr = `${ws.getDate().toString().padStart(2,'0')}.${(ws.getMonth()+1).toString().padStart(2,'0')}`;
        let eStr = `${we.getDate().toString().padStart(2,'0')}.${(we.getMonth()+1).toString().padStart(2,'0')}`;
        weeks.push({ l: `Неделя ${wNum}`, s: sStr + "-" + eStr, start: ws.getTime(), end: we.getTime() + 86399000 });
        cur = new Date(we); cur.setDate(we.getDate() + 1); wNum++;
    }

    let hWComp = `<table id="tableWeekComp"><thead><tr><th>Показатель</th>`;
    let hWB2C = `<table id="tableWeekB2C"><thead><tr><th>Тип сделки B2C</th>`;
    weeks.forEach(w => {
        hWComp += `<th>${w.l}<br><span style="font-weight:normal;font-size:0.72rem">${w.s}</span></th>`;
        hWB2C += `<th>${w.l}<br><span style="font-weight:normal;font-size:0.72rem">${w.s}</span></th>`;
    });
    hWComp += `</tr></thead><tbody>`; hWB2C += `</tr></thead><tbody>`;

    const compMets = ["ARPU Китай", "ARPU LADA", "ARPU ИТОГО", "Средний чек Китай", "Средний чек LADA", "Средний чек ИТОГО"];
    compMets.forEach((met, i) => {
        hWComp += `<tr><td class="font-bold">${met}</td>`;
        weeks.forEach(w => {
            let wD = sDb.filter(r => { let d = excelToJSDate(r.DealDate)?.getTime(); return d && d >= w.start && d <= w.end; });
            let t = wD.length, pr = 0, rev = 0, revLa = 0, cntLa = 0, prLa = 0, revCh = 0, cntCh = 0, prCh = 0;
            wD.forEach(r => {
                rev += (r.Revenue || 0); pr += r.Price;
                if (r.Brand === 'LADA') { revLa += (r.Revenue||0); prLa += r.Price; cntLa++; }
                else { revCh += (r.Revenue||0); prCh += r.Price; cntCh++; }
            });
            let v = 0;
            if (i === 0) v = cntCh > 0 ? (revCh / cntCh) : 0;   
            if (i === 1) v = cntLa > 0 ? (revLa / cntLa) : 0;     
            if (i === 2) v = t > 0 ? (rev / t) : 0;              
            if (i === 3) v = cntCh > 0 ? (prCh / cntCh) : 0;
            if (i === 4) v = cntLa > 0 ? (prLa / cntLa) : 0;
            if (i === 5) v = t > 0 ? (pr / t) : 0;
            hWComp += `<td>${fmtNum(v)}</td>`;
        });
        hWComp += `</tr>`;
    });

    let b2cSet = new Set(sDb.map(r => r.B2C || "(пусто)"));
    Array.from(b2cSet).sort().forEach(b2c => {
        hWB2C += `<tr><td class="font-bold">${b2c}</td>`;
        weeks.forEach(w => {
            let c = sDb.filter(r => (r.B2C||"(пусто)") === b2c && excelToJSDate(r.DealDate)?.getTime() >= w.start && excelToJSDate(r.DealDate)?.getTime() <= w.end).length;
            hWB2C += `<td>${fmtNum(c)}</td>`;
        });
        hWB2C += `</tr>`;
    });

    const elWeekComp = document.getElementById('tableWeekComp');
    if (elWeekComp) {
        elWeekComp.innerHTML = hWComp + `</tbody></table>`;
        setupSmartSearch('searchWeekComp', 'tableWeekComp');
    }
    const elWeekB2C = document.getElementById('tableWeekB2C');
    if (elWeekB2C) {
        elWeekB2C.innerHTML = hWB2C + `</tbody></table>`;
    }
}

/**
 * Escapes HTML characters to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Toggles visibility of partner deals details sub-table.
 * @param {string} key
 */
function togglePartnerDeals(key) {
    const row = document.getElementById('pdeals_row_' + key);
    const icon = document.getElementById('picon_' + key);
    if (!row) return;

    const isHidden = row.classList.contains('hidden');
    if (isHidden) {
        row.classList.remove('hidden');
        if (icon) icon.style.transform = 'rotate(90deg)';
    } else {
        row.classList.add('hidden');
        if (icon) icon.style.transform = 'rotate(0deg)';
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Exports partner deals to formatted Excel (.xlsx) file using SheetJS.
 * @param {string} key
 */
function exportPartnerDealsToExcel(key) {
    const item = window._partnerDealsCache ? window._partnerDealsCache[key] : null;
    if (!item || !item.deals || item.deals.length === 0) {
        showToast('Нет данных по сделкам для выгрузки', 'warning');
        return;
    }

    const partnerName = item.name || 'Партнер';
    const rows = item.deals;

    const wsData = [
        ['№', 'Юр. лицо (CRM)', 'ID (Сумма id)', 'Client_ID', 'ВИН', 'Марка', 'Модель', 'Стоимость авто (руб)', 'АВ (КВ. Авто NEW, руб)', '% АВ от стоимости']
    ];

    let totalAB = 0;
    let totalPrice = 0;
    rows.forEach((d, idx) => {
        const ab = Number(d.comm) || 0;
        const pr = Number(d.price) || 0;
        totalAB += ab;
        totalPrice += pr;
        const pctStr = (pr > 0 && ab > 0) ? `${((ab / pr) * 100).toFixed(1)}%` : '—';
        wsData.push([
            idx + 1,
            d.rawPartner ? String(d.rawPartner) : '—',
            d.leadId ? String(d.leadId) : (d.dealId ? String(d.dealId) : '—'),
            d.clientId ? String(d.clientId) : '—',
            d.vin ? String(d.vin) : '—',
            d.brand ? String(d.brand) : '—',
            d.model ? String(d.model) : '—',
            pr,
            ab,
            pctStr
        ]);
    });

    const totalPctStr = (totalPrice > 0 && totalAB > 0) ? `${((totalAB / totalPrice) * 100).toFixed(1)}%` : '—';
    wsData.push(['', '', '', '', '', '', 'ИТОГО:', totalPrice, totalAB, totalPctStr]);

    const ws = XLSX.utils.aoa_to_sheet(wsData);

    ws['!cols'] = [
        { wch: 6 },
        { wch: 34 },
        { wch: 18 },
        { wch: 16 },
        { wch: 24 },
        { wch: 18 },
        { wch: 22 },
        { wch: 20 },
        { wch: 22 },
        { wch: 18 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Сделки");

    const cleanPartnerName = partnerName.replace(/[/\\?%*:|"<>]/g, '_').trim();
    const periodStr = currentFilterConfig && currentFilterConfig.month ? currentFilterConfig.month : (new Date().toISOString().split('T')[0]);
    const fileName = `Сделки_${cleanPartnerName}_${periodStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
    showToast(`Выгружено ${rows.length} сделок в ${fileName}`, 'success');
}

/**
 * Renders partners summary table with CR calculations, Master ID matching,
 * and interactive expandable deal sub-tables with Excel export.
 * @param {Object} filterCfg
 */
function renderPartnersTable(filterCfg) {
    let fPartners = dbPartners.filter(r => {
        if (filterCfg.mode === 'all') return true;
        if (filterCfg.mode === 'month') return r.Month === filterCfg.month;
        if (filterCfg.mode === 'custom') {
            const fTime = filterCfg.from ? filterCfg.from.getTime() : -Infinity;
            const tTime = filterCfg.to ? filterCfg.to.getTime() : Infinity;
            const d = excelToJSDate(r.Date);
            if (!d) return false;
            const t = d.getTime();
            return t >= fTime && t <= tTime;
        }
        return true;
    });

    window._partnerDealsCache = {};

    let pStats = {};
    fPartners.forEach(r => {
        let pid = r.PartnerId;
        let pName = r.Partner || "Неизвестный";
        let key = pid ? `ID_${pid}` : `RAW_${pName.replace(/[^a-zA-Z0-9а-яА-Я_]/g, '_')}`;

        if (!pStats[key]) {
            pStats[key] = {
                key: key,
                id: pid,
                name: pName,
                leads: 0,
                prepays: 0,
                leadDirectDeals: 0,
                mpDeals: 0,
                deals: 0,
                kam: r.KAM || "",
                dealsList: [],
                rawBitrix: new Set(),
                rawBi: new Set()
            };
        }

        if (r.Type === 'Лид') {
            pStats[key].leads += (r.Qty || 1);
            if (r.RawPartner) pStats[key].rawBi.add(r.RawPartner);
        } else if (r.Type === 'Сделка') {
            pStats[key].deals += (r.Qty || 1);
            if (r.IsLeadSaleNoPrepay === 1) {
                pStats[key].leadDirectDeals += (r.Qty || 1);
            }
            if (r.IsMpSale === 1) {
                pStats[key].mpDeals += (r.Qty || 1);
            }
            if (r.RawPartner) pStats[key].rawBitrix.add(r.RawPartner);

            pStats[key].dealsList.push({
                leadId: r.LeadId || '',
                clientId: r.ClientId || '',
                dealId: r.DealId || '',
                rawPartner: r.RawPartner || '',
                vin: r.VIN || '',
                brand: r.Brand || '',
                model: r.Model || '',
                comm: Number(r.Comm) || 0,
                price: Number(r.Price) || 0,
                date: r.Date || 0,
                manager: r.Manager || '',
                b2c: r.B2C || ''
            });
        } else if (r.Type === 'Предоплата') {
            pStats[key].prepays += (r.Qty || 1);
            if (r.RawPartner) pStats[key].rawBitrix.add(r.RawPartner);
        }
        if (!pStats[key].kam && r.KAM) pStats[key].kam = r.KAM;
    });

    let sorted = Object.values(pStats).sort((a, b) => (b.deals + b.leads) - (a.deals + a.leads));
    let html = `<table id="tablePartners">
        <thead>
            <tr>
                <th style="width: 65px;">ID</th>
                <th>Партнер (Master Name)</th>
                <th>Закрепленный КАМ</th>
                <th>Лиды (BI)</th>
                <th>Предоплаты</th>
                <th>Сделки с лидов</th>
                <th>Сделки с МП</th>
                <th>Сделки Тотал</th>
                <th>CR (Сделка с лида / Лид)</th>
                <th style="text-align: right;">Управление</th>
            </tr>
        </thead>
        <tbody>`;
    
    let tL = 0, tP = 0, tLD = 0, tMP = 0, tD = 0;

    sorted.forEach(data => {
        tL += data.leads; tP += data.prepays; tLD += data.leadDirectDeals; tMP += data.mpDeals; tD += data.deals;
        let crVal = data.leads > 0 ? (data.leadDirectDeals / data.leads * 100) : 0;
        let cr = data.leads > 0 ? `${crVal.toFixed(1)}%` : (data.leadDirectDeals > 0 ? "— (нет лидов)" : "0%");
        let idBadge = data.id ? 
            `<span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-xs">ID: ${data.id}</span>` : 
            `<span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-xs">Не сметчен</span>`;

        let crColor = 'text-gray-500';
        if (data.leads > 0) {
            if (crVal < 7) {
                crColor = 'text-rose-600 font-bold';
            } else if (crVal <= 13) {
                crColor = 'text-amber-600 font-bold';
            } else {
                crColor = 'text-emerald-700 font-black';
            }
        } else if (data.leadDirectDeals > 0) {
            crColor = 'text-blue-600 font-bold';
        }

        const k = data.key;
        const dCount = data.dealsList.length;
        window._partnerDealsCache[k] = {
            name: data.name,
            deals: data.dealsList
        };

        let partnerNameHtml = '';
        if (dCount > 0) {
            partnerNameHtml = `
                <button type="button" onclick="togglePartnerDeals('${k}')" class="partner-title-btn text-left flex items-center justify-between gap-2 w-full font-bold text-gray-900 hover:text-blue-700 group transition py-0.5" title="Нажмите, чтобы развернуть сделки">
                    <span class="group-hover:underline flex items-center gap-1.5">
                        <i data-lucide="chevron-right" id="picon_${k}" class="w-4 h-4 text-blue-500 shrink-0 transition-transform duration-200"></i>
                        <span>${escapeHtml(data.name)}</span>
                    </span>
                    <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 group-hover:bg-blue-100 transition whitespace-nowrap">
                        ${fmtNum(dCount)} ${dCount === 1 ? 'сделка' : (dCount < 5 ? 'сделки' : 'сделок')} ▾
                    </span>
                </button>
            `;
        } else {
            partnerNameHtml = `<span class="font-bold text-gray-900">${escapeHtml(data.name)}</span>`;
        }

        html += `<tr data-partner-key="${k}" class="hover:bg-blue-50/30 transition">
            <td>${idBadge}</td>
            <td>${partnerNameHtml}</td>
            <td class="font-medium text-gray-600">${data.kam || "—"}</td>
            <td class="font-semibold text-gray-700">${fmtNum(data.leads)}</td>
            <td class="font-semibold text-amber-700">${fmtNum(data.prepays)}</td>
            <td class="font-semibold text-purple-700">${fmtNum(data.leadDirectDeals)}</td>
            <td class="font-semibold text-indigo-700">${fmtNum(data.mpDeals)}</td>
            <td class="font-black text-blue-700">${fmtNum(data.deals)}</td>
            <td class="${crColor}">${cr}</td>
            <td style="text-align: right;">
                <a href="partner_matcher.html?partner_id=${encodeURIComponent(data.id || '')}&search=${encodeURIComponent(data.name || '')}" target="_blank" class="px-2.5 py-1 bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 rounded-lg text-xs font-bold transition inline-flex items-center gap-1 shadow-sm" title="Редактировать партнера в Реестре">
                    Править ➔
                </a>
            </td>
        </tr>`;

        if (dCount > 0) {
            let totalAB = data.dealsList.reduce((sum, dl) => sum + (dl.comm || 0), 0);
            let dealRowsHtml = '';
            data.dealsList.forEach((dl, idx) => {
                let leadIdHtml = dl.leadId ? 
                    `<span class="px-2 py-0.5 rounded bg-blue-100 text-blue-900 font-bold text-[11px] border border-blue-200 font-mono">${escapeHtml(dl.leadId)}</span>` : 
                    (dl.dealId ? `<span class="text-slate-500 font-mono text-[11px]">${escapeHtml(dl.dealId)}</span>` : '<span class="text-slate-300">—</span>');

                let clientHtml = dl.clientId ? 
                    `<a href="https://backoffice.x.sberauto.com/crm/manager/${escapeHtml(dl.clientId)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold text-[11px] border border-emerald-200 transition shadow-sm" title="Открыть карточку клиента в CRM БФС">
                        <i data-lucide="external-link" class="w-3 h-3 text-emerald-600"></i>
                        <span>BFS #${escapeHtml(dl.clientId)}</span>
                    </a>` : 
                    '<span class="text-slate-300">—</span>';

                let rawPartnerHtml = dl.rawPartner ? 
                    `<span class="text-[11px] text-slate-600 font-medium truncate max-w-[220px] block" title="${escapeHtml(dl.rawPartner)}">${escapeHtml(dl.rawPartner)}</span>` : 
                    '<span class="text-slate-300">—</span>';

                let vinHtml = dl.vin ? 
                    `<code class="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded font-mono text-[11px] font-bold select-all border border-slate-200">${escapeHtml(dl.vin)}</code>` : 
                    '<span class="text-slate-300">—</span>';

                let pctAB = (dl.price > 0 && dl.comm > 0) ? `${((dl.comm / dl.price) * 100).toFixed(1)}%` : '—';

                dealRowsHtml += `<tr class="hover:bg-blue-50/40 transition">
                    <td class="py-1.5 px-2.5 text-center text-slate-400 font-mono text-xs">${idx + 1}</td>
                    <td class="py-1.5 px-2.5">${rawPartnerHtml}</td>
                    <td class="py-1.5 px-2.5">${leadIdHtml}</td>
                    <td class="py-1.5 px-2.5">${clientHtml}</td>
                    <td class="py-1.5 px-2.5">${vinHtml}</td>
                    <td class="py-1.5 px-2.5 font-bold text-slate-800">${escapeHtml(dl.brand || '—')}</td>
                    <td class="py-1.5 px-2.5 text-slate-700 font-medium">${escapeHtml(dl.model || '—')}</td>
                    <td class="py-1.5 px-2.5 text-right font-medium text-slate-700">${dl.price > 0 ? fmtRub(dl.price) : '—'}</td>
                    <td class="py-1.5 px-2.5 text-right font-black text-emerald-700">${fmtRub(dl.comm)}</td>
                    <td class="py-1.5 px-2.5 text-center font-bold text-blue-700 bg-blue-50/50">${pctAB}</td>
                </tr>`;
            });

            let totalPrice = data.dealsList.reduce((sum, dl) => sum + (dl.price || 0), 0);
            let totalPctAB = (totalPrice > 0 && totalAB > 0) ? `${((totalAB / totalPrice) * 100).toFixed(1)}%` : '—';

            html += `<tr id="pdeals_row_${k}" class="partner-deals-row hidden bg-slate-50/90">
                <td colspan="10" class="!p-0 border-b-2 border-blue-300">
                    <div class="p-3 sm:p-4 bg-gradient-to-br from-slate-50 via-blue-50/20 to-indigo-50/20 border-t border-blue-200 rounded-b-xl shadow-inner">
                        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-2.5 pb-2 border-b border-blue-100">
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                                <span class="text-xs font-black uppercase text-slate-700 tracking-wider">
                                    Сделки компании: <b class="text-blue-800">${escapeHtml(data.name)}</b>
                                </span>
                                <span class="text-[11px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-bold border border-blue-200">
                                    ${dCount} шт.
                                </span>
                                <span class="text-xs text-slate-600 font-medium ml-1">
                                    Сумма АВ: <b class="text-emerald-700 font-bold">${fmtRub(totalAB)}</b>
                                </span>
                                <span class="text-xs text-slate-600 font-medium ml-1">
                                    % АВ: <b class="text-blue-700 font-bold">${totalPctAB}</b>
                                </span>
                            </div>
                            <div>
                                <button type="button" onclick="exportPartnerDealsToExcel('${k}')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm active:scale-95">
                                    <i data-lucide="download" class="w-3.5 h-3.5"></i> Скачать в Excel (.xlsx)
                                </button>
                            </div>
                        </div>

                        <div class="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm max-h-[360px] overflow-y-auto">
                            <table class="min-w-full text-xs text-left">
                                <thead class="bg-slate-800 text-slate-200 text-[11px] font-bold sticky top-0 z-10 shadow">
                                    <tr>
                                        <th class="py-2 px-2.5 w-10 text-center !bg-slate-800">№</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">Юр. лицо (CRM)</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">ID (Сумма id)</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">Client_ID</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">ВИН</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">Марка</th>
                                        <th class="py-2 px-2.5 !bg-slate-800">Модель</th>
                                        <th class="py-2 px-2.5 text-right !bg-slate-800">Стоимость авто</th>
                                        <th class="py-2 px-2.5 text-right !bg-slate-800">АВ (КВ. Авто NEW)</th>
                                        <th class="py-2 px-2.5 text-center !bg-slate-800">% АВ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    ${dealRowsHtml}
                                </tbody>
                                <tfoot class="bg-slate-100 font-black border-t-2 border-slate-300 text-slate-800 sticky bottom-0 z-10">
                                    <tr>
                                        <td colspan="7" class="py-2 px-2.5 text-right font-bold text-slate-700">ИТОГО (${dCount} шт.):</td>
                                        <td class="py-2 px-2.5 text-right text-slate-800 font-bold">${fmtRub(totalPrice)}</td>
                                        <td class="py-2 px-2.5 text-right text-emerald-700 font-black text-sm">${fmtRub(totalAB)}</td>
                                        <td class="py-2 px-2.5 text-center text-blue-800 font-black text-sm bg-blue-100/50">${totalPctAB}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>

                        <div class="mt-2.5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 text-[11px] text-slate-500">
                            <span class="flex items-center gap-1">
                                <i data-lucide="info" class="w-3.5 h-3.5 text-blue-500"></i>
                                Нажмите на ссылку <b class="text-emerald-700">🔗 BFS #ID</b> для перехода в карточку клиента
                            </span>
                            <button type="button" onclick="exportPartnerDealsToExcel('${k}')" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow hover:shadow-md active:scale-95">
                                <i data-lucide="file-spreadsheet" class="w-4 h-4"></i> Скачать таблицу сделок в Excel (.xlsx)
                            </button>
                        </div>
                    </div>
                </td>
            </tr>`;
        }
    });

    let tCrVal = tL > 0 ? (tLD / tL * 100) : 0;
    let tCr = tL > 0 ? `${tCrVal.toFixed(1)}%` : "0%";
    let tCrColor = 'text-gray-800 font-black';
    if (tL > 0) {
        if (tCrVal < 7) tCrColor = 'text-rose-600 font-black';
        else if (tCrVal <= 13) tCrColor = 'text-amber-600 font-black';
        else tCrColor = 'text-emerald-700 font-black';
    }
    html += `<tr class="table-total">
        <td>ИТОГО</td>
        <td>—</td>
        <td>—</td>
        <td>${fmtNum(tL)}</td>
        <td>${fmtNum(tP)}</td>
        <td>${fmtNum(tLD)}</td>
        <td>${fmtNum(tMP)}</td>
        <td>${fmtNum(tD)}</td>
        <td class="${tCrColor}">${tCr}</td>
        <td></td>
    </tr></tbody></table>`;

    const elPartners = document.getElementById('tablePartnersContainer');
    if (elPartners) {
        elPartners.innerHTML = html;
        setupSmartSearch('searchPartners', 'tablePartnersContainer');
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
}

/**
 * Renders grouped manager performance table.
 * @param {Array} sDb Sales data
 * @param {Array} pDb Prepayment data
 */
function renderManagersTable(sDb, pDb) {
    let mStats = {};
    sDb.forEach(r => {
        let m = r.Manager || "Не указан";
        let sen = r.SeniorManager || "Без старшего";
        if (!mStats[m]) mStats[m] = { s: 0, p: 0, senior: sen };
        mStats[m].s += r.SaleQty;
    });
    pDb.forEach(r => {
        let m = r.Manager || "Не указан";
        let sen = r.SeniorManager || "Без старшего";
        if (!mStats[m]) mStats[m] = { s: 0, p: 0, senior: sen };
        mStats[m].p += r.PrepayQty;
    });

    let groups = {};
    Object.entries(mStats).forEach(([mgr, data]) => {
        let sen = data.senior;
        if (!groups[sen]) groups[sen] = [];
        groups[sen].push({ name: mgr, s: data.s, p: data.p });
    });

    Object.values(groups).forEach(g => g.sort((a, b) => b.s - a.s));

    let sortedGroups = Object.entries(groups).sort((a, b) => {
        let tA = a[1].reduce((s, x) => s + x.s, 0);
        let tB = b[1].reduce((s, x) => s + x.p, 0);
        return (b[1].reduce((s,x)=>s+x.s,0)) - (a[1].reduce((s,x)=>s+x.s,0));
    });

    let html = `<table id="tableManagers"><thead><tr><th>Менеджер</th><th>Сделки (шт)</th><th>Предоплаты (шт)</th></tr></thead><tbody>`;
    let grandS = 0, grandP = 0;

    sortedGroups.forEach(([sen, members]) => {
        let gS = members.reduce((s, x) => s + x.s, 0);
        let gP = members.reduce((s, x) => s + x.p, 0);
        grandS += gS; grandP += gP;

        html += `<tr class="group-header"><td colspan="3">Группа: ${sen}</td></tr>`;

        members.forEach(m => {
            if (m.s === 0 && m.p === 0) return;
            html += `<tr><td class="font-semibold pl-6">${m.name}</td><td class="font-bold text-blue-600">${fmtNum(m.s)}</td><td>${fmtNum(m.p)}</td></tr>`;
        });

        html += `<tr class="table-subtotal"><td>ИТОГО (${sen})</td><td>${fmtNum(gS)}</td><td>${fmtNum(gP)}</td></tr>`;
    });

    html += `<tr class="table-total"><td>ОБЩИЙ ИТОГ</td><td>${fmtNum(grandS)}</td><td>${fmtNum(grandP)}</td></tr>`;
    const elMgrs = document.getElementById('tableManagersContainer');
    if (elMgrs) {
        elMgrs.innerHTML = html + `</tbody></table>`;
        setupSmartSearch('searchManagers', 'tableManagersContainer');
    }
}

/**
 * Renders brand waiting counts table.
 * @param {Object} filterCfg
 */
function renderWaitingTable(filterCfg) {
    let wStats = {};
    let channelTotals = { 'МП2': 0, 'Online': 0, 'ФДЦ': 0, 'Прочие': 0 };
    let filteredWaiting = db.filter(r => {
        if (r.WaitQty <= 0) return false;
        if (filterCfg.mode === 'all') return true;
        if (filterCfg.mode === 'month') return r.WaitMonth === filterCfg.month;
        if (filterCfg.mode === 'custom') {
            const fTime = filterCfg.from ? filterCfg.from.getTime() : -Infinity;
            const tTime = filterCfg.to ? filterCfg.to.getTime() : Infinity;
            const d = excelToJSDate(r.DealDate || r.PrepayDate);
            if (!d) return false;
            const t = d.getTime();
            return t >= fTime && t <= tTime;
        }
        return true;
    });

    filteredWaiting.forEach(r => {
        let b = r.Brand || "Неизвестно";
        let c = (r.B2C || "Не указан").trim();
        let w = r.WaitQty || 1;
        if (!wStats[b]) {
            wStats[b] = { total: 0, mp2: 0, online: 0, fdc: 0, other: 0 };
        }
        wStats[b].total += w;
        if (c === 'МП2') {
            wStats[b].mp2 += w;
            channelTotals['МП2'] += w;
        } else if (c === 'Online') {
            wStats[b].online += w;
            channelTotals['Online'] += w;
        } else if (c === 'ФДЦ' || c === 'ФДЦ+ГП') {
            wStats[b].fdc += w;
            channelTotals['ФДЦ'] += w;
        } else {
            wStats[b].other += w;
            channelTotals['Прочие'] += w;
        }
    });

    // Also calculate unassigned retail advances in progress
    let unassignedPrepay = { total: 0, mp2: 0, online: 0, fdc: 0, other: 0 };
    let filteredOpenPrepay = db.filter(r => {
        if (r.PrepayQty <= 0) return false;
        if (r.SaleQty > 0 && r.SaleMonth === filterCfg.month) return false;
        if (r.B2C === 'МП2') return false;
        if (filterCfg.mode === 'all') return true;
        if (filterCfg.mode === 'month') return r.PrepayMonth === filterCfg.month;
        if (filterCfg.mode === 'custom') {
            const fTime = filterCfg.from ? filterCfg.from.getTime() : -Infinity;
            const tTime = filterCfg.to ? filterCfg.to.getTime() : Infinity;
            const d = excelToJSDate(r.PrepayDate);
            if (!d) return false;
            const t = d.getTime();
            return t >= fTime && t <= tTime;
        }
        return true;
    });

    filteredOpenPrepay.forEach(r => {
        let c = (r.B2C || "Не указан").trim();
        unassignedPrepay.total += 1;
        if (c === 'Online') {
            unassignedPrepay.online += 1;
            channelTotals['Online'] += 1;
        } else if (c === 'ФДЦ' || c === 'ФДЦ+ГП') {
            unassignedPrepay.fdc += 1;
            channelTotals['ФДЦ'] += 1;
        } else {
            unassignedPrepay.other += 1;
            channelTotals['Прочие'] += 1;
        }
    });

    let sorted = Object.keys(wStats).sort((a, b) => wStats[b].total - wStats[a].total);
    let html = `<table id="tableWaiting" class="min-w-full">
        <thead>
            <tr>
                <th class="!bg-slate-800 text-left">Марка Авто / Категория</th>
                <th class="!bg-slate-800 text-right text-blue-300">МП2 (Опт)</th>
                <th class="!bg-slate-800 text-right text-emerald-300">Online</th>
                <th class="!bg-slate-800 text-right text-purple-300">ФДЦ (Кредит)</th>
                <th class="!bg-slate-800 text-right text-slate-300">Прочие (МП1/МП3)</th>
                <th class="!bg-slate-800 text-right text-orange-400 font-bold">Всего в ожидании</th>
            </tr>
        </thead>
        <tbody>`;
    
    let tw = 0;
    sorted.forEach(b => {
        let s = wStats[b];
        tw += s.total;
        html += `<tr class="hover:bg-amber-50/40 transition">
            <td class="font-bold text-slate-800 text-left">${b}</td>
            <td class="text-right font-semibold text-blue-700">${s.mp2 > 0 ? `<span class="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100 font-bold">${fmtNum(s.mp2)}</span>` : '<span class="text-slate-300">—</span>'}</td>
            <td class="text-right font-semibold text-emerald-700">${s.online > 0 ? `<span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100 font-bold">${fmtNum(s.online)}</span>` : '<span class="text-slate-300">—</span>'}</td>
            <td class="text-right font-semibold text-purple-700">${s.fdc > 0 ? `<span class="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-100 font-bold">${fmtNum(s.fdc)}</span>` : '<span class="text-slate-300">—</span>'}</td>
            <td class="text-right font-medium text-slate-600">${s.other > 0 ? `<span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 font-semibold">${fmtNum(s.other)}</span>` : '<span class="text-slate-300">—</span>'}</td>
            <td class="text-right text-orange-600 font-black text-sm">${fmtNum(s.total)}</td>
        </tr>`;
    });

    if (unassignedPrepay.total > 0) {
        tw += unassignedPrepay.total;
        html += `<tr class="bg-amber-50/50 hover:bg-amber-100/50 transition border-t-2 border-amber-200">
            <td class="font-bold text-amber-900 text-left flex items-center gap-1.5">
                <span>⚡ Внесение аванса (в оформлении ДЦ / подбор)</span>
            </td>
            <td class="text-right font-semibold text-blue-700"><span class="text-slate-300">—</span></td>
            <td class="text-right font-semibold text-emerald-700"><span class="px-2 py-0.5 rounded bg-emerald-100/70 text-emerald-800 border border-emerald-200 font-bold">${fmtNum(unassignedPrepay.online)}</span></td>
            <td class="text-right font-semibold text-purple-700"><span class="px-2 py-0.5 rounded bg-purple-100/70 text-purple-800 border border-purple-200 font-bold">${fmtNum(unassignedPrepay.fdc)}</span></td>
            <td class="text-right font-medium text-slate-600"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200 font-semibold">${fmtNum(unassignedPrepay.other)}</span></td>
            <td class="text-right text-amber-800 font-black text-sm">${fmtNum(unassignedPrepay.total)}</td>
        </tr>`;
    }

    const elWait = document.getElementById('tableWaitingContainer');
    if (elWait) {
        elWait.innerHTML = html + `<tr class="table-total font-black bg-slate-100">
            <td class="text-left font-black">ВСЕГО</td>
            <td class="text-right text-blue-800 font-black">${fmtNum(channelTotals['МП2'])}</td>
            <td class="text-right text-emerald-800 font-black">${fmtNum(channelTotals['Online'])}</td>
            <td class="text-right text-purple-800 font-black">${fmtNum(channelTotals['ФДЦ'])}</td>
            <td class="text-right text-slate-800 font-black">${fmtNum(channelTotals['Прочие'])}</td>
            <td class="text-right text-orange-600 font-black text-sm">${fmtNum(tw)}</td>
        </tr></tbody></table>`;
        setupSmartSearch('searchWaiting', 'tableWaitingContainer');
    }
}

/**
 * Initializes click-to-sort headers for all tables.
 */
function initTableSorting() {
    document.querySelectorAll('th').forEach(th => {
        if (th.dataset.sorted) return;
        th.dataset.sorted = "true";
        th.style.cursor = "pointer";
        th.title = "Нажмите для сортировки";
        th.addEventListener('click', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'A') return;
            
            const table = th.closest('table');
            if (!table) return;

            const thead = table.querySelector(':scope > thead');
            if (thead && !thead.contains(th)) return;

            const tbody = table.querySelector(':scope > tbody') || table.tBodies[0];
            if (!tbody) return;

            // CRITICAL FIX: Only select direct child <tr> of this table's <tbody>!
            // querySelectorAll('tr') selects nested rows inside accordion deal tables,
            // which pulls inner deal rows out of the drilldown and flattens them into the main table.
            const directRows = Array.from(tbody.children).filter(el => el.tagName === 'TR');
            const colIdx = Array.from(th.parentNode.children).indexOf(th);

            // Determine sort direction: default to desc for numeric, asc for text on first click
            let nextDir = 'desc';
            if (th.classList.contains('sort-desc')) {
                nextDir = 'asc';
            } else if (th.classList.contains('sort-asc')) {
                nextDir = 'desc';
            } else {
                // If text column like Name or KAM, default to asc, else desc
                const isTextCol = (colIdx === 1 || colIdx === 2);
                nextDir = isTextCol ? 'asc' : 'desc';
            }

            table.querySelectorAll(':scope > thead th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            th.classList.add(nextDir === 'asc' ? 'sort-asc' : 'sort-desc');

            const totalRows = directRows.filter(r => r.classList.contains('table-total') || r.classList.contains('table-subtotal') || r.classList.contains('group-header'));
            const sortableRows = directRows.filter(r => !r.classList.contains('table-total') && !r.classList.contains('table-subtotal') && !r.classList.contains('group-header') && !r.classList.contains('partner-deals-row'));

            sortableRows.sort((a, b) => {
                let aCell = a.children[colIdx];
                let bCell = b.children[colIdx];
                let aVal = aCell ? aCell.innerText.trim() : '';
                let bVal = bCell ? bCell.innerText.trim() : '';

                let aNumStr = aVal.replace(/\s+/g, '').replace(/[^\d.-]/g, '');
                let bNumStr = bVal.replace(/\s+/g, '').replace(/[^\d.-]/g, '');
                let aNum = aNumStr !== '' ? parseFloat(aNumStr) : NaN;
                let bNum = bNumStr !== '' ? parseFloat(bNumStr) : NaN;

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return nextDir === 'asc' ? aNum - bNum : bNum - aNum;
                }
                if (!isNaN(aNum)) return -1;
                if (!isNaN(bNum)) return 1;
                return nextDir === 'asc' ? aVal.localeCompare(bVal, 'ru') : bVal.localeCompare(aVal, 'ru');
            });

            // Re-order nodes cleanly using DocumentFragment without touching inner DOM of accordions
            const frag = document.createDocumentFragment();
            sortableRows.forEach(r => {
                frag.appendChild(r);
                const pKey = r.dataset.partnerKey;
                if (pKey) {
                    const childRow = document.getElementById('pdeals_row_' + pKey);
                    if (childRow) frag.appendChild(childRow);
                }
            });
            totalRows.forEach(r => frag.appendChild(r));
            tbody.appendChild(frag);
        });
    });
}
