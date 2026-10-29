/* SP Translations — iGaming page hero: client types → SP Translations → a mock lobby
   that changes language. Cycles through the core languages; the code buttons let
   visitors pick one. Pauses on hover/focus, off screen and in background tabs, and
   does not auto-play for visitors who prefer reduced motion. */
(function(){
  'use strict';
  var root=document.querySelector('[data-igflow]');
  if(!root) return;

  /* reg, play, bonus, offer, casino, live, sports, responsible-gambling line */
  var L=[
    ['EN','English','Register','Play','Welcome bonus','100% up to €500 + 50 free spins','Casino','Live casino','Sports','Play responsibly · 18+'],
    ['ES','Español','Regístrate','Jugar','Bono de bienvenida','100% hasta 500 € + 50 giros gratis','Casino','Casino en vivo','Deportes','Juega con responsabilidad · +18'],
    ['IT','Italiano','Registrati','Gioca','Bonus di benvenuto','100% fino a 500 € + 50 giri gratis','Casinò','Casinò live','Sport','Gioca responsabilmente · 18+'],
    ['FR','Français','S’inscrire','Jouer','Bonus de bienvenue','100 % jusqu’à 500 € + 50 tours gratuits','Casino','Casino en direct','Paris sportifs','Jouez de manière responsable · 18+'],
    ['DE','Deutsch','Registrieren','Spielen','Willkommensbonus','100 % bis zu 500 € + 50 Freispiele','Casino','Live-Casino','Sportwetten','Verantwortungsvoll spielen · 18+'],
    ['PL','Polski','Zarejestruj się','Graj','Bonus powitalny','100% do 500 zł + 50 darmowych spinów','Kasyno','Kasyno na żywo','Zakłady','Graj odpowiedzialnie · 18+'],
    ['RO','Română','Înregistrare','Joacă','Bonus de bun venit','100% până la 500 lei + 50 de rotiri gratuite','Cazino','Cazino live','Pariuri','Joacă responsabil · 18+'],
    ['RU','Русский','Регистрация','Играть','Приветственный бонус','100% до 500 € + 50 фриспинов','Казино','Живое казино','Спорт','Играйте ответственно · 18+'],
    ['PT','Português','Cadastre-se','Jogar','Bônus de boas-vindas','100% até R$ 500 + 50 giros grátis','Cassino','Cassino ao vivo','Esportes','Jogue com responsabilidade · 18+'],
    ['TR','Türkçe','Kayıt ol','Oyna','Hoş geldin bonusu','500 ₺’ye kadar %100 + 50 bedava dönüş','Casino','Canlı casino','Spor','Sorumlu oynayın · 18+'],
    ['EL','Ελληνικά','Εγγραφή','Παίξε','Μπόνους καλωσορίσματος','100% έως 500 € + 50 δωρεάν περιστροφές','Καζίνο','Live καζίνο','Στοίχημα','Παίξτε υπεύθυνα · 21+'],
    ['NL','Nederlands','Registreren','Spelen','Welkomstbonus','100% tot € 500 + 50 gratis spins','Casino','Live casino','Sport','Speel bewust · 24+'],
    ['SR','Srpski','Registruj se','Igraj','Bonus dobrodošlice','100% do 500 € + 50 besplatnih okretaja','Kazino','Kazino uživo','Sport','Igrajte odgovorno · 18+'],
    ['MT','Malti','Irreġistra','Ilgħab','Bonus ta’ merħba','100% sa €500 + 50 spin b’xejn','Każinò','Każinò live','Sports','Ilgħab b’mod responsabbli · 18+']
  ];
  var HTML_LANG={EN:'en',ES:'es',IT:'it',FR:'fr',DE:'de',PL:'pl',RO:'ro',RU:'ru',PT:'pt-BR',TR:'tr',EL:'el',NL:'nl',SR:'sr-Latn',MT:'mt'};
  var KEYS={reg:2,play:3,bonus:4,offer:5,casino:6,live:7,sports:8,rg:9};
  /* which lobby tab lights up for each client type */
  var TAB=['casino','sports','casino','live'];

  var $$=function(s,c){return Array.prototype.slice.call((c||root).querySelectorAll(s))};
  var srcs=$$('.igflow__src'), inPaths=$$('.igflow__links--in .pulse'), dev=root.querySelector('.dev'),
      hubName=root.querySelector('.igflow__lang'), hubCode=root.querySelector('.igflow__code'),
      codes=root.querySelector('.igflow__codes'), tabs=$$('.dev__tabs [data-k]');

  L.forEach(function(l,i){
    var b=document.createElement('button');
    b.type='button'; b.textContent=l[0]; b.setAttribute('lang',HTML_LANG[l[0]]);
    b.setAttribute('aria-label',l[1]); b.setAttribute('aria-pressed','false');
    b.addEventListener('click',function(){ go(i,true); });
    codes.appendChild(b);
  });
  var btns=$$('button',codes);

  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur=-1, step=0, timer=null, swapT=null, hovered=false, visible=true, pinned=false;
  var START=Math.max(0,L.map(function(l){return HTML_LANG[l[0]]}).indexOf(document.documentElement.lang)+1)%L.length;

  function paint(i){
    var l=L[i];
    $$('[data-k]',dev).forEach(function(el){ el.textContent=l[KEYS[el.getAttribute('data-k')]]; });
    dev.setAttribute('lang',HTML_LANG[l[0]]);
    hubName.textContent=l[1]; hubName.setAttribute('lang',HTML_LANG[l[0]]); hubCode.textContent=l[0];
    btns.forEach(function(b,j){ var on=j===i; b.classList.toggle('on',on); b.setAttribute('aria-pressed',String(on)); });
  }
  function source(k){
    srcs.forEach(function(s,j){ s.classList.toggle('on',j===k); });
    inPaths.forEach(function(p,j){ p.classList.toggle('on',j===k); });
    tabs.forEach(function(t){ t.classList.toggle('on',t.getAttribute('data-k')===TAB[k]); });
  }
  function go(i,user){
    if(user){ pinned=true; schedule(); }
    if(i===cur) return;
    cur=i; source(step++%srcs.length);
    if(reduce){ paint(i); return; }
    root.classList.add('is-swapping');
    clearTimeout(swapT);
    swapT=setTimeout(function(){ paint(i); root.classList.remove('is-swapping'); },230);
  }
  function running(){ return !reduce&&!hovered&&visible&&!document.hidden; }
  function schedule(){
    clearTimeout(timer);
    if(!running()) return;
    timer=setTimeout(function(){ pinned=false; go((cur+1)%L.length); schedule(); }, pinned?7000:3200);
  }

  root.addEventListener('mouseenter',function(){ hovered=true; schedule(); });
  root.addEventListener('mouseleave',function(){ hovered=false; schedule(); });
  root.addEventListener('focusin',function(){ hovered=true; schedule(); });
  root.addEventListener('focusout',function(e){ if(!root.contains(e.relatedTarget)){ hovered=false; schedule(); } });
  document.addEventListener('visibilitychange',schedule);
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(en){ visible=en[0].isIntersecting; root.classList.toggle('is-paused',!visible); schedule(); },{threshold:.15}).observe(root);
  }

  cur=START; paint(START); source(step++%srcs.length);
  root.classList.add('is-ready');
  schedule();
})();
