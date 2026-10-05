/* ====================================================================
 * B2C Analytics Dashboard — Utility Functions
 * ====================================================================*/

const MODERN_PALETTE = [
    '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
    '#ec4899', '#06b6d4', '#f97316', '#64748b',
    '#6366f1', '#14b8a6', '#d97706', '#a855f7'
];

// Q3 2026 Budget Targets
const Q3_TARGETS = {
    deals: 5000,
    revenue: 170000000,
    trPercent: 1.9,
    avgCheck: 2600000,
    q3Start: new Date(2026, 6, 1),  // July 1
    q3End: new Date(2026, 8, 30)    // Sep 30
};

// 2026 Annual Budget Targets (from PAD PGK Model)
const ANNUAL_TARGETS_2026 = {
    deals: 13643,            // Row 14: Всего продуктов (13 642.58)
    avgCheck: 2161846,       // Row 27: Средний чек (2.1618M)
    trPercent: 1.76,         // Row 38: TR Новые авто (1.757%)
    revenue: 489060505,      // Row 48 - Row 52: Выручка без доп. продуктов (508.06M - 19.00M = 489.06M)
    yearStart: new Date(2026, 0, 1),
    yearEnd: new Date(2026, 11, 31)
};

const MONTH_NAMES_RU = {
    '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
    '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
    '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
};

const fmtNum = (num) => Math.round(num || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
const fmtPct = (num) => (Math.round((num || 0) * 100)) + "%";
const fmtRub = (num) => fmtNum(num) + " ₽";
const fmtMln = (num) => (num / 1000000).toFixed(1) + "М ₽";

function excelToJSDate(serial) {
    if (!serial || serial === 0) return null;
    let utc_days = Math.floor(serial - 25569);
    return new Date(utc_days * 86400 * 1000 + (new Date().getTimezoneOffset() * 60000));
}

function formatDateDMY(dateStr) {
    let d = excelToJSDate(dateStr);
    if (!d) return "";
    return d.getDate().toString().padStart(2, '0') + "." + (d.getMonth() + 1).toString().padStart(2, '0') + "." + d.getFullYear();
}

function renderVin(vin) {
    if (!vin) return "";
    if (vin.length < 17) return `<span class="vin-error" title="VIN length < 17">${vin}</span>`;
    return vin;
}

function formatMonthLabel(monthStr) {
    if (monthStr === 'all') return '📅 Все месяцы';
    const parts = monthStr.split('-');
    if (parts.length !== 2) return monthStr;
    const name = MONTH_NAMES_RU[parts[1]] || parts[1];
    return `📅 ${name} ${parts[0]}`;
}

// ====================================================================
// Toast Notifications (replaces alert())
// ====================================================================
let _toastTimeout = null;
function showToast(message, type = 'success', duration = 3000) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'fixed top-5 right-5 z-[9999] space-y-2 pointer-events-none';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-red-600 text-white',
        info: 'bg-blue-600 text-white',
        warning: 'bg-amber-500 text-white'
    };
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    toast.className = `${colors[type] || colors.info} px-5 py-3 rounded-xl shadow-2xl text-sm font-bold pointer-events-auto flex items-center gap-2 animate-fade-in`;
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ====================================================================
// Clipboard Helpers
// ====================================================================
function copyTableToClipboard(containerId) {
    let container = document.getElementById(containerId);
    if (!container) return;
    let table = container.querySelector('table') || (container.tagName === 'TABLE' ? container : null);
    if (!table) return;

    // Modern clipboard API with fallback
    const html = table.outerHTML;
    const blob = new Blob([html], { type: 'text/html' });

    if (navigator.clipboard && navigator.clipboard.write) {
        navigator.clipboard.write([new ClipboardItem({ 'text/html': blob })]).then(() => {
            showToast('Таблица скопирована!', 'success');
        }).catch(() => {
            // Fallback
            let range = document.createRange();
            range.selectNode(table);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand('copy');
            window.getSelection().removeAllRanges();
            showToast('Таблица скопирована!', 'success');
        });
    } else {
        let range = document.createRange();
        range.selectNode(table);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        window.getSelection().removeAllRanges();
        showToast('Таблица скопирована!', 'success');
    }
}

async function copyCardToClipboard(cardId, btn) {
    const cardEl = document.getElementById(cardId);
    if (!cardEl) return;
    const origContent = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Копирование...';
        btn.disabled = true;
    }

    try {
        if (typeof html2canvas !== 'undefined') {
            const canvas = await html2canvas(cardEl, {
                scale: 2, backgroundColor: null, logging: false, useCORS: true,
                ignoreElements: (element) => element.tagName === 'BUTTON'
            });

            canvas.toBlob(async (blob) => {
                try {
                    const item = new ClipboardItem({ 'image/png': blob });
                    await navigator.clipboard.write([item]);
                    showToast('Карточка скопирована как изображение!', 'success');
                } catch (err) {
                    showToast('Не удалось скопировать в буфер', 'error');
                }
                if (btn) {
                    btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Скопировано!';
                    btn.style.background = '#22c55e';
                    btn.style.color = 'white';
                    setTimeout(() => {
                        btn.innerHTML = origContent;
                        btn.style.background = '';
                        btn.style.color = '';
                        btn.disabled = false;
                        if (typeof lucide !== 'undefined') lucide.createIcons();
                    }, 2000);
                }
            });
        }
    } catch (e) {
        if (btn) { btn.innerHTML = origContent; btn.disabled = false; }
    }
}

