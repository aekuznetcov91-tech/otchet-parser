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
function normalizeBrandName(b, selectedMonth = window.selectedKamMonth || '') {
    if (!b) return 'Другие';
    let ub = String(b).toUpperCase().trim();
    const aux = ["ВНЕСЕНИЕ", "АВАНС", "КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП", "СЕРВИС", "ФИНАНС", "ДОГОВОР", "ОФОРМЛЕН", "КОМИСС", "УСЛУГ", "НЕИЗВЕСТН", "ДРУГИЕ", "NULL", "UNDEFINED"];
    if (aux.some(k => ub.includes(k))) return 'Другие';
    if (ub.includes('JETOUR')) return 'JETOUR';
    if (ub.includes('LADA') || ub.includes('ЛАДА')) return 'LADA';
    if (ub.includes('HAVAL') || ub.includes('ХАВЕЙЛ')) return 'HAVAL';
    if (ub.includes('CHANGAN') || ub.includes('ЧАНГАН')) return 'CHANGAN';
    if (ub.includes('KNEWSTAR') || ub.includes('КНЬЮСТАР') || ub.includes('КНЮСТАР')) return 'Knewstar';
    if (ub.includes('BELGEE') || ub.includes('БЕЛДЖИ') || ub.includes('ВЕELGEE')) return 'Belgee';
    if (ub.includes('GEELY') || ub.includes('ДЖИЛИ')) return 'Geely';
    if (ub.includes('G B K') || ub.includes('GBK')) return 'Geely & Belgee';
    if (ub.includes('CHERY') || ub.includes('TENET') || ub.includes('ТENET') || ub.includes('ТЕНЕТ') || ub.includes('ЧЕРИ')) return 'CHERY & TENET';
    if (ub.includes('SOLARIS') || ub.includes('SОLARIS') || ub.includes('СОЛЯРИС')) return 'SOLARIS';
    if (ub.includes('SOUEAST') || ub.includes('SOUEAS') || ub.includes('СОУИСТ')) return 'SOUEAST';
    if (ub.includes('GAC')) return 'GAC';
    if (ub.includes('МОСКВИЧ')) return 'МОСКВИЧ';
    if (ub.includes('JELAND') || ub.includes('ДЖЕЙЛЕНД')) return 'JELAND';
    if (ub.includes('OMODA') || ub.includes('JAECOO')) {
        let m = selectedMonth.replace("'", "");
        if (m >= '2026-09') return 'JELAND';
        return 'OMODA & JAECOO';
    }
    if (ub.includes('HONGQI')) return 'HONGQI';
    if (ub.includes('XCITE')) return 'XCITE';
    if (ub.includes('KIA') || ub.includes('КИА')) return 'KIA';
    if (ub.includes('HYUNDAI') || ub.includes('ХЕНДЭ')) return 'HYUNDAI';
    if (ub.includes('TOYOTA') || ub.includes('ТОЙОТА')) return 'TOYOTA';
    if (ub.includes('TANK') || ub.includes('ТАНК')) return 'TANK';
    if (ub.includes('EXEED') || ub.includes('ЭКСИД')) return 'EXEED';
    let res = String(b).trim();
    return res ? res : 'Другие';
}

