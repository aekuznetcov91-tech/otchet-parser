/* ====================================================================
 * B2C Analytics Dashboard — Debtors & DKP Control Module
 * ====================================================================*/

function getDebtorChannelBadge(b2c) {
    const ch = (b2c || "Не указан").trim();
    if (ch === 'МП2') return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 border border-blue-200 shadow-xs">МП2</span>`;
    if (ch === 'Online') return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-xs">Online</span>`;
    if (ch === 'ФДЦ') return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700 border border-purple-200 shadow-xs">ФДЦ</span>`;
    if (ch === 'ФДЦ+ГП') return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-700 border border-indigo-200 shadow-xs">ФДЦ+ГП</span>`;
    if (ch.startsWith('МП')) return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-100 text-cyan-700 border border-cyan-200 shadow-xs">${ch}</span>`;
    if (ch.includes('лида') || ch.includes('Лид')) return `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-200 shadow-xs">${ch}</span>`;
    return `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-700 border border-gray-200">${ch}</span>`;
}

let currentDebtorAgingCohort = 'all';

function getDebtorAgeDays(d) {
    if (d && typeof d.aging_days === 'number') return d.aging_days;
    const prepayDateStr = (d && d.prepay_date) ? d.prepay_date : (typeof d === 'string' ? d : '');
    if (!prepayDateStr || prepayDateStr === '—') return 0;
    try {
        const parts = prepayDateStr.split('.');
        if (parts.length === 3) {
            const pDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
            const now = new Date();
            return Math.max(0, Math.floor((now - pDate) / (1000 * 60 * 60 * 24)));
        }
    } catch(e) {}
    return 0;
}

function getDebtorAgingBadge(prepayDateStr, car) {
    if (!prepayDateStr || prepayDateStr === '—') return '';
    const diffDays = car ? getDebtorAgeDays(car) : getDebtorAgeDays(prepayDateStr);
    if (diffDays > 60) {
        return `<span class="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-black bg-rose-200 text-rose-950 border border-rose-400 shadow-xs" title="Зависший долг более 60 дней">${diffDays} дн.</span>`;
    } else if (diffDays > 30) {
        return `<span class="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 shadow-xs" title="Контроль выдачи (31–60 дней)">${diffDays} дн.</span>`;
    } else if (diffDays > 14) {
        return `<span class="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 shadow-xs" title="В ожидании от 14 до 30 дней">${diffDays} дн.</span>`;
    } else if (diffDays >= 0) {
        return `<span class="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200" title="Свежая бронь (до 14 дней)">${diffDays} дн.</span>`;
    }
    return '';
}

function setDebtorAgingCohort(cohort) {
    currentDebtorAgingCohort = cohort || 'all';
    const btns = document.querySelectorAll('.debtor-cohort-btn');
    btns.forEach(btn => {
        const c = btn.getAttribute('data-cohort');
        if (c === currentDebtorAgingCohort) {
            btn.classList.add('bg-slate-700', 'text-white', 'border-amber-400/80');
            btn.classList.remove('bg-slate-800/80', 'text-slate-400', 'border-slate-700');
        } else {
            btn.classList.remove('bg-slate-700', 'text-white', 'border-amber-400/80');
            btn.classList.add('bg-slate-800/80', 'text-slate-400', 'border-slate-700');
        }
    });
    renderDebtorsTable(currentFilterConfig);
}

function getFilteredDebtors(filterCfg) {
    const cfg = filterCfg || currentFilterConfig;
    return rawDebtorsList.filter(d => {
        // 1. Period filter: debtors are active unclosed advances awaiting vehicle delivery.
        if (cfg && cfg.mode === 'month') {
            let m = d.prepay_date ? d.prepay_date.split('.').reverse().slice(0, 2).join('-') : "";
            if (m && m > cfg.month) return false;
        } else if (cfg && cfg.mode === 'custom') {
            const fTime = cfg.from ? cfg.from.getTime() : -Infinity;
            const tTime = cfg.to ? cfg.to.getTime() : Infinity;
            if (d.prepay_serial && d.prepay_serial > 0) {
                const jsD = excelToJSDate(d.prepay_serial);
                if (jsD) {
                    const t = jsD.getTime();
                    if (t > tTime) return false;
                }
            }
        }

        // 2. Cohort filter (светофор)
        if (currentDebtorAgingCohort && currentDebtorAgingCohort !== 'all') {
            const days = getDebtorAgeDays(d);
            if (currentDebtorAgingCohort === 'fresh') {
                if (days > 30) return false;
            } else if (currentDebtorAgingCohort === 'warning') {
                if (days <= 30 || days > 60) return false;
            } else if (currentDebtorAgingCohort === 'stale') {
                if (days <= 60) return false;
            }
        }

        return true;
    });
}

