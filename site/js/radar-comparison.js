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
 const esc=radarEscape;
 return `<section id="radarComparison" class="radar"><div class="head"><div class="title"><span class="icon" aria-hidden="true">📡</span><div><h3>Радар динамики & отклонений</h3><div class="subtitle">${esc(D.periodLabel)}</div></div></div><div class="headbadge">Исторический ориентир ≠ план</div></div>
<div class="benchmark"><div><div class="benchmark-label">ОСНОВНОЕ СРАВНЕНИЕ</div><strong id="radar-baseLabel">${esc(D.bestLabel)}</strong></div><div class="seg" id="radar-base"><button data-value="best" aria-pressed="true">Лучший из 3 месяцев</button><button data-value="previous" aria-pressed="false">${esc(D.monthNames[2])}</button></div></div>
<div class="seg channels" id="radar-channel"><button data-value="all" aria-pressed="true">Все каналы</button><button data-value="opt" aria-pressed="false">Опт МП2</button><button data-value="retail" aria-pressed="false">Розница и прочие</button></div>
<div class="seg tabs" id="radar-tab"><button data-value="brands" aria-pressed="true">Марки</button><button data-value="dealers" aria-pressed="false">Дилеры</button><button data-value="advances" aria-pressed="false">⏳ Авансы</button></div>
<div class="summaryline" id="radar-summary"></div><div class="tools"><span class="hint" id="radar-hint">Сортировка по отклонению от лучшего MTD, шт.</span><label id="radar-filterLabel">Показать<select id="radar-status"><option value="all">Все состояния</option><option value="record">Новый максимум</option><option value="recovery">Восстановление</option><option value="loss">Ниже максимума</option><option value="equal">На максимуме</option><option value="new">Недостаточно истории</option><option value="zero">Без продаж сейчас</option></select></label></div>
<div class="list" id="radar-list" aria-live="polite"></div><div class="footer"><span id="radar-footer"></span><button class="more" id="radar-more">Показать все</button></div><div class="plan">Планы по брендам и дилерам не заданы в радаре. Статус «Выше плана» появится только при наличии их утверждённых целей.</div>
<details><summary>Как считается сравнение</summary><ul><li>${esc(D.method)}</li><li>Лучший результат определяется отдельно для каждой марки и дилера. Максимумы разных компаний не суммируются. Цвет показывает динамику к истории, а не выполнение плана.</li><li>Восстановление: результат выше предыдущего месяца, но ниже максимума. Нулевая база не превращается в +100%. При неполной истории рекорд не объявляется; дата подключения дилера неизвестна.</li><li>Сохранены группы каналов радара: МП2 и остальные (включая МП1/МП3 и сделки без канала). OMODA/JAECOO/JELAND объединены для сопоставимости.</li><li>Авансы — текущий реестр по прежнему алгоритму, а не исторический снимок. Показано количество автомобилей по дилерам и максимальный срок ожидания.</li></ul></details></section>`;
}
function bindRadarComparison(D) {
const root=document.getElementById("radarComparison");if(!root)return;
const $=id=>root.querySelector('#radar-'+id),esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),n=x=>new Intl.NumberFormat('ru-RU',{maximumFractionDigits:0}).format(x),signed=x=>(x>0?'+':'')+n(x),months=D.monthNames.slice(0,3);const state=radarState;

