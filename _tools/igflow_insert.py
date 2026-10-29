"""Insert (or refresh) the animated hero visual on the two iGaming pages.
Run from the site root:  python3 _tools/igflow_insert.py   (behaviour lives in igflow.js)"""
import re

ICONS = {
 'casino': '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="9" y="5" width="16" height="22" rx="2.5" transform="rotate(12 17 16)"/><rect class="bg" x="6" y="6" width="16" height="22" rx="2.5"/><path d="M14 20.5s-4.5-2.7-4.5-5.6a2.3 2.3 0 0 1 4.5-.8 2.3 2.3 0 0 1 4.5.8c0 2.9-4.5 5.6-4.5 5.6Z" fill="currentColor" stroke="none"/></svg>',
 'sports': '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="16" cy="16" r="11"/><path d="m16 10 5 3.6-1.9 5.9h-6.2L11 13.6 16 10Z" fill="currentColor" fill-opacity=".25"/><path d="M16 10V5.3M21 13.6l4.6-1.6M19.1 19.5l2.8 3.9M12.9 19.5l-2.8 3.9M11 13.6 6.4 12"/></svg>',
 'studio': '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="4" y="7" width="24" height="18" rx="3"/><path d="M10.5 12h3.5l-2.6 8M18.5 12H22l-2.6 8" stroke-linecap="round"/><path d="M4 11.5h24M4 20.5h24" stroke-opacity=".35"/></svg>',
 'platform': '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="4" y="6" width="24" height="17" rx="2.5"/><path d="M4 10.5h24" /><circle cx="7.3" cy="8.3" r=".6" fill="currentColor"/><circle cx="9.5" cy="8.3" r=".6" fill="currentColor"/><path d="M12 27h8M16 23v4" stroke-linecap="round"/><path d="M9 18l3.5-3.5 3 2.5L22 13" stroke-linecap="round"/></svg>',
}
GAMES = [
 '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 8c3 4 4 9 3 15M20 8c-3 5-7 9-9 15" fill="none" stroke="#5C7A4A" stroke-width="2" stroke-linecap="round"/><path d="M20 8c3-2 7-2 9 0-3 2-6 2-9 0Z" fill="#7FA05F"/><circle cx="12" cy="27" r="6.5" fill="#B3402F"/><circle cx="25" cy="27" r="6.5" fill="#C9503C"/><circle cx="10" cy="25" r="1.6" fill="#fff" opacity=".55"/><circle cx="23" cy="25" r="1.6" fill="#fff" opacity=".55"/></svg>',
 '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M10 8h21l-1.5 4.5L20 33h-6.5l9-19H10Z" fill="#8E7243"/><path d="M10 8h21l-1.5 4.5H11.5Z" fill="#C4AC80"/></svg>',
 '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="14" fill="#1B2A3E"/><circle cx="20" cy="20" r="14" fill="none" stroke="#C4AC80" stroke-width="4" stroke-dasharray="5.5 5.5"/><circle cx="20" cy="20" r="8.5" fill="#F5F2ED"/><text x="20" y="23.6" text-anchor="middle" font-size="9.5" font-weight="700" font-family="Inter,Arial,sans-serif" fill="#1B2A3E">50</text></svg>',
]
T = {
 'en': dict(label='How SP Translations works for iGaming: online casinos, sportsbooks, game studios, and platforms and affiliates send content to SP Translations, which delivers it localised in 14 core languages for each market.',
            src=['Online casinos','Sportsbooks','Game studios','Platforms &amp; affiliates'], into='Translating into', out='Your player-facing content', pick='Choose a language', more='+ 120 languages through our network'),
 'es': dict(label='Cómo trabaja SP Translations para el iGaming: casinos online, casas de apuestas, estudios de juegos, y plataformas y afiliados nos envían su contenido y lo entregamos localizado en 14 idiomas principales para cada mercado.',
            src=['Casinos online','Casas de apuestas','Estudios de juegos','Plataformas y afiliados'], into='Traduciendo al', out='Tu contenido para jugadores', pick='Elige un idioma', more='+ 120 idiomas a través de nuestra red'),
}
def block(lang):
    t = T[lang]
    srcs = ''.join(f'<li class="igflow__src"><span class="igflow__ico">{ICONS[k]}</span><b>{n}</b></li>'
                   for k, n in zip(['casino','sports','studio','platform'], t['src']))
    ys = [40.5, 133.5, 226.5, 319.5]
    paths = ''.join(f'<path d="M0 {y} C55 {y} 55 180 110 180"/>' for y in ys)
    pulses = ''.join(f'<path class="pulse" d="M0 {y} C55 {y} 55 180 110 180"/>' for y in ys)
    games = ''.join(f'<div class="dev__game"><span class="dev__art">{g}</span><span class="dev__stars">★★★★<i>★</i></span><span class="dev__ln"></span><span class="dev__ln dev__ln--s"></span><span class="dev__play" data-k="play">Play</span></div>' for g in GAMES)
    return f'''<!-- igflow:start — animated visual below the hero (igflow.js; regenerate with _tools/igflow_insert.py) -->
<section class="section section--ink igflow-section" id="flow">
  <div class="shell">
    <div class="igflow" data-igflow role="group" aria-label="{t['label']}">
      <ul class="igflow__sources" role="list">{srcs}</ul>
      <svg class="igflow__links igflow__links--in" viewBox="0 0 110 360" aria-hidden="true">{paths}{pulses}</svg>
      <div class="igflow__hub">
        <span class="igflow__crest"><img src="img/crest-light.webp" alt="" width="420" height="316"></span>
        <span class="igflow__label">{t['into']}</span>
        <b class="igflow__lang" aria-hidden="true">English</b>
        <span class="igflow__code" aria-hidden="true">EN</span>
        <div class="igflow__codes" role="group" aria-label="{t['pick']}"></div>
        <span class="igflow__more">{t['more']}</span>
      </div>
      <svg class="igflow__links igflow__links--out" viewBox="0 0 80 360" aria-hidden="true"><path d="M0 180H80"/><path class="pulse on" d="M0 180H80"/></svg>
      <div class="igflow__out">
        <p class="igflow__outlabel">{t['out']}</p>
        <div class="dev" aria-hidden="true">
          <div class="dev__bar"><span class="dev__logo"><i></i>LOBBY</span><span class="dev__btn" data-k="reg">Register</span><span class="dev__menu"><i></i><i></i><i></i></span></div>
          <div class="dev__tabs"><span data-k="casino">Casino</span><span data-k="live">Live casino</span><span data-k="sports">Sports</span></div>
          <div class="dev__promo"><small data-k="bonus">Welcome bonus</small><strong data-k="offer">100% up to €500 + 50 free spins</strong></div>
          <div class="dev__games">{games}</div>
          <div class="dev__foot" data-k="rg">Play responsibly · 18+</div>
        </div>
      </div>
    </div>
  </div>
</section>
<!-- igflow:end -->
'''
for f, lang in [('igaming-translation-services.html','en'), ('traduccion-igaming.html','es')]:
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'<!-- igflow:start.*?<!-- igflow:end -->\n', '', s, flags=re.S)
    s = s.replace('<section class="pagehead pagehead--flow" id="top">', '<section class="pagehead" id="top">', 1)
    i = s.index('<section class="pagehead" id="top">')
    j = s.index('</section>', i) + len('</section>\n')
    s = s[:j] + block(lang) + s[j:]
    if 'src="igflow.js' not in s:
        s = re.sub(r'(<script src="app\.js\?v=[^"]+"></script>)', r'\1\n<script src="igflow.js?v=20261029a" defer></script>', s, count=1)
    open(f, 'w', encoding='utf-8').write(s)
    print(f, 'ok')
