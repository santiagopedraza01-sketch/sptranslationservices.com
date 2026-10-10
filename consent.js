/* SP Translations — cookie consent.
   Stores the visitor's choice in localStorage ("sp-consent") for 12 months and exposes
   window.SPConsent = { allowed(category), open(), onChange(fn) }.
   Categories: necessary (always on), preferences, analytics, marketing.
   To add a tool that needs consent later (e.g. Google Analytics), include it as
     <script type="text/plain" data-consent="analytics" src="…"></script>
   and it will only run once the visitor allows that category. */
(function(){
  'use strict';
  var KEY='sp-consent', VERSION=1, MAX_AGE=365*24*60*60*1000;
  var ES=document.documentElement.lang==='es';
  var POLICY=ES?'politica-de-cookies.html':'cookies.html';
  var T=ES?{
    title:'Valoramos tu privacidad',
    body:'Usamos cookies y tecnologías similares para que el sitio funcione, recordar tus preferencias y, solo si lo permites, analizar el tráfico y mostrar contenido relevante. Al hacer clic en «Aceptar todo», das tu consentimiento para el uso de cookies.',
    policy:'Política de cookies', customize:'Personalizar', reject:'Rechazar todo', accept:'Aceptar todo',
    panelTitle:'Preferencias de cookies', panelIntro:'Elige qué cookies permites. Puedes cambiar tu elección en cualquier momento desde «Configuración de cookies», al pie de cada página.',
    save:'Guardar preferencias', close:'Cerrar', always:'Siempre activas',
    cats:{
      necessary:['Necesarias','Imprescindibles para que el sitio funcione y para recordar tu elección de cookies. No se pueden desactivar.'],
      preferences:['Preferencias','Recuerdan opciones como la moneda elegida en las tarifas o que cerraste la tarjeta de WhatsApp.'],
      analytics:['Analíticas','Nos ayudarían a entender cómo se usa el sitio. Actualmente no usamos herramientas analíticas; si las añadimos, solo funcionarán con tu permiso.'],
      marketing:['Marketing','Permitirían mostrar contenido o anuncios personalizados. Actualmente no usamos cookies de marketing; si las añadimos, solo funcionarán con tu permiso.']
    }
  }:{
    title:'We value your privacy',
    body:'We use cookies and similar technologies to make this site work, remember your preferences and, only with your permission, analyse traffic and show relevant content. By clicking “Accept all”, you consent to our use of cookies.',
    policy:'Cookie policy', customize:'Customize', reject:'Reject all', accept:'Accept all',
    panelTitle:'Cookie preferences', panelIntro:'Choose which cookies you allow. You can change your choice at any time from “Cookie settings” at the bottom of every page.',
    save:'Save preferences', close:'Close', always:'Always on',
    cats:{
      necessary:['Necessary','Required for the site to work and to remember your cookie choice. These cannot be switched off.'],
      preferences:['Preferences','Remember choices such as the currency you picked in the fees section, or that you closed the WhatsApp card.'],
      analytics:['Analytics','Would help us understand how the site is used. We do not currently use any analytics tools; if we add them, they will only run with your permission.'],
      marketing:['Marketing','Would allow personalised content or ads. We do not currently use marketing cookies; if we add them, they will only run with your permission.']
    }
  };
  var CATS=['necessary','preferences','analytics','marketing'];
  var listeners=[], state=read();

  function read(){
    try{
      var v=JSON.parse(localStorage.getItem(KEY)||'null');
      if(v&&v.v===VERSION&&Date.now()-v.ts<MAX_AGE) return v;
    }catch(e){}
    return null;
  }
  function write(choice){
    state={v:VERSION,ts:Date.now(),necessary:true,preferences:!!choice.preferences,analytics:!!choice.analytics,marketing:!!choice.marketing};
    try{ localStorage.setItem(KEY,JSON.stringify(state)) }catch(e){}
    if(!state.preferences){ try{ localStorage.removeItem('fx-currency'); localStorage.removeItem('wa-card-dismissed'); }catch(e){} }
    activate(); listeners.forEach(function(fn){ try{fn(state)}catch(e){} });
  }
  function allowed(cat){ return cat==='necessary' || !!(state&&state[cat]); }

  /* Run any <script type="text/plain" data-consent="…"> the visitor has now allowed */
  function activate(){
    var list=document.querySelectorAll('script[type="text/plain"][data-consent]');
    Array.prototype.forEach.call(list,function(old){
      if(!allowed(old.getAttribute('data-consent'))) return;
      var s=document.createElement('script');
      Array.prototype.forEach.call(old.attributes,function(a){ if(a.name!=='type'&&a.name!=='data-consent') s.setAttribute(a.name,a.value) });
      if(!old.src) s.text=old.text;
      old.parentNode.replaceChild(s,old);
    });
  }

  var banner, panel, lastFocus;
  function el(html){ var d=document.createElement('div'); d.innerHTML=html.trim(); return d.firstChild; }
  function buildBanner(){
    banner=el('<div class="cc" role="dialog" aria-live="polite" aria-labelledby="ccTitle" aria-describedby="ccBody">'+
      '<h2 class="cc__title" id="ccTitle">'+T.title+'</h2>'+
      '<p class="cc__body" id="ccBody">'+T.body+' <a href="'+POLICY+'">'+T.policy+'</a></p>'+
      '<div class="cc__btns">'+
        '<button type="button" class="cc__btn" data-cc="customize">'+T.customize+'</button>'+
        '<button type="button" class="cc__btn" data-cc="reject">'+T.reject+'</button>'+
        '<button type="button" class="cc__btn cc__btn--solid" data-cc="accept">'+T.accept+'</button>'+
      '</div></div>');
    banner.addEventListener('click',function(e){
      var a=e.target.getAttribute&&e.target.getAttribute('data-cc'); if(!a) return;
      if(a==='accept'){ write({preferences:1,analytics:1,marketing:1}); hideBanner(); }
      if(a==='reject'){ write({}); hideBanner(); }
      if(a==='customize'){ openPanel(); }
    });
    document.body.appendChild(banner);
  }
  function hideBanner(){ if(banner){ banner.remove(); banner=null; } }

  function buildPanel(){
    var rows=CATS.map(function(c){
      var on=c==='necessary'||allowed(c), lock=c==='necessary';
      return '<div class="cc-row"><div><h3>'+T.cats[c][0]+'</h3><p>'+T.cats[c][1]+'</p></div>'+
        (lock?'<span class="cc-always">'+T.always+'</span>':
        '<label class="cc-switch"><input type="checkbox" data-cat="'+c+'"'+(on?' checked':'')+'><span aria-hidden="true"></span><b class="cc-sr">'+T.cats[c][0]+'</b></label>')+'</div>';
    }).join('');
    panel=el('<div class="cc-modal" role="dialog" aria-modal="true" aria-labelledby="ccPanelTitle">'+
      '<div class="cc-modal__box" tabindex="-1">'+
        '<button type="button" class="cc-modal__x" data-cc="close" aria-label="'+T.close+'">×</button>'+
        '<h2 id="ccPanelTitle">'+T.panelTitle+'</h2><p class="cc-modal__intro">'+T.panelIntro+' <a href="'+POLICY+'">'+T.policy+'</a></p>'+
        rows+
        '<div class="cc__btns">'+
          '<button type="button" class="cc__btn" data-cc="reject">'+T.reject+'</button>'+
          '<button type="button" class="cc__btn" data-cc="save">'+T.save+'</button>'+
          '<button type="button" class="cc__btn cc__btn--solid" data-cc="accept">'+T.accept+'</button>'+
        '</div></div></div>');
    panel.addEventListener('click',function(e){
      if(e.target===panel){ closePanel(); return; }
      var a=e.target.getAttribute&&e.target.getAttribute('data-cc'); if(!a) return;
      if(a==='close'){ closePanel(); return; }
      if(a==='accept') write({preferences:1,analytics:1,marketing:1});
      if(a==='reject') write({});
      if(a==='save'){
        var c={}; Array.prototype.forEach.call(panel.querySelectorAll('input[data-cat]'),function(i){ c[i.getAttribute('data-cat')]=i.checked });
        write(c);
      }
      hideBanner(); closePanel();
    });
    panel.addEventListener('keydown',function(e){
      if(e.key==='Escape'){ closePanel(); return; }
      if(e.key!=='Tab') return;
      var f=panel.querySelectorAll('button,input,a[href]'), first=f[0], last=f[f.length-1];
      if(e.shiftKey&&document.activeElement===first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey&&document.activeElement===last){ e.preventDefault(); first.focus(); }
    });
    document.body.appendChild(panel);
  }
  function openPanel(){
    lastFocus=document.activeElement;
    if(panel) panel.remove();
    buildPanel(); document.documentElement.classList.add('cc-lock');
    panel.querySelector('.cc-modal__box').focus();
  }
  function closePanel(){
    if(!panel) return; panel.remove(); panel=null; document.documentElement.classList.remove('cc-lock');
    if(lastFocus&&lastFocus.focus) lastFocus.focus();
  }

  window.SPConsent={ allowed:allowed, open:openPanel, onChange:function(fn){listeners.push(fn)}, choice:function(){return state} };

  function init(){
    activate();
    if(!state) buildBanner();
    document.addEventListener('click',function(e){
      var t=e.target.closest&&e.target.closest('[data-consent-open]');
      if(t){ e.preventDefault(); openPanel(); }
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
