const CLOUD_PLANS_API = '/api/kam-plans';
let kamAuthenticatedUser = null;
let isSyncingPlansWithCloud = false;
let planSaveDebounceTimer = null;

/* ====================================================================
 * KAM ROLE-BASED ACCESS & ACCOUNT AUTHENTICATION
 * Ensures employees can only edit plans for their own account / partners,
 * while Administrators (Руководитель) have unrestricted access.
 * ====================================================================*/
const KAM_AUTH_STORAGE_KEY = 'sberauto_kam_active_account';

const KAM_AUTH_ACCOUNTS = {
    'admin': {
        id: 'admin',
        name: 'Руководитель',
        role: 'Руководитель / Администратор',
        isAdmin: true,
        displayName: 'Руководитель (Все права)'
    },
    'chikharev': {
        id: 'chikharev',
        name: 'Алексей Чихарев',
        role: 'Ведущий КАМ',
        isAdmin: false,
        displayName: 'Алексей Чихарев'
    },
    'kuznetsov': {
        id: 'kuznetsov',
        name: 'Андрей Кузнецов',
        role: 'Ведущий КАМ',
        isAdmin: false,
        displayName: 'Андрей Кузнецов'
    },
    'darienko': {
        id: 'darienko',
        name: 'Светлана Дариенко',
        role: 'КАМ (СЗФО / Сибирь)',
        isAdmin: false,
        displayName: 'Светлана Дариенко'
    },
    'soldatova': {
        id: 'soldatova',
        name: 'Валерия Солдатова',
        role: 'КАМ (Юг / Черноземье)',
        isAdmin: false,
        displayName: 'Валерия Солдатова'
    },
    'dobrolyubova': {
        id: 'dobrolyubova',
        name: 'Евгения Добролюбова',
        role: 'КАМ (Регионы / Урал)',
        isAdmin: false,
        displayName: 'Евгения Добролюбова'
    }
};

function getKamActiveUser() { return kamAuthenticatedUser; }

async function refreshKamSession() {
    try {
        const response = await fetch('/api/session', {credentials: 'same-origin', cache: 'no-store'});
        kamAuthenticatedUser = response.ok ? (await response.json()).user : null;
    } catch (_) { kamAuthenticatedUser = null; }
    renderKamAuthWidget();
}

async function kamAuthRequest(path, body = {}) {
    const response = await fetch(path, {method: 'POST', credentials: 'same-origin',
        headers: {'Content-Type':'application/json', 'X-Dashboard-Request':'1'}, body: JSON.stringify(body)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Не удалось выполнить запрос');
    return result;
}

function canUserEditOverallPlan(kamName) {
    const user = getKamActiveUser();
    if (!user) return false;
    if (user.isAdmin) return true;
    if (!kamName || kamName === 'all') return false; // Общий план сети меняет только Администратор/Руководитель
    return normalizeKamName(kamName) === normalizeKamName(user.name);
}

function canUserEditPartnerPlan(partnerKam) {
    const user = getKamActiveUser();
    if (!user) return false;
    if (user.isAdmin) return true;
    if (!partnerKam || partnerKam === '—' || partnerKam === 'Не назначен') return false;
    return normalizeKamName(partnerKam) === normalizeKamName(user.name);
}

function renderKamAuthWidget() {
    const cont = document.getElementById('kamAuthWidgetContainer');
    if (!cont) return;
    const user = getKamActiveUser();
    if (user) {
        cont.innerHTML = `
            <div class="flex items-center gap-2 bg-emerald-50 border border-emerald-300 px-3 py-1.5 rounded-xl shadow-xs">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <div class="flex flex-col text-left">
                    <span class="text-xs font-black text-emerald-950 flex items-center gap-1">
                        ${user.isAdmin ? '👑' : '👤'} ${escapeHtml(user.name)}
                    </span>
                    <span class="text-[10px] text-emerald-700 font-semibold leading-none">${escapeHtml(user.role)}</span>
                </div>
                <button type="button" onclick="kamLogout()" class="ml-2 px-2 py-0.5 bg-white hover:bg-rose-50 text-rose-600 hover:text-rose-700 border border-rose-200 rounded-lg text-[10px] font-bold transition shadow-2xs cursor-pointer" title="Выйти из профиля">
                    Выйти
                </button>
            </div>
        `;
    } else {
        cont.innerHTML = `
            <button type="button" onclick="openKamLoginModal()" class="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition cursor-pointer">
                <span>🔐</span>
                <span>Войти в профиль КАМ</span>
            </button>
        `;
    }
}

function openKamLoginModal(preselectKamName = '') {
    const modal = document.getElementById('kamLoginModal');
    if (!modal) return;
    const select = document.getElementById('kamLoginSelect');
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (errEl) errEl.classList.add('hidden');
    if (pinInput) pinInput.value = '';

    if (select && preselectKamName) {
        if (preselectKamName === 'admin' || preselectKamName === 'all') {
            select.value = 'admin';
        } else {
            const norm = normalizeKamName(preselectKamName);
            for (const [id, acc] of Object.entries(KAM_AUTH_ACCOUNTS)) {
                if (normalizeKamName(acc.name) === norm) {
                    select.value = id;
                    break;
                }
            }
        }
    }
    modal.classList.remove('hidden');
    if (pinInput) setTimeout(() => pinInput.focus(), 100);
}

function closeKamLoginModal() {
    const modal = document.getElementById('kamLoginModal');
    if (modal) modal.classList.add('hidden');
}

function onKamLoginAccountSelect(accId) {
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (errEl) errEl.classList.add('hidden');
    if (pinInput) {
        pinInput.value = '';
        pinInput.focus();
    }
}

async function handleKamLoginSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const select = document.getElementById('kamLoginSelect');
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (!select || !pinInput) return;
    try {
        const result = await kamAuthRequest('/api/login', {id:select.value,password:pinInput.value});
        kamAuthenticatedUser = result.user;
        pinInput.value = '';
        closeKamLoginModal();
        await syncKamPlansFromCloud();
        if (!result.user.isAdmin && typeof setKamManagerFilter === 'function') setKamManagerFilter(result.user.name);
        else renderKamTab(currentFilterConfig);
    } catch(error) {
        if(errEl) {errEl.textContent = error.message;errEl.classList.remove('hidden');}
    }
}

async function kamLogout() {
    try { await kamAuthRequest('/api/logout'); }
    catch (_) { if(typeof showToast==='function')showToast('Не удалось завершить сеанс на сервере. Повторите выход.', 'warning');return; }
    kamAuthenticatedUser = null;
    renderKamTab(currentFilterConfig);
}
if (typeof window !== 'undefined') setTimeout(refreshKamSession, 100);
