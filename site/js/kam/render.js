/**
 * Main render function for the KAM tab.
 */
function renderKamTab(filterCfg, tableOnly = false) {
    if (!isSyncingPlansWithCloud) {
        syncKamPlansFromCloud();
    }
    const agg = getKamAggregatedData(filterCfg || currentFilterConfig);
    const s = agg.summary;

    if (!tableOnly) {
        // 0. Render KAM Authentication Status Widget
        renderKamAuthWidget();

        // 1. Render Top 5 Executive KPI Cards
        const elInLeads = document.getElementById('kamKpiInLeads');
        const elQualLeads = document.getElementById('kamKpiQualLeads');
        const elTransLeads = document.getElementById('kamKpiTransLeads');
        const elTransDeals = document.getElementById('kamKpiTransDeals');
        const elCr = document.getElementById('kamKpiCr');

        if (elInLeads) elInLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.total_incoming_leads) : s.total_incoming_leads;
        if (elQualLeads) elQualLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.qual_leads) : s.qual_leads;
        if (elTransLeads) elTransLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.trans_leads) : s.trans_leads;
        if (elTransDeals) elTransDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.trans_deals) : s.trans_deals;
        if (elCr) elCr.innerText = `${s.overall_cr_pct.toFixed(1)}%`;

        // 2. Render 3 Deal Type Cards
        const elMpDeals = document.getElementById('kamKpiMpDeals');
        const elFdcOnlineDeals = document.getElementById('kamKpiFdcOnlineDeals');
        const elTotalDeals = document.getElementById('kamKpiTotalDeals');

        if (elMpDeals) elMpDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.mp_deals) : s.mp_deals;
        if (elFdcOnlineDeals) elFdcOnlineDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.fdc_online_deals) : s.fdc_online_deals;
        if (elTotalDeals) elTotalDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.total_deals) : s.total_deals;

        // 3. Render KAM Overall Plan Block
        renderKamPlanHeader(s);
    }

    // 4. Render Table with Accordion Hierarchy
    renderKamTable(agg.partners);

    // 5. Render Brand Breakdown Analytics Card
    renderKamBrandsSplit(agg.partners);

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Re-renders only the table without changing top cards or resetting inputs.
 */
