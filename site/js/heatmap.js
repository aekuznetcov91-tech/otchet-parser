/* ====================================================================
 * B2C Analytics Dashboard — Regional Heatmap (SVG Russia Map)
 * ====================================================================*/

// City → Region mapping for partner names
const CITY_TO_REGION = {
    'москв': 'Москва', 'мск': 'Москва',
    'санкт-петербург': 'Санкт-Петербург', 'спб': 'Санкт-Петербург', 'питер': 'Санкт-Петербург',
    'новгород': 'Нижегородская обл.', 'нижегородец': 'Нижегородская обл.',
    'краснодар': 'Краснодарский край', 'кубань': 'Краснодарский край', 'сочи': 'Краснодарский край',
    'ростов': 'Ростовская обл.', 'таганрог': 'Ростовская обл.',
    'самар': 'Самарская обл.', 'тольятти': 'Самарская обл.',
    'екатеринбург': 'Свердловская обл.', 'екб': 'Свердловская обл.',
    'казан': 'Татарстан', 'челны': 'Татарстан', 'набережн': 'Татарстан',
    'новосибирск': 'Новосибирская обл.', 'нск': 'Новосибирская обл.',
    'красноярск': 'Красноярский край',
    'пермь': 'Пермский край', 'пермск': 'Пермский край',
    'воронеж': 'Воронежская обл.',
    'волгоград': 'Волгоградская обл.',
    'уфа': 'Башкортостан', 'башавто': 'Башкортостан', 'башкир': 'Башкортостан',
    'челябинск': 'Челябинская обл.',
    'омск': 'Омская обл.',
    'тюмень': 'Тюменская обл.',
    'владимир': 'Владимирская обл.',
    'тверь': 'Тверская обл.',
    'рязан': 'Рязанская обл.',
    'тула': 'Тульская обл.',
    'калуг': 'Калужская обл.',
    'курск': 'Курская обл.',
    'брянск': 'Брянская обл.',
    'смоленск': 'Смоленская обл.',
    'ярославл': 'Ярославская обл.',
    'иваново': 'Ивановская обл.',
    'кострома': 'Костромская обл.',
    'архангельск': 'Архангельская обл.',
    'мурманск': 'Мурманская обл.',
    'вологда': 'Вологодская обл.',
    'калининград': 'Калининградская обл.',
    'пятигорск': 'Ставропольский край', 'ставропол': 'Ставропольский край',
    'саратов': 'Саратовская обл.',
    'пенза': 'Пензенская обл.',
    'ульяновск': 'Ульяновская обл.',
    'оренбург': 'Оренбургская обл.',
    'барнаул': 'Алтайский край', 'алтай': 'Алтайский край',
    'иркутск': 'Иркутская обл.',
    'хабаровск': 'Хабаровский край',
    'владивосток': 'Приморский край', 'приморск': 'Приморский край',
    'кемерово': 'Кемеровская обл.', 'новокузнецк': 'Кемеровская обл.',
    'рыбинск': 'Ярославская обл.',
    'липецк': 'Липецкая обл.',
    'белгород': 'Белгородская обл.',
    'орёл': 'Орловская обл.', 'орел': 'Орловская обл.',
    'тамбов': 'Тамбовская обл.',
    'чебоксар': 'Чувашия',
    'йошкар': 'Марий Эл',
    'сургут': 'ХМАО',
    'грозн': 'Чечня', 'махачкала': 'Дагестан',
    'симферопол': 'Крым', 'крым': 'Крым',
};

function detectRegion(partnerName) {
    if (!partnerName) return 'Не определен';
    const lower = partnerName.toLowerCase();
    for (const [key, region] of Object.entries(CITY_TO_REGION)) {
        if (lower.includes(key)) return region;
    }
    return 'Не определен';
}

