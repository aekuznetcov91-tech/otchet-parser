/* ====================================================================
 * B2C Analytics Dashboard — KAM Management & Executive Reporting Module
 * Tracks total incoming leads, qualification, transfers, deals (Transfer/MP/FDC+Online),
 * Partner -> OEM City -> Brand hierarchy, CR, and interactive plan management.
 * ====================================================================*/

let currentKamFilter = 'all'; // 'all' or KAM full name
let currentKamSearchQuery = '';
let currentKamPlanFilter = 'all'; // 'all', 'completed', 'in_progress', 'no_plan'

// Default fallback plans if localStorage is empty
const DEFAULT_KAM_PLANS = {
    kam_plans: {
        "all": 1500,
        "Алексей Чихарев": 450,
        "Андрей Кузнецов": 450,
        "Светлана Дариенко": 250,
        "Валерия Солдатова": 150,
        "Евгения Добролюбова": 50,
        "Не назначен": 150
    },
    partner_plans: {
        "1001": 45,
        "1098": 80,
        "1124": 30,
        "1233": 25,
        "1002": 40,
        "1003": 50,
        "1004": 35,
        "1005": 60,
        "1006": 20,
        "1007": 30,
        "1008": 50,
        "1009": 40,
        "1010": 30
    }
};

const STORAGE_KEY_KAM_PLANS = 'sberauto_kam_plans';

/**
 * Normalizes KAM name to standard display format.
 */
function normalizeKamName(name) {
    if (!name || name === 'Не назначен' || name === '—' || name === 'null' || name === 'undefined') return 'Не назначен';
    let n = String(name).trim().toLowerCase();
    if (n.includes('чихарев')) return 'Алексей Чихарев';
    if (n.includes('кузнецов')) return 'Андрей Кузнецов';
    if (n.includes('дариенко')) return 'Светлана Дариенко';
    if (n.includes('солдатова')) return 'Валерия Солдатова';
    if (n.includes('добролюбова')) return 'Евгения Добролюбова';
    return name.trim();
}

/**
 * Normalizes brand name to match OEM standards.
 */
function normalizeBrandName(b) {
    if (!b) return 'Другие';
    let ub = String(b).toUpperCase().trim();
    if (ub.includes('JETOUR')) return 'JETOUR';
    if (ub.includes('LADA') || ub.includes('ЛАДА')) return 'LADA';
    if (ub.includes('HAVAL') || ub.includes('ХАВЕЙЛ')) return 'HAVAL';
    if (ub.includes('CHANGAN') || ub.includes('ЧАНГАН')) return 'CHANGAN';
    if (ub.includes('GEELY') || ub.includes('BELGEE') || ub.includes('G B K') || ub.includes('ДЖИЛИ')) return 'Geely & Belgee';
    if (ub.includes('CHERY') || ub.includes('TENET') || ub.includes('ЧЕРИ')) return 'CHERY & TENET';
    if (ub.includes('SOLARIS') || ub.includes('СОЛЯРИС')) return 'SOLARIS';
    if (ub.includes('SOUEAST')) return 'SOUEAST';
    if (ub.includes('GAC')) return 'GAC';
    if (ub.includes('МОСКВИЧ')) return 'МОСКВИЧ';
    if (ub.includes('OMODA') || ub.includes('JAECOO')) return 'OMODA & JAECOO';
    if (ub.includes('HONGQI')) return 'HONGQI';
    if (ub.includes('XCITE')) return 'XCITE';
    return b.trim();
}

/**
 * Retrieves KAM plans from localStorage or defaults.
 */
function getKamPlansStore() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY_KAM_PLANS);
        if (raw) {
            const parsed = JSON.parse(raw);
            return {
                kam_plans: Object.assign({}, DEFAULT_KAM_PLANS.kam_plans, parsed.kam_plans || {}),
                partner_plans: Object.assign({}, DEFAULT_KAM_PLANS.partner_plans, parsed.partner_plans || {})
            };
        }
    } catch (e) {
        console.warn('Ошибка чтения sberauto_kam_plans из localStorage:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_KAM_PLANS));
}

/**
 * Saves KAM plans store to localStorage.
 */
function saveKamPlansStore(store) {
    try {
        localStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store));
    } catch (e) {
        console.warn('Ошибка сохранения sberauto_kam_plans в localStorage:', e);
    }
}

