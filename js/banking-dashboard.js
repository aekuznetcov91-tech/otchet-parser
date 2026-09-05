/**
 * banking-dashboard.js
 * ====================
 * Интерактивный модуль дашборда "Лиды, Сделки ДЦ и Банки (СберАвто)".
 * 
 * Включает:
 * 1. Воронка передач лидов и сделок (Pipeline 1-4, кликабельный просмотр)
 * 2. Графики структуры оплат: Donut (Сбер / Др.банки / Нал) и Stacked Bar (Лиды СА vs Сделки ДЦ)
 * 3. Виджеты ТОП-10 Сбербанк vs АНТИТОП-10 Другие банки с переключением режима (% / шт.)
 *    и раскрытием полного списка партнеров
 * 4. Сводная матрица по 8 макрорегионам (РЦ)
 * 5. Рейтинг всех дилеров с живым поиском на лету
 * 6. Модальное окно детального просмотра базы сделок с фильтрами по банкам
 */

let bankingCharts = {
    paymentDonut: null,
    leadsVsDcBar: null
};

let currentBankingRankMode = 'share'; // 'share' (%) или 'volume' (шт.)
let isTopSberExpanded = false;
let isAntiTopExpanded = false;
let currentActiveDb = 'lead_deals'; // 'lead_deals' или 'other_deals'
let currentDbFilter = 'all'; // 'all', 'sber', 'other_banks', 'cash'

function getBankingData() {
    return (window.dataPayload && window.dataPayload.banking_analytics)
        || (window.currentData && window.currentData.banking_analytics)
        || (window.bankingAnalyticsData || null);
}

function switchBankingSection(secId, btn) {
    const secFunnel = document.getElementById('b_sec_funnel');
    const secRankings = document.getElementById('b_sec_rankings');
    const secPartners = document.getElementById('b_sec_partners');

    document.querySelectorAll('[id^="b_tabBtn_"]').forEach(b => {
        b.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition cursor-pointer';
    });
    if (btn) {
        btn.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-sm transition cursor-pointer';
    }

    if (secId === 'all') {
        if (secFunnel) secFunnel.classList.remove('hidden');
        if (secRankings) secRankings.classList.remove('hidden');
        if (secPartners) secPartners.classList.remove('hidden');
    } else {
        if (secFunnel) secFunnel.classList.toggle('hidden', secId !== 'funnel');
        if (secRankings) secRankings.classList.toggle('hidden', secId !== 'rankings');
        if (secPartners) secPartners.classList.toggle('hidden', secId !== 'partners');
    }
}

