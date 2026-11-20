"""Build the blog hubs: /blog/ (English) and /blog/es/ (Spanish).

Run from the site root:  python3 _tools/build_blog.py   (then build_search_index.py and build_sitemap.py)
Posts are the guide pages (guide-*.html, guia-*.html) plus any posts added later as
blog/<slug>/index.html (English) or blog/es/<slug>/index.html (Spanish).
Each card takes its title (H1), summary (meta description), dates (Article schema) and
reading time from the post itself; the category comes from CATEGORIES below. The header and
footer are copied from about.html / sobre-nosotros.html, with asset paths made absolute so
they work inside the blog/ folder.
"""
import glob, html, json, os, re

BASE = 'https://sptranslationservices.com'

CATEGORIES = {   # first keyword found in the post URL wins
    'en': [('igaming', 'iGaming'), ('residency', 'Moving to Malta'), ('apostil', 'Certified translation'), ('sworn', 'Certified translation')],
    'es': [('igaming', 'iGaming'), ('residencia', 'Mudarse a Malta'), ('apostil', 'Traducción certificada'), ('jurada', 'Traducción certificada')],
}
ORDER = ['residen', 'apostil', 'sworn|jurada', 'igaming']

T = {
 'en': dict(shell='about.html', url=f'{BASE}/blog/', other=f'{BASE}/blog/es/', locale='en_GB', home='/', home_name='Home',
            title='Translation Blog: Guides on Certified Translation, Malta & iGaming | SP Translations',
            desc='The SP Translations blog: practical guides on certified and sworn translations, apostilles, documents for moving to Malta, and iGaming localisation for new markets.',
            h1='The SP Translations blog', lede='Practical guides and insights on certified translation, moving to Malta and iGaming localisation, from the translators who handle them every day.',
            all='All articles', featured='Latest article', read='Read the article', min='min read', mark='Articles', side='Guides and insights.',
            months=['January','February','March','April','May','June','July','August','September','October','November','December'],
            date=lambda d, M: f'{int(d[8:10])} {M[int(d[5:7])-1]} {d[:4]}',
            cta='<p><strong>Have a document to translate?</strong> Send a scan or a clear photo and receive a fixed quotation, with no obligation.</p>',
            quote='/#quote', quote_t='Request a quote', wa_t='Message on WhatsApp',
            wa='https://wa.me/35679066398?text=Hello%2C%20I%20would%20like%20a%20quote%20for%20a%20translation.'),
 'es': dict(shell='sobre-nosotros.html', url=f'{BASE}/blog/es/', other=f'{BASE}/blog/', locale='es_ES', home='/es', home_name='Inicio',
            title='Blog de traducción: guías sobre traducción certificada, Malta e iGaming | SP Translations',
            desc='El blog de SP Translations: guías prácticas sobre traducciones certificadas y juradas, apostillas, documentos para mudarse a Malta y localización para iGaming.',
            h1='El blog de SP Translations', lede='Guías prácticas y novedades sobre traducción certificada, mudarse a Malta y localización para iGaming, de los traductores que las trabajan cada día.',
            all='Todos los artículos', featured='Último artículo', read='Leer el artículo', min='min de lectura', mark='Artículos', side='Guías y novedades.',
            months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
            date=lambda d, M: f'{int(d[8:10])} de {M[int(d[5:7])-1]} de {d[:4]}',
            cta='<p><strong>¿Tienes un documento para traducir?</strong> Envíanos un escaneo o una foto clara y recibe una cotización fija, sin compromiso.</p>',
            quote='/es#quote', quote_t='Solicitar una cotización', wa_t='Escribir por WhatsApp',
            wa='https://wa.me/35679066398?text=Hola%2C%20me%20gustar%C3%ADa%20solicitar%20una%20cotizaci%C3%B3n%20para%20una%20traducci%C3%B3n.'),
}

