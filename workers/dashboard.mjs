import {COOKIE,PROFILES,digest,equal,json,harden,gate,validOrigin,readJson,fixedUpstream} from './security.mjs';
import permissions from './permissions.json';

export default {
  async fetch(request,env) {
    try {
      const denied=await gate(request,env); if(denied)return harden(denied);
      const url=new URL(request.url);
      if(url.pathname.startsWith('/api/')) {
        if(!['GET','HEAD'].includes(request.method) && !validOrigin(request))return harden(json({error:'Источник запроса запрещён'},403));
        if(!env.PLANS)return harden(json({error:'Хранилище недоступно'},503));
        return harden(await env.PLANS.get(env.PLANS.idFromName('dashboard-plans-v1')).fetch(request));
      }
      if(!['GET','HEAD'].includes(request.method))return harden(json({error:'Метод запрещён'},405));
      const target=fixedUpstream(url,'https://dashbord-partners1.pages.dev');
      return harden(await fetch(new Request(target,request),{redirect:'manual',cf:{cacheTtl:0,cacheEverything:false}}));
    } catch {return harden(json({error:'Сервис временно недоступен'},503));}
  }
};

// A single Durable Object serializes plan updates, sessions and audit records.
// KV is used only to import the pre-migration snapshot once, never for new writes.
export class PlanStore {
  constructor(state,env) {
    this.state=state;this.env=env;
    this.ready=state.blockConcurrencyWhile(async()=>{
      if(!await state.storage.get('plans')) {
        const raw=await env.SBERAUTO_DB.get('kam_plans');
        const legacy=raw?JSON.parse(raw):{};
        await state.storage.put('plans',{revision:0,kam_plans:legacy.kam_plans||{},partner_plans:legacy.partner_plans||{}});
      }
    });
  }
  async session(request) {
    const token=(request.headers.get('Cookie')||'').split(';').map(x=>x.trim()).find(x=>x.startsWith(COOKIE+'='))?.slice(COOKIE.length+1);
    if(!token || !/^[a-f0-9]{64}$/.test(token))return null;
    const key='session:'+await digest(token),s=await this.state.storage.get(key);
    if(!s || s.expires<=Date.now())return null;
    return {...s,key,user:PROFILES[s.id]};
  }
  async fetch(request) {
    await this.ready;
    try {
      const path=new URL(request.url).pathname;
      if(path==='/api/login' && request.method==='POST')return await this.login(request);
      const session=await this.session(request);
      if(path==='/api/session' && request.method==='GET')return json({user:session?.user||null});
      if(path==='/api/logout' && request.method==='POST') {
        if(session)await this.state.storage.delete(session.key);
        return json({success:true},200,{'Set-Cookie':`${COOKIE}=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0`});
      }
      if(path==='/api/kam-plans' && request.method==='GET')return json(await this.state.storage.get('plans'));
      if(!session?.user)return json({error:'Войдите в профиль для изменения планов'},401);
      if(path==='/api/kam-plans' && request.method==='POST')return await this.save(request,session.user);
      if(path==='/api/kam-plans/restore' && request.method==='POST' && session.user.isAdmin)return await this.restore(request,session.user);
      if(path==='/api/kam-plans/audit' && request.method==='GET' && session.user.isAdmin) {
        return json({entries:Array.from((await this.state.storage.list({prefix:'audit:',reverse:true,limit:100})).values())});
      }
      return json({error:'Недоступный маршрут или метод'},404);
    } catch(error) {return json({error:error.status?error.message:'Сервис временно недоступен'},error.status||503);}
  }
  async login(request) {
    const body=await readJson(request,2048);
    const ip=request.headers.get('CF-Connecting-IP')||'unknown';
    const account=typeof body?.id==='string' && Object.hasOwn(PROFILES,body.id)?body.id:'unknown';
    const bucket='rate:'+await digest(ip+':'+account);
    const blocked=await this.state.storage.transaction(async tx=>{
      const now=Date.now();let v=await tx.get(bucket);
      if(!v||v.expires<=now)v={count:0,expires:now+15*60*1000};
      v.count++;await tx.put(bucket,v);return v.count>10;
    });
    if(await this.state.storage.getAlarm()===null)await this.state.storage.setAlarm(Date.now()+24*60*60*1000);
    if(blocked)return json({error:'Слишком много попыток. Повторите через 15 минут.'},429,{'Retry-After':'900'});
    const credentials=JSON.parse(this.env.KAM_PASSWORD_HASHES||'{}');
    if(!body || typeof body.id!=='string' || typeof body.password!=='string' || !Object.hasOwn(PROFILES,body.id) || !equal(await digest(body.password),credentials[body.id]))return json({error:'Неверная учётная запись или пароль'},401);
    const token=Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');
    const old=await this.session(request);if(old)await this.state.storage.delete(old.key);
    await this.state.storage.put('session:'+await digest(token),{id:body.id,expires:Date.now()+8*60*60*1000});
    return json({user:PROFILES[body.id]},200,{'Set-Cookie':`${COOKIE}=${token}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=28800`});
  }
  async save(request,user) {
    const body=await readJson(request);
    const fail=(message,status=400)=>{throw Object.assign(new Error(message),{status});};
    if(!body || !Number.isSafeInteger(body.revision) || body.revision<0 || !body.changes || Object.keys(body).some(k=>!['revision','changes'].includes(k)))fail('Некорректный запрос');
    const entries=[];
    for(const [section,values] of Object.entries(body.changes)) {
      if(!['kam_plans','partner_plans'].includes(section)||!values||Array.isArray(values)||typeof values!=='object')fail('Некорректный раздел');
      for(const [key,value] of Object.entries(values)) {
        if(['__proto__','constructor','prototype'].includes(key)||key.length>300||!Number.isSafeInteger(value)||value<0||value>100000)fail('Некорректный план');
        const owner=section==='kam_plans'?(Object.values(PROFILES).find(p=>p.name===key)?.id):permissions[key];
        if(!user.isAdmin && owner!==user.id)fail('Нельзя изменять планы другого сотрудника',403);
        entries.push({section,key,value});
      }
    }
    if(!entries.length||entries.length>500)fail('Допустимо от 1 до 500 изменений');
    return this.state.storage.transaction(async tx=>{
      const current=await tx.get('plans');
      if(current.revision!==body.revision)return json({error:'Планы изменены другим пользователем. Обновите данные и повторите.',revision:current.revision},409);
      const changes=entries.map(({section,key,value})=>({section,key,before:current[section][key]??null,after:value}));
      const next=structuredClone(current);for(const e of entries)next[e.section][e.key]=e.value;
      if(new TextEncoder().encode(JSON.stringify(next)).byteLength>100000)return json({error:'Превышен объём хранилища планов'},413);
      next.revision++; const at=new Date().toISOString();
      await tx.put('snapshot:'+String(current.revision).padStart(10,'0'),current);
      await tx.put('audit:'+String(next.revision).padStart(10,'0'),{at,actor:user.id,revision:next.revision,changes});
      await tx.put('plans',next);
      return json({success:true,...next});
    });
  }
  async restore(request,user) {
    const body=await readJson(request,2048);
    if(!Number.isSafeInteger(body?.revision)||!Number.isSafeInteger(body?.snapshot)||body.snapshot<0)return json({error:'Некорректная версия'},400);
    return this.state.storage.transaction(async tx=>{
      const current=await tx.get('plans');
      if(current.revision!==body.revision)return json({error:'Обновите текущие планы перед восстановлением'},409);
      const snapshot=await tx.get('snapshot:'+String(body.snapshot).padStart(10,'0'));
      if(!snapshot)return json({error:'Снимок не найден'},404);
      const next={...snapshot,revision:current.revision+1};
      await tx.put('snapshot:'+String(current.revision).padStart(10,'0'),current);
      await tx.put('audit:'+String(next.revision).padStart(10,'0'),{at:new Date().toISOString(),actor:user.id,revision:next.revision,restoredFrom:body.snapshot});
      await tx.put('plans',next);return json({success:true,...next});
    });
  }
  async alarm() {
    for(const prefix of ['rate:','session:']) {
      const values=await this.state.storage.list({prefix});
      for(const [key,value] of values)if(value.expires<=Date.now())await this.state.storage.delete(key);
    }
  }
}
