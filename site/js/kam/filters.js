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

