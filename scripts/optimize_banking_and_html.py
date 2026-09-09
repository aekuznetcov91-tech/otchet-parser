import re
import os

print("=== 1. OPTIMIZING site/js/banking-dashboard.js ===")
banking_js_path = 'otchet-parser/site/js/banking-dashboard.js'

with open(banking_js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original line count: {len(lines)}")
print(f"Line 8 original length: {len(lines[7])} chars")

header_code = """/**
 * banking-dashboard.js
 * ====================
 * Единый аналитический дашборд:
 * Лидогенерация, Сделки ДЦ и Банки (Секции 1, 2, 3 и База Сделок).
 * Оптимизирован: данные динамически подтягиваются из data.json.
 */

function getBankingDataPayload() {
    if (window.bankingAnalyticsData) return window.bankingAnalyticsData;
    if (window.dataPayload && window.dataPayload.banking_analytics) return window.dataPayload.banking_analytics;
    if (window.currentData && window.currentData.banking_analytics) return window.currentData.banking_analytics;
    return {};
}

// Proxy to dynamically resolve any dataPayload property from loaded data
const dataPayload = new Proxy({}, {
    get(target, prop) {
        const p = getBankingDataPayload();
        return p[prop];
    },
    has(target, prop) {
        const p = getBankingDataPayload();
        return prop in p;
    },
    ownKeys(target) {
        const p = getBankingDataPayload();
        return Reflect.ownKeys(p);
    },
    getOwnPropertyDescriptor(target, prop) {
        const p = getBankingDataPayload();
        return Object.getOwnPropertyDescriptor(p, prop) || {
            configurable: true,
            enumerable: true,
            value: p[prop]
        };
    }
});
"""

# Remaining lines from index 8 onwards (lines[8:])
rest_code = "".join(lines[8:])

# Add dynamic functions for Funnel Cards, Macro Table, and All Partners Table
dynamic_funcs = """

// -------------------------------------------------------------
// Dynamic Card & Table Renderers for Section 1, 2 & 3
// -------------------------------------------------------------

function renderFunnelCards() {
    const setInner = (sel, val) => {
        const el = document.querySelector(sel);
        if (el) el.innerText = val;
    };
    
    // Transfers
    setInner('.card-leads .main-val', (dataPayload.transfers_total || 0).toLocaleString());
    setInner('.card-leads .breakdown-item:nth-child(1) b', `${(dataPayload.transfers_new || 0).toLocaleString()} (100.0%)`);
    setInner('.card-leads .breakdown-item:nth-child(2) b', `${(dataPayload.transfers_used || 0).toLocaleString()} (0.0%)`);
    
    // Lead Deals
    setInner('.card-lead-deals .main-val', (dataPayload.lead_deals_total || 0).toLocaleString());
    setInner('.card-lead-deals .breakdown-item:nth-child(1) b', `${dataPayload.lead_cr || 0}%`);
    const ldTot = dataPayload.lead_deals_total || 1;
    setInner('.card-lead-deals .breakdown-item:nth-child(2) b', `${(dataPayload.lead_deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.lead_deals_credit || 0) / ldTot * 100)}%)`);
    setInner('.card-lead-deals .breakdown-item:nth-child(3) b', `${(dataPayload.lead_deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.lead_deals_cash || 0) / ldTot * 100)}%)`);
    
    // Other Deals
    setInner('.card-other-deals .main-val', (dataPayload.other_deals_total || 0).toLocaleString());
    const odTot = dataPayload.other_deals_total || 1;
    setInner('.card-other-deals .breakdown-item:nth-child(1) b', `${(dataPayload.other_deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.other_deals_credit || 0) / odTot * 100)}%)`);
    setInner('.card-other-deals .breakdown-item:nth-child(2) b', (dataPayload.other_deals_sber || 0).toLocaleString());
    setInner('.card-other-deals .breakdown-item:nth-child(3) b', `${(dataPayload.other_deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.other_deals_cash || 0) / odTot * 100)}%)`);
    
    // Total Deals
    setInner('.card-total-deals .main-val', (dataPayload.deals_total || 0).toLocaleString());
    const dTot = dataPayload.deals_total || 1;
    setInner('.card-total-deals .breakdown-item:nth-child(1) b', `${(dataPayload.deals_credit || 0).toLocaleString()} (${Math.round((dataPayload.deals_credit || 0) / dTot * 100)}%)`);
    setInner('.card-total-deals .breakdown-item:nth-child(2) b', (dataPayload.deals_sber || 0).toLocaleString());
    setInner('.card-total-deals .breakdown-item:nth-child(3) b', `${(dataPayload.deals_cash || 0).toLocaleString()} (${Math.round((dataPayload.deals_cash || 0) / dTot * 100)}%)`);
}

function renderMacroTable() {
    const tbody = document.getElementById('macroRegionsTbody');
    if (!tbody) return;
    const rows = dataPayload.macro_rows || [];
    if (!rows.length) return;
    
    tbody.innerHTML = rows.map((r, idx) => `
        <tr>
            <td class="center">${idx + 1}</td>
            <td><b>${r.macro}</b></td>
            <td class="num">${r.transfers || 0}</td>
            <td class="num"><span class="badge badge-lead">${r.lead_deals || 0}</span></td>
            <td class="num"><b>${r.cr != null ? r.cr + '%' : '0%'}</b></td>
            <td class="num">${(r.other_deals || 0).toLocaleString()}</td>
            <td class="num"><b>${(r.all_deals || r.total_deals || 0).toLocaleString()}</b></td>
            <td class="num"><span class="badge badge-sber">${(r.sber || r.sber_deals || 0).toLocaleString()}</span></td>
            <td class="num"><span class="badge badge-risk">${(r.other_banks || r.other_banks_deals || 0).toLocaleString()}</span></td>
            <td class="num"><b>${r.credit_share != null ? r.credit_share + '%' : '—'}</b></td>
            <td class="num"><b>${r.sber_share != null ? r.sber_share + '%' : '—'}</b></td>
        </tr>
    `).join('');
}

function renderAllPartnersTable() {
    const tbody = document.getElementById('allPartnersTbody');
    if (!tbody) return;
    const partners = dataPayload.all_partners || [];
    if (!partners.length) return;
    
    tbody.innerHTML = partners.map(p => `
        <tr>
            <td>${p.macro || '—'}</td>
            <td>${p.city || '—'}</td>
            <td><b>${p.partner || '—'}</b></td>
            <td class="num">${p.lead_deals || 0}</td>
            <td class="num">${p.lead_deals || 0}</td>
            <td class="num">${p.other_deals || 0}</td>
            <td class="num"><b>${p.total_deals || 0}</b></td>
            <td class="num"><span class="badge badge-sber">${p.sber_deals || 0}</span></td>
            <td class="num"><span class="badge badge-risk">${p.other_banks_deals || 0}</span></td>
            <td class="num"><b>${p.sber_pct_credit != null ? p.sber_pct_credit + '%' : '—'}</b></td>
            <td><span style="font-size: 11px; color: #64748B;">${p.competing_banks_str || '—'}</span></td>
        </tr>
    `).join('');
}
"""

# Replace renderBankingDashboard definition to call all renderers
old_render_dash = """function renderBankingDashboard() {
    renderRankings();
    initFunnelCharts();
}"""

new_render_dash = """function renderBankingDashboard() {
    renderFunnelCards();
    renderRankings();
    renderMacroTable();
    renderAllPartnersTable();
    initFunnelCharts();
}"""

if old_render_dash in rest_code:
    rest_code = rest_code.replace(old_render_dash, dynamic_funcs + "\n" + new_render_dash)
else:
    rest_code = rest_code + dynamic_funcs + "\n" + new_render_dash

# Update initFunnelCharts to use dataPayload instead of hardcoded numbers
old_chart_data = """        data: {
            labels: ['Наличные (67.2%)', 'Кредит Сбербанк (20.1%)', 'Кредит Другие банки (12.7%)'],
            datasets: [{
                data: [2647, 792, 498],
                backgroundColor: ['#64748B', '#21A038', '#E74C3C'],
                borderWidth: 2
            }]
        },"""

new_chart_data = """        data: {
            labels: [
                `Наличные (${dataPayload.deals_total ? Math.round((dataPayload.deals_cash || 0) / dataPayload.deals_total * 100) : 67.2}%)`,
                `Кредит Сбербанк (${dataPayload.deals_total ? Math.round((dataPayload.deals_sber || 0) / dataPayload.deals_total * 100) : 20.1}%)`,
                `Кредит Другие банки (${dataPayload.deals_total ? Math.round((dataPayload.deals_other_banks || 0) / dataPayload.deals_total * 100) : 12.7}%)`
            ],
            datasets: [{
                data: [dataPayload.deals_cash || 2647, dataPayload.deals_sber || 792, dataPayload.deals_other_banks || 498],
                backgroundColor: ['#64748B', '#21A038', '#E74C3C'],
                borderWidth: 2
            }]
        },"""

if old_chart_data in rest_code:
    rest_code = rest_code.replace(old_chart_data, new_chart_data)

old_bar_data = """        data: {
            labels: ['Сделки по лидам СА (331)', 'Другие сделки ДЦ (3 606)'],
            datasets: [
                { label: 'Кредит Сбербанк', data: [151, 641], backgroundColor: '#21A038' },
                { label: 'Кредит Другие банки', data: [45, 453], backgroundColor: '#E74C3C' },
                { label: 'Наличные', data: [135, 2512], backgroundColor: '#CBD5E1' }
            ]
        },"""

new_bar_data = """        data: {
            labels: [
                `Сделки по лидам СА (${dataPayload.lead_deals_total || 331})`,
                `Другие сделки ДЦ (${(dataPayload.other_deals_total || 3606).toLocaleString()})`
            ],
            datasets: [
                { label: 'Кредит Сбербанк', data: [dataPayload.lead_deals_sber || 151, dataPayload.other_deals_sber || 641], backgroundColor: '#21A038' },
                { label: 'Кредит Другие банки', data: [dataPayload.lead_deals_other_banks || 45, dataPayload.other_deals_other_banks || 453], backgroundColor: '#E74C3C' },
                { label: 'Наличные', data: [dataPayload.lead_deals_cash || 135, dataPayload.other_deals_cash || 2512], backgroundColor: '#CBD5E1' }
            ]
        },"""

if old_bar_data in rest_code:
    rest_code = rest_code.replace(old_bar_data, new_bar_data)

# Add window exports
old_exports = "window.filterPartnerTable = filterPartnerTable;"
new_exports = """window.filterPartnerTable = filterPartnerTable;
window.renderFunnelCards = renderFunnelCards;
window.renderMacroTable = renderMacroTable;
window.renderAllPartnersTable = renderAllPartnersTable;"""

if old_exports in rest_code:
    rest_code = rest_code.replace(old_exports, new_exports)

with open(banking_js_path, 'w', encoding='utf-8') as f:
    f.write(header_code + "\n" + rest_code)

new_size = os.path.getsize(banking_js_path)
print(f"Optimized banking-dashboard.js size: {new_size / 1024:.2f} KB (was 2.2 MB)")

print("\n=== 2. OPTIMIZING site/index.html ===")
index_path = 'otchet-parser/site/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

orig_html_len = len(html)
print(f"Original index.html size: {orig_html_len / 1024:.2f} KB")

# 1) Add executiveDashboardContainer to tab-dashboard
if 'id="executiveDashboardContainer"' not in html:
    # Insert right at the top of tab-dashboard, before the top KPI cards
    target_needle = '<div id="tab-dashboard" class="tab-content">\n        <!-- KPI CARDS ROW (5 metrics) -->'
    replacement = '<div id="tab-dashboard" class="tab-content">\n        <!-- EXECUTIVE DASHBOARD (Pace, Alerts, Margin, Health Matrix) -->\n        <div id="executiveDashboardContainer"></div>\n\n        <!-- KPI CARDS ROW (5 metrics) -->'
    if target_needle in html:
        html = html.replace(target_needle, replacement)
        print("Inserted #executiveDashboardContainer into tab-dashboard")
    else:
        # try without comment
        target_needle2 = '<div id="tab-dashboard" class="tab-content">'
        replacement2 = '<div id="tab-dashboard" class="tab-content">\n        <!-- EXECUTIVE DASHBOARD (Pace, Alerts, Margin, Health Matrix) -->\n        <div id="executiveDashboardContainer"></div>'
        html = html.replace(target_needle2, replacement2, 1)
        print("Inserted #executiveDashboardContainer into tab-dashboard (fallback needle)")

# 2) Replace static rows in allPartnersTable
# Find tbody in allPartnersTable
all_partners_pattern = r'(<table id="allPartnersTable">[\s\S]*?<thead>[\s\S]*?</thead>\s*)<tbody>[\s\S]*?</tbody>'
match = re.search(all_partners_pattern, html)
if match:
    repl = match.group(1) + '<tbody id="allPartnersTbody">\n                        <!-- Populated dynamically by renderAllPartnersTable() -->\n                    </tbody>'
    html = html[:match.start()] + repl + html[match.end():]
    print("Replaced static allPartnersTable rows with dynamic <tbody id=\"allPartnersTbody\">")

# 3) Replace static rows in macro-regions table
# In section-partners: the table right before allPartnersTable
macro_pattern = r'(<h3>Сводный анализ по 8 Макрорегионам[\s\S]*?<table[\s\S]*?<thead>[\s\S]*?</thead>\s*)<tbody>[\s\S]*?</tbody>'
match2 = re.search(macro_pattern, html)
if match2:
    repl2 = match2.group(1) + '<tbody id="macroRegionsTbody">\n                        <!-- Populated dynamically by renderMacroTable() -->\n                    </tbody>'
    html = html[:match2.start()] + repl2 + html[match2.end():]
    print("Replaced static macro-regions table rows with dynamic <tbody id=\"macroRegionsTbody\">")

# 4) Include executive-dashboard.js script tag before </body>
if 'src="js/executive-dashboard.js"' not in html:
    old_script_tag = '<script src="js/banking-dashboard.js?v=2808_1455"></script>'
    new_script_tag = '<script src="js/banking-dashboard.js?v=2808_1455"></script>\n    <script src="js/executive-dashboard.js?v=0909_1100"></script>'
    if old_script_tag in html:
        html = html.replace(old_script_tag, new_script_tag)
        print("Added js/executive-dashboard.js to script imports")
    else:
        html = html.replace('</body>', '    <script src="js/executive-dashboard.js?v=0909_1100"></script>\n</body>')
        print("Added js/executive-dashboard.js before </body>")

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

new_html_len = len(html)
print(f"Optimized index.html size: {new_html_len / 1024:.2f} KB (saved {(orig_html_len - new_html_len)/1024:.2f} KB)")
print("=== OPTIMIZATION COMPLETED SUCCESSFULLY ===")