function renderBankingDashboard() {
    const banking = getBankingData();
    if (!banking) {
        const container = document.getElementById('tab-banking');
        if (container) {
            container.innerHTML = `
                <div class="p-8 text-center bg-white rounded-2xl border border-gray-200 shadow-sm">
                    <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center">
                        <i data-lucide="alert-circle" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-lg font-bold text-gray-800 mb-2">Данные по банковскому проникновению не найдены</h3>
                    <p class="text-sm text-gray-500 max-w-md mx-auto mb-4">
                        Для отображения этой вкладки поместите обогащенную выгрузку сделок (со столбцом «Банк») в папку <code class="bg-gray-100 px-1.5 py-0.5 rounded text-gray-700 font-mono text-xs">raw_data/</code> и запустите парсер.
                    </p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
        return;
    }

    // 1. Обновление KPI карточек сквозной воронки
    document.getElementById('b_transfers_total').innerText = (banking.transfers_total || 0).toLocaleString();
    document.getElementById('b_transfers_new').innerText = (banking.transfers_new || 0).toLocaleString();
    document.getElementById('b_transfers_used').innerText = (banking.transfers_used || 0).toLocaleString();

    document.getElementById('b_lead_deals_total').innerText = (banking.lead_deals_total || 0).toLocaleString();
    document.getElementById('b_lead_deals_sber').innerText = (banking.lead_deals_sber || 0).toLocaleString();
    document.getElementById('b_lead_deals_other_banks').innerText = (banking.lead_deals_other_banks || 0).toLocaleString();
    document.getElementById('b_lead_deals_cash').innerText = (banking.lead_deals_cash || 0).toLocaleString();
    document.getElementById('b_lead_cr').innerText = (banking.lead_cr || 0) + '%';

    document.getElementById('b_other_deals_total').innerText = (banking.other_deals_total || 0).toLocaleString();
    document.getElementById('b_other_deals_sber').innerText = (banking.other_deals_sber || 0).toLocaleString();
    document.getElementById('b_other_deals_other_banks').innerText = (banking.other_deals_other_banks || 0).toLocaleString();
    document.getElementById('b_other_deals_cash').innerText = (banking.other_deals_cash || 0).toLocaleString();

    document.getElementById('b_deals_total').innerText = (banking.deals_total || 0).toLocaleString();
    document.getElementById('b_deals_sber').innerText = (banking.deals_sber || 0).toLocaleString();
    document.getElementById('b_deals_other_banks').innerText = (banking.deals_other_banks || 0).toLocaleString();
    document.getElementById('b_deals_cash').innerText = (banking.deals_cash || 0).toLocaleString();

    const totalCredits = (banking.deals_sber || 0) + (banking.deals_other_banks || 0);
    const credPct = banking.deals_total > 0 ? ((totalCredits / banking.deals_total) * 100).toFixed(1) : '0.0';
    const sberPct = totalCredits > 0 ? (((banking.deals_sber || 0) / totalCredits) * 100).toFixed(1) : '0.0';

    document.getElementById('b_deals_credit_pct').innerText = credPct + '%';
    document.getElementById('b_deals_sber_pct').innerText = sberPct + '%';

    if (banking.source_file) {
        const srcEl = document.getElementById('b_source_badge');
        if (srcEl) srcEl.innerText = `Источник: ${banking.source_file}`;
    }

    // 2. Рендеринг графиков
    renderBankingCharts(banking);

    // 3. Рендеринг ТОП / АНТИТОП
    renderBankingRankings(banking);

    // 4. Рендеринг 8 макрорегионов
    renderBankingMacroTable(banking.macro_rows || []);

    // 5. Рендеринг таблицы всех партнеров
    renderBankingAllPartnersTable(banking.all_partners || []);

    if (window.lucide) lucide.createIcons();
}

function renderBankingCharts(banking) {
    // Donut Chart: Общая структура оплат
    const ctxDonut = document.getElementById('b_chart_payments');
    if (ctxDonut) {
        if (bankingCharts.paymentDonut) bankingCharts.paymentDonut.destroy();

        const sber = banking.deals_sber || 0;
        const ob = banking.deals_other_banks || 0;
        const cash = banking.deals_cash || 0;
        const total = banking.deals_total || 1;

        const pSber = ((sber / total) * 100).toFixed(1);
        const pOb = ((ob / total) * 100).toFixed(1);
        const pCash = ((cash / total) * 100).toFixed(1);

        bankingCharts.paymentDonut = new Chart(ctxDonut, {
            type: 'doughnut',
            data: {
                labels: [`Наличные (${pCash}%)`, `Сбербанк (${pSber}%)`, `Другие банки (${pOb}%)`],
                datasets: [{
                    data: [cash, sber, ob],
                    backgroundColor: ['#64748B', '#21A038', '#E74C3C'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11, weight: 'bold' } } },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return ` ${ctx.label}: ${ctx.raw.toLocaleString()} шт.`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    }

    // Stacked Bar Chart: Лиды СА vs Сделки ДЦ
    const ctxBar = document.getElementById('b_chart_comparison');
    if (ctxBar) {
        if (bankingCharts.leadsVsDcBar) bankingCharts.leadsVsDcBar.destroy();

        bankingCharts.leadsVsDcBar = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: [
                    `Сделки по лидам СА (${banking.lead_deals_total || 0})`,
                    `Другие сделки ДЦ (${(banking.other_deals_total || 0).toLocaleString()})`
                ],
                datasets: [
                    {
                        label: 'Кредит Сбербанк',
                        data: [banking.lead_deals_sber || 0, banking.other_deals_sber || 0],
                        backgroundColor: '#21A038'
                    },
                    {
                        label: 'Кредит Другие банки',
                        data: [banking.lead_deals_other_banks || 0, banking.other_deals_other_banks || 0],
                        backgroundColor: '#E74C3C'
                    },
                    {
                        label: 'Наличные',
                        data: [banking.lead_deals_cash || 0, banking.other_deals_cash || 0],
                        backgroundColor: '#CBD5E1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 11, weight: 'bold' } } },
                    y: { stacked: true, grid: { color: '#F1F5F9' } }
                },
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return ` ${ctx.dataset.label}: ${ctx.raw.toLocaleString()} шт.`;
                            }
                        }
                    }
                }
            }
        });
    }
}

function setBankingRankMode(mode) {
    currentBankingRankMode = mode;
    const btnShare = document.getElementById('btnRankShare');
    const btnVolume = document.getElementById('btnRankVolume');

    if (mode === 'share') {
        if (btnShare) btnShare.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-indigo-600 text-white shadow-sm';
        if (btnVolume) btnVolume.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-700 hover:bg-slate-200';
    } else {
        if (btnShare) btnShare.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-700 hover:bg-slate-200';
        if (btnVolume) btnVolume.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-indigo-600 text-white shadow-sm';
    }

    const banking = getBankingData();
    if (banking) renderBankingRankings(banking);
}

function toggleBankingExpand(type) {
    if (type === 'topSber') {
        isTopSberExpanded = !isTopSberExpanded;
    } else {
        isAntiTopExpanded = !isAntiTopExpanded;
    }
    const banking = getBankingData();
    if (banking) renderBankingRankings(banking);
}

function renderBankingRankings(banking) {
    const isShare = currentBankingRankMode === 'share';

    let topSberData;
    let antiTopData;

    if (isShare) {
        topSberData = isTopSberExpanded ? banking.left_group_all : banking.left_group_top10;
        antiTopData = isAntiTopExpanded ? banking.right_group_all : banking.right_group_top10;

        document.getElementById('b_topSberSub').innerText = isTopSberExpanded ?
            `Все ДЦ с долей Сбера ≥ 50% (${(banking.left_group_all || []).length} партнеров)` :
            `ТОП-10 (от 10 сделок) • Доля Сбера в кредитах ≥ 50%`;

        document.getElementById('b_antiTopSub').innerText = isAntiTopExpanded ?
            `Все ДЦ с долей Др.Банков > 50% (${(banking.right_group_all || []).length} партнеров)` :
            `АНТИТОП-10 (от 10 сделок) • Доля Др.Банков в кредитах > 50%`;
    } else {
        topSberData = isTopSberExpanded ? banking.left_group_all : (banking.left_group_top10_by_units || banking.left_group_top10);
        antiTopData = isAntiTopExpanded ? banking.right_group_all : (banking.right_group_top10_by_units || banking.right_group_top10);

        document.getElementById('b_topSberSub').innerText = `Рейтинг по числу кредитов Сбера (шт.)`;
        document.getElementById('b_antiTopSub').innerText = `Рейтинг по числу кредитов сторонних банков (шт.)`;
    }

    // Кнопки разворачивания
    const btnExpandTop = document.getElementById('b_btnExpandTopSber');
    if (btnExpandTop) {
        btnExpandTop.innerText = isTopSberExpanded ?
            '▲ Свернуть до ТОП-10' :
            `▼ Раскрыть всех партнеров (${(banking.left_group_all || []).length} ДЦ)`;
    }
    const btnExpandAnti = document.getElementById('b_btnExpandAntiTop');
    if (btnExpandAnti) {
        btnExpandAnti.innerText = isAntiTopExpanded ?
            '▲ Свернуть до АНТИТОП-10' :
            `▼ Раскрыть всех партнеров (${(banking.right_group_all || []).length} ДЦ)`;
    }

    // Рендеринг таблицы ТОП Сбербанк
    const tbodyTop = document.getElementById('b_topSberTbody');
    if (tbodyTop) {
        tbodyTop.innerHTML = (topSberData || []).map((p, idx) => `
            <tr class="hover:bg-slate-50 transition border-b border-gray-100">
                <td class="text-center py-2 px-2.5"><span class="px-2 py-0.5 rounded text-[11px] font-black bg-emerald-100 text-emerald-800">${idx + 1}</span></td>
                <td class="py-2 px-2.5">
                    <div class="font-bold text-gray-800 text-xs">${p.partner}</div>
                    <div class="text-[10px] text-gray-400 font-medium">${p.city} • ${p.macro}</div>
                </td>
                <td class="text-right py-2 px-2.5 font-extrabold text-gray-800 text-xs">${p.total_deals}</td>
                <td class="text-right py-2 px-2.5"><span class="px-2 py-0.5 rounded text-xs font-black bg-emerald-50 text-emerald-700 border border-emerald-200">${p.sber_deals}</span></td>
                <td class="text-right py-2 px-2.5 text-xs text-gray-500 font-semibold">${p.other_banks_deals}</td>
                <td class="text-right py-2 px-2.5 min-w-[110px]">
                    <div class="font-black text-xs text-emerald-700">${p.sber_pct_credit}%</div>
                    <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden mt-1 flex">
                        <div class="bg-emerald-600 h-full" style="width: ${p.sber_pct_credit}%;"></div>
                        <div class="bg-rose-500 h-full" style="width: ${p.ob_pct_credit}%;"></div>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Рендеринг таблицы АНТИТОП Другие банки
    const tbodyAnti = document.getElementById('b_antiTopTbody');
    if (tbodyAnti) {
        tbodyAnti.innerHTML = (antiTopData || []).map((p, idx) => `
            <tr class="hover:bg-slate-50 transition border-b border-gray-100">
                <td class="text-center py-2 px-2.5"><span class="px-2 py-0.5 rounded text-[11px] font-black bg-rose-100 text-rose-800">${idx + 1}</span></td>
                <td class="py-2 px-2.5">
                    <div class="font-bold text-gray-800 text-xs">${p.partner}</div>
                    <div class="text-[10px] text-gray-400 font-medium">${p.city} • ${p.macro} <span class="text-rose-600 font-semibold">• ${p.competing_banks_str}</span></div>
                </td>
                <td class="text-right py-2 px-2.5 font-extrabold text-gray-800 text-xs">${p.total_deals}</td>
                <td class="text-right py-2 px-2.5"><span class="px-2 py-0.5 rounded text-xs font-black bg-rose-50 text-rose-700 border border-rose-200">${p.other_banks_deals}</span></td>
                <td class="text-right py-2 px-2.5 text-xs text-emerald-600 font-semibold">${p.sber_deals}</td>
                <td class="text-right py-2 px-2.5 min-w-[110px]">
                    <div class="font-black text-xs text-rose-600">${p.ob_pct_credit}%</div>
                    <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden mt-1 flex">
                        <div class="bg-rose-500 h-full" style="width: ${p.ob_pct_credit}%;"></div>
                        <div class="bg-emerald-600 h-full" style="width: ${p.sber_pct_credit}%;"></div>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function renderBankingMacroTable(macroRows) {
    const tbody = document.getElementById('b_macroTbody');
    if (!tbody) return;

    tbody.innerHTML = macroRows.map((m, idx) => {
        const sberShare = m.sber_share || 0;
        const sberColorClass = sberShare >= 70 ? 'text-emerald-700 font-black' : (sberShare >= 50 ? 'text-emerald-600 font-bold' : 'text-amber-600 font-bold');

        return `
            <tr class="hover:bg-slate-50 transition border-b border-gray-100 text-xs">
                <td class="py-2.5 px-3 font-bold text-gray-800 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-indigo-600 inline-block"></span>
                    ${m.macro}
                </td>
                <td class="text-right py-2.5 px-3 font-semibold text-sky-700 bg-sky-50/40">${m.transfers.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-black text-emerald-700">${m.lead_deals.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 text-gray-500">${m.cr}%</td>
                <td class="text-right py-2.5 px-3 font-medium text-gray-600 border-l border-gray-100">${m.other_deals.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-black text-gray-900 border-l border-gray-200 bg-slate-50/50">${m.all_deals.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-extrabold text-emerald-700 bg-emerald-50/30">${m.sber.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-extrabold text-rose-600 bg-rose-50/30">${m.other_banks.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-medium text-gray-500">${m.cash.toLocaleString()}</td>
                <td class="text-right py-2.5 px-3 font-bold text-gray-700 border-l border-gray-100">${m.credit_share}%</td>
                <td class="text-right py-2.5 px-3 ${sberColorClass} bg-slate-50/40">${sberShare}%</td>
            </tr>
        `;
    }).join('');
}

function renderBankingAllPartnersTable(partners) {
    const tbody = document.getElementById('b_partnersTbody');
    if (!tbody) return;

    tbody.innerHTML = partners.map((p, idx) => `
        <tr class="hover:bg-slate-50 transition border-b border-gray-100 text-xs partner-row-item">
            <td class="py-2 px-3 text-center text-gray-400 font-mono text-[11px]">${idx + 1}</td>
            <td class="py-2 px-3">
                <div class="font-bold text-gray-800 partner-search-field">${p.partner}</div>
                <div class="text-[10px] text-gray-400 font-medium">${p.city} • ${p.macro}</div>
            </td>
            <td class="py-2 px-3 text-right font-black text-gray-900">${p.total_deals}</td>
            <td class="py-2 px-3 text-right font-bold text-emerald-700 bg-emerald-50/30">${p.sber_deals}</td>
            <td class="py-2 px-3 text-right font-bold text-rose-600 bg-rose-50/30">${p.other_banks_deals}</td>
            <td class="py-2 px-3 text-right font-medium text-gray-500">${p.cash_deals}</td>
            <td class="py-2 px-3 text-right font-semibold text-sky-700">${p.lead_deals}</td>
            <td class="py-2 px-3 text-right font-medium text-gray-600">${p.other_deals}</td>
            <td class="py-2 px-3 text-right font-black text-emerald-700">${p.sber_pct_credit}%</td>
            <td class="py-2 px-3 text-right font-black text-rose-600">${p.ob_pct_credit}%</td>
            <td class="py-2 px-3 text-[11px] text-gray-500 font-medium">${p.competing_banks_str}</td>
        </tr>
    `).join('');
}

function filterBankingPartners(query) {
    const q = (query || '').toLowerCase().trim();
    const rows = document.querySelectorAll('.partner-row-item');
    let visible = 0;
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (!q || text.includes(q)) {
            row.style.display = '';
            visible++;
        } else {
            row.style.display = 'none';
        }
    });
    const cntEl = document.getElementById('b_partnersVisibleCount');
    if (cntEl) cntEl.innerText = `Показано: ${visible} ДЦ`;
}

// ==========================================
// МОДАЛЬНОЕ ОКНО ДЕТАЛЬНОЙ БАЗЫ СДЕЛОК
// ==========================================

function openBankingDatabaseModal(type) {
    currentActiveDb = type;
    const banking = getBankingData();
    if (!banking) return;

    const modal = document.getElementById('bankingDbModal');
    const title = document.getElementById('b_dbModalTitle');
    const badge = document.getElementById('b_dbModalBadge');

    if (type === 'lead_deals') {
        if (title) title.innerText = 'Сделки по переданным лидам СберАвто';
        if (badge) {
            badge.innerText = `${(banking.lead_deals_total || 0)} сделок (CR ${(banking.lead_cr || 0)}%)`;
            badge.className = 'px-3 py-1 rounded-lg text-xs font-black bg-emerald-100 text-emerald-800';
        }
    } else {
        if (title) title.innerText = 'Другие сделки ДЦ (без лида СберАвто)';
        if (badge) {
            badge.innerText = `${(banking.other_deals_total || 0).toLocaleString()} сделок`;
            badge.className = 'px-3 py-1 rounded-lg text-xs font-black bg-amber-100 text-amber-800';
        }
    }

    setBankingDbFilter('all');
    if (modal) modal.classList.remove('hidden');
}

function closeBankingDatabaseModal() {
    const modal = document.getElementById('bankingDbModal');
    if (modal) modal.classList.add('hidden');
}

function setBankingDbFilter(filter) {
    currentDbFilter = filter;
    ['all', 'sber', 'other_banks', 'cash'].forEach(f => {
        const btn = document.getElementById(`b_chip_${f}`);
        if (btn) {
            if (f === filter) {
                btn.className = 'px-3 py-1 rounded-lg text-xs font-bold transition bg-emerald-600 text-white shadow-sm';
            } else {
                btn.className = 'px-3 py-1 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-700 hover:bg-slate-200';
            }
        }
    });
    renderBankingDbRows();
}

function renderBankingDbRows() {
    const banking = getBankingData();
    if (!banking) return;

    const raw = currentActiveDb === 'lead_deals' ? (banking.lead_deals_db || []) : (banking.other_deals_db || []);
    const searchInput = document.getElementById('b_dbSearchInput');
    const search = searchInput ? searchInput.value.toLowerCase().trim() : '';

    let filtered = raw.filter(d => {
        if (currentDbFilter === 'sber' && d.bank_cat !== 'Сбер') return false;
        if (currentDbFilter === 'other_banks' && d.bank_cat !== 'Другие банки') return false;
        if (currentDbFilter === 'cash' && d.bank_cat !== 'Наличные') return false;

        if (search) {
            const matchStr = `${d.cid} ${d.partner} ${d.comp} ${d.product} ${d.vin} ${d.bank} ${d.city} ${d.macro} ${d.fdc}`.toLowerCase();
            if (!matchStr.includes(search)) return false;
        }
        return true;
    });

    const countEl = document.getElementById('b_dbRecordCount');
    if (countEl) countEl.innerText = `Найдено записей: ${filtered.length.toLocaleString()} из ${raw.length.toLocaleString()}`;

    const tbody = document.getElementById('b_dbTbody');
    if (!tbody) return;

    const displayData = filtered.slice(0, 300);

    tbody.innerHTML = displayData.map((d, i) => {
        let bankBadge = '';
        if (d.bank_cat === 'Сбер') {
            bankBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-black bg-emerald-100 text-emerald-800 border border-emerald-200">${d.bank}</span>`;
        } else if (d.bank_cat === 'Другие банки') {
            bankBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-black bg-rose-100 text-rose-800 border border-rose-200">${d.bank}</span>`;
        } else {
            bankBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">Наличные</span>`;
        }

        return `
            <tr class="hover:bg-slate-50 transition border-b border-gray-100 text-xs">
                <td class="py-2 px-2.5 text-center text-gray-400 font-mono text-[11px]">${i + 1}</td>
                <td class="py-2 px-2.5 font-bold text-gray-900 font-mono">${d.cid}</td>
                <td class="py-2 px-2.5 font-semibold text-gray-800 max-w-[220px] truncate" title="${d.partner}">${d.partner}</td>
                <td class="py-2 px-2.5 text-gray-700">${d.brand} ${d.model}</td>
                <td class="py-2 px-2.5 font-mono text-[11px] text-gray-500">${d.vin}</td>
                <td class="py-2 px-2.5">${bankBadge}</td>
                <td class="py-2 px-2.5 text-center font-bold ${d.bank_cat === 'Сбер' ? 'text-emerald-700' : (d.bank_cat === 'Другие банки' ? 'text-rose-600' : 'text-slate-600')}">${d.bank_cat}</td>
                <td class="py-2 px-2.5 text-gray-600">${d.city}</td>
                <td class="py-2 px-2.5 text-gray-500">${d.macro}</td>
                <td class="py-2 px-2.5 text-center text-gray-500 text-[11px]">${d.date}</td>
                <td class="py-2 px-2.5 text-center font-mono text-[11px] text-indigo-700 font-bold">${d.fdc}</td>
            </tr>
        `;
    }).join('');

    const footerEl = document.getElementById('b_dbFooterInfo');
    if (footerEl) {
        if (filtered.length > 300) {
            footerEl.innerText = `Показаны первые 300 записей из ${filtered.length.toLocaleString()}. Уточните поисковый запрос для точной выборки.`;
        } else {
            footerEl.innerText = `Отображено записей: ${filtered.length.toLocaleString()}`;
        }
    }
}