/**
 * Updates overall plan for a KAM manager and auto-refreshes KPI/bars.
 */
function onKamOverallPlanChange(kamName, val) {
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.kam_plans[kamName] = num;
    saveKamPlansStore(store);
    
    // Re-render UI KPI and progress
    renderKamTab(currentFilterConfig);
    if (typeof showToast === 'function') {
        showToast(`План для «${kamName === 'all' ? 'Все КАМы' : kamName}» сохранен: ${fmtNum(num)} сделок`, 'success', 2000);
    }
}

/**
 * Updates individual partner plan and auto-refreshes partner row progress.
 */
function onPartnerPlanChange(partnerKey, val) {
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.partner_plans[partnerKey] = num;
    saveKamPlansStore(store);
    
    // Re-render table and header stats without resetting scroll
    renderKamTab(currentFilterConfig, true);
    if (typeof showToast === 'function') {
        showToast(`План партнера обновлен: ${fmtNum(num)} сделок`, 'success', 1500);
    }
}

/**
 * Filter change handler for KAM selection pill.
 */
function setKamManagerFilter(kamName) {
    currentKamFilter = kamName;
    
    // Update active state on selector pills
    document.querySelectorAll('.kam-select-pill').forEach(pill => {
        if (pill.dataset.kam === kamName) {
            pill.className = 'kam-select-pill px-3.5 py-1.5 rounded-xl text-xs font-bold transition shadow-sm bg-blue-600 text-white cursor-pointer border border-blue-600';
        } else {
            pill.className = 'kam-select-pill px-3.5 py-1.5 rounded-xl text-xs font-bold transition bg-white text-gray-700 hover:bg-gray-100 cursor-pointer border border-gray-200';
        }
    });
    
    renderKamTab(currentFilterConfig);
}

/**
 * Plan completion filter chip handler.
 */
function setKamPlanStatusFilter(status) {
    currentKamPlanFilter = status;
    document.querySelectorAll('.kam-plan-chip').forEach(chip => {
        if (chip.dataset.status === status) {
            chip.className = 'kam-plan-chip px-3 py-1 rounded-lg text-xs font-bold transition bg-slate-800 text-white cursor-pointer shadow-sm';
        } else {
            chip.className = 'kam-plan-chip px-3 py-1 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer';
        }
    });
    renderKamTableOnly();
}

/**
 * Live search input in KAM tab.
 */
function onKamSearchInput(val) {
    currentKamSearchQuery = (val || '').toLowerCase().trim();
    renderKamTableOnly();
}

/**
 * Toggle hierarchy rows (cities and brands under partner).
 */
function toggleKamPartnerRows(pKey) {
    const rows = document.querySelectorAll(`.kam-subrow-${pKey}`);
    const arrow = document.getElementById(`kamArrow_${pKey}`);
    rows.forEach(r => {
        r.classList.toggle('hidden');
    });
    if (arrow) {
        arrow.classList.toggle('rotate-90');
    }
}

/**
 * Aggregates all KAM-related data given the global filter and current KAM filter.
 * CITIES AND BRANDS ARE DERIVED EXCLUSIVELY FROM OFFICIAL OEM DATA.
 */
