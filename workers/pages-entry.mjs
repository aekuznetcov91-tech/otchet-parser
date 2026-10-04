export default {
  async fetch(request,env) {
    try {
      const denied=await gate(request,env);if(denied)return harden(denied);
      const url=new URL(request.url);
      if(url.pathname.startsWith('/api/')) {
        // Same-origin browser API, no permissive CORS and no API secrets in JS.
        const target=fixedUpstream(url,'https://dashbord-partners.beckelaguas723.workers.dev');
        return harden(await fetch(new Request(target,request),{redirect:'manual'}));
      }
      if(!['GET','HEAD'].includes(request.method))return harden(json({error:'Метод запрещён'},405));
      return harden(await env.ASSETS.fetch(request));
    } catch {return harden(json({error:'Доступ временно закрыт'},503));}
  }
};