function renderKamTableOnly() {
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamTable(agg.partners);
    renderKamBrandsSplit(agg.partners);
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Renders the interactive KAM Overall Plan card.
 */
function renderKamPlanHeader(s) {
    const cont = document.getElementById('kamPlanHeaderContainer');
    if (!cont) return;

    const kamName = currentKamFilter;
    const displayName = kamName === 'all' ? 'Все КАМ-менеджеры (Сводный план)' : `КАМ: ${kamName}`;
    const planVal = s.overall_plan;
    const factVal = s.total_deals;
    const pct = s.overall_plan_pct;

    let badgeColor = 'bg-blue-100 text-blue-700 border-blue-200';
    let progressColor = 'bg-blue-600';
    if (pct >= 100) {
        badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-300';
        progressColor = 'bg-emerald-600';
    } else if (pct < 70 && planVal > 0) {
        badgeColor = 'bg-amber-100 text-amber-800 border-amber-300';
        progressColor = 'bg-amber-500';
    }

    const canEditOverall = canUserEditOverallPlan(kamName);
    const activeAuthUser = getKamActiveUser();
    let overallPlanInputHtml = '';

    if (canEditOverall) {
        overallPlanInputHtml = `
            <input type="number" min="0" step="1"
                value="${planVal || ''}"
                placeholder="0"
                class="w-24 text-center text-base font-black text-blue-700 bg-blue-50/70 border border-blue-300 rounded-lg px-2 py-1 outline-none focus:ring-2 focus:ring-blue-500 transition"
                onchange="onKamOverallPlanChange('${kamName}', this.value)"
                onkeyup="if(event.key==='Enter') this.blur();"
                title="Введите общий план сделок (сохраняется автоматически)">
        `;
    } else {
        const lockTitle = activeAuthUser
            ? (kamName === 'all'
                ? 'Общий план сети может устанавливать только Руководитель / Администратор'
                : `План сотрудника «${displayName}» может редактировать только он сам или Руководитель`)
            : `Для изменения плана войдите в профиль сотрудника «${displayName}» или Руководителя`;
        overallPlanInputHtml = `
            <div class="flex items-center gap-1.5 cursor-pointer group" onclick="openKamLoginModal('${kamName}')" title="${lockTitle} (нажмите для входа)">
                <input type="number" disabled
                    value="${planVal || ''}"
                    placeholder="0"
                    class="w-24 text-center text-base font-black text-gray-500 bg-gray-100 border border-gray-200 rounded-lg px-2 py-1 cursor-not-allowed opacity-80">
                <span class="text-xs text-amber-600 group-hover:text-blue-600 transition" title="Заблокировано (требуется вход)">🔒</span>
            </div>
        `;
    }

    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    cont.innerHTML = `
    <div class="card !p-4 bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-white border border-blue-200 shadow-sm rounded-2xl">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="w-11 h-11 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-xl shadow-md shrink-0">
                    🎯
                </div>
                <div>
                    <div class="flex items-center gap-2 flex-wrap">
                        <h3 class="text-base font-black text-gray-900">${displayName}</h3>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${badgeColor}">
                            Выполнение: ${pct.toFixed(1)}%
                        </span>
                    </div>
                    <p class="text-xs text-gray-500 mt-0.5 flex items-center gap-1.5 flex-wrap">
                        <span>Факт: <b class="text-gray-800">${fmt(factVal)} сделок</b></span>
                        <span>|</span>
                        <span>Сумма планов партнеров: <b class="text-blue-700">${fmt(s.sum_partner_plans)}</b></span>
                        <span class="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-bold">☁️ Онлайн-синхронизация активна</span>
                    </p>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <!-- Item 4: Legal Entities & Rooftops Card -->
                <div class="bg-white px-3.5 py-2 rounded-xl border border-indigo-200 shadow-sm cursor-pointer hover:bg-indigo-50/70 hover:border-indigo-400 transition min-w-[280px]" onclick="openKamLegalEntitiesModal('rooftops')" title="Нажмите, чтобы посмотреть детализацию по крышам и юр. лицам">
                    <div class="flex items-center justify-between gap-2 mb-1">
                        <div class="flex items-center gap-1.5">
                            <span class="text-xs">🏢</span>
                            <span class="text-[10px] font-black text-indigo-900 uppercase tracking-wider">Юр. лица и Крыши</span>
                        </div>
                        <span class="text-[10px] text-indigo-600 font-bold underline">детализация ➔</span>
                    </div>
                    <div class="flex items-center justify-between gap-2 text-xs">
                        <div class="flex-1">
                            <span class="text-[9px] font-bold text-gray-400 uppercase block leading-none">Юр. лица</span>
                            <div class="font-black text-gray-900 flex items-center gap-1 mt-0.5">
                                <span class="text-indigo-950 font-black text-xs">${fmt(s.legal_entities_count || 0)}</span>
                                <span class="text-gray-400 text-[10px] font-normal">из ${fmt(s.total_assigned_partners || s.legal_entities_count)}</span>
                                <span class="text-[9px] font-bold px-1 py-0.2 bg-indigo-50 text-indigo-700 rounded border border-indigo-200">${(s.active_pct || 0).toFixed(0)}%</span>
                            </div>
                            <span class="text-[9px] text-gray-500 block leading-tight mt-0.5">Сделок: <b class="text-gray-800">${fmt(s.total_deals || 0)}</b></span>
                        </div>
                        <div class="h-8 w-[1px] bg-indigo-100 shrink-0"></div>
                        <div class="flex-1 pl-1">
                            <span class="text-[9px] font-bold text-gray-400 uppercase block leading-none">Крыши (Город+Бренд)</span>
                            <div class="font-black text-gray-900 flex items-center gap-1 mt-0.5">
                                <span class="text-indigo-950 font-black text-xs">${fmt(s.rooftops_count || 0)}</span>
                                <span class="text-gray-400 text-[10px] font-normal">из ${fmt(s.total_assigned_rooftops || s.rooftops_count)}</span>
                                <span class="text-[9px] font-bold px-1 py-0.2 bg-purple-50 text-purple-700 rounded border border-purple-200">${(s.rooftops_active_pct || 0).toFixed(0)}%</span>
                            </div>
                            <span class="text-[9px] text-gray-500 block leading-tight mt-0.5">Сделок: <b class="text-gray-800">${fmt(s.total_deals || 0)}</b></span>
                        </div>
                    </div>
                </div>

                <!-- Interactive Plan Input with Auto-Save -->
                <div class="flex items-center gap-3 bg-white p-2 rounded-xl border border-gray-200 shadow-sm">
                    <div class="text-right">
                        <span class="text-[11px] font-bold text-gray-500 uppercase block">Общий план сделок</span>
                        <span class="text-[10px] text-emerald-600 font-semibold" title="Все изменения моментально сохраняются в облачную базу данных Cloudflare KV для всех пользователей">⚡ Автосохранение в облако</span>
                    </div>
                    <div class="relative">
                        ${overallPlanInputHtml}
                    </div>
                    <span class="text-xs font-bold text-gray-400">шт.</span>
                </div>

                <!-- Export / Import Plans Backup -->
                <div class="flex items-center gap-1.5 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
                    <button type="button" onclick="exportKamPlansJson()" class="px-2.5 py-1 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-[11px] font-bold shadow-xs flex items-center gap-1 transition" title="Скопировать все планы КАМ и партнеров в буфер обмена (JSON)">
                        <span>📋</span> Экспорт
                    </button>
                    <button type="button" onclick="importKamPlansPrompt()" class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-[11px] font-bold shadow-xs flex items-center gap-1 transition" title="Импортировать планы из JSON">
                        <span>📥</span> Импорт
                    </button>
                </div>
            </div>
        </div>

        <!-- Progress Bar -->
        <div class="mt-3">
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden shadow-inner">
                <div class="h-full ${progressColor} rounded-full transition-all duration-500" style="width: ${Math.min(100, pct)}%"></div>
            </div>
            <div class="flex justify-between text-[11px] font-semibold text-gray-500 mt-1">
                <span>0 сделок</span>
                <span>Факт: <b>${fmt(factVal)}</b> из <b>${fmt(planVal)}</b></span>
                <span>Цель: 100%</span>
            </div>
        </div>
    </div>
    `;
}

/**
 * Formats MTD deal comparison with percentage dynamic.
 * Formula: ((Текущие - MTD) / MTD) * 100%
 */
function getMtdDynamicsHtml(currentDeals, mtdDeals) {
    if (mtdDeals === null || mtdDeals === undefined || (typeof currentFilterConfig !== 'undefined' && currentFilterConfig.mode === 'all')) {
        return '<span class="text-gray-400 font-medium">—</span>';
    }
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    const cur = currentDeals || 0;
    const mtd = mtdDeals || 0;

    if (mtd === 0) {
        if (cur > 0) {
            return `<div class="flex items-center justify-center gap-1">
                <span class="font-bold text-gray-700 text-xs">${fmt(mtd)}</span>
                <span class="text-[10px] font-black text-emerald-700 bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200">+${fmt(cur)}</span>
            </div>`;
        }
        return `<span class="text-gray-400 font-medium text-xs">${fmt(mtd)} <span class="text-[10px] text-gray-400">(0%)</span></span>`;
    }

    const diffPct = ((cur - mtd) / mtd) * 100;
    const sign = diffPct > 0 ? '+' : '';
    const pctStr = `${sign}${diffPct.toFixed(0)}%`;

    let badgeClass = 'text-gray-600 bg-gray-50 border-gray-200';
    if (diffPct > 0) {
        badgeClass = 'text-emerald-700 bg-emerald-50 border-emerald-200 font-black';
    } else if (diffPct < 0) {
        badgeClass = 'text-rose-700 bg-rose-50 border-rose-200 font-bold';
    }

    return `<div class="flex items-center justify-center gap-1">
        <span class="font-bold text-gray-800 text-xs">${fmt(mtd)}</span>
        <span class="text-[10px] px-1 py-0.2 rounded border ${badgeClass}">${pctStr}</span>
    </div>`;
}

/**
 * Formats Debts count with interactive clickable badge opening Debtors tab.
 */
function getDebtsHtml(debtsCount, partnerName) {
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    if (!debtsCount || debtsCount <= 0) {
        return `<span class="text-gray-400 font-medium text-xs">—</span>`;
    }
    const safeName = (partnerName || '').replace(/'/g, "\\'");
    return `<button type="button"
        onclick="event.stopPropagation(); openDebtorsTabForPartner('${safeName}')"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-black bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 shadow-xs transition cursor-pointer"
        title="Нажмите, чтобы открыть реестр должников по партнеру ${safeName}">
        <span>⚠️</span> ${fmt(debtsCount)}
    </button>`;
}

/**
 * Formats Debts count for brand subrows.
 */
function getBrandDebtsHtml(debtsCount, partnerName, brandName) {
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    if (!debtsCount || debtsCount <= 0) {
        return `<span class="text-gray-400 font-medium text-[11px]">—</span>`;
    }
    const safeSearch = `${partnerName} ${brandName}`.replace(/'/g, "\\'");
    return `<button type="button"
        onclick="event.stopPropagation(); openDebtorsTabForPartner('${safeSearch}')"
        class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 transition cursor-pointer"
        title="Нажмите, чтобы открыть должников по ${safeSearch}">
        ${fmt(debtsCount)}
    </button>`;
}

/**
 * Opens Debtors tab with pre-filled search query for this partner
 */
function openDebtorsTabForPartner(partnerQuery) {
    window.lastKamPartnerQuery = partnerQuery;
    const btn = document.querySelector("button[onclick*='tab-details']");
    if (typeof switchTab === 'function') {
        switchTab('tab-details', btn);
    }

    // Show return button in debtors tab
    const returnBtn = document.getElementById('btnReturnToKam');
    const returnText = document.getElementById('btnReturnToKamText');
    if (returnBtn) {
        returnBtn.classList.remove('hidden');
        if (returnText) {
            const shortQ = (partnerQuery && partnerQuery.length > 20) ? (partnerQuery.slice(0, 18) + '...') : (partnerQuery || 'партнеру');
            returnText.innerText = `Назад в КАМ (${shortQ})`;
        }
    }

    setTimeout(() => {
        const searchInput = document.getElementById('searchDebtors');
        if (searchInput) {
            searchInput.value = partnerQuery || '';
            if (typeof filterDebtorsTable === 'function') {
                filterDebtorsTable(partnerQuery || '');
            }
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 50);
}

/**
 * Renders the hierarchical table: Partner -> City -> Brand.
 */
function renderKamTable(partners) {
    const cont = document.getElementById('kamTableContainer');
    if (!cont) return;

    const q = currentKamSearchQuery;
    const planStatus = currentKamPlanFilter;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    // Filter partners by search and plan status
    const displayList = partners.filter(p => {
        if (q) {
            const matchName = (p.name || '').toLowerCase().includes(q);
            const matchKam = (p.kam || '').toLowerCase().includes(q);
            const matchCity = Object.keys(p.cities || {}).some(c => c.toLowerCase().includes(q));
            const matchBrand = Object.keys(p.brands || {}).some(b => b.toLowerCase().includes(q));
            if (!matchName && !matchKam && !matchCity && !matchBrand) return false;
        }
        if (planStatus === 'completed' && p.plan_pct < 100) return false;
        if (planStatus === 'in_progress' && (p.plan <= 0 || p.plan_pct >= 100)) return false;
        if (planStatus === 'no_plan' && p.plan > 0) return false;
        return true;
    });

    // Sort by Total Deals descending
    displayList.sort((a, b) => (b.total_deals + b.trans_leads) - (a.total_deals + a.trans_leads));

    let html = `
    <table id="tableKamPartners" class="min-w-full">
        <thead>
            <tr>
                <th style="min-width: 250px;">Партнер / Город / Бренд</th>
                <th style="width: 140px; text-align: center;">Закрепленный КАМ</th>
                <th style="width: 120px; text-align: center;">План сделок</th>
                <th style="width: 100px; text-align: center;">% плана</th>
                <th style="width: 110px; text-align: center;">Передано лидов</th>
                <th style="width: 130px; text-align: center;" title="Чистые сделки с передачи лидов (без сделок, закрытых через МП или ФДЦ/Online)">
                    Сделки с передачи <span class="text-[10px] text-purple-600 block">(из переданных)</span>
                </th>
                <th style="width: 110px; text-align: center;" title="Конверсия: Сделки с передачи / Передано лидов">CR (Передача)</th>
                <th style="width: 105px; text-align: center;">Сделки МП</th>
                <th style="width: 130px; text-align: center;">Сделки ФДЦ / Online</th>
                <th style="width: 115px; text-align: center;">Сделки Всего</th>
                <th style="width: 130px; text-align: center;" title="Сделок на эту же дату в прошлом месяце (динамика к текущим сделкам)">
                    MTD <span class="text-[10px] text-blue-500 block font-normal">(прошлый мес.)</span>
                </th>
                <th style="width: 110px; text-align: center;" title="Количество ДКП с внесенной предоплатой в ожидании реализации сделки">
                    Долги <span class="text-[10px] text-amber-500 block font-normal">(ожидание ДКП)</span>
                </th>
            </tr>
        </thead>
        <tbody>
    `;

    if (displayList.length === 0) {
        html += `
        <tr>
            <td colspan="12" class="text-center py-8 text-gray-400 font-medium">
                🔍 Партнеры по выбранным фильтрам не найдены
            </td>
        </tr>
        </tbody></table>`;
        cont.innerHTML = html;
        return;
    }

    let tPlan = 0, tTransL = 0, tTransD = 0, tMpD = 0, tFdcOnlD = 0, tMtdD = 0, tTotD = 0, tDebts = 0;

    displayList.forEach((p, idx) => {
        tPlan += (p.plan || 0);
        tTransL += p.trans_leads;
        tTransD += p.trans_deals;
        tMpD += p.mp_deals;
        tFdcOnlD += p.fdc_online_deals;
        tMtdD += (p.mtd_deals || 0);
        tTotD += p.total_deals;
        tDebts += (p.debts_count || 0);

        const safeKey = 'krow_' + idx + '_' + (p.id ? String(p.id) : 'raw') + '_' + p.key.replace(/[^a-zA-Z0-9_-]/g, '_');
        const crFormatted = p.trans_leads > 0 ? `${p.cr_pct.toFixed(1)}%` : (p.trans_deals > 0 ? '—' : '0%');

        let crColor = 'text-gray-500';
        if (p.trans_leads > 0) {
            if (p.cr_pct < 7) {
                crColor = 'text-rose-600 font-bold';
            } else if (p.cr_pct <= 13) {
                crColor = 'text-amber-600 font-bold';
            } else {
                crColor = 'text-emerald-700 font-black';
            }
        } else if (p.trans_deals > 0) {
            crColor = 'text-blue-600 font-bold';
        }

        let planBadge = 'text-gray-400';
        if (p.plan > 0) {
            planBadge = p.plan_pct >= 100 ? 'text-emerald-700 font-black' : (p.plan_pct >= 70 ? 'text-blue-600 font-bold' : 'text-amber-600 font-bold');
        }

        const idBadge = p.id ? `<span class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px] mr-1.5">ID:${p.id}</span>` : '';
        const citiesList = Object.keys(p.cities || {});
        const citiesCount = citiesList.length;
        const brandsCount = Object.keys(p.brands || {}).length;
        const hasSubrows = citiesCount > 0 || brandsCount > 0;

        const safePNameAttr = (p.name || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

        // Level 1: Partner Row
        html += `
        <tr class="font-semibold bg-white hover:bg-blue-50/40 transition cursor-pointer select-none border-b border-gray-200"
            data-total-deals="${p.total_deals}"
            onclick="toggleKamPartnerRows('${safeKey}')">
            <td class="py-2.5 px-3">
                <div class="flex items-center gap-1.5">
                    ${hasSubrows ? `<span id="kamArrow_${safeKey}" class="text-xs text-gray-400 transition-transform transform">▶</span>` : '<span class="w-3"></span>'}
                    <div>
                        <div class="flex items-center gap-1">
                            ${idBadge}
                            <span class="text-gray-900 font-bold text-xs hover:text-blue-600">${p.name}</span>
                        </div>
                        <div class="text-[10px] text-gray-400 flex items-center gap-2 mt-0.5">
                            <span>🏙️ ${citiesCount > 0 ? citiesList.slice(0, 2).join(', ') + (citiesCount > 2 ? ` (+${citiesCount - 2})` : '') : 'Город не указан'}</span>
                            <span>🏷️ ${brandsCount} ${brandsCount === 1 ? 'бренд' : 'брендов'}</span>
                        </div>
                    </div>
                </div>
            </td>
            <td class="text-center text-xs text-gray-600">${p.kam || '—'}</td>

            <!-- Interactive Partner Plan Input with Auto-Save (Role Protected) -->
            <td class="text-center" onclick="event.stopPropagation()">
                <div class="flex items-center justify-center gap-1">
                    ${getPartnerPlanCellHtml(p)}
                </div>
            </td>

            <td class="text-center ${planBadge} kam-plan-pct">${p.plan > 0 ? `${p.plan_pct.toFixed(0)}%` : '—'}</td>
            <td class="text-center font-bold text-gray-700">
                ${p.trans_leads > 0
                    ? `<button type="button" data-pid="${p.id || ''}" data-pname="${safePNameAttr}" onclick="event.stopPropagation(); handleTransLeadsButtonClick(this)" class="px-2 py-0.5 rounded font-bold text-blue-600 hover:text-blue-900 hover:bg-blue-100 transition underline decoration-dotted cursor-pointer" title="Посмотреть переданные лиды (${p.trans_leads} шт.)">${fmt(p.trans_leads)}</button>`
                    : `<span class="text-gray-400">0</span>`}
            </td>
            <td class="text-center font-black text-purple-700 bg-purple-50/40">${fmt(p.trans_deals)}</td>
            <td class="text-center ${crColor}">${crFormatted}</td>
            <td class="text-center font-bold text-amber-700">${fmt(p.mp_deals)}</td>
            <td class="text-center font-bold text-sky-700 bg-sky-50/30">${fmt(p.fdc_online_deals)}</td>
            <td class="text-center font-black text-blue-700 bg-blue-50/40 text-sm kam-total-deals">${fmt(p.total_deals)}</td>
            <td class="text-center bg-blue-50/20">${getMtdDynamicsHtml(p.total_deals, p.mtd_deals)}</td>
            <td class="text-center bg-amber-50/30">${getDebtsHtml(p.debts_count, p.name)}</td>
        </tr>
        `;

        // Level 2 & 3: Breakdown by City & Brands (Hidden Accordion Subrows)
        if (hasSubrows) {
            const renderCities = Object.keys(p.cities || {}).length > 0 ? p.cities : {
                'Город не указан': {
                    name: 'Город не указан',
                    brands: p.brands || {}
                }
            };

            Object.entries(renderCities).forEach(([cityName, cityData]) => {
                const cityBrands = (cityData.brands && Object.keys(cityData.brands).length > 0) ? cityData.brands : (p.brands || {});
                html += `
                <tr class="kam-subrow-${safeKey} hidden bg-slate-50/90 text-xs border-l-4 border-blue-400">
                    <td class="py-1.5 pl-8 font-semibold text-gray-800 flex items-center gap-2">
                        <span class="text-blue-600 font-bold">📍 ${cityName}</span>
                        <span class="text-[10px] text-gray-400">(${Object.keys(cityBrands).length} брендов)</span>
                    </td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-700 font-bold">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                </tr>
                `;

                Object.entries(cityData.brands || {}).forEach(([brandName, brandInfo]) => {
                    const bStats = p.brands[brandName] || brandInfo || { trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                    const bCrVal = bStats.trans_leads > 0 ? (bStats.trans_deals / bStats.trans_leads * 100) : 0;
                    const bCr = bStats.trans_leads > 0 ? `${bCrVal.toFixed(1)}%` : (bStats.trans_deals > 0 ? '—' : '0%');
                    let bCrColor = 'text-gray-500';
                    if (bStats.trans_leads > 0) {
                        if (bCrVal < 7) bCrColor = 'text-rose-600 font-bold';
                        else if (bCrVal <= 13) bCrColor = 'text-amber-600 font-bold';
                        else bCrColor = 'text-emerald-700 font-black';
                    } else if (bStats.trans_deals > 0) {
                        bCrColor = 'text-blue-600 font-bold';
                    }
                    const safeBNameAttr = brandName.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

                    html += `
                    <tr class="kam-subrow-${safeKey} hidden bg-white/90 text-[11px] hover:bg-gray-100 transition border-b border-gray-100">
                        <td class="py-1 pl-12 text-gray-600">
                            <span class="px-2 py-0.5 rounded bg-gray-100 text-gray-800 font-bold border border-gray-200">${brandName}</span>
                            ${brandInfo.dealer_name ? `<span class="text-[10px] text-gray-400 ml-1.5">${brandInfo.dealer_name}</span>` : ''}
                        </td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-600">
                            ${bStats.trans_leads > 0
                                ? `<button type="button" data-pid="${p.id || ''}" data-pname="${safePNameAttr}" data-brand="${safeBNameAttr}" onclick="event.stopPropagation(); handleTransLeadsButtonClick(this)" class="px-1.5 py-0.5 rounded font-semibold text-blue-600 hover:text-blue-900 hover:bg-blue-100 transition underline decoration-dotted cursor-pointer" title="Посмотреть переданные лиды по марке ${brandName}">${fmt(bStats.trans_leads)}</button>`
                                : `<span class="text-gray-400">0</span>`}
                        </td>
                        <td class="text-center text-purple-700 font-semibold">${fmt(bStats.trans_deals)}</td>
                        <td class="text-center ${bCrColor}">${bCr}</td>
                        <td class="text-center text-amber-700">${fmt(bStats.mp_deals)}</td>
                        <td class="text-center text-sky-700">${fmt(bStats.fdc_online_deals)}</td>
                        <td class="text-center font-bold text-blue-600">${fmt(bStats.total_deals)}</td>
                        <td class="text-center">${getMtdDynamicsHtml(bStats.total_deals, bStats.mtd_deals)}</td>
                        <td class="text-center">${getBrandDebtsHtml(bStats.debts_count, p.name, brandName)}</td>
                    </tr>
                    `;
                });
            });
        }
    });

    // Table Total Footer
    const totalCrVal = tTransL > 0 ? (tTransD / tTransL * 100) : 0;
    const totalCr = tTransL > 0 ? `${totalCrVal.toFixed(1)}%` : '0%';
    let totalCrColor = 'text-gray-700';
    if (tTransL > 0) {
        if (totalCrVal < 7) totalCrColor = 'text-rose-600 font-bold';
        else if (totalCrVal <= 13) totalCrColor = 'text-amber-600 font-bold';
        else totalCrColor = 'text-emerald-700 font-black';
    }
    const totalPlanPct = tPlan > 0 ? `${(tTotD / tPlan * 100).toFixed(1)}%` : '—';

    html += `
        <tr class="table-total font-black">
            <td class="py-2.5 px-3">ИТОГО ПО ВЫБРАННЫМ</td>
            <td class="text-center">—</td>
            <td class="text-center">${fmt(tPlan)}</td>
            <td class="text-center">${totalPlanPct}</td>
            <td class="text-center">${fmt(tTransL)}</td>
            <td class="text-center">${fmt(tTransD)}</td>
            <td class="text-center ${totalCrColor}">${totalCr}</td>
            <td class="text-center">${fmt(tMpD)}</td>
            <td class="text-center">${fmt(tFdcOnlD)}</td>
            <td class="text-center">${fmt(tTotD)}</td>
            <td class="text-center">${getMtdDynamicsHtml(tTotD, tMtdD)}</td>
            <td class="text-center text-amber-900">${tDebts > 0 ? fmt(tDebts) : '—'}</td>
        </tr>
    </tbody>
    </table>
    `;

    cont.innerHTML = html;
}

/**
 * Renders the brand split analytics for the selected KAM.
 */
function renderKamBrandsSplit(partners) {
    const cont = document.getElementById('kamBrandsSummaryContainer');
    if (!cont) return;

    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    const brandTotals = {};

    partners.forEach(p => {
        Object.entries(p.brands || {}).forEach(([brand, stats]) => {
            const nb = normalizeBrandName(brand);
            if (!nb) return; // exclude non-auto categories
            if (!brandTotals[nb]) {
                brandTotals[nb] = {
                    name: nb,
                    trans_leads: 0,
                    trans_deals: 0,
                    mp_deals: 0,
                    fdc_online_deals: 0,
                    total_deals: 0
                };
            }
            brandTotals[nb].trans_leads += stats.trans_leads;
            brandTotals[nb].trans_deals += stats.trans_deals;
            brandTotals[nb].mp_deals += stats.mp_deals;
            brandTotals[nb].fdc_online_deals += stats.fdc_online_deals;
            brandTotals[nb].total_deals += stats.total_deals;
        });
    });

    const sortedBrands = Object.values(brandTotals).sort((a, b) => b.total_deals - a.total_deals);

    if (sortedBrands.length === 0) {
        cont.innerHTML = '';
        return;
    }

    let html = `
    <div class="card !p-4 bg-white border border-gray-200 shadow-sm rounded-2xl">
        <div class="flex items-center justify-between border-b pb-3 mb-3">
            <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                <i data-lucide="tag" class="w-4 h-4 text-blue-600"></i>
                Сплит брендов у партнеров (${currentKamFilter === 'all' ? 'Все КАМы' : currentKamFilter})
            </h3>
            <span class="text-xs text-gray-500 font-semibold">${sortedBrands.length} брендов</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
    `;

    sortedBrands.forEach(b => {
        const cr = b.trans_leads > 0 ? `${(b.trans_deals / b.trans_leads * 100).toFixed(1)}%` : '0%';
        html += `
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-3 flex flex-col justify-between hover:border-blue-400 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-black text-gray-800">${b.name}</span>
                <span class="text-[11px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 font-bold">${fmt(b.total_deals)} шт</span>
            </div>
            <div class="text-[10px] text-gray-500 space-y-0.5 mt-2 pt-2 border-t border-gray-200">
                <div class="flex justify-between">
                    <span>Передано:</span>
                    <b class="text-gray-700">${fmt(b.trans_leads)}</b>
                </div>
                <div class="flex justify-between">
                    <span>Сделки перев:</span>
                    <b class="text-purple-700">${fmt(b.trans_deals)}</b>
                </div>
                <div class="flex justify-between">
                    <span>CR перевода:</span>
                    <b class="text-emerald-700">${cr}</b>
                </div>
                <div class="flex justify-between">
                    <span>МП:</span>
                    <b class="text-amber-700">${fmt(b.mp_deals)}</b>
                </div>
                <div class="flex justify-between">
                    <span>ФДЦ/Online:</span>
                    <b class="text-sky-700">${fmt(b.fdc_online_deals)}</b>
                </div>
            </div>
        </div>
        `;
    });

    html += `</div></div>`;
    cont.innerHTML = html;
}

/**
 * Export current KAM report to Excel (.xlsx) using SheetJS.
 */