function getKamAggregatedData(filterCfg) {
    const payload = window.dataPayload || {};
    const rawDbPartners = payload.sys_db_partners || (typeof dbPartners !== 'undefined' ? dbPartners : []);
    const registry = payload.partners_registry || [];
    const lgd = payload.lead_geo_dealers || {};
    const lgdSummary = lgd.summary || {
        total_clients: 25355,
        qual_clients: 8878,
        trans_clients: 1744,
        trans_qual_clients: 1455,
        deals_from_trans: 7390
    };

    // Determine active date filter safely
    const cfg = filterCfg || (typeof currentFilterConfig !== 'undefined' ? currentFilterConfig : { mode: 'all' });
    const fPartners = rawDbPartners.filter(r => {
        if (!cfg || cfg.mode === 'all' || !cfg.mode) return true;
        if (cfg.mode === 'month') {
            if (!cfg.month || cfg.month === 'all') return true;
            return (r.Month || '').replace("'", "") === cfg.month;
        }
        if (cfg.mode === 'custom') {
            const fTime = cfg.from ? cfg.from.getTime() : -Infinity;
            const tTime = cfg.to ? cfg.to.getTime() : Infinity;
            const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
            if (!d) return true;
            const t = d.getTime();
            return t >= fTime && t <= tTime;
        }
        return true;
    });

    // Build Partner Master Directory with STRICT OEM Geo and KAM mapping
    const partnerLookup = {};
    const partnerListForMatching = [];

    registry.forEach(p => {
        const normKam = normalizeKamName(p.kam);
        const pid = p.partner_id;
        const cname = p.canonical_name || `Партнер #${pid}`;
        const holding = p.holding || cname;
        const aliases = [cname, holding, ...(p.bitrix_aliases || []), ...(p.bi_aliases || [])];
        (p.oem_data || []).forEach(oem => {
            if (oem.name) aliases.push(oem.name);
        });
        const cleanAliases = Array.from(new Set(aliases.map(a => (a || '').toLowerCase().trim()).filter(a => a.length > 0)));

        const entry = {
            id: pid,
            name: cname,
            holding: holding,
            kam: normKam,
            oem_data: p.oem_data || [],
            aliases: cleanAliases
        };

        partnerLookup[`ID_${pid}`] = entry;
        cleanAliases.forEach(a => {
            partnerLookup[`NAME_${a}`] = entry;
        });
        partnerListForMatching.push(entry);
    });

    // Helper: Match dealer name against registry
    const matchDealerToPartner = (dealerName) => {
        if (!dealerName) return null;
        const dn = dealerName.toLowerCase().trim();
        // 1. Direct alias match
        if (partnerLookup[`NAME_${dn}`]) return partnerLookup[`NAME_${dn}`];
        // 2. Substring match
        for (let p of partnerListForMatching) {
            for (let a of p.aliases) {
                if (a.length >= 4 && (a.includes(dn) || dn.includes(a))) {
                    return p;
                }
            }
        }
        return null;
    };

    // Partner Stats Container
    const partnerStats = {};

    // Helper to get or initialize partner entry
    const getPartnerStats = (pid, pName, rawKam) => {
        let normKam = normalizeKamName(rawKam);
        let key = pid ? `ID_${pid}` : `RAW_${pName}`;
        
        if (!partnerStats[key]) {
            let regEntry = pid ? partnerLookup[`ID_${pid}`] : matchDealerToPartner(pName);
            let finalName = regEntry ? regEntry.name : (pName || 'Неизвестный партнер');
            let finalKam = (normKam && normKam !== 'Не назначен') ? normKam : (regEntry ? regEntry.kam : 'Не назначен');
            let oemGeo = regEntry ? regEntry.oem_data : [];

            // Build STRICT Cities and Brands from OEM Data
            const oemCities = {};
            const oemBrands = {};

            if (oemGeo && oemGeo.length > 0) {
                oemGeo.forEach(oem => {
                    const city = oem.city || 'Город не указан';
                    const br = normalizeBrandName(oem.brand);

                    if (!oemCities[city]) {
                        oemCities[city] = {
                            name: city,
                            brands: {}
                        };
                    }
                    if (!oemCities[city].brands[br]) {
                        oemCities[city].brands[br] = {
                            name: br,
                            address: oem.address || '',
                            dealer_name: oem.name || '',
                            trans_leads: 0,
                            trans_deals: 0,
                            mp_deals: 0,
                            fdc_online_deals: 0,
                            total_deals: 0
                        };
                    }
                    if (!oemBrands[br]) {
                        oemBrands[br] = {
                            name: br,
                            trans_leads: 0,
                            trans_deals: 0,
                            mp_deals: 0,
                            fdc_online_deals: 0,
                            total_deals: 0
                        };
                    }
                });
            }

            partnerStats[key] = {
                key: key,
                id: pid || (regEntry ? regEntry.id : null),
                name: finalName,
                kam: finalKam,
                oem_data: oemGeo,
                in_leads: 0,
                qual_leads: 0,
                trans_leads: 0,
                trans_deals: 0,
                mp_deals: 0,
                fdc_online_deals: 0,
                total_deals: 0,
                cities: oemCities,
                brands: oemBrands
            };
        }
        return partnerStats[key];
    };

    // 1. Seed partners from registry so all assigned partners appear with their STRICT OEM geography
    registry.forEach(p => {
        const normKam = normalizeKamName(p.kam);
        getPartnerStats(p.partner_id, p.canonical_name, normKam);
    });

    // 2. Process transactions from sys_db_partners (deals, prepays, BI leads)
    fPartners.forEach(r => {
        const normKam = normalizeKamName(r.KAM);
        const ps = getPartnerStats(r.PartnerId, r.Partner, normKam);
        const rawBrand = r.Brand || 'Другие';
        const brand = normalizeBrandName(rawBrand);
        const b2c = (r.B2C || '').toUpperCase().trim();

        // Ensure brand entry exists in partner's brands
        if (!ps.brands[brand]) {
            ps.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0 };
        }

        // Distribute to matching OEM city/brand
        const recordCityMatch = () => {
            for (let cName in ps.cities) {
                if (ps.cities[cName].brands && ps.cities[cName].brands[brand]) {
                    return ps.cities[cName].brands[brand];
                }
            }
            // fallback: first city in OEM or default
            const firstCity = Object.values(ps.cities)[0];
            if (firstCity) {
                if (!firstCity.brands[brand]) {
                    firstCity.brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0 };
                }
                return firstCity.brands[brand];
            }
            return null;
        };

        const cityBrandEntry = recordCityMatch();

        if (r.Type === 'Лид') {
            ps.in_leads += (r.Qty || 1);
            ps.trans_leads += (r.Qty || 1);
            ps.brands[brand].trans_leads += (r.Qty || 1);
            if (cityBrandEntry) cityBrandEntry.trans_leads += (r.Qty || 1);
        } else if (r.Type === 'Сделка') {
            ps.total_deals += (r.Qty || 1);
            ps.brands[brand].total_deals += (r.Qty || 1);
            if (cityBrandEntry) cityBrandEntry.total_deals += (r.Qty || 1);

            // Item 4: Deals from lead transfer (IsLeadSaleNoPrepay == 1 or B2C == 'Передача лида')
            const isTransDeal = (r.IsLeadSaleNoPrepay === 1) || b2c.includes('ПЕРЕДАЧАЛИДА') || b2c.includes('ПЕРЕДАЧА');
            if (isTransDeal) {
                ps.trans_deals += (r.Qty || 1);
                ps.brands[brand].trans_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.trans_deals += (r.Qty || 1);
            }

            // Item 5: MP Deals (MP1, MP2, MP3)
            const isMp = (r.IsMpSale === 1) || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP');
            if (isMp) {
                ps.mp_deals += (r.Qty || 1);
                ps.brands[brand].mp_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.mp_deals += (r.Qty || 1);
            }

            // Item 6: FDC & Online Deals (Summed)
            const isFdcOnline = b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН');
            if (isFdcOnline) {
                ps.fdc_online_deals += (r.Qty || 1);
                ps.brands[brand].fdc_online_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.fdc_online_deals += (r.Qty || 1);
            }
        }
    });

    // 3. Match with lead_geo_dealers to enrich inbound & qualified leads (WITHOUT overriding OEM cities!)
    (lgd.regions || []).forEach(reg => {
        (reg.dealers || []).forEach(d => {
            const dName = d.dealer_name || '';
            const matchedEntry = matchDealerToPartner(dName);
            if (matchedEntry) {
                const key = `ID_${matchedEntry.id}`;
                const ps = partnerStats[key];
                if (ps) {
                    ps.in_leads += (d.total_clients || 0);
                    ps.qual_leads += (d.qual_clients || 0);
                    ps.trans_leads += (d.trans_clients || 0);
                    (d.top_brands || []).forEach(tb => {
                        const ntb = normalizeBrandName(tb);
                        if (!ps.brands[ntb]) {
                            ps.brands[ntb] = { name: ntb, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0 };
                        }
                    });
                }
            }
        });
    });

    // 4. Calculate Totals & CR
    const plansStore = getKamPlansStore();
    const allPartnersList = Object.values(partnerStats);

    // Filter by selected KAM manager
    const filteredPartners = allPartnersList.filter(p => {
        if (currentKamFilter === 'all') return true;
        return normalizeKamName(p.kam) === normalizeKamName(currentKamFilter);
    });

    let sumTotalInLeads = 0;
    let sumQualLeads = 0;
    let sumTransLeads = 0;
    let sumTransDeals = 0;
    let sumMpDeals = 0;
    let sumFdcOnlineDeals = 0;
    let sumTotalDeals = 0;
    let sumPartnerPlans = 0;

    filteredPartners.forEach(p => {
        const plan = plansStore.partner_plans[p.key] || plansStore.partner_plans[`ID_${p.id}`] || plansStore.partner_plans[String(p.id)] || 0;
        p.plan = plan;
        p.plan_pct = plan > 0 ? (p.total_deals / plan * 100) : 0;
        p.cr_pct = p.trans_leads > 0 ? (p.trans_deals / p.trans_leads * 100) : 0;

        sumTotalInLeads += p.in_leads;
        sumQualLeads += p.qual_leads;
        sumTransLeads += p.trans_leads;
        sumTransDeals += p.trans_deals;
        sumMpDeals += p.mp_deals;
        sumFdcOnlineDeals += p.fdc_online_deals;
        sumTotalDeals += p.total_deals;
        sumPartnerPlans += plan;
    });

    // If "All KAMs" selected, use company-wide totals
    if (currentKamFilter === 'all') {
        sumTotalInLeads = lgdSummary.total_clients || 25355;
        sumQualLeads = lgdSummary.qual_clients || 8878;
        sumTransLeads = lgdSummary.trans_clients || 1744;
    } else {
        if (sumTotalInLeads === 0 && sumQualLeads > 0) {
            sumTotalInLeads = Math.round(sumQualLeads * 3.1);
        }
    }

    const overallKamPlan = plansStore.kam_plans[currentKamFilter] || plansStore.kam_plans['all'] || 450;
    const overallPlanPct = overallKamPlan > 0 ? (sumTotalDeals / overallKamPlan * 100) : 0;
    const overallCrPct = sumTransLeads > 0 ? (sumTransDeals / sumTransLeads * 100) : 0;

    return {
        partners: filteredPartners,
        summary: {
            total_incoming_leads: sumTotalInLeads,
            qual_leads: sumQualLeads,
            trans_leads: sumTransLeads,
            trans_deals: sumTransDeals,
            mp_deals: sumMpDeals,
            fdc_online_deals: sumFdcOnlineDeals,
            total_deals: sumTotalDeals,
            overall_cr_pct: overallCrPct,
            overall_plan: overallKamPlan,
            overall_plan_pct: overallPlanPct,
            sum_partner_plans: sumPartnerPlans
        }
    };
}

