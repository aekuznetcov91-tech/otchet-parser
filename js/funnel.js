/* ====================================================================
 * B2C Analytics Dashboard — Brand Funnel Revamped (Bottleneck & Drop-off Focus)
 * Strictly Pure Retail (Excluding Wholesale: MP1, MP2, MP3)
 * ====================================================================*/

let currentFunnelMonth = null; // Auto-detect, no hardcode
let currentFunnelBrand = 'ALL';
let funnelRawData = {};

// Auto-generate month buttons from data.json
function initFunnelMonths() {
    const bf = window.brandFunnelFullData;
    if (!bf || !bf.by_month) return;

    const months = Object.keys(bf.by_month).filter(m => m !== 'all').sort().reverse();
    if (months.length === 0) return;

    // Set default to latest month
    if (!currentFunnelMonth) {
        const now = new Date();
        const preferred = new Date(now.getFullYear(), now.getMonth() - (now.getDate() <= 3 ? 1 : 0), 1);
        const key = `${preferred.getFullYear()}-${String(preferred.getMonth() + 1).padStart(2, '0')}`;
        currentFunnelMonth = months.includes(key) ? key : months[0];
    }

    const container = document.getElementById('funnelMonthButtons');
    if (!container) return;

    let html = '';
    months.forEach(m => {
        const label = formatMonthLabel(m);
        const isActive = m === currentFunnelMonth;
        html += `<button onclick="setFunnelMonth('${m}')" id="f-month-${m}" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isActive ? 'font-bold bg-[#107C41] !text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">${label}</button>`;
    });
    // "All" button
    const isAllActive = currentFunnelMonth === 'all';
    html += `<button onclick="setFunnelMonth('all')" id="f-month-all" class="f-month-btn px-3.5 py-1.5 rounded-xl text-xs transition ${isAllActive ? 'font-bold bg-[#107C41] !text-white shadow-sm' : 'font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-200'}">📅 Все месяцы</button>`;

    container.innerHTML = html;

    // Update badge
    const badge = document.getElementById('funnelPeriodBadge');
    if (badge) badge.innerText = formatMonthLabel(currentFunnelMonth).replace('📅 ', '');

    // Also auto-generate brand pills from data
    initFunnelBrandPills();
}

function initFunnelBrandPills() {
    const bf = window.brandFunnelFullData;
    if (!bf || !bf.by_month) return;

    const monthData = getActiveMonthFunnelData();
    const brands = Object.keys(monthData).filter(b => b !== 'OVERALL_LATEST_DATE' && typeof monthData[b] === 'object').sort();

    const container = document.getElementById('funnelBrandPills');
    if (!container) return;

    let html = `<button onclick="selectFunnelBrand('ALL')" id="f-tab-ALL" class="f-tab-btn shrink-0 px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#107C41] text-white shadow-md">📊 Сводная воронка (Все бренды)</button>`;

    brands.forEach(b => {
        html += `<button onclick="selectFunnelBrand('${b}')" id="f-tab-${b}" class="f-tab-btn shrink-0 px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 shadow-sm">${b}</button>`;
    });

    container.innerHTML = html;
}

function setFunnelMonth(month) {
    currentFunnelMonth = month;
    const badge = document.getElementById('funnelPeriodBadge');
    if (badge) badge.innerText = formatMonthLabel(month).replace('📅 ', '');

    document.querySelectorAll('.f-month-btn').forEach(b => {
        b.className = 'f-month-btn px-3.5 py-1.5 rounded-xl font-semibold text-xs transition text-slate-700 hover:text-slate-900 hover:bg-slate-200';
    });
    const activeMBtn = document.getElementById('f-month-' + month);
    if (activeMBtn) {
        activeMBtn.className = 'f-month-btn px-3.5 py-1.5 rounded-xl font-bold text-xs transition bg-[#107C41] text-white shadow-sm';
    }
    initFunnelBrandPills();
    selectFunnelBrand(currentFunnelBrand);
}

function getActiveMonthFunnelData() {
    if (window.brandFunnelFullData && window.brandFunnelFullData.by_month && window.brandFunnelFullData.by_month[currentFunnelMonth]) {
        return window.brandFunnelFullData.by_month[currentFunnelMonth].brands;
    }
    return window.brandFunnelFullData || {};
}

