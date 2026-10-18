/* SP Translations — site search.
   The magnifier in the header ([data-search-open]), "/" or Ctrl/Cmd+K opens a search panel.
   Results come from search-index.json (rebuild it with: python3 _tools/build_search_index.py).
   Pages in the visitor's language are listed first. /?q=apostille opens the panel pre-filled. */
(function(){
  'use strict';
  var ES=document.documentElement.lang==='es', LANG=ES?'es':'en';
  var T=ES?{
    label:'Buscar en el sitio', placeholder:'Buscar: apostilla, iGaming, precios…', close:'Cerrar',
    hint:'Escribe al menos 2 letras.', none:'No hay resultados para', other:'En inglés', tips:'Prueba con',
    sugg:['traducción certificada','apostilla','iGaming','precios','residencia en Malta'], error:'No se pudo cargar la búsqueda. Inténtalo de nuevo.'
  }:{
    label:'Search the site', placeholder:'Search: apostille, iGaming, prices…', close:'Close',
    hint:'Type at least 2 letters.', none:'No results for', other:'In Spanish', tips:'Try',
    sugg:['certified translation','apostille','iGaming','prices','Malta residence'], error:'Search could not be loaded. Please try again.'
  };
  var index=null, loading=null, panel, input, list, status, lastFocus, active=-1, items=[];

  function norm(s){ return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
  function esc(s){ return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  function load(){
    if(index) return Promise.resolve(index);
    if(loading) return loading;
    loading=fetch('/search-index.json?v=20261018c').then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(d){
        index=d.map(function(e){ e._t=norm(e.title); e._h=norm(e.heading)+' '+norm(e.sub); e._d=norm(e.description); e._x=norm(e.text); return e; });
        return index;
      }).catch(function(err){ loading=null; throw err; });
    return loading;
  }

  /* A few words people use for the same thing, and a plural-stripping so "prices" also finds "pricing" */
  var SYN={price:['fee','cost','rate'],cost:['price','fee'],fee:['price','cost','rate'],rate:['fee','price'],
           precio:['tarifa','coste','costo'],tarifa:['precio','coste'],coste:['precio','tarifa'],costo:['precio','tarifa'],
           quote:['quotation'],cotizacion:['presupuesto'],presupuesto:['cotizacion']};
  function variants(t){
    var v=[t], base=t.replace(/(es|s)$/,'');
    if(t.length>4&&base!==t) v.push(base);
    (SYN[base]||SYN[t]||[]).forEach(function(x){ v.push(x); });
    return v;
  }
  function count(hay,t){ var n=0, p=hay.indexOf(t); while(p>-1&&n<5){ n++; p=hay.indexOf(t,p+t.length); } return n; }
  function score(e,terms){
    var s=0;
    for(var i=0;i<terms.length;i++){
      var vs=variants(terms[i]), best=0;
      for(var j=0;j<vs.length;j++){
        var t=vs[j], w=j===0?1:.6, hit=0;              /* the word as typed beats its variants */
        if(e._t.indexOf(t)>-1) hit+=10;
        if(e._h.indexOf(t)>-1) hit+=8;
        if(e._d.indexOf(t)>-1) hit+=4;
        hit+=count(e._x,t);
        best=Math.max(best,hit*w);
      }
      if(!best) return 0;                    /* every word must appear somewhere */
      s+=best;
    }
    if(e.lang===LANG) s+=6;
    if(!e.section) s+=2;                      /* whole page beats one of its sections */
    return s;
  }

  function snippet(e,terms){
    var x=e.text, nx=e._x, at=-1, len=0;
    for(var i=0;i<terms.length;i++){ var vs=variants(terms[i]); for(var j=0;j<vs.length;j++){ var p=nx.indexOf(vs[j]); if(p>-1&&(at<0||p<at)){ at=p; len=vs[j].length; } } }
    if(at<0) return esc(e.description||x.slice(0,150));
    var a=Math.max(0,at-60), b=Math.min(x.length,at+110);
    var out=(a>0?'…':'')+esc(x.slice(a,at))+'<mark>'+esc(x.slice(at,at+len))+'</mark>'+esc(x.slice(at+len,b))+(b<x.length?'…':'');
    return out;
  }

  function run(){
    var q=input.value.trim(), terms=norm(q).split(/\s+/).filter(function(t){return t.length>1;});
    active=-1;
    if(!terms.length){ list.innerHTML=''; items=[]; status.innerHTML=q?T.hint:suggestions(); bindSugg(); return; }
    load().then(function(idx){
      var res=idx.map(function(e){ return {e:e,s:score(e,terms)}; }).filter(function(r){return r.s>0;})
        .sort(function(a,b){ return b.s-a.s; });
      var perPage={}, mine=[], other=[];
      res.forEach(function(r){
        var k=r.e.page; perPage[k]=(perPage[k]||0)+1; if(perPage[k]>2) return;   /* at most 2 hits per page */
        (r.e.lang===LANG?mine:other).push(r.e);
      });
      mine=mine.slice(0,12); other=other.slice(0,4);
      if(!mine.length&&!other.length){ list.innerHTML=''; items=[]; status.innerHTML=esc(T.none)+' “'+esc(q)+'”. '+suggestions(); bindSugg(); return; }
      status.textContent='';
      var html=mine.map(function(e){return row(e,terms);}).join('');
      if(other.length) html+='<li class="srch__sep" role="presentation">'+T.other+'</li>'+other.map(function(e){return row(e,terms);}).join('');
      list.innerHTML=html; items=[].slice.call(list.querySelectorAll('a'));
    }).catch(function(){ status.textContent=T.error; });
  }
  function row(e,terms){
    var crumb=e.section&&e.heading?esc(e.title)+' <span aria-hidden="true">›</span> '+esc(e.heading):esc(e.title);
    return '<li><a href="'+esc(e.url)+'"'+(e.lang!==LANG?' hreflang="'+e.lang+'" lang="'+e.lang+'"':'')+'><b>'+crumb+'</b><span>'+snippet(e,terms)+'</span><em>'+esc(e.url.replace(/^https?:\/\/[^/]+/,'')||'/')+'</em></a></li>';
  }
  function suggestions(){
    return T.tips+': '+T.sugg.map(function(s){return '<button type="button" class="srch__chip">'+esc(s)+'</button>';}).join(' ');
  }
  function bindSugg(){
    [].forEach.call(status.querySelectorAll('.srch__chip'),function(b){ b.addEventListener('click',function(){ input.value=b.textContent; run(); input.focus(); }); });
  }

  function build(){
    panel=document.createElement('div');
    panel.className='srch'; panel.setAttribute('role','dialog'); panel.setAttribute('aria-modal','true'); panel.setAttribute('aria-label',T.label);
    panel.innerHTML='<div class="srch__box">'+
      '<form class="srch__form" role="search" action="#" onsubmit="return false">'+
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg>'+
        '<input type="search" class="srch__input" placeholder="'+esc(T.placeholder)+'" aria-label="'+esc(T.label)+'" autocomplete="off" spellcheck="false" enterkeyhint="search">'+
        '<button type="button" class="srch__x" aria-label="'+T.close+'">Esc</button>'+
      '</form>'+
      '<p class="srch__status" aria-live="polite"></p>'+
      '<ul class="srch__list" role="list"></ul>'+
    '</div>';
    document.body.appendChild(panel);
    input=panel.querySelector('.srch__input'); list=panel.querySelector('.srch__list'); status=panel.querySelector('.srch__status');
    var timer; input.addEventListener('input',function(){ clearTimeout(timer); timer=setTimeout(run,120); });
    panel.addEventListener('click',function(e){ if(e.target===panel||e.target.closest('.srch__x')) close(); });
    list.addEventListener('click',function(e){ if(e.target.closest('a')) close(true); });
    panel.addEventListener('keydown',function(e){
      if(e.key==='Escape'){ e.preventDefault(); close(); return; }
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){
        if(!items.length) return; e.preventDefault();
        active=e.key==='ArrowDown'?Math.min(items.length-1,active+1):Math.max(-1,active-1);
        if(active<0) input.focus(); else items[active].focus();
      }
      if(e.key==='Enter'&&document.activeElement===input&&items.length){ e.preventDefault(); items[0].click(); }
      if(e.key==='Tab'){
        var f=[].slice.call(panel.querySelectorAll('input,button,a[href]')), first=f[0], last=f[f.length-1];
        if(e.shiftKey&&document.activeElement===first){ e.preventDefault(); last.focus(); }
        else if(!e.shiftKey&&document.activeElement===last){ e.preventDefault(); first.focus(); }
      }
    });
  }
  function open(q){
    if(!panel) build();
    lastFocus=document.activeElement;
    panel.classList.add('is-open'); document.documentElement.classList.add('srch-lock');
    if(typeof q==='string') input.value=q;
    run(); load().catch(function(){});
    requestAnimationFrame(function(){ input.focus(); input.select(); });
  }
  function close(navigating){
    if(!panel||!panel.classList.contains('is-open')) return;
    panel.classList.remove('is-open'); document.documentElement.classList.remove('srch-lock');
    if(!navigating&&lastFocus&&lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click',function(e){
    var t=e.target.closest&&e.target.closest('[data-search-open]');
    if(t){ e.preventDefault(); open(); }
  });
  document.addEventListener('keydown',function(e){
    var typing=/^(INPUT|TEXTAREA|SELECT)$/.test((e.target||{}).tagName||'')||(e.target&&e.target.isContentEditable);
    if((e.key==='k'||e.key==='K')&&(e.metaKey||e.ctrlKey)){ e.preventDefault(); open(); }
    else if(e.key==='/'&&!typing&&!e.metaKey&&!e.ctrlKey){ e.preventDefault(); open(); }
  });
  var q=new URLSearchParams(location.search).get('q');
  if(q){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){open(q);}); else open(q); }
})();