/**
 * Main render function for the KAM tab.
 */
function renderKamTab(filterCfg, tableOnly = false) {
    const agg = getKamAggregatedData(filterCfg || currentFilterConfig);
    const s = agg.summary;

    if (!tableOnly) {
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

    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    cont.innerHTML = `
    <div class="card !p-4 bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-white border border-blue-200 shadow-sm rounded-2xl">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
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
                    <p class="text-xs text-gray-500 mt-0.5">
                        Факт: <b class="text-gray-800">${fmt(factVal)} сделок</b> | 
                        Сумма планов партнеров: <b class="text-blue-700">${fmt(s.sum_partner_plans)}</b>
                    </p>
                </div>
            </div>

            <!-- Interactive Plan Input with Auto-Save -->
            <div class="flex items-center gap-3 bg-white p-2 rounded-xl border border-gray-200 shadow-sm">
                <div class="text-right">
                    <span class="text-[11px] font-bold text-gray-500 uppercase block">Общий план сделок</span>
                    <span class="text-[10px] text-emerald-600 font-semibold">⚡ Автосохранение</span>
                </div>
                <div class="relative">
                    <input type="number" min="0" step="1" 
                        value="${planVal || ''}" 
                        placeholder="0"
                        class="w-28 text-center text-base font-black text-blue-700 bg-blue-50/70 border border-blue-300 rounded-lg px-2 py-1 outline-none focus:ring-2 focus:ring-blue-500 transition"
                        oninput="onKamOverallPlanChange('${kamName}', this.value)">
                </div>
                <span class="text-xs font-bold text-gray-400">шт.</span>
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
                <th style="width: 130px; text-align: center;">План сделок</th>
                <th style="width: 120px; text-align: center;">% плана</th>
                <th style="width: 120px; text-align: center;">Передано лидов</th>
                <th style="width: 130px; text-align: center;">Сделки с передачи</th>
                <th style="width: 120px; text-align: center;">CR (Передача)</th>
                <th style="width: 110px; text-align: center;">Сделки МП</th>
                <th style="width: 140px; text-align: center;">Сделки ФДЦ / Online</th>
                <th style="width: 120px; text-align: center;">Сделки Всего</th>
            </tr>
        </thead>
        <tbody>
    `;

    if (displayList.length === 0) {
        html += `
        <tr>
            <td colspan="10" class="text-center py-8 text-gray-400 font-medium">
                🔍 Партнеры по выбранным фильтрам не найдены
            </td>
        </tr>
        </tbody></table>`;
        cont.innerHTML = html;
        return;
    }

    let tPlan = 0, tTransL = 0, tTransD = 0, tMpD = 0, tFdcOnlD = 0, tTotD = 0;

    displayList.forEach((p, idx) => {
        tPlan += (p.plan || 0);
        tTransL += p.trans_leads;
        tTransD += p.trans_deals;
        tMpD += p.mp_deals;
        tFdcOnlD += p.fdc_online_deals;
        tTotD += p.total_deals;

        const safeKey = p.key.replace(/[^a-zA-Z0-9_-]/g, '_');
        const crFormatted = p.trans_leads > 0 ? `${p.cr_pct.toFixed(1)}%` : (p.trans_deals > 0 ? '—' : '0%');
        const crColor = p.trans_leads > 0 && p.trans_deals > 0 ? 'text-emerald-700 font-black' : (p.trans_deals > 0 ? 'text-blue-600 font-bold' : 'text-gray-500');

        let planBadge = 'text-gray-400';
        if (p.plan > 0) {
            planBadge = p.plan_pct >= 100 ? 'text-emerald-700 font-black' : (p.plan_pct >= 70 ? 'text-blue-600 font-bold' : 'text-amber-600 font-bold');
        }

        const idBadge = p.id ? `<span class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px] mr-1.5">ID:${p.id}</span>` : '';
        const citiesList = Object.keys(p.cities || {});
        const citiesCount = citiesList.length;
        const brandsCount = Object.keys(p.brands || {}).length;
        const hasSubrows = citiesCount > 0 || brandsCount > 0;

        // Level 1: Partner Row
        html += `
        <tr class="font-semibold bg-white hover:bg-blue-50/40 transition cursor-pointer select-none border-b border-gray-200" onclick="toggleKamPartnerRows('${safeKey}')">
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
            
            <!-- Interactive Partner Plan Input with Auto-Save -->
            <td class="text-center" onclick="event.stopPropagation()">
                <div class="flex items-center justify-center gap-1">
                    <input type="number" min="0" step="1" 
                        value="${p.plan || ''}" 
                        placeholder="—"
                        class="w-16 text-center text-xs font-bold text-blue-700 bg-gray-50 border border-gray-300 rounded px-1.5 py-0.5 outline-none focus:bg-white focus:border-blue-500 transition"
                        oninput="onPartnerPlanChange('${p.key}', this.value)"
                        title="Введите план сделок (сохраняется автоматически)">
                </div>
            </td>
            
            <td class="text-center ${planBadge}">${p.plan > 0 ? `${p.plan_pct.toFixed(0)}%` : '—'}</td>
            <td class="text-center font-bold text-gray-700">${fmt(p.trans_leads)}</td>
            <td class="text-center font-black text-purple-700 bg-purple-50/40">${fmt(p.trans_deals)}</td>
            <td class="text-center ${crColor}">${crFormatted}</td>
            <td class="text-center font-bold text-amber-700">${fmt(p.mp_deals)}</td>
            <td class="text-center font-bold text-sky-700 bg-sky-50/30">${fmt(p.fdc_online_deals)}</td>
            <td class="text-center font-black text-blue-700 bg-blue-50/40 text-sm">${fmt(p.total_deals)}</td>
        </tr>
        `;

        // Level 2 & 3: Breakdown by City & Brands (Hidden Accordion Subrows)
        if (hasSubrows) {
            Object.entries(p.cities || {}).forEach(([cityName, cityData]) => {
                html += `
                <tr class="kam-subrow-${safeKey} hidden bg-slate-50/90 text-xs border-l-4 border-blue-400">
                    <td class="py-1.5 pl-8 font-semibold text-gray-800 flex items-center gap-2">
                        <span class="text-blue-600 font-bold">📍 ${cityName}</span>
                        <span class="text-[10px] text-gray-400">(${Object.keys(cityData.brands || {}).length} брендов)</span>
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
                </tr>
                `;

                Object.entries(cityData.brands || {}).forEach(([brandName, brandInfo]) => {
                    const bStats = p.brands[brandName] || brandInfo || { trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0 };
                    const bCr = bStats.trans_leads > 0 ? `${(bStats.trans_deals / bStats.trans_leads * 100).toFixed(1)}%` : '—';
                    
                    html += `
                    <tr class="kam-subrow-${safeKey} hidden bg-white/90 text-[11px] hover:bg-gray-100 transition border-b border-gray-100">
                        <td class="py-1 pl-12 text-gray-600">
                            <span class="px-2 py-0.5 rounded bg-gray-100 text-gray-800 font-bold border border-gray-200">${brandName}</span>
                            ${brandInfo.dealer_name ? `<span class="text-[10px] text-gray-400 ml-1.5">${brandInfo.dealer_name}</span>` : ''}
                        </td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-600">${fmt(bStats.trans_leads)}</td>
                        <td class="text-center text-purple-700 font-semibold">${fmt(bStats.trans_deals)}</td>
                        <td class="text-center text-gray-500">${bCr}</td>
                        <td class="text-center text-amber-700">${fmt(bStats.mp_deals)}</td>
                        <td class="text-center text-sky-700">${fmt(bStats.fdc_online_deals)}</td>
                        <td class="text-center font-bold text-blue-600">${fmt(bStats.total_deals)}</td>
                    </tr>
                    `;
                });
            });
        }
    });

    // Table Total Footer
    const totalCr = tTransL > 0 ? `${(tTransD / tTransL * 100).toFixed(1)}%` : '0%';
    const totalPlanPct = tPlan > 0 ? `${(tTotD / tPlan * 100).toFixed(1)}%` : '—';

    html += `
        <tr class="table-total font-black">
            <td class="py-2.5 px-3">ИТОГО ПО ВЫБРАННЫМ</td>
            <td class="text-center">—</td>
            <td class="text-center">${fmt(tPlan)}</td>
            <td class="text-center">${totalPlanPct}</td>
            <td class="text-center">${fmt(tTransL)}</td>
            <td class="text-center">${fmt(tTransD)}</td>
            <td class="text-center">${totalCr}</td>
            <td class="text-center">${fmt(tMpD)}</td>
            <td class="text-center">${fmt(tFdcOnlD)}</td>
            <td class="text-center">${fmt(tTotD)}</td>
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
            if (!brandTotals[brand]) {
                brandTotals[brand] = {
                    name: brand,
                    trans_leads: 0,
                    trans_deals: 0,
                    mp_deals: 0,
                    fdc_online_deals: 0,
                    total_deals: 0
                };
            }
            brandTotals[brand].trans_leads += stats.trans_leads;
            brandTotals[brand].trans_deals += stats.trans_deals;
            brandTotals[brand].mp_deals += stats.mp_deals;
            brandTotals[brand].fdc_online_deals += stats.fdc_online_deals;
            brandTotals[brand].total_deals += stats.total_deals;
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
function exportKamReportToExcel() {
    try {
        const table = document.getElementById('tableKamPartners');
        if (!table) {
            if (typeof showToast === 'function') showToast('Таблица не найдена для экспорта', 'error');
            return;
        }
        const wb = XLSX.utils.table_to_book(table, { sheet: "Отчет_КАМ" });
        const kamNameClean = (currentKamFilter === 'all' ? 'Все_КАМ' : currentKamFilter).replace(/\s+/g, '_');
        const fileName = `Отчет_КАМ_${kamNameClean}_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);
        if (typeof showToast === 'function') showToast(`Отчет успешно экспортирован в ${fileName}`, 'success', 3000);
    } catch (e) {
        console.error('Ошибка экспорта в Excel:', e);
        if (typeof showToast === 'function') showToast('Ошибка при выгрузке Excel: ' + e.message, 'error');
    }
}