function selectFunnelBrand(brand) {
    currentFunnelBrand = brand;
    document.querySelectorAll('.f-tab-btn').forEach(b => {
        b.className = 'f-tab-btn shrink-0 px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 shadow-sm';
    });
    const activeBtn = document.getElementById('f-tab-' + brand);
    if (activeBtn) {
        activeBtn.className = 'f-tab-btn shrink-0 px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap bg-[#107C41] text-white shadow-md border-transparent';
    }

    const monthData = getActiveMonthFunnelData();
    if (brand === 'ALL') {
        renderFunnelComparisonView(monthData);
    } else {
        renderFunnelSingleBrandView(brand, monthData[brand] || {});
    }
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function getCurrentFunnelPeriodLabel() {
    return formatMonthLabel(currentFunnelMonth).replace('📅 ', '');
}

/**
 * Extract clean retail channels (excluding MP1, MP2, MP3)
 */
function extractRetailMetrics(d) {
    const dealsByB2C = d.deals_by_b2c || {};
    const revByB2C = d.rev_by_b2c || {};

    const dealsDealer = dealsByB2C['Передача лида'] || 0;
    const revDealer = revByB2C['Передача лида'] || 0.0;

    // FDC includes pure FDC + optional FDC+GP if present
    const dealsFdc = (dealsByB2C['ФДЦ'] || 0) + (dealsByB2C['ФДЦ+ГП'] || 0);
    const revFdc = (revByB2C['ФДЦ'] || 0.0) + (revByB2C['ФДЦ+ГП'] || 0.0);

    const dealsOnline = dealsByB2C['Online'] || 0;
    const revOnline = revByB2C['Online'] || 0.0;

    const dealsPureRetail = dealsDealer + dealsFdc + dealsOnline;
    const revPureRetail = revDealer + revFdc + revOnline;

    // Wholesale (excluded)
    const mp1Count = dealsByB2C['МП1'] || 0;
    const mp1Rev = revByB2C['МП1'] || 0.0;
    const mp3Count = dealsByB2C['МП3'] || 0;
    const mp3Rev = revByB2C['МП3'] || 0.0;
    const mp2Count = d.mp2_count || dealsByB2C['МП2'] || 0;
    const mp2Rev = d.mp2_rev || revByB2C['МП2'] || 0.0;

    const totalMpCount = mp1Count + mp2Count + mp3Count;
    const totalMpRev = mp1Rev + mp2Rev + mp3Rev;

    return {
        dealsDealer, revDealer,
        dealsFdc, revFdc,
        dealsOnline, revOnline,
        dealsPureRetail, revPureRetail,
        mp1Count, mp1Rev,
        mp2Count, mp2Rev,
        mp3Count, mp3Rev,
        totalMpCount, totalMpRev
    };
}

/**
 * 📊 RENDER COMPARISON VIEW (ALL BRANDS SUMMARIZED)
 * Shows high-level KPIs, Step Pipeline Funnel with drop-offs, Top Bottlenecks, and Brand Efficiency Matrix
 */
// Null means unavailable; a measured zero remains zero.
function funnelNumber(value) {
    return value === null || value === undefined ? 'Нет данных' : Number(value).toLocaleString('ru-RU');
}
function funnelEscape(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function funnelTable(headers, rows) {
    return `<div class="overflow-x-auto"><table class="w-full text-sm text-left"><thead><tr>${headers.map(h => `<th class="p-3 border-b !text-white">${funnelEscape(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(v => `<td class="p-3 border-b border-slate-100">${funnelEscape(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function renderEvidenceFunnel(brand, brandsData) {
    const period = window.brandFunnelFullData?.by_month?.[currentFunnelMonth] || {};
    const source = window.brandFunnelFullData?.calculator_source;
    const rows = Object.entries(brandsData);
    const logs = brand === 'ALL' ? period.calculator : brandsData[brand]?.calculator;
    const crm = brand === 'ALL' ? period.crm_totals : brandsData[brand];
    const totals = rows.reduce((acc, [, d]) => {
        const r = extractRetailMetrics(d);
        for (const key of Object.keys(r)) acc[key] = (acc[key] || 0) + r[key];
        return acc;
    }, {});
    const cards = [
        ['События расчёта', logs?.calc?.events], ['Клиенты с расчётом', logs?.calc?.clients],
        ['Отправки офферов', logs?.offer?.events], ['Заполнения анкет ФДЦ', logs?.fdc_form?.events],
        ['Сделки розницы', totals.dealsPureRetail], ['Выручка розницы, ₽', Math.round(totals.revPureRetail || 0)]
    ];
    document.getElementById('funnelKpiCards').innerHTML = cards.map(([label, value]) => `<div class="card !p-4"><div class="text-xs text-slate-500">${label}</div><div class="text-xl font-black mt-2">${funnelNumber(value)}</div></div>`).join('');
    const sourceText = source
        ? `Google Таблица калькулятора. События: ${source.first_event.replace('T', ' ')} — ${source.last_event.replace('T', ' ')} (время источника). Снимок получен: ${new Date(source.fetched_at).toLocaleString('ru-RU', {timeZone: 'Europe/Moscow'})} МСК.`
        : 'Google Таблица калькулятора: снимок не загружен.';
    const logRows = [['calc', 'Расчёты и повторная работа'], ['offer', 'Отправки офферов / подборок / сравнений'], ['fdc_form', 'Заполнения анкет ФДЦ']].map(([key, label]) => [label, funnelNumber(logs?.[key]?.events), funnelNumber(logs?.[key]?.clients), funnelNumber(logs?.[key]?.without_id)]);
    const saleRows = rows.filter(([, d]) => d.deals_total_all > 0).map(([b, d]) => {
        const r = extractRetailMetrics(d);
        return [b, funnelNumber(r.dealsDealer), funnelNumber(r.dealsFdc), funnelNumber(r.dealsOnline), funnelNumber(r.dealsPureRetail), funnelNumber(Math.round(r.revPureRetail)), funnelNumber(r.totalMpCount)];
    });
    const vitrinaRows = rows.filter(([, d]) => d.vitrina).map(([b, d]) => [b, ...['page_view', 'car_card_show', 'car_card_click', 'offer_show', 'offer_click', 'offer_success'].map(k => funnelNumber(d.vitrina[k]))]);
    const calculatorBrands = brand === 'ALL' ? `<section class="card !p-5"><h3 class="font-bold mb-2">Калькулятор по брендам</h3>${funnelTable(['Бренд', 'Расчёты: события', 'Расчёты: клиенты', 'Офферы: события', 'Анкеты: события'], rows.filter(([,d]) => !d.calculator || Object.values(d.calculator).some(v => v.events > 0)).map(([b,d]) => [b, funnelNumber(d.calculator?.calc?.events), funnelNumber(d.calculator?.calc?.clients), funnelNumber(d.calculator?.offer?.events), funnelNumber(d.calculator?.fdc_form?.events)]))}<p class="text-xs text-slate-500 mt-3">Итог клиентов посчитан по уникальным ID, а не суммой брендов. Один клиент может сравнивать несколько марок. События без распознанного автомобиля отнесены в «НЕ ОПРЕДЕЛЁН».</p></section>` : '';
    document.getElementById('funnelDynamicView').innerHTML = `
        <div class="p-4 rounded-xl bg-blue-50 text-blue-900 text-sm space-y-2">
            <p>${funnelEscape(sourceText)}</p>
            <p>Показаны наблюдаемые события выбранного периода. Оценки по коэффициентам удалены. «Нет данных» означает отсутствие подтверждённого источника или события. Ноль в журнале означает отсутствие зарегистрированных событий в покрытом периоде, а не гарантию отсутствия действий.</p>
            <p>Клиенты — уникальные корректные ID; события без ID показаны отдельно. Это не сквозная конверсия: CRM, витрина, калькулятор и сделки пока не объединены в когорты. Заполненная анкета не равна отправленной или одобренной банком заявке.</p>
        </div>
        <section class="card !p-5"><h3 class="font-bold mb-2">Калькулятор — ${funnelEscape(brand === 'ALL' ? 'все бренды' : brand)}</h3>${funnelTable(['Действие', 'События', 'Уникальные клиенты', 'События без ID'], logRows)}<p class="text-xs text-slate-500 mt-3">Логируются действия менеджеров после паузы 15 секунд; расчёты администратора не записываются. Точные дубли строк исключены. Число событий не равно числу клиентов.</p></section>
        ${calculatorBrands}
        <section class="card !p-5"><h3 class="font-bold mb-2">CRM — подтверждённые клиенты</h3>${funnelTable(['Новый лид', 'Квалификация: лид → менеджер', 'Переданы дилеру', 'Заявки отправлены в банк', 'Одобрения банка'], [[funnelNumber(crm?.leads), funnelNumber(crm?.qual), funnelNumber(crm?.dealer), 'Нет данных', funnelNumber(crm?.fdc_appr)]])}<p class="text-xs text-slate-500 mt-3">Новый лид и квалификация — события CRM. Передачи — уникальные ClientId из sys_db_partners (Тип «Лид»). Одобрения — только явные события одобрения банка. Даты и охват источников могут различаться.</p></section>
        <section class="card !p-5"><h3 class="font-bold mb-2">Сделки и выручка розницы</h3>${funnelTable(['Бренд', 'Передача лида', 'ФДЦ + ФДЦ+ГП', 'Online', 'Розница', 'Выручка, ₽', 'МП1/2/3 (исключены)'], saleRows)}<p class="text-xs text-slate-500 mt-3">Источник — реестр сделок. Каналы без значения не включены в розницу. Опт МП1/МП2/МП3 (Искл.).</p></section>
        <section class="card !p-5"><h3 class="font-bold mb-2">Витрина PostHog — доступные наблюдения</h3>${vitrinaRows.length ? funnelTable(['Бренд', 'Просмотры', 'Показы карточек', 'Клики карточек', 'Показы офферов', 'Клики отправки', 'Экраны успеха'], vitrinaRows) : '<p class="text-sm text-slate-500">Нет данных за выбранный период.</p>'}<p class="text-xs text-slate-500 mt-3">Источник — сохранённые выгрузки PostHog. В режиме «Все месяцы» суммируются только имеющиеся наблюдения; охват может быть неполным. Экраны успеха не подменяют CRM-лиды.</p></section>`;
}
function renderFunnelComparisonView(brandsData) { renderEvidenceFunnel('ALL', brandsData); }
function renderFunnelSingleBrandView(brand, data) { renderEvidenceFunnel(brand, {[brand]: data}); }