def text(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def posts(lang):
    files = sorted(glob.glob('guide-*.html' if lang == 'en' else 'guia-*.html'))
    files += sorted(f for f in glob.glob('blog/*/index.html' if lang == 'en' else 'blog/es/*/index.html') if f != 'blog/es/index.html')
    out = []
    for f in files:
        s = open(f, encoding='utf-8').read()
        url = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
        main = s[s.index('<main'):s.index('</main>')]
        pub = (re.search(r'"datePublished": "([^"]+)"', s) or [None, '2026-01-01'])[1][:10]
        mod = (re.search(r'"dateModified": "([^"]+)"', s) or [None, pub])[1][:10]
        cat = next((c for k, c in CATEGORIES[lang] if k in url), CATEGORIES[lang][-1][1])
        out.append(dict(url=url, path=url.replace(BASE, ''), title=text(re.search(r'<h1[^>]*>(.*?)</h1>', main, re.S).group(1)),
                        desc=html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1)),
                        pub=pub, mod=mod, cat=cat, mins=max(2, round(len(text(main).split()) / 220))))
    # newest first; posts published the same day keep the order of ORDER (same in both languages)
    rank = lambda p: next((i for i, k in enumerate(ORDER) if re.search(k, p['url'])), len(ORDER))
    return sorted(out, key=lambda p: (p['pub'], -rank(p)), reverse=True)

def absolute(chunk):
    chunk = re.sub(r'(\s(?:src|href)=")(?!https?:|/|#|mailto:|tel:|data:)([^"]+)"', r'\1/\2"', chunk)
    return re.sub(r'(\ssrcset=")([^"]+)"', lambda m: m.group(1) + ', '.join(
        p if p.strip().startswith(('/', 'http')) else '/' + p.strip() for p in m.group(2).split(',')) + '"', chunk)

def build(lang):
    t = T[lang]; P = posts(lang); M = t['months']
    shell = open(t['shell'], encoding='utf-8').read()
    shell_url = re.search(r'<link rel="canonical" href="([^"]+)"', shell).group(1).replace(BASE, '')
    header = shell[shell.index('</head>') + len('</head>'):shell.index('<main id="main">')]
    footer = shell[shell.index('</main>') + len('</main>'):]
    header = header.replace(' aria-current="page"', '')
    other_shell = 'sobre-nosotros' if lang == 'en' else 'about'
    header = header.replace(f'href="{shell_url}" hreflang', f'href="{t["url"].replace(BASE, "")}" hreflang') \
                   .replace(f'href="/{other_shell}" hreflang', f'href="{t["other"].replace(BASE, "")}" hreflang')
    header, footer = absolute(header), absolute(footer)
    css = re.search(r'<link rel="stylesheet" href="([^"]+)">', shell).group(1)
    head_icons = absolute(shell[shell.index('<link rel="icon"'):shell.index('<script type="application/ld+json">')])

    es_variants = re.findall(r'<link rel="alternate" hreflang="(es-[A-Z]{2})"', shell)
    en_url, es_url = (t['url'], t['other']) if lang == 'en' else (t['other'], t['url'])
    alts = '\n'.join([f'<link rel="alternate" hreflang="es" href="{es_url}">'] +
                     [f'<link rel="alternate" hreflang="{v}" href="{es_url}">' for v in es_variants] +
                     [f'<link rel="alternate" hreflang="en" href="{en_url}">', f'<link rel="alternate" hreflang="x-default" href="{en_url}">'])

    cats = []
    for p in P:
        if p['cat'] not in cats: cats.append(p['cat'])
    slug = lambda c: re.sub(r'[^a-z]+', '-', c.lower().replace('ó', 'o').replace('í', 'i')).strip('-')

    def card(p, big=False):
        return (f'<article class="post{" post--featured" if big else ""}" data-cat="{slug(p["cat"])}">'
                f'<a href="{p["path"]}">'
                + (f'<span class="post__flag">{t["featured"]}</span>' if big else '') +
                f'<span class="post__meta"><span class="post__cat">{html.escape(p["cat"])}</span>'
                f'<time datetime="{p["pub"]}">{t["date"](p["pub"], M)}</time><span>{p["mins"]} {t["min"]}</span></span>'
                f'<b class="post__title">{html.escape(p["title"])}</b>'
                f'<span class="post__desc">{html.escape(p["desc"])}</span>'
                f'<em class="post__more">{t["read"]}<span class="btn__arrow" aria-hidden="true"></span></em></a></article>')

    chips = ''.join([f'<button type="button" class="chip on" data-filter="all" aria-pressed="true">{t["all"]}</button>'] +
                    [f'<button type="button" class="chip" data-filter="{slug(c)}" aria-pressed="false">{html.escape(c)}</button>' for c in cats])

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "@id": t['url'] + '#blog', "url": t['url'], "name": t['h1'], "description": t['desc'], "inLanguage": lang,
         "isPartOf": {"@id": f"{BASE}/#website"}, "publisher": {"@id": f"{BASE}/#practice"},
         "breadcrumb": {"@id": t['url'] + '#breadcrumb'},
         "blogPost": [{"@type": "BlogPosting", "headline": p['title'], "url": p['url'], "description": p['desc'],
                       "datePublished": p['pub'], "dateModified": p['mod'], "articleSection": p['cat'], "inLanguage": lang,
                       "author": {"@id": f"{BASE}/#santiago"}, "publisher": {"@id": f"{BASE}/#practice"}} for p in P]},
        {"@type": "BreadcrumbList", "@id": t['url'] + '#breadcrumb', "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t['home_name'], "item": BASE + t['home'] if t['home'] != '/' else BASE + '/'},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": t['url']}]}]}

    page = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{html.escape(t['title'])}</title>
