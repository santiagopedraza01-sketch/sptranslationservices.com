"""Build the language pages (EN + ES) and the Languages hub from the certified-page shell.
Run from the site root:  python3 <this file>"""
import json, re, sys, os, html as H
sys.path.insert(0, os.path.dirname(__file__)); from data import LANGS
D = 'https://sptranslationservices.com'
ES_VARIANTS = 'ES MX CO AR PE VE CL EC GT CU BO DO HN PY SV NI CR PA UY PR GQ US'.split()
SHELL = {'en': open('certified-translations-malta.html', encoding='utf-8').read(),
         'es': open('traducciones-certificadas-malta.html', encoding='utf-8').read()}
SHELL_URL = {'en': '/certified-translations-malta', 'es': '/traducciones-certificadas-malta'}
HUB = {'en': 'languages', 'es': 'idiomas'}
HOME = {'en': f'{D}/', 'es': f'{D}/es'}

def esc(s): return H.escape(s, quote=True)
def strip(s): return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def hreflang(en_slug, es_slug):
    out = [f'<link rel="alternate" hreflang="es" href="{D}/{es_slug}">']
    out += [f'<link rel="alternate" hreflang="es-{c}" href="{D}/{es_slug}">' for c in ES_VARIANTS]
    out += [f'<link rel="alternate" hreflang="en" href="{D}/{en_slug}">', f'<link rel="alternate" hreflang="x-default" href="{D}/{en_slug}">']
    return '\n'.join(out)

def page(lang, slug, other_slug, title, desc, graph, main):
    s = SHELL[lang]
    en_slug, es_slug = (slug, other_slug) if lang == 'en' else (other_slug, slug)
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{D}/{slug}">', s, count=1)
    s = re.sub(r'(<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n)+', hreflang(en_slug, es_slug) + '\n', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{D}/{slug}">', s, count=1)
    s = re.sub(r'(<script type="application/ld\+json">).*?(</script>)', lambda m: m.group(1) + '\n' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2) + '\n' + m.group(2), s, count=1, flags=re.S)
    def sw(m):
        return m.group(0).replace(f'href="{SHELL_URL["en"]}"', f'href="/{en_slug}"').replace(f'href="{SHELL_URL["es"]}"', f'href="/{es_slug}"')
    s = re.sub(r'<p class="lang".*?</p>', sw, s, flags=re.S)
    a, b = s.index('<main id="main">') + len('<main id="main">'), s.index('</main>')
    open(f'{slug}.html', 'w', encoding='utf-8').write(s[:a] + '\n' + main + '\n' + s[b:])

def start_section(lang):
    s = SHELL[lang]; i = s.index('<section class="section section--ink" id="start">'); return s[i:s.index('</section>', i) + len('</section>')]

def section(mod, sid, mark, sub, h2, inner):
    subh = f'\n      <p>{sub}</p>' if sub else ''
    return f'''<section class="section section--{mod}" id="{sid}">
  <div class="shell spread">
    <div class="spread__index rise">
      <span class="mark">{mark}</span>{subh}
    </div>
    <div>
      <h2 class="h2 opening rise" style="margin-bottom:clamp(30px,4vw,46px)">{h2}</h2>
{inner}
    </div>
  </div>
</section>
'''
def lst(items):
    return '        <ul class="schedule__list schedule__list--2">\n' + '\n'.join(f'          <li><span>—</span><div>{x}</div></li>' for x in items) + '\n        </ul>'
def block(h, inner, foot=None):
    f = f'\n        <p class="schedule__foot">{foot}</p>' if foot else ''
    return f'      <div class="block rise">\n        <h3 class="block__h">{h}</h3>\n{inner}{f}\n      </div>'