/**
 * Returns formatted HTML badge for deal channel / B2C subtype.
 * @param {string} b2c
 * @returns {string}
 */
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

/**
 * Normalizes brand name for presentation and charts.
 * @param {string} b
 * @returns {string}
 */
function normalizeBrandPresentation(b) {
    if (typeof normalizeBrandJS === 'function') return normalizeBrandJS(b);
    if (!b) return '';
    let s = String(b).trim();
    let sUpper = s.toUpperCase();
    if (sUpper === 'TENET' || sUpper === 'ТENET' || sUpper === 'ТЕНЕТ' || sUpper === 'CHERY' || sUpper === 'ЧЕРИ') return 'CHERY & TENET';
    if (sUpper === 'SОLARIS' || sUpper === 'SOLARIS' || sUpper === 'СОЛЯРИС') return 'SOLARIS';
    if (sUpper === 'KNEWSTAR' || sUpper === 'КНЬЮСТАР' || sUpper === 'КНЮСТАР') return 'Knewstar';
    if (sUpper === 'ВЕELGEE' || sUpper === 'BELGEE' || sUpper === 'БЕЛДЖИ') return 'Belgee';
    if (sUpper === 'GEELY' || sUpper === 'ДЖИЛИ') return 'Geely';
    if (sUpper === 'G B K' || sUpper === 'GBK') return 'Geely & Belgee';
    if (sUpper === 'SOUEAS') return 'SOUEAST';
    if (sUpper === 'JAECO0' || sUpper === 'ДЖЕЙКУ') return 'JAECOO';
    return s;
}

/**
 * Formats brand sales into a presentation string identical to the chart/table:
 * {BRAND_1} {N} шт. | {BRAND_2} {N} шт. | ...
 * @param {Array} salesDb - Optional sales array
 * @returns {string}
 */
function formatBrandsForPresentation(salesDb) {
    let list = salesDb || window.currentFilteredSales;
    if (!list || !list.length) {
        if (typeof getFilteredData === 'function') {
            const fd = getFilteredData();
            if (fd && fd.sDb && fd.sDb.length) list = fd.sDb;
        }
    }
    if (!list || !list.length) {
        if (typeof db !== 'undefined' && Array.isArray(db) && db.length) {
            list = db.filter(r => r.SaleQty > 0);
        } else if (window.dataPayload && Array.isArray(window.dataPayload.sys_db)) {
            list = window.dataPayload.sys_db.filter(r => r.SaleQty > 0);
        }
    }
    list = list || [];

    const aux = ["ВНЕСЕНИЕ", "АВАНС", "КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП", "СЕРВИС", "ФИНАНС", "ДОГОВОР", "ОФОРМЛЕН", "КОМИСС", "УСЛУГ", "НЕИЗВЕСТН", "ДРУГИЕ", "NULL", "UNDEFINED"];

    const counts = {};
    list.forEach(r => {
        let b = normalizeBrandPresentation(r.Brand);
        if (!b || b === 'null' || b === 'undefined' || b === 'Другие' || aux.some(k => String(b).toUpperCase().includes(k))) return;
        counts[b] = (counts[b] || 0) + 1;
    });

    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    if (sorted.length === 0) return '';

    const parts = sorted.map(([brand, count]) => `${brand} ${count} шт.`);
    return parts.join(' | ') + ' | ';
}

/**
 * Copies brand presentation string to clipboard with toast notification
 * @param {HTMLElement} btn
 */
async function copyBrandsPresentationText(btn) {
    const text = formatBrandsForPresentation();
    const origContent = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Копирование...';
        btn.disabled = true;
    }

    try {
        let copied = false;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            try {
                await navigator.clipboard.writeText(text);
                copied = true;
            } catch (clipErr) {
                console.warn('navigator.clipboard.writeText failed, using fallback textarea', clipErr);
            }
        }
        if (!copied) {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            ta.style.top = '-9999px';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }
        showToast('Текст для презентации скопирован!', 'success');
        if (btn) {
            btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Скопировано!';
            btn.style.background = '#22c55e';
            btn.style.color = 'white';
            setTimeout(() => {
                btn.innerHTML = origContent;
                btn.style.background = '';
                btn.style.color = '';
                btn.disabled = false;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }, 2000);
        }
    } catch (e) {
        showToast('Не удалось скопировать', 'error');
        if (btn) {
            btn.innerHTML = origContent;
            btn.disabled = false;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    }
}


// Use for text/HTML attributes; event-handler arguments require JSON + escaping.
function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function safeCrmUrl(value) {
    try { const url=new URL(value);return url.protocol==='https:' && url.hostname==='backoffice.x.sberauto.com' && !url.username && !url.password ? url.href : '#'; }
    catch (_) { return '#'; }
}
