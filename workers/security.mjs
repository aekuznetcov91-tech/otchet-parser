// Server-only primitives; credentials are Cloudflare secrets, never static assets.
export const COOKIE = '__Host-dashboard_session';
export const PROFILES = {
  admin: {id:'admin',name:'Руководитель',role:'Руководитель / Администратор',isAdmin:true},
  chikharev: {id:'chikharev',name:'Алексей Чихарев',role:'Ведущий КАМ',isAdmin:false},
  kuznetsov: {id:'kuznetsov',name:'Андрей Кузнецов',role:'Ведущий КАМ',isAdmin:false},
  darienko: {id:'darienko',name:'Светлана Дариенко',role:'КАМ',isAdmin:false},
  soldatova: {id:'soldatova',name:'Валерия Солдатова',role:'КАМ',isAdmin:false},
  dobrolyubova: {id:'dobrolyubova',name:'Евгения Добролюбова',role:'КАМ',isAdmin:false}
};
export async function digest(value) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value))), b=>b.toString(16).padStart(2,'0')).join('');
}
export function equal(a,b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff=0; for(let i=0;i<a.length;i++) diff |= a.charCodeAt(i)^b.charCodeAt(i); return diff===0;
}
export function json(value,status=200,headers={}) {return new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json; charset=utf-8',...headers}});}
export function harden(response) {
  const r=new Response(response.body,response); const h=r.headers;
  h.delete('Access-Control-Allow-Origin'); h.delete('Access-Control-Allow-Credentials');
  h.set('Cache-Control','private, no-store, max-age=0'); h.set('Pragma','no-cache');
  h.set('X-Content-Type-Options','nosniff'); h.set('X-Frame-Options','DENY');
  h.set('Referrer-Policy','no-referrer'); h.set('Permissions-Policy','camera=(), microphone=(), geolocation=()');
  h.set('Strict-Transport-Security','max-age=31536000');
  h.set('Content-Security-Policy',"base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'");
  h.set('Content-Security-Policy-Report-Only',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'");
  return r;
}
export async function gate(request,env) {
  if (!env.AUTH_DIGEST) return json({error:'Доступ временно закрыт'},503);
  const header=request.headers.get('Authorization') || '';
  if(!header.startsWith('Basic ') || !equal(await digest(header),env.AUTH_DIGEST)) {
    return new Response('Введите новый логин и пароль доступа к дашборду.',{status:401,headers:{'WWW-Authenticate':'Basic realm="B2C Dashboard", charset="UTF-8"'}});
  }
  return null;
}
export function validOrigin(request) {
  const origin=request.headers.get('Origin');
  if(!origin || request.headers.get('X-Dashboard-Request')!=='1') return false;
  try {
    const u=new URL(origin);
    return u.protocol==='https:' && u.port==='' && (u.hostname==='dashbord-partners.beckelaguas723.workers.dev' || u.hostname==='dashbord-partners1.pages.dev' || /^[a-z0-9-]+\.dashbord-partners1\.pages\.dev$/.test(u.hostname));
  } catch {return false;}
}
export async function readJson(request,limit=65536) {
  if(!(request.headers.get('Content-Type') || '').toLowerCase().startsWith('application/json')) throw Object.assign(new Error('Ожидается JSON'),{status:415});
  if(Number(request.headers.get('Content-Length'))>limit) throw Object.assign(new Error('Запрос слишком большой'),{status:413});
  const reader=request.body?.getReader(); let size=0,parts=[];
  if(reader) for(;;) {const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>limit){await reader.cancel();throw Object.assign(new Error('Запрос слишком большой'),{status:413});}parts.push(value);}
  const bytes=new Uint8Array(size);let offset=0;for(const p of parts){bytes.set(p,offset);offset+=p.length;}
  try {return JSON.parse(new TextDecoder().decode(bytes));} catch {throw Object.assign(new Error('Некорректный JSON'),{status:400});}
}

export function fixedUpstream(url, origin) {
  // Assign path/search separately: a path starting // must never select a host.
  const target=new URL(origin);target.pathname=url.pathname;target.search=url.search;return target;
}