def faq(items, lang):
    d = '\n'.join(f'''        <details{' open' if i == 0 else ''}>
          <summary>{q}</summary>
          <p>{a}</p>
        </details>''' for i, (q, a) in enumerate(items))
    return f'''<section class="section section--warm" id="faq">
  <div class="shell spread">
    <div class="spread__index rise">
      <span class="mark">{'Questions' if lang == 'en' else 'Preguntas'}</span>
    </div>
    <div class="rise">
      <h2 class="h2 opening" style="margin-bottom:clamp(30px,4vw,44px)">{'Frequently asked questions' if lang == 'en' else 'Preguntas frecuentes'}</h2>
      <div class="questions">
{d}
      </div>
    </div>
  </div>
</section>
'''
def related(lang, links):
    rd = 'Read' if lang == 'en' else 'Ver'
    a = '\n'.join(f'        <a href="/{u}"><b>{b}</b><span>{t}</span><em>{rd}</em></a>' for u, b, t in links)
    return f'''<section class="section section--bone" id="related">
  <div class="shell spread">
    <div class="spread__index rise"><span class="mark">{'Keep reading' if lang == 'en' else 'Sigue leyendo'}</span></div>
    <div class="related rise">
{a}
    </div>
  </div>
</section>
'''
def pagehead(crumbs, h1, lede):
    c = ' <span aria-hidden="true">·</span> '.join(f'<a href="{u}">{t}</a>' if u else t for t, u in crumbs)
    return f'''<section class="pagehead" id="top">
  <div class="shell pagehead__inner">
    <div>
      <p class="crumb">{c}</p>
      <h1>{h1}</h1>
    </div>
    <p class="lede">{lede}</p>
  </div>
</section>
'''
def standards(items):
    r = ['I', 'II', 'III']
    return '      <div class="standards rise">\n' + '\n'.join(f'<div class="standards__item"><span class="standards__num">{r[i]}</span><h3 class="h3">{h}</h3><p>{p}</p></div>' for i, (h, p) in enumerate(items)) + '\n      </div>'
def crumbs_ld(slug, items):
    return {'@type': 'BreadcrumbList', '@id': f'{D}/{slug}#breadcrumb', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}