function buildRegionStats(salesDb) {
    const stats = {};
    // Use sys_db_partners for geographic attribution
    if (typeof dbPartners !== 'undefined' && dbPartners.length > 0) {
        dbPartners.forEach(r => {
            if (r.Type !== 'Сделка') return;
            const region = detectRegion(r.Partner);
            if (!stats[region]) stats[region] = { deals: 0, revenue: 0, partners: new Set() };
            stats[region].deals += (r.Qty || 1);
            stats[region].partners.add(r.Partner);
        });
    }
    // Fallback: use salesDb with SeniorManager grouping
    if (Object.keys(stats).length <= 1) {
        salesDb.forEach(r => {
            const region = 'Не определен';
            if (!stats[region]) stats[region] = { deals: 0, revenue: 0, partners: new Set() };
            stats[region].deals++;
            stats[region].revenue += (r.Revenue || 0);
        });
    }
    // Convert sets to counts
    for (const k in stats) {
        stats[k].partnerCount = stats[k].partners ? stats[k].partners.size : 0;
        delete stats[k].partners;
    }
    return stats;
}

function getHeatColor(value, max) {
    if (max === 0) return '#f1f5f9';
    const ratio = Math.min(value / max, 1);
    // Scale from light green to deep Sber green
    const r = Math.round(240 - ratio * 207);
    const g = Math.round(253 - ratio * 93);
    const b = Math.round(244 - ratio * 179);
    return `rgb(${r}, ${g}, ${b})`;
}

function updateHeatmap(salesDb) {
    const container = document.getElementById('heatmapContainer');
    if (!container) return;

    const stats = buildRegionStats(salesDb);
    // Remove "Не определен" for display
    const displayStats = {};
    let undetermined = 0;
    for (const [region, data] of Object.entries(stats)) {
        if (region === 'Не определен') {
            undetermined = data.deals;
            continue;
        }
        displayStats[region] = data;
    }

    const sorted = Object.entries(displayStats).sort((a, b) => b[1].deals - a[1].deals);
    const maxDeals = sorted.length > 0 ? sorted[0][1].deals : 1;
    const totalDeals = sorted.reduce((s, [, d]) => s + d.deals, 0);

    // Render as styled horizontal bar chart (works without external SVG map)
    let barsHtml = '';
    sorted.slice(0, 20).forEach(([region, data], idx) => {
        const pct = totalDeals > 0 ? (data.deals / totalDeals * 100).toFixed(1) : 0;
        const barWidth = maxDeals > 0 ? (data.deals / maxDeals * 100) : 0;
        const medal = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : ''));
        barsHtml += `
            <div class="flex items-center gap-3 py-1.5 group hover:bg-emerald-50/50 rounded-lg px-2 transition">
                <span class="text-xs font-semibold text-slate-600 w-5 text-right shrink-0">${idx + 1}</span>
                <span class="text-xs font-bold text-slate-800 w-48 truncate shrink-0" title="${region}">${medal} ${region}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden relative">
                    <div class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2" style="width: ${barWidth}%; background: linear-gradient(90deg, #21A038, #107C41);">
                        ${barWidth > 15 ? `<span class="text-[10px] font-black text-white">${fmtNum(data.deals)}</span>` : ''}
                    </div>
                    ${barWidth <= 15 ? `<span class="absolute left-2 top-0.5 text-[10px] font-bold text-slate-600">${fmtNum(data.deals)}</span>` : ''}
                </div>
                <span class="text-xs font-bold text-emerald-700 w-14 text-right shrink-0">${pct}%</span>
                <span class="text-[10px] text-slate-400 w-16 text-right shrink-0">${data.partnerCount} ДЦ</span>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="card !p-5 space-y-4">
            <div class="flex items-center justify-between border-b pb-3">
                <h2 class="text-base font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                    <i data-lucide="map-pin" class="w-5 h-5 text-emerald-600"></i>
                    Распределение сделок по регионам РФ
                </h2>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-200">${sorted.length} регионов</span>
                    <span class="text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200">${fmtNum(totalDeals)} сделок</span>
                    ${undetermined > 0 ? `<span class="text-[10px] px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">${fmtNum(undetermined)} не определен</span>` : ''}
                </div>
            </div>
            <div class="space-y-0.5 max-h-[500px] overflow-y-auto">${barsHtml}</div>
        </div>
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons();
}
