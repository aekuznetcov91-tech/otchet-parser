/* Radar only: comparable calendar windows; no changes to other executive metrics. */
'use strict';
const radarState = {base:'best', channel:'all', tab:'brands', status:'all', expanded:false};
function radarCategory(r){const cur=r.values[3],prev=r.values[2];if(r.incomplete)return 'new';if(cur>r.best)return 'record';if(cur===r.best)return 'equal';if(cur>prev)return 'recovery';return 'loss';}
function radarEscape(value) {
    return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function calculateRadarComparison(allDb, partners, filter, metadata, legacy) {
    const dayMs=86400000, epoch=Date.UTC(1899,11,30);
    const serialDate=n=>Number(n)>0?new Date(epoch+Math.floor(Number(n))*dayMs):null;
    const key=d=>d.toISOString().slice(0,7);
    const clean=v=>String(v||'').replace(/'/g,'');
    const sales=(allDb||[]).filter(r=>Number(r.SaleQty)>0);
    const dates=sales.map(r=>serialDate(r.SaleDate||r.DealDate)).filter(Boolean);
    const stamp=String(metadata?.updated_at||'').match(/^(\d{2})\.(\d{2})\.(\d{4})/);
    // A refresh day's data may be partial. Exclude that day in every comparison.
    const snapshot=stamp?new Date(Date.UTC(+stamp[3],+stamp[2]-1,+stamp[1])):null;
    const latest=dates.length?new Date(Math.max(...dates.map(Number))):null;
    const asOf=snapshot?new Date(+snapshot-dayMs):latest;
    const defaultMonth=snapshot?key(snapshot):latest?key(latest):null;
    let selected=filter?.mode==='month'?filter.month:defaultMonth;
    let start=1,end=31,custom=false,error='';
    if(filter?.mode==='custom') {
        const a=filter.from,b=filter.to;
        if(!a||!b||a.getFullYear()!==b.getFullYear()||a.getMonth()!==b.getMonth()) error='Для сравнения с тремя месяцами выберите период внутри одного месяца.';
        else {selected=`${a.getFullYear()}-${String(a.getMonth()+1).padStart(2,'0')}`;start=a.getDate();end=b.getDate();custom=true;}
    }
    if(!selected||!/^\d{4}-\d{2}$/.test(selected)||!asOf) error='Недостаточно данных для определения периода.';
    const [year,month]=(selected||'2000-01').split('-').map(Number);
    const months=Array.from({length:4},(_,i)=>key(new Date(Date.UTC(year,month-4+i,1))));
    const monthNames=months.map(m=>new Date(m+'-01T00:00:00Z').toLocaleDateString('ru-RU',{month:'long',timeZone:'UTC'}));
    const lengths=months.map(m=>{const[y,n]=m.split('-').map(Number);return new Date(Date.UTC(y,n,0)).getUTCDate();});
    end=Math.min(end,lengths[3]);
    if(asOf&&selected>key(asOf)) end=0;
    else if(asOf&&selected===key(asOf))end=Math.min(end,asOf.getUTCDate());
    if(end<start&&!error)error='В выбранном периоде ещё нет завершённых дней в снимке данных.';
    const windowLabels=months.map((m,i)=>`${start}–${Math.min(end,lengths[i])} ${monthNames[i]} ${m.slice(0,4)}`);
    const D={months,monthNames,windowLabels,updated:metadata?.updated_at||'',channels:{},error,
        periodLabel:error||`${monthNames[3]} ${year} · ${custom?'период':'MTD'} ${start}–${end} · по завершённым дням`,
        bestLabel:'Лучший сопоставимый период: '+monthNames.slice(0,3).join(', '),
        method:`Сравниваются ${windowLabels[3]} и такие же дни трёх предыдущих месяцев. Если в месяце меньше дней, окно заканчивается последним днём месяца. День обновления снимка исключён. ${snapshot?'Снимок: '+metadata.updated_at:'Дата обновления неизвестна: граница — последняя дата сделки.'}`};
    const group=(rows,isDealer,channel)=>{
        const result=new Map(),coverage=new Set();
        for(const r of rows) {
            const qty=Number(isDealer?(r.Qty||1):r.SaleQty);
            if(isDealer&&r.Type!=='Сделка'||!(qty>0))continue;
            const dt=serialDate(isDealer?r.Date:r.SaleDate||r.DealDate);
            const m=clean(isDealer?r.Month:r.SaleMonth);
            if(!dt||!m||m>selected||key(dt)!==m||+dt>+asOf)continue;
            coverage.add(m);
            if(channel!=='all'&&getAlertDealChannelKey(r.B2C)!==channel)continue;
            let name=isDealer?canonicalPartnerName(r.Partner):String(r.Brand||'').trim();
            if(!isDealer){if(['OMODA','JAECOO','JAELAND','JELAND'].includes(name.toUpperCase()))name='JELAND';if(name==='SOUEAS')name='SOUEAST';if(!isAutomotiveBrand(name))continue;}
            if(!name)continue;
            if(!result.has(name))result.set(name,{name,values:[0,0,0,0],first:m,kams:new Set()});
            const row=result.get(name);row.first=row.first<m?row.first:m;
            const index=months.indexOf(m);
            if(index>=0&&dt.getUTCDate()>=start&&dt.getUTCDate()<=Math.min(end,lengths[index])){
                row.values[index]+=qty;if(isDealer&&r.KAM)row.kams.add(r.KAM);
            }
        }
        return [...result.values()].filter(r=>r.values.some(Boolean)).map(r=>({...r,kams:[...r.kams],available:months.map(m=>coverage.has(m)),best:Math.max(...r.values.slice(0,3)),incomplete:r.first>months[0]||months.slice(0,3).some(m=>!coverage.has(m))}));
    };
    for(const channel of ['all','opt','retail']) {
        const advances=new Map();
        for(const r of legacy?.channelsData?.[channel]?.stuckPrepays||[]) {
            if(!advances.has(r.partner))advances.set(r.partner,{name:r.partner,count:0,days:0});
            const a=advances.get(r.partner);a.count++;a.days=Math.max(a.days,Number(r.days)||0);
        }
        D.channels[channel]={brands:error?[]:group(sales,false,channel),dealers:error?[]:group(partners||[],true,channel),advances:[...advances.values()].sort((a,b)=>b.count-a.count)};
    }
    return D;
}
function renderRadarComparisonHTML(D) {
    const esc = radarEscape;
    return `<section id="radarComparison" aria-label="Радар динамики и отклонений">
        <header class="head"><span class="icon" aria-hidden="true">📡</span><h3>Радар динамики & отклонений</h3></header>
        <div class="period"><span title="${esc(D.periodLabel)}">${esc(D.error || D.windowLabels[3])}</span>
            <select id="radar-base" aria-label="Ориентир сравнения"><option value="best">Лучший из 3 мес.</option><option value="previous">${esc(D.monthNames[2])}</option></select></div>
        <div class="seg channels" id="radar-channel" aria-label="Каналы"><button data-value="all">Все каналы</button><button data-value="opt">Опт МП2</button><button data-value="retail">Розница и прочие</button></div>
        <div class="seg tabs" id="radar-tab" aria-label="Объекты сравнения"><button data-value="brands">Марки</button><button data-value="dealers">Дилеры</button><button data-value="advances">⏳ Авансы</button></div>
        <div class="tools"><div id="radar-summary" class="summaryline"></div><select id="radar-status" aria-label="Состояние">
            <option value="all">Все состояния</option><option value="record">Новый максимум</option><option value="recovery">Восстановление</option><option value="loss">Ниже максимума</option><option value="equal">На максимуме</option><option value="new">Недостаточно истории</option><option value="zero">Без продаж сейчас</option></select></div>
        <div class="list" id="radar-list" tabindex="0" aria-label="Результаты сравнения"></div>
        <footer class="footer"><span id="radar-footer" role="status"></span><button id="radar-help" aria-expanded="false" aria-controls="radar-method">ⓘ Как считаем</button></footer>
        <section id="radar-method" class="method" hidden aria-label="Методика сравнения"><button id="radar-close" aria-label="Закрыть методику">×</button><h4>Как считаем</h4>
            <p>${esc(D.method)}</p><p>Лучший результат определяется отдельно для каждой марки и дилера. Максимумы не суммируются. Исторический ориентир — не план; планы по брендам и дилерам в радаре не заданы.</p>
            <p>Восстановление: выше предыдущего месяца, но ниже максимума. Нулевая база не превращается в +100%. При неполной истории рекорд не объявляется.</p>
            <p>Цвет и состояние всегда относятся к лучшему периоду. Число справа — отклонение от выбранного ориентира. Сортировка — по величине отклонения в штуках.</p>
            <p>Группы каналов сохранены: МП2 и остальные (включая МП1/МП3 и сделки без канала). OMODA/JAECOO/JELAND объединены.</p>
            <p>Авансы — текущий реестр по прежнему алгоритму, без исторического сравнения. Нажмите на строку, чтобы увидеть историю и КАМов.</p></section>
    </section>`;
}
function bindRadarComparison(D) {
    const root = document.getElementById('radarComparison');
    if (!root) return;
    const $ = id => root.querySelector('#radar-' + id);
    const esc = radarEscape, state = radarState;
    const n = x => new Intl.NumberFormat('ru-RU', {maximumFractionDigits:0}).format(x);
    const signed = x => (x > 0 ? '+' : '') + n(x);
    const delta = (cur, base) => signed(cur - base) + (base ? ' / ' + signed((cur - base) / base * 100) + '%' : ' · база 0');
    const labels = {record:'🚀 Новый максимум', recovery:'↗ Восстановление', loss:'↓ Ниже максимума', equal:'● На максимуме', new:'◷ Мало истории'};
    function render() {
        const data = D.channels[state.channel], advance = state.tab === 'advances';
        for (const id of ['channel','tab']) $(id).querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.value === state[id])));
        $('base').value = state.base;
        $('base').disabled = advance;
        $('base').title = state.base === 'best' ? D.bestLabel : D.windowLabels[2];
        $('status').value = state.status;
        $('status').hidden = advance;
        for (const key of ['brands','dealers','advances']) {
            const count = key === 'advances' ? data[key].reduce((s,r) => s+r.count,0) : data[key].length;
            $('tab').querySelector(`[data-value="${key}"]`).textContent = {brands:'Марки',dealers:'Дилеры',advances:'⏳ Авансы'}[key] + ` (${count})`;
        }
        const rows = data[state.tab], counts = {};
        for (const r of advance ? [] : rows) counts[radarCategory(r)] = (counts[radarCategory(r)] || 0) + 1;
        $('summary').textContent = advance ? 'Текущий реестр · ожидание от 7 дней' : `🟢 ${counts.record||0} рек. · 🟡 ${counts.recovery||0} восст. · 🔴 ${counts.loss||0} ниже`;
        $('summary').title = advance ? 'Количество автомобилей и максимальный возраст аванса по дилеру' : `Новые максимумы: ${counts.record||0}; восстановление: ${counts.recovery||0}; ниже максимума: ${counts.loss||0}; на максимуме: ${counts.equal||0}; мало истории: ${counts.new||0}`;
        const filtered = advance ? rows : [...rows].filter(r => state.status === 'all' || (state.status === 'zero' ? r.values[3] === 0 : radarCategory(r) === state.status)).sort((a,b) => Math.abs(b.values[3]-(state.base==='best'?b.best:b.values[2]))-Math.abs(a.values[3]-(state.base==='best'?a.best:a.values[2])) || a.name.localeCompare(b.name,'ru'));
        $('list').innerHTML = filtered.map(r => {
            if (advance) return `<article class="item recovery advance"><div class="row-top"><strong class="name">${esc(r.name)}</strong><span class="delta">${n(r.count)} авто</span></div><div class="stats">Максимальное ожидание: <b>${n(r.days)} дн.</b></div></article>`;
            const cur=r.values[3], prev=r.values[2], cat=radarCategory(r), ref=state.base==='best'?r.best:prev;
            const bestMonths=D.monthNames.slice(0,3).filter((_,i)=>r.values[i]===r.best).join(', ');
            return `<details class="item ${cat}"><summary><div class="row-top"><strong class="name">${esc(r.name)}</strong><span class="tag">${labels[cat]}</span><span class="delta" title="${state.base==='best'?'К лучшему периоду':'К предыдущему месяцу'}">${delta(cur,ref)}</span><span class="chevron" aria-hidden="true">⌄</span></div>
                <div class="stats"><span>Факт <b>${n(cur)}</b></span><span>Лучший <b>${n(r.best)}</b>, ${esc(bestMonths)}</span><span>К ${esc(D.monthNames[2])}: <b class="${cur>=prev?'up':'down'}">${delta(cur,prev)}</b></span></div></summary>
                <div class="detail-body"><div class="trail">${r.values.slice(0,3).map((v,i)=>`<span class="${v===r.best?'best':''}">${esc(D.windowLabels[i])}: <b>${r.available[i]?n(v):'нет данных'}</b></span>`).join('')}</div>
                ${state.tab==='dealers'?`<p>КАМ: ${esc(r.kams.join(', ')||'Не указан')}</p>`:''}<p>${labels[cat]} · справа — ${state.base==='best'?'к лучшему сопоставимому периоду':'к предыдущему месяцу'}. ${r.incomplete?'История неполная; дата подключения неизвестна.':''}</p></div></details>`;
        }).join('') || `<div class="empty">${esc(D.error||'Нет записей с выбранным состоянием.')}</div>`;
        $('list').scrollTop = 0;
        $('footer').textContent = `${filtered.length} ${advance||state.tab==='dealers'?'дилеров':'брендов'} · листайте список`;
    }
    for (const id of ['channel','tab']) $(id).querySelectorAll('button').forEach(b => b.onclick = () => {
        state[id] = b.dataset.value;
        if (id === 'tab') state.status = 'all';
        render();
    });
    $('base').onchange = e => {state.base=e.target.value;render();};
    $('status').onchange = e => {state.status=e.target.value;render();};
    const help = open => { $('method').hidden=!open; $('help').setAttribute('aria-expanded',String(open)); (open?$('close'):$('help')).focus(); };
    $('help').onclick = () => help($('method').hidden);
    $('close').onclick = () => help(false);
    root.addEventListener('keydown',e => {if(e.key==='Escape'&&!$('method').hidden)help(false);});
    render();
}
