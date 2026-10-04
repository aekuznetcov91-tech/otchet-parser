const fs=require('fs'),vm=require('vm');
const {join}=require('path');const root=join(__dirname,'..');
const read=p=>fs.readFileSync(join(root,p),'utf8');
const payload=JSON.parse(read('site/data.json'));
const ctx=vm.createContext({window:{dataPayload:payload},setTimeout:()=>{},localStorage:{getItem:()=>null,setItem:()=>{}},sessionStorage:{getItem:()=>null,setItem:()=>{}},document:{getElementById:()=>null,querySelectorAll:()=>[]}});
vm.runInContext(read('site/js/utils.js'),ctx);vm.runInContext(read('site/js/kam-dashboard.js'),ctx);
const names={'Алексей Чихарев':'chikharev','Андрей Кузнецов':'kuznetsov','Светлана Дариенко':'darienko','Валерия Солдатова':'soldatova','Евгения Добролюбова':'dobrolyubova'};
const owners=new Map();function add(key,id){if(!key||!id)return;if(!owners.has(key))owners.set(key,new Set());owners.get(key).add(id);}
// Use current portfolio and actual split keys; unknown/ambiguous keys are admin-only.
const month=payload.sys_db_partners.map(r=>(r.Month||'').replace("'",'')).filter(x=>/^2026-\d{2}$/.test(x)).sort().at(-1);
const agg=ctx.getKamAggregatedData({mode:'month',month});
for(const p of agg.partners)add(p.key,names[p.kam]);
for(const p of payload.partners_registry||[]) {
  const id=names[p.kam];for(const key of [String(p.partner_id),'ID_'+p.partner_id,p.canonical_name,p.canonical_name?.toLowerCase()])add(key,id);
}
const permissions=Object.fromEntries([...owners].filter(([,ids])=>ids.size===1).sort(([a],[b])=>a.localeCompare(b)).map(([key,ids])=>[key,[...ids][0]]));
const common=read('workers/security.mjs').replace(/^export /gm,'');
const outputs={'workers/permissions.json':JSON.stringify(permissions,null,2)+'\n','site/_worker.js':common+'\n'+read('workers/pages-entry.mjs'),'site/_routes.json':JSON.stringify({version:1,include:['/*'],exclude:[]})+'\n'};
for(const [path,value]of Object.entries(outputs)) {
  if(process.argv.includes('--check')){if(read(path)!==value)throw new Error('Security generated file out of sync: '+path);}
  else fs.writeFileSync(join(root,path),value);
}
console.log('Security routes and permissions:',Object.keys(permissions).length,'keys, portfolio',month);