<meta name="description" content="{html.escape(t['desc'])}">
<link rel="canonical" href="{t['url']}">

{alts}

<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(t['title'])}">
<meta property="og:description" content="{html.escape(t['desc'])}">
<meta property="og:url" content="{t['url']}">
<meta property="og:image" content="{BASE}/img/og-image.jpg">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#111D2C">

{head_icons.strip()}

<script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
</script>

<link rel="stylesheet" href="/{css}">
</head>{header}<main id="main">

<section class="pagehead" id="top">
  <div class="shell pagehead__inner">
    <div>
      <p class="crumb"><a href="{t['home']}">{t['home_name']}</a> <span aria-hidden="true">·</span> Blog</p>
      <h1>{t['h1']}</h1>
    </div>
    <p class="lede">{t['lede']}</p>
  </div>
</section>

<section class="section section--bone" id="articles">
  <div class="shell spread">
    <div class="spread__index rise">
      <span class="mark">{t['mark']}</span>
      <p>{t['side']}</p>
    </div>
    <div>
      <div class="chips rise" role="group" aria-label="{t['all']}" data-filter-group>{chips}</div>
      <div class="posts rise" data-filter-list>
        {card(P[0], True)}
        {''.join(card(p) for p in P[1:])}
      </div>
    </div>
  </div>
</section>

<section class="section section--ink" id="start">
  <div class="shell">
    <div class="process__note rise" style="margin-top:0">
      {t['cta']}
      <p style="display:flex;flex-wrap:wrap;gap:12px">
        <a class="btn btn--gold" href="{t['quote']}">{t['quote_t']}<span class="btn__arrow" aria-hidden="true"></span></a>
        <a class="btn btn--line-light" href="{t['wa']}" target="_blank" rel="noopener">{t['wa_t']}</a>
      </p>
    </div>
  </div>
</section>

</main>{footer}'''
    path = 'blog/index.html' if lang == 'en' else 'blog/es/index.html'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(page)
    print(f'{path}: {len(P)} posts, categories: {", ".join(cats)}')

if __name__ == '__main__':
    build('en'); build('es')
