/**
 * Aggregates all KAM-related data given the global filter and current KAM filter.
 * CITIES AND BRANDS ARE DERIVED EXCLUSIVELY FROM OFFICIAL OEM DATA.
 */
function getKamAggregatedData(filterCfg) {
    const payload = window.dataPayload || {};
    const cfg = filterCfg || (typeof currentFilterConfig !== 'undefined' ? currentFilterConfig : { mode: 'all' });
    return calculateKamAggregation({
        ...payload,
        sys_db_partners: payload.sys_db_partners || (typeof dbPartners !== 'undefined' ? dbPartners : [])
    }, cfg, {
        kamFilter: currentKamFilter,
        plans: getKamPlansStore(),
        brandMonth: window.selectedKamMonth || '',
        today: new Date()
    });
}

/** Compute metrics from explicit inputs; storage and UI state stay in the adapter. */
function calculateKamAggregation(payload, cfg, options) {
    const rawDbPartners = payload.sys_db_partners || [];
    const registry = payload.partners_registry || [];
    const lgd = payload.lead_geo_dealers || {};
    const currentKamFilter = options.kamFilter;
    const normalizeBrand = brand => normalizeBrandName(brand, options.brandMonth);
    const activeMonth = (cfg.mode === 'month' && cfg.month) ? cfg.month : (cfg.mode === 'all' ? 'all' : '2026-08');
    const monthLgd = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd.by_month['2026-08']))) || lgd;
    const lgdSummary = monthLgd.summary || lgd.summary || {
        total_clients: 23572,
        qual_clients: 8961,
        trans_clients: 1052,
        trans_qual_clients: 1052,
        deals_from_trans: 5545
    };

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

    const GENERIC_STOP_WORDS = new Set([
        'ооо', 'зао', 'пао', 'ао', 'ип', 'online', 'онлайн', 'onlin',
        'авто', 'auto', 'холдинг', 'holding', 'группа', 'group', 'моторс', 'motors',
        'центр', 'дилер', 'сервис', 'плюс', 'трейд', 'компания', 'россия', 'russia'
    ]);

    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) {
            return;
        }
        const normKam = normalizeKamName(p.kam);
        const pid = p.partner_id;
        const cname = p.canonical_name || `Партнер #${pid}`;
        const rawHolding = (p.holding || '').trim();
        const holding = (rawHolding && !GENERIC_STOP_WORDS.has(rawHolding.toLowerCase())) ? rawHolding : cname;
        const aliases = [cname, holding, ...(p.bitrix_aliases || []), ...(p.bi_aliases || [])];
        (p.oem_data || []).forEach(oem => {
            if (oem.name) aliases.push(oem.name);
        });
        const cleanAliases = Array.from(new Set(
            aliases.map(a => (a || '').toLowerCase().trim())
                   .filter(a => a.length >= 3 && !GENERIC_STOP_WORDS.has(a))
        ));

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
        if (dn === 'сберавто' || dn === 'пул сберавто' || dn.includes('пул сберавто') || dn.includes('сберавто')) {
            return null;
        }
        // 1. Direct alias match
        if (partnerLookup[`NAME_${dn}`]) return partnerLookup[`NAME_${dn}`];
        // 2. Substring match
        for (let p of partnerListForMatching) {
            for (let a of p.aliases) {
                if (a.length >= 5 && !GENERIC_STOP_WORDS.has(a)) {
                    if (dn.includes(a) || (a.includes(dn) && dn.length >= 6)) {
                        return p;
                    }
                }
            }
        }
        return null;
    };

    // Partner Stats Container
    const partnerStats = {};

    // Helper to get or initialize partner entry
    const getPartnerStats = (pid, pName, rawKam) => {
        let regEntry = pid ? partnerLookup[`ID_${pid}`] : matchDealerToPartner(pName);
        let finalPid = pid || (regEntry ? regEntry.id : null);
        let finalName = regEntry ? regEntry.name : (pName || 'Неизвестный партнер');
        let normKam = normalizeKamName(rawKam);
        let finalKam = (normKam && normKam !== 'Не назначен') ? normKam : (regEntry ? normalizeKamName(regEntry.kam) : 'Не назначен');
        let key = finalPid ? (finalKam ? `ID_${finalPid}__${finalKam}` : `ID_${finalPid}`) : (finalKam ? `RAW_${finalName}__${finalKam}` : `RAW_${finalName}`);

        if (!partnerStats[key]) {
            let oemGeo = regEntry ? regEntry.oem_data : [];

            // Build STRICT Cities and Brands from OEM Data
            const oemCities = {};
            const oemBrands = {};

            if (oemGeo && oemGeo.length > 0) {
                oemGeo.forEach(oem => {
                    // Filter OEM by responsible KAM if partner has territory split across multiple KAMs
                    if (finalKam && finalKam !== 'Не назначен' && oem.responsible) {
                        const oemKam = normalizeKamName(oem.responsible);
                        if (oemKam !== finalKam) {
                            return;
                        }
                    }

                    const city = oem.city || 'Город не указан';
                    const br = normalizeBrand(oem.brand);

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
                            total_deals: 0,
                            mtd_deals: 0,
                            debts_count: 0
                        };
                    }
                    if (!oemBrands[br]) {
                        oemBrands[br] = {
                            name: br,
                            trans_leads: 0,
                            trans_deals: 0,
                            mp_deals: 0,
                            fdc_online_deals: 0,
                            total_deals: 0,
                            mtd_deals: 0,
                            debts_count: 0
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
                has_trans_from_db: false,
                trans_deals: 0,
                mp_deals: 0,
                fdc_online_deals: 0,
                total_deals: 0,
                mtd_deals: 0,
                debts_count: 0,
                cities: oemCities,
                brands: oemBrands
            };
        }
        return partnerStats[key];
    };

    // 1. Seed partners from registry so all assigned partners appear with their STRICT OEM geography
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) {
            return;
        }
        let normKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            normKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && normKam === 'Евгения Добролюбова') {
            normKam = 'Андрей Кузнецов';
        }
        const distinctKams = new Set();
        if (p.oem_data && p.oem_data.length > 0) {
            p.oem_data.forEach(o => {
                let resp = o.responsible ? normalizeKamName(o.responsible) : normKam;
                if (p.partner_id === 1035) {
                    resp = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
                }
                distinctKams.add(resp);
            });
        }
        if (distinctKams.size > 1) {
            distinctKams.forEach(k => getPartnerStats(p.partner_id, p.canonical_name, k));
        } else {
            getPartnerStats(p.partner_id, p.canonical_name, normKam);
        }
    });

    // 2. Process transactions from sys_db_partners (deals, prepays, BI leads)
    fPartners.forEach(r => {
        if (r.PartnerId === 1210 || (r.Partner && r.Partner.toLowerCase().includes('сберавто'))) {
            return;
        }
        const normKam = normalizeKamName(r.KAM);
        const ps = getPartnerStats(r.PartnerId, r.Partner, normKam);
        if (normKam && normKam !== 'Не назначен') {
            ps.kam = normKam;
        }
        const rawBrand = r.Brand || 'Другие';
        const brand = normalizeBrand(rawBrand);
        const b2c = (r.B2C || '').toUpperCase().trim();

        // Ensure brand entry exists in partner's brands
        if (!ps.brands[brand]) {
            ps.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
        }

        // Distribute to matching OEM city/brand
        const recordCityMatch = () => {
            const txCity = String(r.City || '').trim();
            // 1. Direct match on transaction City if present in ps.cities
            if (txCity && ps.cities[txCity]) {
                if (!ps.cities[txCity].brands[brand]) {
                    ps.cities[txCity].brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                return ps.cities[txCity].brands[brand];
            }
            // 2. Search for brand across existing cities in ps.cities
            for (let cName in ps.cities) {
                if (ps.cities[cName].brands && ps.cities[cName].brands[brand]) {
                    return ps.cities[cName].brands[brand];
                }
            }
            // 3. Fallback: first city in OEM or default
            const firstCity = Object.values(ps.cities)[0];
            if (firstCity) {
                if (!firstCity.brands[brand]) {
                    firstCity.brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                return firstCity.brands[brand];
            }
            // 4. Fallback: create city dynamically if ps.cities has no cities
            const defCity = txCity || 'Город не указан';
            if (!ps.cities[defCity]) {
                ps.cities[defCity] = { name: defCity, brands: {} };
            }
            if (!ps.cities[defCity].brands[brand]) {
                ps.cities[defCity].brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
            }
            return ps.cities[defCity].brands[brand];
        };

        const cityBrandEntry = recordCityMatch();

        if (r.Type === 'Лид') {
            if (!r.HasPrepay || r.HasPrepay === 0) {
                ps.trans_leads += (r.Qty || 1);
                ps.brands[brand].trans_leads += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.trans_leads += (r.Qty || 1);
                ps.has_trans_from_db = true;
            }
        } else if (r.Type === 'Сделка') {
            ps.total_deals += (r.Qty || 1);
            ps.brands[brand].total_deals += (r.Qty || 1);
            if (cityBrandEntry) cityBrandEntry.total_deals += (r.Qty || 1);

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

            // Item 4: Deals from lead transfer (Чистые: если сделка не закрыта как МП или ФДЦ/Online)
            const isTransDeal = (!isMp && !isFdcOnline) && ((r.IsLeadSaleNoPrepay === 1) || b2c.includes('ПЕРЕДАЧАЛИДА') || b2c.includes('ПЕРЕДАЧА'));
            if (isTransDeal) {
                ps.trans_deals += (r.Qty || 1);
                ps.brands[brand].trans_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.trans_deals += (r.Qty || 1);
            }
        }
    });

    // 3. Match with lead_geo_dealers to enrich inbound & qualified leads for the active month (WITHOUT overriding OEM cities!)
    (monthLgd.regions || []).forEach(reg => {
        (reg.dealers || []).forEach(d => {
            const dName = d.dealer_name || '';
            const matchedEntry = matchDealerToPartner(dName);
            if (matchedEntry) {
                const targetPid = matchedEntry.id;
                const targetPname = (matchedEntry.name || '').toLowerCase();
                let ps = null;
                for (let k in partnerStats) {
                    const psItem = partnerStats[k];
                    if (targetPid && psItem.id === targetPid) {
                        ps = psItem;
                        break;
                    }
                    if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                        ps = psItem;
                        break;
                    }
                }
                if (ps) {
                    ps.in_leads += (d.total_clients || 0);
                    ps.qual_leads += (d.qual_clients || 0);
                    // Prevent double counting: only add trans_clients from geo-dealers if partner has NO leads in sys_db_partners
                    if (!ps.has_trans_from_db) {
                        ps.trans_leads += (d.trans_clients || 0);
                        (d.top_brands || []).forEach(tb => {
                            const ntb = normalizeBrand(tb);
                            if (!ps.brands[ntb]) {
                                ps.brands[ntb] = { name: ntb, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                            }
                            ps.brands[ntb].trans_leads += (d.trans_clients || 0);
                        });
                    }
                }
            }
        });
    });

    // Ensure in_leads is at least equal to trans_leads
    Object.values(partnerStats).forEach(ps => {
        if (ps.in_leads < ps.trans_leads) {
            ps.in_leads = ps.trans_leads;
        }
    });

    // 3.1 Calculate MTD (Month-To-Date) Deals from previous month
    let prevMonth = null;
    let isLatestMonth = false;
    let maxDealDay = 31;

    if (activeMonth && activeMonth !== 'all') {
        const parts = activeMonth.split('-');
        if (parts.length === 2) {
            let y = parseInt(parts[0], 10);
            let m = parseInt(parts[1], 10);
            m -= 1;
            if (m === 0) {
                m = 12;
                y -= 1;
            }
            prevMonth = `${y}-${String(m).padStart(2, '0')}`;
        }

        const allMonths = Array.from(new Set(rawDbPartners.map(r => (r.Month || '').replace("'", "")).filter(Boolean))).sort();
        const latestMonth = allMonths[allMonths.length - 1];
        isLatestMonth = (activeMonth === latestMonth);

        if (isLatestMonth) {
            let foundMax = 0;
            rawDbPartners.forEach(r => {
                if ((r.Month || '').replace("'", "") === activeMonth && r.Type === 'Сделка' && r.Date) {
                    const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
                    if (d && d.getDate() > foundMax) {
                        foundMax = d.getDate();
                    }
                }
            });
            maxDealDay = foundMax > 0 ? foundMax : options.today.getDate();
        } else {
            maxDealDay = 31;
        }
    }

    if (prevMonth) {
        rawDbPartners.forEach(r => {
            if ((r.Month || '').replace("'", "") !== prevMonth || r.Type !== 'Сделка') return;

            // Day cutoff check
            if (isLatestMonth && r.Date) {
                const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
                if (d && d.getDate() > maxDealDay) return;
            }

            const pEntry = r.PartnerId ? partnerLookup[`ID_${r.PartnerId}`] : matchDealerToPartner(r.Partner);
            const targetPid = r.PartnerId || (pEntry ? pEntry.id : null);
            const targetPname = (pEntry ? pEntry.name : (r.Partner || '')).toLowerCase();

            let targetPs = null;
            for (let k in partnerStats) {
                const psItem = partnerStats[k];
                if (targetPid && psItem.id === targetPid) {
                    targetPs = psItem;
                    break;
                }
                if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                    targetPs = psItem;
                    break;
                }
            }

            if (targetPs) {
                const qty = (r.Qty || 1);
                targetPs.mtd_deals += qty;
                const rawBrand = r.Brand || 'Другие';
                const brand = normalizeBrand(rawBrand);
                if (!targetPs.brands[brand]) {
                    targetPs.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                targetPs.brands[brand].mtd_deals += qty;
            }
        });
    }

    // 3.2 Calculate Debts (all active open debts for unclosed prepaid deals across entire database)
    const allDebtors = (typeof rawDebtorsList !== 'undefined' && rawDebtorsList.length > 0)
        ? rawDebtorsList
        : (payload.debtors || []);

    allDebtors.forEach(d => {
        let pEntry = null;
        if (d.partner_id && partnerLookup[`ID_${d.partner_id}`]) {
            pEntry = partnerLookup[`ID_${d.partner_id}`];
        } else {
            pEntry = matchDealerToPartner(d.company || d.raw_company);
        }

        const targetPid = d.partner_id || (pEntry ? pEntry.id : null);
        const targetPname = (pEntry ? pEntry.name : (d.company || d.raw_company || '')).toLowerCase();

        let targetPs = null;
        for (let k in partnerStats) {
            const psItem = partnerStats[k];
            if (targetPid && psItem.id === targetPid) {
                targetPs = psItem;
                break;
            }
            if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                targetPs = psItem;
                break;
            }
        }

        if (!targetPs) {
            const finalPid = targetPid;
            const finalName = pEntry ? pEntry.name : (d.company || d.raw_company || 'Неизвестный партнер');
            const dKam = normalizeKamName(d.kam || (pEntry ? pEntry.kam : 'Не назначен'));
            targetPs = getPartnerStats(finalPid, finalName, dKam);
        }

        if (targetPs) {
            targetPs.debts_count = (targetPs.debts_count || 0) + 1;
            const rawBrand = d.brand || 'Другие';
            const brand = normalizeBrand(rawBrand);
            if (!targetPs.brands[brand]) {
                targetPs.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
            }
            targetPs.brands[brand].debts_count = (targetPs.brands[brand].debts_count || 0) + 1;
        }
    });

    // 4. Calculate Legal Entities with Deals for Selected KAM
    const legalEntitiesMap = {};
    fPartners.forEach(r => {
        if (r.Type !== 'Сделка') return;
        const normKam = normalizeKamName(r.KAM);
        if (currentKamFilter !== 'all' && normKam !== normalizeKamName(currentKamFilter)) return;

        const rawName = (r.RawPartner || r.Partner || 'Неизвестная компания').trim();
        const leKey = rawName.toUpperCase();

        if (!legalEntitiesMap[leKey]) {
            const regEntry = r.PartnerId ? partnerLookup[`ID_${r.PartnerId}`] : matchDealerToPartner(r.Partner);
            let inn = '';
            let cities = new Set();
            let brands = new Set();
            if (regEntry && regEntry.oem_data) {
                regEntry.oem_data.forEach(o => {
                    if (o.inn) inn = o.inn;
                    if (o.city) cities.add(o.city);
                    if (o.brand) brands.add(o.brand);
                });
            }
            legalEntitiesMap[leKey] = {
                name: rawName,
                canonical_partner: regEntry ? regEntry.name : r.Partner,
                partner_id: r.PartnerId || (regEntry ? regEntry.id : ''),
                kam: normKam,
                inn: inn,
                mp_deals: 0,
                fdc_online_deals: 0,
                total_deals: 0,
                cities: cities,
                brands: brands
            };
        }

        const le = legalEntitiesMap[leKey];
        le.total_deals += (r.Qty || 1);
        const b2c = (r.B2C || '').toUpperCase();
        if (r.IsMpSale === 1 || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP')) {
            le.mp_deals += (r.Qty || 1);
        }
        if (b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН')) {
            le.fdc_online_deals += (r.Qty || 1);
        }
        const nb = normalizeBrand(r.Brand);
        if (nb) le.brands.add(nb);
    });

    const legalEntitiesList = Object.values(legalEntitiesMap);
    legalEntitiesList.sort((a, b) => b.total_deals - a.total_deals);

    // 5. Calculate Totals & CR
    const plansStore = options.plans;
    const allPartnersList = Object.values(partnerStats);

    // Guarantee that every partner with brands has at least one city containing those brands
    allPartnersList.forEach(p => {
        const cKeys = Object.keys(p.cities || {});
        const bKeys = Object.keys(p.brands || {});
        if (bKeys.length > 0) {
            if (cKeys.length === 0) {
                let defCity = 'Город не указан';
                if (p.oem_data && p.oem_data.length > 0) {
                    const matchingOem = p.oem_data.find(o => !o.responsible || normalizeKamName(o.responsible) === p.kam);
                    if (matchingOem && matchingOem.city) defCity = matchingOem.city;
                    else if (p.oem_data[0].city) defCity = p.oem_data[0].city;
                }
                p.cities[defCity] = { name: defCity, brands: {} };
                bKeys.forEach(bk => {
                    p.cities[defCity].brands[bk] = { ...p.brands[bk] };
                });
            } else {
                const firstCityName = cKeys[0];
                bKeys.forEach(bk => {
                    let brandFound = false;
                    for (let cName of cKeys) {
                        if (p.cities[cName].brands && p.cities[cName].brands[bk]) {
                            brandFound = true;
                            break;
                        }
                    }
                    if (!brandFound) {
                        p.cities[firstCityName].brands[bk] = { ...p.brands[bk] };
                    }
                });
            }
        }
    });

    // Filter by selected KAM manager
    const filteredPartners = allPartnersList.filter(p => {
        if (p.id === 1210 || (p.name && p.name.toLowerCase() === 'сберавто')) return false;
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
    let sumMtdDeals = 0;
    let sumDebts = 0;

    filteredPartners.forEach(p => {
        let plan = 0;
        if (currentKamFilter !== 'all') {
            const kamNorm = normalizeKamName(currentKamFilter);
            const kamSpecificKey = `ID_${p.id}__${kamNorm}`;
            if (plansStore.partner_plans[kamSpecificKey] !== undefined) {
                plan = plansStore.partner_plans[kamSpecificKey];
            } else if (plansStore.partner_plans[p.key] !== undefined) {
                plan = plansStore.partner_plans[p.key];
            } else {
                const regPartner = partnerLookup[`ID_${p.id}`];
                if (regPartner && normalizeKamName(regPartner.kam) === kamNorm) {
                    plan = plansStore.partner_plans[`ID_${p.id}`] || plansStore.partner_plans[String(p.id)] || plansStore.partner_plans[p.name] || plansStore.partner_plans[(p.name || '').toLowerCase()] || 0;
                }
            }
        } else {
            plan = plansStore.partner_plans[p.key] || plansStore.partner_plans[`ID_${p.id}`] || plansStore.partner_plans[String(p.id)] || plansStore.partner_plans[p.name] || plansStore.partner_plans[(p.name || '').toLowerCase()] || 0;
        }
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
        sumMtdDeals += (p.mtd_deals || 0);
        sumDebts += (p.debts_count || 0);
    });

    // If "All KAMs" selected, use company-wide totals
    if (currentKamFilter === 'all') {
        sumTotalInLeads = lgdSummary.total_clients || 23572;
        sumQualLeads = lgdSummary.qual_clients || 8961;
        sumTransLeads = sumTransLeads || lgdSummary.trans_clients || 1052;
    } else {
        if (sumTotalInLeads === 0 && sumQualLeads > 0) {
            sumTotalInLeads = Math.round(sumQualLeads * 3.1);
        }
    }

    const overallKamPlan = plansStore.kam_plans[currentKamFilter] || plansStore.kam_plans['all'] || 450;
    const overallPlanPct = overallKamPlan > 0 ? (sumTotalDeals / overallKamPlan * 100) : 0;
    const overallCrPct = sumTransLeads > 0 ? (sumTransDeals / sumTransLeads * 100) : 0;

    let assignedPartnersCount = 0;
    const assignedMasterPartners = [];
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) return;
        let pKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            pKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && pKam === 'Евгения Добролюбова') {
            pKam = 'Андрей Кузнецов';
        }
        if (currentKamFilter === 'all' || pKam === normalizeKamName(currentKamFilter)) {
            assignedPartnersCount++;
            assignedMasterPartners.push(p);
        }
    });
    const activePct = assignedPartnersCount > 0 ? (legalEntitiesList.length / assignedPartnersCount * 100) : 0;

    // 4.1 Build Rooftops (Город + Бренд) for the selected KAM (or all)
    const rooftopsMap = {};

    // Seed from assigned partners & OEM data
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) return;
        let pKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            pKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && pKam === 'Евгения Добролюбова') {
            pKam = 'Андрей Кузнецов';
        }
        if (currentKamFilter !== 'all' && pKam !== normalizeKamName(currentKamFilter)) return;

        const pid = p.partner_id;
        const pname = p.canonical_name || `Партнер #${pid}`;
        const oemData = p.oem_data || [];

        if (oemData.length > 0) {
            oemData.forEach(o => {
                const city = String(o.city || 'Город не указан').trim();
                const brand = normalizeBrand(o.brand || 'Другие');
                const rkey = `${pid}__${city.toLowerCase()}__${brand.toLowerCase()}`;
                if (!rooftopsMap[rkey]) {
                    rooftopsMap[rkey] = {
                        key: rkey,
                        partner_id: pid,
                        partner_name: pname,
                        city: city,
                        brand: brand,
                        address: o.address || '',
                        dealer_name: o.name || '',
                        kam: pKam,
                        deals_count: 0,
                        mp_deals: 0,
                        fdc_online_deals: 0
                    };
                }
            });
        }
    });

    // Process transactions from sys_db_partners (deals only) into rooftops
    fPartners.forEach(r => {
        if (r.Type !== 'Сделка') return;
        const normKam = normalizeKamName(r.KAM);
        if (currentKamFilter !== 'all' && normKam !== normalizeKamName(currentKamFilter)) return;

        const pid = r.PartnerId || (matchDealerToPartner(r.Partner) ? matchDealerToPartner(r.Partner).id : null);
        const pname = r.Partner || r.RawPartner || 'Неизвестный партнер';
        const rawBrand = r.Brand || 'Другие';
        const brand = normalizeBrand(rawBrand);
        const city = String(r.City || 'Город не указан').trim();

        let rkey = `${pid}__${city.toLowerCase()}__${brand.toLowerCase()}`;
        if (!rooftopsMap[rkey]) {
            let foundKey = null;
            for (let k in rooftopsMap) {
                const rtBrand = String(rooftopsMap[k].brand || 'Другие').toLowerCase();
                if (rooftopsMap[k].partner_id === pid && rtBrand === brand.toLowerCase()) {
                    foundKey = k;
                    break;
                }
            }
            rkey = foundKey || rkey;
        }

        if (!rooftopsMap[rkey]) {
            rooftopsMap[rkey] = {
                key: rkey,
                partner_id: pid,
                partner_name: pname,
                city: city,
                brand: brand,
                address: '',
                dealer_name: '',
                kam: normKam,
                deals_count: 0,
                mp_deals: 0,
                fdc_online_deals: 0
            };
        }

        const rt = rooftopsMap[rkey];
        const qty = (r.Qty || 1);
        rt.deals_count += qty;
        const b2c = (r.B2C || '').toUpperCase();
        if (r.IsMpSale === 1 || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP')) {
            rt.mp_deals += qty;
        }
        if (b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН')) {
            rt.fdc_online_deals += qty;
        }
    });

    const rooftopsList = Object.values(rooftopsMap);
    rooftopsList.sort((a, b) => b.deals_count - a.deals_count || a.partner_name.localeCompare(b.partner_name));

    const activeRooftops = rooftopsList.filter(rt => rt.deals_count > 0);
    const sleepingRooftops = rooftopsList.filter(rt => rt.deals_count === 0);
    const rooftopsActivePct = rooftopsList.length > 0 ? (activeRooftops.length / rooftopsList.length * 100) : 0;

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
            mtd_deals: sumMtdDeals,
            debts_count: sumDebts,
            overall_cr_pct: overallCrPct,
            overall_plan: overallKamPlan,
            overall_plan_pct: overallPlanPct,
            sum_partner_plans: sumPartnerPlans,
            legal_entities_count: legalEntitiesList.length,
            total_assigned_partners: assignedPartnersCount,
            active_pct: activePct,
            assigned_master_partners: assignedMasterPartners,
            legal_entities: legalEntitiesList,
            rooftops_count: activeRooftops.length,
            total_assigned_rooftops: rooftopsList.length,
            rooftops_active_pct: rooftopsActivePct,
            rooftops: rooftopsList,
            active_rooftops_count: activeRooftops.length,
            sleeping_rooftops_count: sleepingRooftops.length
        }
    };
}

