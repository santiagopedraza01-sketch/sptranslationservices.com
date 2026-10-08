/* SP Translations — shared behaviour for every page, both languages. */
(function(){
  'use strict';

  /* Interface strings — chosen from the document language, so one script serves both */
  var ES = document.documentElement.lang === 'es';
  var T = ES ? {
    open:'Abrir menú', close:'Cerrar menú', sending:'Enviando…',
    submit:'Solicitar presupuesto',
    failed:'No ha sido posible transmitir su solicitud. Escriba directamente a ',
    failedEnd:' y recibirá respuesta en breve.',
    noEndpoint:'[Formulario de presupuesto] Sin endpoint configurado: sustituya YOUR_FORM_ID en el action del formulario. Datos recogidos:'
  } : {
    open:'Open menu', close:'Close menu', sending:'Sending…',
    submit:'Request a quote',
    failed:'Your request could not be transmitted. Please email ',
    failedEnd:' directly and you will have a reply shortly.',
    noEndpoint:'[Quotation form] No endpoint configured — replace YOUR_FORM_ID in the form action. Captured:'
  };
  var $=function(s,c){return (c||document).querySelector(s)},
      $$=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};

  var yearEl=$('#year'); if(yearEl) yearEl.textContent=new Date().getFullYear();

  /* ── Masthead state + mobile dock ── */
  var masthead=$('#masthead'), dock=$('#dock');
  function onScroll(){
    masthead.classList.toggle('settled', window.scrollY>20);
    if(dock) dock.classList.toggle('on', window.scrollY>640);
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();

  /* ── Drawer ── */
  var toggle=$('#toggle');
  function closeDrawer(){
    document.body.classList.remove('menu-open');
    toggle.setAttribute('aria-expanded','false');
    toggle.setAttribute('aria-label',T.open);
    document.documentElement.style.overflow='';
  }
  toggle.addEventListener('click',function(){
    var open=document.body.classList.toggle('menu-open');
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',open?T.close:T.open);
    document.documentElement.style.overflow=open?'hidden':'';
  });
  $$('#drawer a').forEach(function(a){a.addEventListener('click',closeDrawer)});
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&document.body.classList.contains('menu-open')) closeDrawer();
  });

  /* ── Reveal: opacity and 12px only, lightly staggered ── */
  if('IntersectionObserver' in window){
    var reveal=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(!en.isIntersecting) return;
        var el=en.target, peers=el.parentElement?$$('.rise',el.parentElement):[], i=peers.indexOf(el);
        el.style.transitionDelay=Math.min(Math.max(i,0)*70,280)+'ms';
        el.classList.add('shown');
        reveal.unobserve(el);
      });
    },{threshold:.1,rootMargin:'0px 0px -60px 0px'});
    $$('.rise').forEach(function(el){reveal.observe(el)});
  }else{
    $$('.rise').forEach(function(el){el.classList.add('shown')});
  }

  /* ── Current section in the masthead ── */
  var links=$$('.nav a').filter(function(a){return a.getAttribute('href').charAt(0)==='#'}),
      targets=links.map(function(a){return document.querySelector(a.getAttribute('href'))}).filter(Boolean);
  if('IntersectionObserver' in window && targets.length){
    var spy=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(!en.isIntersecting) return;
        links.forEach(function(a){a.classList.toggle('current',a.getAttribute('href')==='#'+en.target.id)});
      });
    },{rootMargin:'-45% 0px -50% 0px'});
    targets.forEach(function(t){spy.observe(t)});
  }

  /* ── Language exchange ── */
  var source=$('#source'), target=$('#target'), exchange=$('#exchange');
  if(exchange){
  exchange.addEventListener('click',function(){
    var held=source.value; source.value=target.value; target.value=held;
    exchange.classList.add('turn');
    setTimeout(function(){exchange.classList.remove('turn')},420);
  });
  }

  /* ── Service-specific fields: show the group the chosen service needs,
        and disable the rest so hidden fields are never submitted ── */
  var service=$('#service'), groups=$$('.group[data-group]');
  function showGroup(){
    var opt=service&&service.options[service.selectedIndex],
        want=opt?opt.getAttribute('data-group'):null;
    groups.forEach(function(g){
      var on=g.getAttribute('data-group')===want;
      g.hidden=!on;
      $$('input,select,textarea',g).forEach(function(el){el.disabled=!on});
    });
    var mode=$('#mode'), preset=opt&&opt.getAttribute('data-mode');
    if(mode&&preset) mode.value=preset;
  }
  if(service&&groups.length){
    service.addEventListener('change',showGroup);
    showGroup();
  }

  /* ── Attachments ── */
  var deposit=$('#deposit'), files=$('#files'), manifest=$('#manifest'),
      LIMIT=10*1024*1024; /* 10 MB per file — match to your form handler's limit */
  function size(b){
    if(b<1024) return b+' B';
    if(b<1048576) return Math.round(b/1024)+' KB';
    return (b/1048576).toFixed(1)+' MB';
  }
  function listFiles(){
    manifest.innerHTML='';
    Array.prototype.forEach.call(files.files,function(f){
      var row=document.createElement('div');
      row.className='manifest__item';
      row.innerHTML='<i aria-hidden="true"></i><b></b><small></small>';
      $('b',row).textContent=f.name;
      var big=f.size>LIMIT;
      $('small',row).textContent = big ? size(f.size)+' — exceeds limit' : size(f.size);
      if(big) $('small',row).style.color='#9E4B2F';
      manifest.appendChild(row);
    });
  }
  if(files){
  files.addEventListener('change',listFiles);
  ['dragenter','dragover'].forEach(function(ev){
    deposit.addEventListener(ev,function(e){e.preventDefault();deposit.classList.add('over')});
  });
  ['dragleave','drop'].forEach(function(ev){
    deposit.addEventListener(ev,function(e){e.preventDefault();deposit.classList.remove('over')});
  });
  deposit.addEventListener('drop',function(e){
    if(e.dataTransfer&&e.dataTransfer.files.length){files.files=e.dataTransfer.files;listFiles()}
  });
  }

  /* ── Validation and submission ── */
  var form=$('#docket'), received=$('#received'), send=$('#send'), consent=$('#consent'), consentAlert=$('#consentAlert');
  if(form){

  function flag(input,bad){
    var field=input.closest('.f');
    if(field) field.classList.toggle('invalid',bad);
  }
  function emailOk(v){return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim())}

  function check(){
    var ok=true, first=null;
    [['#name',function(v){return v.trim().length>1}],
     ['#email',emailOk],
     ['#service',function(v){return v!==''}],
     ['#source',function(v){return v.trim()!==''}],
     ['#target',function(v){return v.trim()!==''}]].forEach(function(rule){
      var el=$(rule[0]), good=rule[1](el.value);
      flag(el,!good);
      if(!good){ok=false;first=first||el}
    });
    consentAlert.style.display=consent.checked?'none':'block';
    if(!consent.checked){ok=false;first=first||consent}
    if(first){first.focus();first.scrollIntoView({behavior:'smooth',block:'center'})}
    return ok;
  }

  ['#name','#email','#service','#source','#target'].forEach(function(sel){
    var el=$(sel);
    el.addEventListener('input',function(){flag(el,false)});
    el.addEventListener('change',function(){flag(el,false)});
  });
  consent.addEventListener('change',function(){consentAlert.style.display=this.checked?'none':'block'});

  function confirmReceipt(){
    form.style.display='none';
    received.classList.add('on');
    received.scrollIntoView({behavior:'smooth',block:'center'});
  }

  form.addEventListener('submit',function(e){
    e.preventDefault();
    if(!check()) return;

    var endpoint=form.getAttribute('action')||'',
        live=endpoint.indexOf('YOUR_FORM_ID')===-1&&/^https?:\/\//.test(endpoint);

    if(!live){
      console.warn(T.noEndpoint,
        Object.fromEntries(new FormData(form).entries()));
      confirmReceipt();
      return;
    }

    send.disabled=true;
    send.textContent=T.sending;

    fetch(endpoint,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}})
      .then(function(r){ if(!r.ok) throw new Error('Request failed: '+r.status); confirmReceipt(); })
      .catch(function(err){
        console.error(err);
        send.disabled=false;
        send.innerHTML=T.submit+'<span class="btn__arrow" aria-hidden="true"></span>';
        $('#notice').innerHTML='<p style="border:1px solid #C9A08C;background:#FBF3EF;color:#8C3F26;'+
          'padding:14px 16px;font-size:.88rem;line-height:1.6;margin-bottom:22px;border-radius:2px">'+
          T.failed+
          '<a href="mailto:santiagopedraza01@gmail.com" style="color:inherit;text-decoration:underline">santiagopedraza01@gmail.com</a>'+
          T.failedEnd+'</p>';
      });
  });


  }

  /* ── WhatsApp card: opens once on a first visit, then stays dismissed ── */
  var wa=$('#waCard'), waDismiss=$('#waDismiss'), WA_KEY='wa-card-dismissed';
  if(wa){
  function stored(key){ try{ return localStorage.getItem(key) }catch(e){ return null } }
  function store(key,val){ try{ localStorage.setItem(key,val) }catch(e){} }
  function closeCard(){ wa.classList.remove('open'); store(WA_KEY,'1') }
  if(!stored(WA_KEY)){
    setTimeout(function(){
      /* hold back while the visitor is reading the quotation form */
      if(!document.body.classList.contains('menu-open')) wa.classList.add('open');
    },5200);
  }
  if(waDismiss) waDismiss.addEventListener('click',closeCard);
  var waLink=$('#waCardLink'); if(waLink) waLink.addEventListener('click',closeCard);

  }


  /* ══════════════════════════════════════════════════════════════════════
     CURRENCY
     BASE is the currency your fee figures are written in — the data-amount
     values in the HTML. RATES are units of each currency per 1 BASE.

     ⚠ THESE RATES ARE DISPLAY ONLY AND GO STALE. Review them monthly, or
     whenever a rate has moved materially. ARS in particular moves fast.
     Nothing here binds you: the invoice is issued at the figure agreed in
     the written quotation, in the currency the client requests.
     ══════════════════════════════════════════════════════════════════════ */
  var FX = {
    base: 'EUR',
    rates: {
      EUR: 1,        /* Malta, Spain, eurozone */
      USD: 1.08,     /* United States, Ecuador, Panama, El Salvador */
      GBP: 0.85,     /* United Kingdom */
      MXN: 19.80,    /* Mexico */
      COP: 4450,     /* Colombia */
      CLP: 1030,     /* Chile */
      PEN: 4.05,     /* Peru */
      ARS: 1180,     /* Argentina — review often */
      BRL: 6.05      /* Brazil */
    }
  };

  /* Where the visitor appears to be. The device time zone is a better signal
     than the browser language, which is often left on a default. */
  var ZONE_CURRENCY = {
    'America/Bogota':'COP',
    'America/Mexico_City':'MXN','America/Tijuana':'MXN','America/Monterrey':'MXN',
    'America/Cancun':'MXN','America/Merida':'MXN','America/Chihuahua':'MXN',
    'America/Hermosillo':'MXN','America/Mazatlan':'MXN',
    'America/Santiago':'CLP','America/Punta_Arenas':'CLP',
    'America/Lima':'PEN',
    'America/Sao_Paulo':'BRL','America/Bahia':'BRL','America/Fortaleza':'BRL',
    'America/Recife':'BRL','America/Manaus':'BRL','America/Belem':'BRL',
    'America/Campo_Grande':'BRL','America/Cuiaba':'BRL',
    'Europe/London':'GBP'
  };
  var LOCALE_CURRENCY = {
    co:'COP', mx:'MXN', cl:'CLP', pe:'PEN', ar:'ARS', br:'BRL', gb:'GBP',
    us:'USD', ec:'USD', pa:'USD', sv:'USD', ve:'USD', uy:'USD', py:'USD',
    bo:'USD', gt:'USD', hn:'USD', ni:'USD', cr:'USD', do:'USD', pr:'USD', cu:'USD',
    mt:'EUR', es:'EUR', pt:'EUR', fr:'EUR', de:'EUR', it:'EUR', ie:'EUR', nl:'EUR', be:'EUR'
  };

  function guessCurrency(){
    try{
      var zone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
      if(ZONE_CURRENCY[zone]) return ZONE_CURRENCY[zone];
      if(zone.indexOf('America/Argentina/')===0) return 'ARS';
      /* anywhere else in the Americas settles in dollars */
      if(zone.indexOf('America/')===0 || zone.indexOf('Pacific/')===0) return 'USD';
      /* Europe — Malta, Spain and the rest quote in euro */
      if(zone.indexOf('Europe/')===0 || zone.indexOf('Atlantic/')===0) return 'EUR';
      if(zone.indexOf('Africa/')===0 || zone.indexOf('Asia/')===0) return 'EUR';
    }catch(e){}
    var loc = (navigator.language || '').toLowerCase();
    var country = loc.split('-')[1];
    if(country && LOCALE_CURRENCY[country]) return LOCALE_CURRENCY[country];
    return FX.base;
  }

  /* Round to a figure a person would actually quote, whatever the magnitude */
  function tidy(v){
    if(v >= 10000) return Math.round(v/1000)*1000;
    if(v >= 1000)  return Math.round(v/100)*100;
    if(v >= 100)   return Math.round(v/10)*10;
    if(v >= 10)    return Math.round(v);
    return Math.round(v*100)/100;
  }

  function money(amount, cur){
    var v = tidy(amount * (FX.rates[cur] / FX.rates[FX.base]));
    var digits = v < 10 ? 2 : 0;
    try{
      return new Intl.NumberFormat(ES ? 'es-ES' : 'en-GB', {
        style:'currency', currency:cur, currencyDisplay:'code',
        minimumFractionDigits:digits, maximumFractionDigits:digits
      }).format(v);
    }catch(e){
      return v + ' ' + cur;
    }
  }

  var fxSelect = $('#fxSelect'), fxNote = $('#fxNote'), FX_KEY = 'fx-currency';

  function applyCurrency(cur){
    if(!FX.rates[cur]) cur = FX.base;
    $$('[data-amount]').forEach(function(el){
      el.textContent = money(parseFloat(el.getAttribute('data-amount')), cur);
    });
    if(fxNote){
      fxNote.innerHTML = cur === FX.base
        ? (ES ? '<b>Importes en ' + cur + '.</b> La factura puede emitirse en la moneda que solicite.'
              : '<b>Figures in ' + cur + '.</b> Invoices can be issued in the requested currency.')
        : (ES ? '<b>Conversión orientativa a ' + cur + '.</b> La factura puede emitirse en la moneda que solicite.'
              : '<b>Indicative conversion to ' + cur + '.</b> Invoices can be issued in the requested currency.');
    }
    try{ localStorage.setItem(FX_KEY, cur) }catch(e){}
  }

  if(fxSelect){
    var chosen;
    try{ chosen = localStorage.getItem(FX_KEY) }catch(e){}
    if(!chosen || !FX.rates[chosen]) chosen = guessCurrency();
    fxSelect.value = chosen;
    applyCurrency(chosen);
    fxSelect.addEventListener('change', function(){ applyCurrency(this.value) });
  }


  /* ══════════════════════════════════════════════════════════════════════
     WHATSAPP OPENING MESSAGE
     Written in the visitor's own language rather than the page's, so an
     English speaker reading the Spanish site still opens an English chat.
     Preference order: browser languages → the language of this page.
     The hard-coded ?text= in the HTML remains the no-JavaScript fallback.
     SUSTITUIR / REPLACE the wording below to taste.
     ══════════════════════════════════════════════════════════════════════ */
  var WA_TEXT = {
    es: 'Hola, les escribo desde la web de SP Translations. Quisiera un presupuesto para una traducción.',
    en: "Hello, I'm writing from the SP Translations website. I would like a quote for a translation."
  };

  function visitorLanguage(){
    var list = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || ''];
    for (var i = 0; i < list.length; i++){
      var tag = (list[i] || '').toLowerCase();
      if (tag.indexOf('es') === 0) return 'es';
      if (tag.indexOf('en') === 0) return 'en';
    }
    return ES ? 'es' : 'en';          /* neither offered — follow the page */
  }

  (function setWhatsAppMessage(){
    var text = WA_TEXT[visitorLanguage()];
    if (!text) return;
    $$('a[href*="wa.me/"]').forEach(function(a){
      var base = (a.getAttribute('href') || '').split('?')[0];
      if (!base) return;
      a.setAttribute('href', base + '?text=' + encodeURIComponent(text));
    });
  })();

  /* ── Smooth scroll fallback ── */
  if(!('scrollBehavior' in document.documentElement.style)){
    $$('a[href^="#"]').forEach(function(a){
      a.addEventListener('click',function(e){
        var t=document.querySelector(a.getAttribute('href'));
        if(!t) return;
        e.preventDefault();
        window.scrollTo(0,t.getBoundingClientRect().top+window.pageYOffset-84);
      });
    });
  }
})();