let currentDebtorKamFilter = 'all';

function applyDebtorKamFilter(kam) {
    currentDebtorKamFilter = kam || 'all';
    renderDebtorsTable(currentFilterConfig);
}

function returnToKamDashboard() {
    const kamBtn = document.querySelector("button[onclick*='tab-kam']");
    if (typeof switchTab === 'function') {
        switchTab('tab-kam', kamBtn);
    }
    const q = window.lastKamPartnerQuery;
    if (q) {
        setTimeout(() => {
            const rows = document.querySelectorAll('#kamTableContainer tr');
            for (let r of rows) {
                if (r.innerText.toLowerCase().includes(q.toLowerCase())) {
                    r.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    r.classList.add('bg-amber-100');
                    setTimeout(() => r.classList.remove('bg-amber-100'), 2500);
                    break;
                }
            }
        }, 150);
    }
}

function toggleDebtorCompany(cIdx) {
    const rows = document.querySelectorAll(`.debtor-car-row-${cIdx}`);
    const arrow = document.getElementById(`debtor-arrow-${cIdx}`);
    let isExpanding = false;
    rows.forEach(r => {
        if (r.classList.contains('hidden')) {
            r.classList.remove('hidden');
            isExpanding = true;
        } else {
            r.classList.add('hidden');
        }
    });
    if (arrow) {
        arrow.textContent = isExpanding ? '▼' : '▶';
    }
}