function render(){for(const id of ['base','channel','tab'])$(id).querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.value===state[id])));$('status').value=state.status;const data=D.channels[state.channel],rows=data[state.tab];$('baseLabel').textContent=state.base==='best'?D.bestLabel:D.windowLabels[2];
 for(const key of ['brands','dealers','advances'])root.querySelector(`#radar-tab [data-value="${key}"]`).textContent=({brands:'Марки',dealers:'Дилеры',advances:'⏳ Авансы'})[key]+' ('+(key==='advances'?data[key].reduce((s,r)=>s+r.count,0):data[key].length)+')';
 const advance=state.tab==='advances';$('filterLabel').hidden=advance;$('base').querySelectorAll('button').forEach(b=>b.disabled=advance);$('hint').textContent=advance?'Текущий реестр · алгоритм авансов сохранён':state.base==='best'?'Самые большие отклонения от максимума — первыми':'Самые большие изменения к предыдущему месяцу — первыми';
 if(advance){$('summary').textContent='Авансы показаны по текущему реестру, без сравнения с историческим максимумом.';}else{const counts={};for(const r of rows)counts[radarCategory(r)]=(counts[radarCategory(r)]||0)+1;$('summary').textContent=`${counts.record||0} новых максимумов · ${counts.recovery||0} восстановлений · ${counts.loss||0} ниже максимума · ${counts.equal||0} на максимуме · ${counts.new||0} с неполной историей`;}
 let filtered=advance?rows:[...rows].filter(r=>state.status==='all'||(state.status==='zero'?r.values[3]===0:radarCategory(r)===state.status)).sort((a,b)=>Math.abs(b.values[3]-(state.base==='best'?b.best:b.values[2]))-Math.abs(a.values[3]-(state.base==='best'?a.best:a.values[2]))||a.name.localeCompare(b.name,'ru'));
 const shown=state.expanded?filtered:filtered.slice(0,6);
 $('list').innerHTML=shown.map(r=>{if(advance)return `<article class="item recovery advances"><div class="item-top"><div><div class="item-name">${esc(r.name)}</div><p>Максимальный возраст по реестру: ${n(r.days)} дн.</p></div><div class="delta"><strong>${n(r.count)} авто</strong></div></div></article>`;
 const cur=r.values[3],prev=r.values[2],cat=radarCategory(r),ref=state.base==='best'?r.best:prev,diff=cur-ref,deltaPrev=cur-prev,bestMonths=months.filter((_,i)=>r.values[i]===r.best).join(', '),pct=ref?' ('+signed(diff/ref*100)+'%)':'',label=cat==='record'?'🚀 Новый максимум':cat==='recovery'?'↗ Восстановление':cat==='equal'?'● На уровне максимума':cat==='new'?'◷ Недостаточно истории':cur<prev?'↓ Ниже обоих ориентиров':'↓ Ниже максимума';
 return `<article class="item ${cat==='record'?'':cat}"><div class="item-top"><div><div class="item-name">${esc(r.name)}</div><div class="tag">${label}</div></div><div class="delta"><strong>${signed(diff)} шт.${pct}</strong><small>${state.base==='best'?'к лучшему MTD':'к предыдущему месяцу'}${ref?'':' · нулевая база'}</small></div></div><div class="rowstats"><span class="fact">${cur} <small>сделок сейчас</small></span><span class="ref">${r.available.slice(0,3).every(Boolean)?'Лучший MTD':'Максимум известных периодов'}: <b>${r.best}</b> · ${esc(bestMonths)}</span></div><div class="prev">К ${esc(months[2])}: <span class="${deltaPrev>=0?'up':'down'}">${signed(deltaPrev)} шт.${prev?' ('+signed(deltaPrev/prev*100)+'%)':' · нулевая база'}</span> · было ${prev}${state.tab==='dealers'?' · КАМ: '+esc(r.kams.join(', ')):''}</div><div class="trail">${r.values.slice(0,3).map((v,i)=>`<span class="${v===r.best?'best':''}">${esc(D.windowLabels[i])}: ${r.available[i]?v:'нет данных'}</span>`).join('')}</div></article>`;}).join('')||`<div class="empty">${esc(D.error||'В этом срезе нет записей с выбранным состоянием.')}</div>`;
 $('footer').textContent=`Показано ${shown.length} из ${filtered.length} · ${advance?'дилеров в реестре':state.tab==='brands'?'брендов':'дилеров'}`;$('more').hidden=filtered.length<=6;$('more').textContent=state.expanded?'Свернуть':'Показать все';
}
for(const id of ['base','channel','tab'])$(id).querySelectorAll('button').forEach(b=>b.onclick=()=>{state[id]=b.dataset.value;state.expanded=false;if(id==='tab'){state.status='all';$('status').value='all';}$(id).querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render();});$('status').onchange=e=>{state.status=e.target.value;state.expanded=false;render();};$('more').onclick=()=>{state.expanded=!state.expanded;render();};render();

}
