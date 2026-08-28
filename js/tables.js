/* ====================================================================
 * B2C Analytics Dashboard — Table Rendering & Interactions
 * ====================================================================*/

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
        let text = row.textContent.toLowerCase();
        row.style.display = text.includes(val) ? '' : 'none';
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
    let brands = Array.from(new Set(sDb.map(r => r.Brand))).filter(b => b && b !== "ВНЕСЕНИЕ").sort();
    let b2cTypes = new Set(sDb.map(r => r.B2C || "(пусто)"));
    let b2cArr = Array.from(b2cTypes).sort();

    const calcMet = (sales, prepays, brand, idx) => {
        let filteredS = brand ? sales.filter(r => r.Brand === brand) : sales;
        let filteredP = brand ? prepays.filter(r => r.Brand === brand) : prepays;
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
    brands.forEach(b => brandTotals[b] = sDb.filter(r => r.Brand === b).length);
    let grandTotal = sDb.length;

    b2cArr.forEach(t => {
        let rowCount = sDb.filter(r => (r.B2C||"(пусто)") === t).length;
        b2cTotals[t] = rowCount;
        h2 += `<tr><td class="font-bold">${t}</td><td class="font-bold bg-gray-50">${fmtNum(rowCount)}</td>`;
        h3 += `<tr><td class="font-bold">${t}</td><td class="font-bold bg-gray-50">${grandTotal > 0 ? fmtPct(rowCount/grandTotal) : "0%"}</td>`;
        brands.forEach(b => {
            let cell = sDb.filter(r => (r.B2C||"(пусто)") === t && r.Brand === b).length;
            h2 += `<td>${fmtNum(cell)}</td>`;
            h3 += `<td>${brandTotals[b] > 0 ? fmtPct(cell/brandTotals[b]) : "0%"}</td>`;
        });
        h2 += `</tr>`; h3 += `</tr>`;
    });
    h2 += `<tr class="table-total"><td>ИТОГО (шт.)</td><td>${fmtNum(grandTotal)}</td>`;
    h3 += `<tr class="table-total"><td>ДОЛЯ БРЕНДА</td><td>100%</td>`;
    brands.forEach(b => {
        h2 += `<td>${fmtNum(brandTotals[b])}</td>`;
        h3 += `<td>${fmtPct(brandTotals[b]/grandTotal)}</td>`;
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
    let hDb = db.filter(r => r.SaleQty > 0 || r.PrepayQty > 0);
    let hData = {};
    hDb.forEach(r => {
        let b = r.Brand || "N/A"; let m = (r.SaleMonth || r.PrepayMonth || "N/A").replace("'", "");
        let k = b + "|" + m;
        if (!hData[k]) hData[k] = {s:0, rev:0, pr:0, p:0, b, m};
        if (r.SaleQty > 0) { hData[k].s++; hData[k].rev += (r.Revenue||0); hData[k].pr += r.Price; }
        if (r.PrepayQty > 0) hData[k].p++;
    });
    let histRows = Object.values(hData).sort((a,b) => a.b.localeCompare(b.b) || a.m.localeCompare(b.m));
    let hHist = `<table id="tableHistDyn"><thead><tr><th>Марка авто</th><th>Месяц</th><th>Кол-во продаж</th><th>Средний чек</th><th>ARPU (без НДС)</th><th>Предоплат</th></tr></thead><tbody>`;
    histRows.forEach(r => {
        hHist += `<tr><td class="font-bold">${r.b}</td><td>${r.m}</td><td>${fmtNum(r.s)}</td>
        <td>${r.s>0?fmtNum(r.pr/r.s):0}</td><td>${r.s>0?fmtNum(r.rev/r.s):0}</td><td>${fmtNum(r.p)}</td></tr>`;
    });
    const elHistDyn = document.getElementById('tableHistDyn');
    if (elHistDyn) {
        elHistDyn.innerHTML = hHist + `</tbody></table>`;
        setupSmartSearch('searchHistDyn', 'tableHistDyn');
    }

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
 * Renders partners summary table with CR calculations and Master ID matching.
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

    let pStats = {};
    fPartners.forEach(r => {
        let pid = r.PartnerId;
        let pName = r.Partner || "Неизвестный";
        let key = pid ? `ID_${pid}` : `RAW_${pName}`;

        if (!pStats[key]) {
            pStats[key] = {
                id: pid,
                name: pName,
                leads: 0,
                prepays: 0,
                leadDirectDeals: 0,
                mpDeals: 0,
                deals: 0,
                kam: r.KAM || "",
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
                <th>Конверсия (Сделка/Лид)</th>
                <th style="text-align: right;">Управление</th>
            </tr>
        </thead>
        <tbody>`;
    
    let tL = 0, tP = 0, tLD = 0, tMP = 0, tD = 0;

    sorted.forEach(data => {
        tL += data.leads; tP += data.prepays; tLD += data.leadDirectDeals; tMP += data.mpDeals; tD += data.deals;
        let cr = data.leads > 0 ? fmtPct(data.deals / data.leads) : (data.deals > 0 ? "— (нет лидов)" : "0%");
        let idBadge = data.id ? 
            `<span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-xs">ID: ${data.id}</span>` : 
            `<span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-xs">Не сметчен</span>`;

        let crColor = data.leads > 0 && data.deals > 0 ? 'text-emerald-700 font-black' : (data.deals > 0 ? 'text-blue-600 font-bold' : 'text-gray-500');

        html += `<tr>
            <td>${idBadge}</td>
            <td class="font-bold text-gray-900">${data.name}</td>
            <td class="font-medium text-gray-600">${data.kam || "—"}</td>
            <td class="font-semibold text-gray-700">${fmtNum(data.leads)}</td>
            <td class="font-semibold text-amber-700">${fmtNum(data.prepays)}</td>
            <td class="font-semibold text-purple-700">${fmtNum(data.leadDirectDeals)}</td>
            <td class="font-semibold text-indigo-700">${fmtNum(data.mpDeals)}</td>
            <td class="font-black text-blue-700">${fmtNum(data.deals)}</td>
            <td class="${crColor}">${cr}</td>
            <td style="text-align: right;">
                <a href="partner_matcher.html" target="_blank" class="px-2.5 py-1 bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 rounded-lg text-xs font-bold transition inline-flex items-center gap-1 shadow-sm">
                    Править ➔
                </a>
            </td>
        </tr>`;
    });

    let tCr = tL > 0 ? fmtPct(tD / tL) : "0%";
    html += `<tr class="table-total">
        <td>ИТОГО</td>
        <td>—</td>
        <td>—</td>
        <td>${fmtNum(tL)}</td>
        <td>${fmtNum(tP)}</td>
        <td>${fmtNum(tLD)}</td>
        <td>${fmtNum(tMP)}</td>
        <td>${fmtNum(tD)}</td>
        <td>${tCr}</td>
        <td></td>
    </tr></tbody></table>`;

    const elPartners = document.getElementById('tablePartnersContainer');
    if (elPartners) {
        elPartners.innerHTML = html;
        setupSmartSearch('searchPartners', 'tablePartnersContainer');
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
        th.addEventListener('click', () => {
            const table = th.closest('table');
            if (!table) return;
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const colIdx = Array.from(th.parentNode.children).indexOf(th);
            const isAsc = th.classList.contains('sort-asc');

            table.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            th.classList.toggle('sort-asc', !isAsc);
            th.classList.toggle('sort-desc', isAsc);

            const totalRows = rows.filter(r => r.classList.contains('table-total') || r.classList.contains('table-subtotal') || r.classList.contains('group-header'));
            const sortableRows = rows.filter(r => !r.classList.contains('table-total') && !r.classList.contains('table-subtotal') && !r.classList.contains('group-header'));

            sortableRows.sort((a, b) => {
                let aVal = a.children[colIdx]?.innerText.trim() || '';
                let bVal = b.children[colIdx]?.innerText.trim() || '';
                let aNum = parseFloat(aVal.replace(/[^0-9.-]+/g, ''));
                let bNum = parseFloat(bVal.replace(/[^0-9.-]+/g, ''));

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? aNum - bNum : bNum - aNum;
                }
                return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            });

            tbody.innerHTML = '';
            sortableRows.forEach(r => tbody.appendChild(r));
            totalRows.forEach(r => tbody.appendChild(r));
        });
    });
}