def faq_ld(slug, items):
    return {'@type': 'FAQPage', '@id': f'{D}/{slug}#faq', 'isPartOf': {'@id': f'{D}/{slug}#webpage'},
            'mainEntity': [{'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in items]}

T = {
 'en': dict(home='Home', hub='Languages', pairs='Language pairs', docs='Documents', right='Getting it right'),
 'es': dict(home='Inicio', hub='Idiomas', pairs='Combinaciones', docs='Documentos', right='Detalles que importan'),
}

def lang_page(L, lang):
    en = lang == 'en'
    name = L['en'] if en else L['es']; low = name if en else name.lower()
    an = 'an' if name[0] in 'AEIOU' else 'a'
    slug, other = (L['slug_en'], L['slug_es']) if en else (L['slug_es'], L['slug_en'])
    hub = HUB[lang]; home = '/' if en else '/es'
    cert = 'certified-translations-malta' if en else 'traducciones-certificadas-malta'
    mt = L['code'] == 'mt'
    if en:
        title = f'{name} Translation Services in Malta — Certified {name} ⇄ English | SP Translations'
        desc = f'{name} translation in Malta: certified {name} ⇄ English translations of civil, academic, legal and company documents, signed, dated and stamped by an accredited translator.'
        h1 = f'{name} translation services in Malta'
        lede = f'Certified {name} ⇄ English translations for documents from {L["where_en"]}, ordered online and signed, dated and stamped by a professional, accredited translator.'
    else:
        title = f'Traducción de {low} en Malta — Traducción certificada {low} ⇄ inglés | SP Translations'
        desc = f'Traducción de {low} en Malta: traducciones certificadas {low} ⇄ inglés de documentos civiles, académicos, legales y de empresa, firmadas, fechadas y selladas por un traductor acreditado.'
        h1 = f'Traducción de {low} en Malta'
        lede = f'Traducciones certificadas {low} ⇄ inglés para documentos {"de " + L["where_es"] if not L["where_es"].startswith("los ") else "de " + L["where_es"]}, con solicitud online, firmadas, fechadas y selladas por un traductor profesional acreditado.'
    pairs = ([f'{name} → English', f'English → {name}'] if en else
             [f'{name} → inglés', f'Inglés → {low}'])
    who = L['who_en'] if en else L['who_es']
    s1 = section('bone', 'pairs', T[lang]['pairs'], (f'Into and out of {name}.' if en else f'Desde y hacia el {low}.'),
                 (f'{name} translation for life and work in Malta.' if en else f'Traducción de {low} para vivir y trabajar en Malta.'),
                 f'      <div class="prose rise" style="margin-bottom:clamp(30px,4vw,46px)">\n        <p>{who}</p>\n      </div>\n' +
                 block('Language pairs we translate' if en else 'Combinaciones que traducimos', lst(pairs),
                       (f'{name} translations are carried out by professional native-speaker translators.' if en else
                        f'Las traducciones de {low} las realizan traductores profesionales nativos.')))
    docs = [f'{e if en else s} <em class="orig" lang="{L["code"]}">{o}</em>' for e, s, o in L['docs']]
    s2 = section('warm', 'documents', T[lang]['docs'], ('From certificates to company papers.' if en else 'De certificados a documentos de empresa.'),
                 (f'{name} documents we translate.' if en else f'Documentos en {low} que traducimos.'),
                 block('Most requested' if en else 'Los más solicitados', lst(docs),
                       (f'Also contracts, payslips, bank statements, medical reports, court and notarial documents. See <a href="/{cert}">certified translations in Malta</a>.' if en else
                        f'También contratos, nóminas, extractos bancarios, informes médicos y documentos judiciales y notariales. Consulta <a href="/{cert}">traducciones certificadas en Malta</a>.')))
    nt_en, nt_es, nx_en, nx_es = L['note']
    s3 = section('ink', 'details', T[lang]['right'], ('So your documents match.' if en else 'Para que tus documentos coincidan.'),
                 (f'What matters in {an} {name} translation.' if en else f'Lo que importa en una traducción de {low}.'),
                 standards([
                   (('Names exactly as in your passport', 'Names, places and dates are copied exactly as they appear in your passport or ID, so every document in your application matches.') if en else
                    ('Nombres como en tu pasaporte', 'Nombres, lugares y fechas se copian exactamente como aparecen en tu pasaporte o documento de identidad, para que todos los documentos de tu trámite coincidan.')),
                   (('Stamps, seals and handwriting', 'Official stamps, seals, signatures and handwritten notes are described and translated, so nothing on the original is left out.') if en else
                    ('Sellos, firmas y anotaciones', 'Los sellos oficiales, firmas y anotaciones a mano se describen y traducen, para que no falte nada del original.')),
                   ((nt_en, nx_en) if en else (nt_es, nx_es)),
                 ]))
    if mt:
        apo_q = ('Do Maltese documents need an apostille to be used abroad?' if en else '¿Los documentos malteses necesitan apostilla para usarse en el extranjero?')
        apo_a = ('Usually, yes. Maltese public documents are apostilled by the Ministry for Foreign and European Affairs (MFEA). Check the requirements of the receiving country; we translate the apostille too.' if en else
                 'Normalmente sí. Los documentos públicos malteses los apostilla el Ministerio de Asuntos Exteriores y Europeos (MFEA). Confirma los requisitos del país de destino; también traducimos la apostilla.')
    else:
        apo_q = (f'Does a document from {L["country_en"]} need an apostille?' if en else f'¿Un documento {L["es_from"]} necesita apostilla?')
        ce = L['country_en']; ce_cap = ce[0].upper() + ce[1:]
        apo_a = (f'{ce_cap} is a party to the Hague Apostille Convention, so a public document from {ce} that will be used in Malta is normally legalised with an apostille issued in {ce}. Check the receiving authority’s requirements; we translate the apostille too.' if en else
                 f'{L["es_subj"]} del Convenio de La Haya sobre la apostilla, así que un documento público {L["es_from"]} que se vaya a usar en Malta normalmente se legaliza con una apostilla emitida allí. Confirma los requisitos de la institución que lo recibe; también traducimos la apostilla.')
    faqs = [
        ((f'Do you translate both {name} to English and English to {name}?', f'Yes. We translate {name} into English and English into {name}. Translations are carried out by professional native-speaker translators, and every official translation is signed, dated and stamped by a professional, accredited translator.') if en else
         (f'¿Traducen del {low} al inglés y del inglés al {low}?', f'Sí. Traducimos del {low} al inglés y del inglés al {low}. Las traducciones las realizan traductores profesionales nativos, y cada traducción oficial la firma, fecha y sella un traductor profesional acreditado.')),
        ((f'Will my {name} translation be accepted in Malta?' if not mt else 'Will my translation be accepted abroad?',
          'Official translations are signed, dated and stamped by a professional, accredited translator, which is what most authorities, employers, banks and universities ask for. If an institution has its own requirements, send them with your documents and we prepare the translation accordingly.') if en else
         ((f'¿Aceptarán mi traducción de {low} en Malta?' if not mt else '¿Aceptarán mi traducción en el extranjero?'),
          'Las traducciones oficiales las firma, fecha y sella un traductor profesional acreditado, que es lo que piden la mayoría de autoridades, empleadores, bancos y universidades. Si una institución tiene requisitos propios, envíalos con tus documentos y preparamos la traducción según ellos.')),
        (apo_q, apo_a),
        ((f'How much does {an} {name} translation cost, and how long does it take?', 'Every document is quoted individually, based on its length, layout and language pair, and the delivery date is confirmed in your quotation before you pay. Priority service is available, subject to availability.') if en else
         (f'¿Cuánto cuesta una traducción de {low} y cuánto tarda?', 'Cada documento se cotiza de forma individual según su extensión, formato y combinación de idiomas, y la fecha de entrega se confirma en la cotización antes de pagar. Hay servicio urgente según disponibilidad.')),
    ]
    rel = ([(hub, 'All our languages', 'Our 14 core languages, plus 120+ through our network.'),
            (cert, 'Certified translations in Malta', 'Official documents for the Public Registry, JobsPlus, courts, banks and employers.'),
            ('guide-malta-residency-documents', 'Documents for a Malta residence application', 'Which personal documents usually need translating, and how to prepare them.')] if en else
           [(hub, 'Todos nuestros idiomas', 'Nuestros 14 idiomas principales, además de más de 120 a través de nuestra red.'),
            (cert, 'Traducciones certificadas en Malta', 'Documentos oficiales para el Public Registry, JobsPlus, tribunales, bancos y empleadores.'),
            ('guia-documentos-residencia-malta', 'Documentos para la residencia en Malta', 'Qué documentos personales suelen necesitar traducción y cómo prepararlos.')])
    main = (pagehead([(T[lang]['home'], home), (T[lang]['hub'], f'/{hub}'), (name, None)], h1, lede) + s1 + s2 + s3 + faq(faqs, lang) + related(lang, rel) + '\n' + start_section(lang) + '\n')
    graph = [
        {'@type': 'WebPage', '@id': f'{D}/{slug}#webpage', 'url': f'{D}/{slug}', 'name': title, 'description': desc, 'inLanguage': lang,
         'isPartOf': {'@id': f'{D}/#website'}, 'about': {'@id': f'{D}/#practice'}, 'breadcrumb': {'@id': f'{D}/{slug}#breadcrumb'}, 'mainEntity': {'@id': f'{D}/{slug}#service'}},
        {'@type': 'Service', '@id': f'{D}/{slug}#service', 'name': h1, 'serviceType': (f'{name} translation' if en else f'Traducción de {low}'), 'description': desc,
         'url': f'{D}/{slug}', 'provider': {'@id': f'{D}/#practice'}, 'areaServed': ['Malta', 'European Union'],
         'availableLanguage': [{'@type': 'Language', 'name': L['en'], 'alternateName': L['code']}, {'@type': 'Language', 'name': 'English', 'alternateName': 'en'}],
         'offers': {'@type': 'Offer', 'url': f'{HOME[lang]}#quote', 'priceCurrency': 'EUR', 'availability': 'https://schema.org/InStock'}},
        faq_ld(slug, faqs),
        crumbs_ld(slug, [(T[lang]['home'], HOME[lang]), (T[lang]['hub'], f'{D}/{hub}'), (name, f'{D}/{slug}')]),
    ]
    page(lang, slug, other, title, desc, graph, main)
    return slug

def hub_page(lang):
    en = lang == 'en'; slug, other = HUB[lang], HUB['es' if en else 'en']; home = '/' if en else '/es'
    cert = 'certified-translations-malta' if en else 'traducciones-certificadas-malta'
    title = ('Translation Languages — Spanish, English, Italian, French, German and 120+ More | SP Translations' if en else
             'Idiomas de traducción — español, inglés, italiano, francés, alemán y más de 120 | SP Translations')
    desc = ('Certified translation in Malta in 14 core languages, including Spanish, English, Italian, French, German, Polish, Romanian, Russian, Portuguese, Turkish, Greek, Dutch, Serbian and Maltese, plus 120+ more through our translator network.' if en else
            'Traducción certificada en Malta en 14 idiomas principales, como español, inglés, italiano, francés, alemán, polaco, rumano, ruso, portugués, turco, griego, neerlandés, serbio y maltés, y más de 120 a través de nuestra red de traductores.')
    h1 = 'Our languages' if en else 'Nuestros idiomas'
    lede = ('Spanish ⇄ English in-house, twelve more languages we work in regularly, and more than 120 others through our professional translator network.' if en else
            'Español ⇄ inglés en nuestro equipo, doce idiomas más con los que trabajamos habitualmente y más de 120 a través de nuestra red profesional de traductores.')
    cards = [(('Spain · Latin America · UK' if en else 'España · Latinoamérica · Reino Unido'), ('Spanish ⇄ English' if en else 'Español ⇄ inglés'), f'/{cert}',
              ('Our principal pair, handled in-house: certified translations in both directions.' if en else 'Nuestra combinación principal, en nuestro equipo: traducciones certificadas en ambos sentidos.'),
              (['English → Spanish', 'Spanish → English'] if en else ['Inglés → español', 'Español → inglés']))]
    for L in LANGS:
        name = L['en'] if en else L['es']; low = name if en else name.lower()
        cards.append((L['where_en'] if en else L['where_es'][0].upper() + L['where_es'][1:], name, f'/{L["slug_en"] if en else L["slug_es"]}',
                      (f'Certified {name} translations into and out of English.' if en else f'Traducciones certificadas del {low} al inglés y del inglés al {low}.'),
                      ([f'{name} → English', f'English → {name}'] if en else [f'{name} → inglés', f'Inglés → {low}'])))
    cards_html = '      <div class="types rise">\n' + '\n'.join(f'''          <article class="type">
            <span class="type__tag">{tag}</span>
            <h3><a href="{u}">{h}</a></h3>
            <p>{p}</p>
            <ul>{''.join(f'<li>{x}</li>' for x in li)}</ul>
          </article>''' for tag, h, u, p, li in cards) + '\n      </div>'
    s1 = section('warm', 'list', ('Languages' if en else 'Idiomas'), ('Fourteen core languages.' if en else 'Catorce idiomas principales.'),
                 ('Languages we work in most often.' if en else 'Idiomas con los que más trabajamos.'), cards_html)
    more = section('bone', 'more', ('120+ languages' if en else 'Más de 120 idiomas'), ('Ask about any pair.' if en else 'Consúltanos por cualquier combinación.'),
                   ('Need another language?' if en else '¿Necesitas otro idioma?'),
                   '      <div class="prose rise">\n        <p>' + ('Through our professional translator network we cover more than 120 languages, from Arabic, Ukrainian and Chinese to Hindi, Tagalog and many less common languages. Tell us the language pair and what the translation is for, and we confirm availability, price and delivery date in your quotation.' if en else
                    'A través de nuestra red profesional de traductores cubrimos más de 120 idiomas, del árabe, el ucraniano y el chino al hindi, el tagalo y muchas lenguas menos comunes. Indícanos la combinación de idiomas y para qué es la traducción, y te confirmamos disponibilidad, precio y plazo en la cotización.') +
                   f'</p>\n        <p><a href="{home}#quote">' + ('Request a quote →' if en else 'Solicitar una cotización →') + '</a></p>\n      </div>')
    faqs = [((('Are all languages certified the same way?', 'Yes. Whatever the language, every official translation is signed, dated and stamped by a professional, accredited translator.') if en else
              ('¿Todas las traducciones se certifican igual?', 'Sí. Sea cual sea el idioma, cada traducción oficial la firma, fecha y sella un traductor profesional acreditado.'))),
            (('Can you translate other language pairs?', 'Our core languages are translated into and out of English, and Spanish ⇄ English is our principal pair. Tell us the pair you need and we confirm availability in your quotation.') if en else
             ('¿Pueden traducir otras combinaciones de idiomas?', 'Nuestros idiomas principales se traducen desde y hacia el inglés, y español ⇄ inglés es nuestra combinación principal. Dinos la combinación que necesitas y te confirmamos la disponibilidad en la cotización.'))]
    main = pagehead([(T[lang]['home'], home), (T[lang]['hub'], None)], h1, lede) + s1 + more + faq(faqs, lang) + '\n' + start_section(lang) + '\n'
    graph = [{'@type': 'CollectionPage', '@id': f'{D}/{slug}#webpage', 'url': f'{D}/{slug}', 'name': title, 'description': desc, 'inLanguage': lang,
              'isPartOf': {'@id': f'{D}/#website'}, 'about': {'@id': f'{D}/#practice'}, 'breadcrumb': {'@id': f'{D}/{slug}#breadcrumb'},
              'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': c[1], 'url': D + c[2]} for i, c in enumerate(cards)]}},
             faq_ld(slug, faqs), crumbs_ld(slug, [(T[lang]['home'], HOME[lang]), (T[lang]['hub'], f'{D}/{slug}')])]
    page(lang, slug, other, title, desc, graph, main)

made = []
for lang in ('en', 'es'):
    hub_page(lang); made.append(HUB[lang])
    for L in LANGS: made.append(lang_page(L, lang))
print(len(made), 'pages:', ' '.join(made))
