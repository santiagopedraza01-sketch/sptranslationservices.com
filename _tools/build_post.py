"""Build blog posts from their sources in _tools/blog/posts/*.json.

Run from the site root:  python3 _tools/build_post.py            (all posts)
                         python3 _tools/build_post.py <slug>     (one post)
then: python3 _tools/build_blog.py && python3 _tools/build_search_index.py && python3 _tools/build_sitemap.py

A source file holds one post, in one or both languages:
{
  "en": {                                   # and/or "es": {...} with the same keys
    "slug": "malta-single-permit-documents",            # → /blog/<slug>/  (es → /blog/es/<slug>/)
    "title": "SEO title (≤ 60 chars before the brand)",
    "description": "Meta description, 140–160 characters.",
    "h1": "Visible headline",
    "lede": "One or two sentences under the headline.",
    "category": "Moving to Malta",           # must match a category in build_blog.py
    "published": "2026-11-20", "updated": "2026-11-20",
    "body": "<p>…</p><h2 id=\"…\">…</h2>…",   # article HTML; every <h2> needs an id (used for the contents list)
    "faqs": [["Question?", "Answer (plain text or simple HTML)."], …],
    "sources": [["Label", "https://…"], …],  # official / primary sources checked for the facts
    "related": [["/certified-translations-malta", "Title", "One-line summary"], …]
  }
}
Posts are written in the site's own HTML classes: .prose (headings, lists, tables), .callout,
.checklist. Asset paths are absolute so pages work inside blog/.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from build_blog import absolute, BASE

L = {
 'en': dict(shell='about.html', home='/', home_name='Home', blog='/blog/', contents='In this article', faq='Frequently asked questions',
            sources='Sources', sources_note='Official and primary sources checked when this article was written. Rules change: always confirm with the institution that will receive your documents.',
            related='Keep reading', read='Read', updated='Updated', min='min read', by='Written by', author_role='Founder and certified translator, SP Translations',
            author_bio='Santiago Pedraza Castillo is a professional, accredited translator based in Malta. He and his team of native translators translate official documents for people moving to and working in Malta, and localise content for international companies.',
            cta='<p><strong>Need documents translated?</strong> Send a scan or a clear photo and receive a fixed quotation within a few working hours, with no obligation.</p>',
            quote='/#quote', quote_t='Request a quote', wa_t='Message on WhatsApp', locale='en_GB',
            wa='https://wa.me/35679066398?text=Hello%2C%20I%20would%20like%20a%20quote%20for%20a%20translation.',
            months=['January','February','March','April','May','June','July','August','September','October','November','December'],
            date=lambda d, M: f'{int(d[8:10])} {M[int(d[5:7])-1]} {d[:4]}'),
 'es': dict(shell='sobre-nosotros.html', home='/es', home_name='Inicio', blog='/blog/es/', contents='En este artículo', faq='Preguntas frecuentes',
            sources='Fuentes', sources_note='Fuentes oficiales y primarias consultadas al redactar este artículo. Las normas cambian: confirma siempre con la institución que recibirá tus documentos.',
            related='Sigue leyendo', read='Leer', updated='Actualizado', min='min de lectura', by='Escrito por', author_role='Fundador y traductor certificado, SP Translations',
            author_bio='Santiago Pedraza Castillo es traductor profesional acreditado con sede en Malta. Junto con su equipo de traductores nativos traduce documentos oficiales para quienes se mudan y trabajan en Malta, y localiza contenido para empresas internacionales.',
            cta='<p><strong>¿Necesitas traducir documentos?</strong> Envíanos un escaneo o una foto clara y recibe una cotización fija en pocas horas laborables, sin compromiso.</p>',
            quote='/es#quote', quote_t='Solicitar una cotización', wa_t='Escribir por WhatsApp', locale='es_ES',
            wa='https://wa.me/35679066398?text=Hola%2C%20me%20gustar%C3%ADa%20solicitar%20una%20cotizaci%C3%B3n%20para%20una%20traducci%C3%B3n.',
            months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
            date=lambda d, M: f'{int(d[8:10])} de {M[int(d[5:7])-1]} de {d[:4]}'),
}

def text(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
def url_of(lang, slug): return f'{BASE}/blog/{slug}/' if lang == 'en' else f'{BASE}/blog/es/{slug}/'

def build(src):
    data = json.load(open(src, encoding='utf-8'))
    for lang, p in data.items():
        t = L[lang]; M = t['months']; url = url_of(lang, p['slug'])
        other = 'es' if lang == 'en' else 'en'
        shell = open(t['shell'], encoding='utf-8').read()
        shell_url = re.search(r'<link rel="canonical" href="([^"]+)"', shell).group(1).replace(BASE, '')
        header = shell[shell.index('</head>') + 7:shell.index('<main id="main">')].replace(' aria-current="page"', '')
        footer = shell[shell.index('</main>') + 7:]
        # language switcher: to the other-language version if there is one, else to the other blog hub
        other_url = url_of(other, data[other]['slug']) if other in data else (f'{BASE}/blog/es/' if lang == 'en' else f'{BASE}/blog/')
        other_shell = '/sobre-nosotros' if lang == 'en' else '/about'
        header = header.replace(f'href="{shell_url}" hreflang', f'href="{url.replace(BASE, "")}" hreflang') \
                       .replace(f'href="{other_shell}" hreflang', f'href="{other_url.replace(BASE, "")}" hreflang')
        header, footer = absolute(header), absolute(footer)
        css = re.search(r'<link rel="stylesheet" href="([^"]+)">', shell).group(1)
        icons = absolute(shell[shell.index('<link rel="icon"'):shell.index('<script type="application/ld+json">')]).strip()

        if other in data:
            en_u, es_u = (url, other_url) if lang == 'en' else (other_url, url)
            variants = re.findall(r'<link rel="alternate" hreflang="(es-[A-Z]{2})"', open('about.html', encoding='utf-8').read())
            alts = '\n'.join([f'<link rel="alternate" hreflang="es" href="{es_u}">'] + [f'<link rel="alternate" hreflang="{v}" href="{es_u}">' for v in variants] +
                             [f'<link rel="alternate" hreflang="en" href="{en_u}">', f'<link rel="alternate" hreflang="x-default" href="{en_u}">'])
        else:
            alts = f'<link rel="alternate" hreflang="{lang}" href="{url}">' + (f'\n<link rel="alternate" hreflang="x-default" href="{url}">' if lang == 'en' else '')

        body = p['body']
        heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
        assert heads and len(heads) == body.count('<h2'), f'{src}: every <h2> in the body needs an id'
        words = len(text(body + ' '.join(q + ' ' + a for q, a in p.get('faqs', []))).split())
        mins = max(2, round(words / 220))
        toc = ''.join(f'<li><a href="#{i}">{h}</a></li>' for i, h in heads)
        faqs = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in p.get('faqs', []))
        sources = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(n)}</a></li>' for n, u in p.get('sources', []))
        related = ''.join(f'<a href="{h}"><b>{html.escape(n)}</b><span>{html.escape(d)}</span><em>{t["read"]}</em></a>' for h, n, d in p.get('related', []))

        graph = [
            {"@type": "WebPage", "@id": url + '#webpage', "url": url, "name": p['title'], "description": p['description'], "inLanguage": lang,
             "isPartOf": {"@id": f"{BASE}/#website"}, "breadcrumb": {"@id": url + '#breadcrumb'}},
            {"@type": "BlogPosting", "@id": url + '#article', "headline": p['h1'], "description": p['description'], "inLanguage": lang, "url": url,
             "mainEntityOfPage": {"@id": url + '#webpage'}, "image": f"{BASE}/img/og-image.jpg", "datePublished": p['published'],
             "dateModified": p['updated'], "articleSection": p['category'], "wordCount": words,
             "author": {"@id": f"{BASE}/#santiago"}, "publisher": {"@id": f"{BASE}/#practice"},
             "isPartOf": {"@id": f"{BASE}{t['blog']}#blog"}},
            {"@type": "BreadcrumbList", "@id": url + '#breadcrumb', "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": t['home_name'], "item": BASE + (t['home'] if t['home'] != '/' else '/')},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + t['blog']},
                {"@type": "ListItem", "position": 3, "name": p['h1'], "item": url}]}]
        if p.get('faqs'):
            graph.append({"@type": "FAQPage", "@id": url + '#faq', "isPartOf": {"@id": url + '#webpage'}, "mainEntity": [
                {"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in p['faqs']]})
        ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
        esc = html.escape

        page = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{esc(p['title'])} | SP Translations</title>
<meta name="description" content="{esc(p['description'])}">
<link rel="canonical" href="{url}">

{alts}

<meta property="og:type" content="article">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/img/og-image.jpg">
<meta property="og:locale" content="{t['locale']}">
<meta property="article:published_time" content="{p['published']}">
<meta property="article:modified_time" content="{p['updated']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#111D2C">

{icons}

<script type="application/ld+json">
{ld}
</script>

<link rel="stylesheet" href="/{css}">
</head>{header}<main id="main">

<section class="pagehead" id="top">
  <div class="shell pagehead__inner">
    <div>
      <p class="crumb"><a href="{t['home']}">{t['home_name']}</a> <span aria-hidden="true">·</span> <a href="{t['blog']}">Blog</a> <span aria-hidden="true">·</span> {esc(p['category'])}</p>
      <h1>{esc(p['h1'])}</h1>
      <p class="article-meta">{esc(p['category'])} · {t['updated']} <time datetime="{p['updated']}">{t['date'](p['updated'], M)}</time> · {mins} {t['min']}</p>
    </div>
    <p class="lede">{p['lede']}</p>
  </div>
</section>

<section class="section section--bone" id="article">
  <div class="shell spread">
    <div class="spread__index rise">
      <nav class="toc" aria-label="{t['contents']}">
        <span class="mark">{t['contents']}</span>
        <ol>{toc}</ol>
      </nav>
    </div>
    <div>
      <div class="prose rise">
{body}
      </div>
      <aside class="byline rise">
        <img src="/santiago.jpg" alt="" width="64" height="64" loading="lazy">
        <div><span>{t['by']}</span><b><a href="{'/translators' if lang == 'en' else '/traductores'}">Santiago Pedraza Castillo</a></b><em>{t['author_role']}</em><p>{t['author_bio']}</p></div>
      </aside>
    </div>
  </div>
</section>
''' + (f'''
<section class="section section--warm" id="faq">
  <div class="shell spread">
    <div class="spread__index rise"><span class="mark">FAQ</span></div>
    <div class="rise">
      <h2 class="h2 opening" style="margin-bottom:clamp(30px,4vw,44px)">{t['faq']}</h2>
      <div class="questions">{faqs}</div>
    </div>
  </div>
</section>
''' if faqs else '') + (f'''
<section class="section section--bone" id="sources">
  <div class="shell spread">
    <div class="spread__index rise"><span class="mark">{t['sources']}</span></div>
    <div class="rise">
      <p class="sources__note">{t['sources_note']}</p>
      <ul class="sources">{sources}</ul>
    </div>
  </div>
</section>
''' if sources else '') + (f'''
<section class="section section--warm" id="related">
  <div class="shell spread">
    <div class="spread__index rise"><span class="mark">{t['related']}</span></div>
    <div class="related rise">{related}</div>
  </div>
</section>
''' if related else '') + f'''
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
        out = f'blog/{p["slug"]}/index.html' if lang == 'en' else f'blog/es/{p["slug"]}/index.html'
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(page)
        print(f'{out}: {words} words, {mins} min, {len(heads)} sections, {len(p.get("faqs", []))} FAQs')

if __name__ == '__main__':
    import glob
    want = sys.argv[1:]
    for src in sorted(glob.glob('_tools/blog/posts/*.json')):
        if not want or os.path.basename(src)[:-5] in want: build(src)