function renderDebtorsTable(filterCfg) {
    let filtered = getFilteredDebtors(filterCfg);

    // Apply KAM filter if active
    if (currentDebtorKamFilter && currentDebtorKamFilter !== 'all') {
        const normFilter = (typeof normalizeKamName === 'function') ? normalizeKamName(currentDebtorKamFilter) : currentDebtorKamFilter.trim();
        filtered = filtered.filter(d => {
            const dKam = (typeof normalizeKamName === 'function') ? normalizeKamName(d.kam) : (d.kam || '').trim();
            return dKam === normFilter;
        });
    }

    // Group by company
    let compMap = {};
    let totalPrepaySum = 0;
    let kamSet = new Set();

    filtered.forEach(d => {
        let c = d.company || "Неизвестная компания";
        if (!compMap[c]) {
            compMap[c] = {
                name: c,
                kam: d.kam || "",
                cars: []
            };
        }
        compMap[c].cars.push(d);
        totalPrepaySum += (d.price || 0);
        if (d.kam) kamSet.add(d.kam);
    });

    let sortedCompanies = Object.values(compMap).sort((a, b) => b.cars.length - a.cars.length || a.name.localeCompare(b.name));

    // Update Cohort Counts for Current Period
    const periodAllDebtors = rawDebtorsList.filter(d => {
        const cfg = filterCfg || currentFilterConfig;
        if (!cfg || cfg.mode === 'all') return true;
        if (cfg.mode === 'month') {
            let m = d.prepay_date ? d.prepay_date.split('.').reverse().slice(0, 2).join('-') : "";
            return !m || m <= cfg.month;
        }
        if (cfg.mode === 'custom') {
            const tTime = cfg.to ? cfg.to.getTime() : Infinity;
            if (d.prepay_serial && d.prepay_serial > 0) {
                const jsD = excelToJSDate(d.prepay_serial);
                if (jsD) {
                    const t = jsD.getTime();
                    return t <= tTime;
                }
            }
        }
        return true;
    });

    let countAll = periodAllDebtors.length;
    let countFresh = 0, countWarning = 0, countStale = 0;
    periodAllDebtors.forEach(d => {
        const days = getDebtorAgeDays(d);
        if (days <= 30) countFresh++;
        else if (days <= 60) countWarning++;
        else countStale++;
    });

    const bAll = document.getElementById('cohortBadgeAll');
    const bFresh = document.getElementById('cohortBadgeFresh');
    const bWarning = document.getElementById('cohortBadgeWarning');
    const bStale = document.getElementById('cohortBadgeStale');
    if (bAll) bAll.innerText = countAll;
    if (bFresh) bFresh.innerText = countFresh;
    if (bWarning) bWarning.innerText = countWarning;
    if (bStale) bStale.innerText = countStale;

    // Update Mini KPIs
    const elDebtorComps = document.getElementById('kpiDebtorCompanies');
    const elDebtorCars = document.getElementById('kpiDebtorCars');
    const elBadgeDebtors = document.getElementById('badgeTotalDebtors');
    const elDebtorKams = document.getElementById('kpiDebtorKams');
    const elDebtorPrepaySum = document.getElementById('kpiDebtorPrepaySum');
    const elDebtorCounter = document.getElementById('debtorRowsCounter');

    if (elDebtorComps) elDebtorComps.innerText = sortedCompanies.length;
    if (elDebtorCars) elDebtorCars.innerText = fmtNum(filtered.length);
    if (elBadgeDebtors) elBadgeDebtors.innerText = `${fmtNum(filtered.length)} авто`;
    if (elDebtorKams) elDebtorKams.innerText = kamSet.size;
    if (elDebtorPrepaySum) elDebtorPrepaySum.innerText = fmtRub(totalPrepaySum);
    if (elDebtorCounter) elDebtorCounter.innerText = `${sortedCompanies.length} компаний, ${filtered.length} авто`;

    const container = document.getElementById('tableDebtorsContainer');
    if (!container) return;

    if (sortedCompanies.length === 0) {
        container.innerHTML = `
            <div class="text-center py-10 text-gray-400">
                <div class="text-3xl mb-2">🎉</div>
                <p class="font-bold text-gray-700">Нет незакрытых сделок по выбранному фильтру</p>
                <p class="text-xs text-gray-400 mt-1">Все предоплаты успешно закрыты и реализованы в ДКП</p>
            </div>
        `;
        return;
    }

    let html = `<table id="tableDebtors" class="min-w-full text-xs">
        <thead class="bg-slate-800 text-white font-bold sticky top-0 z-10">
            <tr>
                <th class="py-2.5 px-3 text-left">Компания / ДЦ</th>
                <th class="py-2.5 px-3 text-center">КАМ</th>
                <th class="py-2.5 px-3 text-left">Дата аванса</th>
                <th class="py-2.5 px-3 text-center">Канал</th>
                <th class="py-2.5 px-3 text-left">Марка</th>
                <th class="py-2.5 px-3 text-left">Модель</th>
                <th class="py-2.5 px-3 text-left">ВИН</th>
                <th class="py-2.5 px-3 text-center">Стадия</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">`;

    sortedCompanies.forEach((comp, cIdx) => {
        let safeCompName = (comp.name || '').replace(/"/g, '&quot;');
        let safeKamName = (comp.kam || '').replace(/"/g, '&quot;');
        let brandsList = Array.from(new Set(comp.cars.map(c => c.brand).filter(Boolean))).slice(0, 3).join(', ');
        let channelsList = Array.from(new Set(comp.cars.map(c => c.b2c).filter(Boolean))).slice(0, 2).join(', ');

        // Header Row (Collapsed by default!)
        html += `
        <tr id="debtor-comp-row-${cIdx}" 
            data-company="${safeCompName}" 
            data-kam="${safeKamName}" 
            data-comp-idx="${cIdx}"
            onclick="toggleDebtorCompany('${cIdx}')"
            class="company-header-row bg-white hover:bg-amber-50/60 transition cursor-pointer font-semibold border-b border-gray-200 select-none">
            <td class="py-2.5 px-3">
                <div class="flex items-center gap-2">
                    <span id="debtor-arrow-${cIdx}" class="text-xs text-blue-600 font-bold transition-transform transform">▶</span>
                    <span class="font-bold text-slate-900 text-xs hover:text-blue-700">${comp.name}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-bold border border-amber-200 shrink-0">
                        ${comp.cars.length} авто
                    </span>
                </div>
            </td>
            <td class="text-center text-xs font-semibold text-slate-700">${comp.kam || "Не назначен"}</td>
            <td class="text-xs text-slate-500 whitespace-nowrap">—</td>
            <td class="text-center text-xs text-slate-600">${channelsList || '—'}</td>
            <td class="font-bold text-xs text-blue-900">${brandsList || '—'}</td>
            <td class="text-xs text-slate-400 italic">Нажмите, чтобы раскрыть</td>
            <td class="text-xs text-slate-400">—</td>
            <td class="text-center">
                <button type="button" class="text-blue-600 hover:text-blue-800 text-[11px] font-bold">
                    Список (${comp.cars.length}) ▾
                </button>
            </td>
        </tr>
        `;

        // Child Car Rows (Hidden by default!)
        comp.cars.forEach((car, carIdx) => {
            let rowClass = (carIdx % 2 === 0) ? "bg-slate-50/80" : "bg-white";
            let did = car.deal_id || '—';
            let didLink = (did !== '—') 
                ? `<a href="https://back.sberauto.com/crm/leads/${did}" target="_blank" class="text-blue-600 hover:underline font-bold">${did}</a>` 
                : '—';

            html += `
            <tr class="debtor-car-row-${cIdx} hidden ${rowClass} hover:bg-blue-50/50 transition border-b border-gray-100 text-xs debtor-row" 
                data-company="${safeCompName}" 
                data-kam="${safeKamName}" 
                data-car-idx="${carIdx}">
                <td class="py-1.5 pl-9 pr-3 text-slate-600 text-[11px]">
                    <div class="flex items-center gap-1.5">
                        <span class="text-amber-500 font-bold">↳</span>
                        <span class="text-gray-400 font-medium">#${carIdx + 1}</span>
                        <span class="font-medium text-slate-700">${car.manager ? `Менеджер: ${car.manager}` : ''}</span>
                        ${did !== '—' ? `<span class="text-gray-400 text-[10px]">(${didLink})</span>` : ''}
                    </div>
                </td>
                <td class="text-center text-slate-400 text-[11px]">${comp.kam || '—'}</td>
                <td class="whitespace-nowrap font-medium text-slate-700">${car.prepay_date || "—"}${getDebtorAgingBadge(car.prepay_date, car)}</td>
                <td class="text-center">${getDebtorChannelBadge(car.b2c)}</td>
                <td class="font-bold text-blue-900">${car.brand}</td>
                <td class="text-slate-700 font-medium">${car.model || car.brand}</td>
                <td class="font-mono text-[11px] text-slate-600 select-all font-semibold">${car.vin || "—"}</td>
                <td class="text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100/70 text-amber-900 border border-amber-300/60 whitespace-nowrap">${car.stage || "В ожидании ДКП"}</span></td>
            </tr>`;
        });
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function filterDebtorsTable(query) {
    let q = (query || "").toLowerCase().trim();
    let table = document.getElementById('tableDebtors');
    if (!table) return;
    
    let headerRows = table.querySelectorAll('tbody tr.company-header-row');
    if (!q) {
        headerRows.forEach(hr => {
            hr.style.display = "";
            let cIdx = hr.getAttribute('data-comp-idx');
            let carRows = table.querySelectorAll(`.debtor-car-row-${cIdx}`);
            carRows.forEach(cr => {
                cr.style.display = "";
                cr.classList.add('hidden'); // collapse back by default when search cleared
            });
            let arrow = document.getElementById(`debtor-arrow-${cIdx}`);
            if (arrow) arrow.textContent = '▶';
        });
        return;
    }

    headerRows.forEach(hr => {
        let comp = (hr.getAttribute('data-company') || '').toLowerCase();
        let kam = (hr.getAttribute('data-kam') || '').toLowerCase();
        let cIdx = hr.getAttribute('data-comp-idx');
        let carRows = table.querySelectorAll(`.debtor-car-row-${cIdx}`);
        let arrow = document.getElementById(`debtor-arrow-${cIdx}`);

        let compMatches = comp.includes(q) || kam.includes(q);
        let anyCarMatches = false;

        carRows.forEach(cr => {
            let txt = cr.innerText.toLowerCase();
            if (compMatches || txt.includes(q)) {
                cr.style.display = "";
                cr.classList.remove('hidden'); // auto-expand matched records!
                anyCarMatches = true;
            } else {
                cr.style.display = "none";
            }
        });

        if (compMatches || anyCarMatches) {
            hr.style.display = "";
            if (arrow) arrow.textContent = '▼';
        } else {
            hr.style.display = "none";
        }
    });
}

function openDebtorsExportModal() {
    const modal = document.getElementById('modalDebtorsExport');
    const container = document.getElementById('modalCompanyList');
    if (!modal || !container) return;

    let filtered = getFilteredDebtors(currentFilterConfig);

    let compMap = {};
    filtered.forEach(d => {
        let c = d.company || "Неизвестная компания";
        if (!compMap[c]) {
            compMap[c] = { name: c, kam: d.kam || "", cars: [] };
        }
        compMap[c].cars.push(d);
    });

    let sortedCompanies = Object.values(compMap).sort((a, b) => b.cars.length - a.cars.length || a.name.localeCompare(b.name));

    const subEl = document.getElementById('modalDebtorsSubtitle');
    let periodName = currentFilterConfig.mode === 'month' ? currentFilterConfig.month : (currentFilterConfig.mode === 'all' ? 'Весь период' : 'Выбранные даты');
    if (subEl) {
        subEl.innerText = `Период: ${periodName} | Компаний: ${sortedCompanies.length} (${filtered.length} авто)`;
    }

    let html = "";
    sortedCompanies.forEach((comp, idx) => {
        let safeName = encodeURIComponent(comp.name);
        html += `
            <label class="debtor-comp-item flex items-center justify-between p-2.5 rounded-xl hover:bg-emerald-50/60 transition cursor-pointer border border-transparent hover:border-emerald-200 select-none">
                <div class="flex items-center gap-3">
                    <input type="checkbox" data-company="${safeName}" data-cars-count="${comp.cars.length}" class="debtor-checkbox w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500 cursor-pointer" onchange="updateModalSelectionStats()">
                    <div>
                        <div class="font-bold text-gray-800 text-xs">${comp.name}</div>
                        <div class="text-[11px] text-gray-500">КАМ: <b class="text-slate-700">${comp.kam || "Не назначен"}</b></div>
                    </div>
                </div>
                <div class="text-right shrink-0">
                    <span class="px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 font-bold text-[11px] border border-amber-200">
                        ${comp.cars.length} авто
                    </span>
                </div>
            </label>
        `;
    });

    container.innerHTML = html;
    toggleAllDebtorCheckboxes(true);
    modal.classList.remove('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function closeDebtorsExportModal() {
    const modal = document.getElementById('modalDebtorsExport');
    if (modal) modal.classList.add('hidden');
}

function filterModalCompanies(q) {
    let query = (q || "").toLowerCase().trim();
    let items = document.querySelectorAll('.debtor-comp-item');
    items.forEach(it => {
        let txt = it.innerText.toLowerCase();
        it.style.display = txt.includes(query) ? "" : "none";
    });
}

function toggleAllDebtorCheckboxes(checked) {
    let checkboxes = document.querySelectorAll('.debtor-checkbox');
    checkboxes.forEach(cb => {
        let item = cb.closest('.debtor-comp-item');
        if (item && item.style.display !== 'none') {
            cb.checked = checked;
        }
    });
    updateModalSelectionStats();
}

function updateModalSelectionStats() {
    let checked = document.querySelectorAll('.debtor-checkbox:checked');
    let totalCars = 0;
    checked.forEach(cb => {
        totalCars += parseInt(cb.getAttribute('data-cars-count') || 0);
    });
    const elCount = document.getElementById('modalSelectedCount');
    const elCars = document.getElementById('modalSelectedCarsCount');
    if (elCount) elCount.innerText = checked.length;
    if (elCars) elCars.innerText = totalCars;
}


function executeDebtorsSingleTableExport() {
    let checked = Array.from(document.querySelectorAll('.debtor-checkbox:checked'));
    if (checked.length === 0) {
        alert("Пожалуйста, выберите хотя бы одну компанию для выгрузки.");
        return;
    }

    let selectedCompanyNames = checked.map(cb => decodeURIComponent(cb.getAttribute('data-company')));
    let filtered = getFilteredDebtors(currentFilterConfig);

    let wsData = [
        ["Компания", "Дата аванса", "Марка", "ВИН"]
    ];

    let totalCars = 0;
    filtered.forEach(d => {
        if (selectedCompanyNames.includes(d.company)) {
            wsData.push([
                d.company || "—",
                d.prepay_date || "—",
                d.brand || "—",
                d.vin || "—"
            ]);
            totalCars++;
        }
    });

    if (totalCars === 0) {
        alert("Нет данных для выгрузки по выбранным компаниям.");
        return;
    }

    let ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 35 }, // Компания
        { wch: 18 }, // Дата аванса
        { wch: 20 }, // Марка
        { wch: 25 }  // ВИН
    ];

    let wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Должники_ДКП");

    let todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    let fileName = `Должники_ДКП_Общий_реестр_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
    closeDebtorsExportModal();
    alert(`✅ Успешно выгружена таблица должников ДКП (${totalCars} авто) в файл «${fileName}»!`);
}

function executeDebtorsExcelExport() {
    let checked = Array.from(document.querySelectorAll('.debtor-checkbox:checked'));
    if (checked.length === 0) {
        alert("Пожалуйста, выберите хотя бы одну компанию для выгрузки.");
        return;
    }

    let selectedCompanyNames = checked.map(cb => decodeURIComponent(cb.getAttribute('data-company')));
    let filtered = getFilteredDebtors(currentFilterConfig);

    let compMap = {};
    filtered.forEach(d => {
        if (selectedCompanyNames.includes(d.company)) {
            if (!compMap[d.company]) compMap[d.company] = [];
            compMap[d.company].push(d);
        }
    });

    let todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    let exportedCount = 0;

    selectedCompanyNames.forEach(compName => {
        let cars = compMap[compName] || [];
        if (cars.length === 0) return;

        let wsData = [
            ["Компания", "Дата предоплаты", "Марка", "Модель", "ВИН"]
        ];

        cars.forEach(c => {
            wsData.push([
                c.company || compName,
                c.prepay_date || "—",
                c.brand || "—",
                c.model || c.brand || "—",
                c.vin || "—"
            ]);
        });

        let ws = XLSX.utils.aoa_to_sheet(wsData);
        ws['!cols'] = [
            { wch: 32 },
            { wch: 18 },
            { wch: 18 },
            { wch: 22 },
            { wch: 24 }
        ];

        let wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Долги ДКП");

        let cleanName = compName.replace(/["*\\/?:<>|]/g, '').replace(/\s+/g, '_').slice(0, 35) || 'Компания';
        let fileName = `Долги_ДКП_${cleanName}_${todayStr}.xlsx`;

        XLSX.writeFile(wb, fileName);
        exportedCount++;
    });

    closeDebtorsExportModal();
    alert(`✅ Успешно выгружено ${exportedCount} файлов Excel в папку «Загрузки»!`);
}

function executeStaleDebtorsExcelExport() {
    if (typeof XLSX === 'undefined') {
        alert("Библиотека экспорта в Excel еще загружается, повторите попытку через секунду.");
        return;
    }
    let staleDebtors = rawDebtorsList.filter(d => getDebtorAgeDays(d) > 60);
    if (staleDebtors.length === 0) {
        alert("Нет зависших долгов со сроком более 60 дней.");
        return;
    }

    let wsData = [
        ["ID Сделки", "Компания", "КАМ", "Дата аванса", "Срок просрочки (дн.)", "Марка", "Модель", "ВИН", "Стадия", "Цена авто (руб.)", "Менеджер", "Рекомендация"]
    ];

    staleDebtors.forEach(d => {
        const days = getDebtorAgeDays(d);
        wsData.push([
            d.deal_id || "—",
            d.company || "—",
            d.kam || "Не назначен",
            d.prepay_date || "—",
            days,
            d.brand || "—",
            d.model || d.brand || "—",
            d.vin || "—",
            d.stage || "В ожидании ДКП",
            d.price || 0,
            d.manager || "—",
            "Сверить с ДЦ / Закрыть в CRM (Сделка провалена/Возврат)"
        ]);
    });

    let ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 14 },
        { wch: 32 },
        { wch: 22 },
        { wch: 15 },
        { wch: 20 },
        { wch: 18 },
        { wch: 20 },
        { wch: 24 },
        { wch: 20 },
        { wch: 16 },
        { wch: 20 },
        { wch: 45 }
    ];

    let wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Зависшие_долги_более_60дн");

    let todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    let fileName = `Реестр_зависших_долгов_более_60дней_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
    alert(`✅ Успешно выгружен реестр зависших долгов (${staleDebtors.length} авто) в файл «${fileName}» для передачи координаторам и КАМам!`);
}

function executeAging20DebtorsExcelExport() {
    if (typeof XLSX === 'undefined') {
        alert("Библиотека экспорта в Excel еще загружается, повторите попытку через секунду.");
        return;
    }
    let staleDebtors = rawDebtorsList.filter(d => getDebtorAgeDays(d) >= 20);
    if (staleDebtors.length === 0) {
        alert("Нет зависших авансов со сроком от 20 дней.");
        return;
    }

    staleDebtors.sort((a, b) => getDebtorAgeDays(b) - getDebtorAgeDays(a));

    let wsData = [
        ["№", "ID Сделки", "ID Клиента", "Партнер / ДЦ", "Юрлицо в CRM", "КАМ", "Дата аванса", "Срок зависания (дн.)", "Марка", "Модель", "ВИН", "Канал", "Менеджер", "Стадия", "Цена авто (руб.)", "Ссылка на CRM BackOffice", "Рекомендация для координатора"]
    ];

    staleDebtors.forEach((d, idx) => {
        const days = getDebtorAgeDays(d);
        const did = d.deal_id || '—';
        const cid = d.client_id || '—';
        const backofficeUrl = (did !== '—') ? `https://back.sberauto.com/crm/leads/${did}` : ((cid !== '—') ? `https://back.sberauto.com/crm/clients/${cid}` : '—');

        wsData.push([
            idx + 1,
            did,
            cid,
            d.company || "—",
            d.raw_company || d.company || "—",
            d.kam || "Не назначен",
            d.prepay_date || "—",
            days,
            d.brand || "—",
            d.model || d.brand || "—",
            d.vin || "—",
            d.b2c || "—",
            d.manager || "—",
            d.stage || "В ожидании ДКП",
            d.price || 0,
            backofficeUrl,
            "Сверить с ДЦ / Закрыть в CRM (Выдача ДКП либо возврат аванса)"
        ]);
    });

    let ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 6 },
        { wch: 14 },
        { wch: 14 },
        { wch: 30 },
        { wch: 30 },
        { wch: 22 },
        { wch: 14 },
        { wch: 22 },
        { wch: 16 },
        { wch: 20 },
        { wch: 24 },
        { wch: 12 },
        { wch: 20 },
        { wch: 20 },
        { wch: 16 },
        { wch: 45 },
        { wch: 45 }
    ];

    let wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Зависшие_авансы_от_20дней");

    let todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    let fileName = `Зависшие_авансы_от_20_дней_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
    alert(`✅ Успешно сформирован и выгружен реестр (${staleDebtors.length} авто со сроком от 20 дней) в файл «${fileName}» для координаторов и КАМов!`);
}

