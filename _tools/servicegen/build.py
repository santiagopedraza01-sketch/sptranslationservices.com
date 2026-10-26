"""Build the museum translation and content writing service pages (EN + ES).
Run from the site root:  python3 _tools/servicegen/build.py
Uses the page shell and helpers of _tools/langgen/build.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'langgen'))
from build import D, HOME, page, pagehead, section, faq, related, start_section, standards, steps_html, faq_ld, crumbs_ld, esc

def types(cards):
    out = []
    for tag, h, p, items in cards:
        out.append(f'''          <article class="type">
            <span class="type__tag">{tag}</span>
            <h3>{h}</h3>
            <p>{p}</p>
            <ul>{''.join(f'<li>{x}</li>' for x in items)}</ul>
          </article>''')
    return '      <div class="types rise">\n' + '\n'.join(out) + '\n      </div>'

def prose(paras, link=None):
    body = '\n'.join(f'        <p>{p}</p>' for p in paras)
    if link: body += f'\n        <p><a href="{link[0]}">{link[1]}</a></p>'
    return f'      <div class="prose rise">\n{body}\n      </div>'

def service_graph(slug, lang, title, desc, name, stype, catalog, faqs, crumb):
    return [
        {'@type': 'WebPage', '@id': f'{D}/{slug}#webpage', 'url': f'{D}/{slug}', 'name': title, 'description': desc, 'inLanguage': lang,
         'isPartOf': {'@id': f'{D}/#website'}, 'about': {'@id': f'{D}/#practice'}, 'breadcrumb': {'@id': f'{D}/{slug}#breadcrumb'}, 'mainEntity': {'@id': f'{D}/{slug}#service'}},
        {'@type': 'Service', '@id': f'{D}/{slug}#service', 'name': name, 'serviceType': stype, 'description': desc, 'url': f'{D}/{slug}',
         'provider': {'@id': f'{D}/#practice'}, 'areaServed': ['Malta', 'European Union', 'Spain', 'Latin America', 'United Kingdom'],
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': name, 'itemListElement': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n}} for n in catalog]},
         'offers': {'@type': 'Offer', 'url': f'{HOME[lang]}#quote', 'priceCurrency': 'EUR', 'availability': 'https://schema.org/InStock'}},
        faq_ld(slug, faqs),
        crumbs_ld(slug, [(('Home' if lang == 'en' else 'Inicio'), HOME[lang]), (crumb, f'{D}/{slug}')]),
    ]

# ───────────────────────── Museum and exhibition translation ─────────────────────────
M = {'en': 'museum-translation-services', 'es': 'traduccion-para-museos'}
def museum(lang):
    en = lang == 'en'; slug, other = M[lang], M['es' if en else 'en']; home = '/' if en else '/es'
    title = ('Museum & Exhibition Translation Services in Malta | SP Translations' if en else
             'Traducción para museos y exposiciones en Malta | SP Translations')
    desc = ('Museum and exhibition translation: audio guide scripts, artwork and painting descriptions, cultural heritage and tourism content, visitor information and museum leaflets, in English, Spanish and 120+ languages.' if en else
            'Traducción para museos y exposiciones: guiones de audioguías, descripciones de obras y pinturas, contenido de patrimonio cultural y turismo, información al visitante y folletos de museo, en inglés, español y más de 120 idiomas.')
    h1 = 'Museum and exhibition translation' if en else 'Traducción para museos y exposiciones'
    lede = ('For museums, galleries, heritage sites and tourism operators: exhibition panels, audio guides, artwork descriptions and visitor information, translated to be read, or heard, in front of the object.' if en else
            'Para museos, galerías, sitios patrimoniales y operadores turísticos: paneles de exposición, audioguías, descripciones de obras e información al visitante, traducidos para leerse, o escucharse, frente a la obra.')
    cards = types([
        (('Exhibitions' if en else 'Exposiciones'), ('Museum and exhibition translation' if en else 'Traducción de museos y exposiciones'),
         ('Wall panels, object labels and exhibition catalogues that keep the curator’s voice and fit the space on the wall.' if en else 'Paneles, cartelas y catálogos de exposición que conservan la voz del comisario y caben en el espacio de la pared.'),
         (['Wall panels and object labels', 'Exhibition catalogues', 'Press kits and invitations'] if en else ['Paneles y cartelas', 'Catálogos de exposición', 'Dossieres de prensa e invitaciones'])),
        (('Audio' if en else 'Audio'), ('Audio guide translation' if en else 'Traducción de audioguías'),
         ('Scripts translated for the ear, close to the length of each original track and ready for the voice artist.' if en else 'Guiones traducidos para el oído, con una duración cercana a la de cada pista original y listos para la locución.'),
         (['Audio guide and app scripts', 'Track-by-track timing', 'Family and children’s tours'] if en else ['Guiones de audioguías y apps', 'Duración pista por pista', 'Recorridos familiares e infantiles'])),
        (('Collections' if en else 'Colecciones'), ('Artwork and painting descriptions' if en else 'Descripciones de obras y pinturas'),
         ('Descriptions, captions and artist biographies with the correct art-historical terms and the established titles of works.' if en else 'Descripciones, pies de foto y biografías de artistas con la terminología de historia del arte correcta y los títulos consagrados de las obras.'),
         (['Artwork labels and captions', 'Artist biographies', 'Online collection records'] if en else ['Cartelas y pies de foto', 'Biografías de artistas', 'Fichas de colecciones online'])),
        (('Heritage' if en else 'Patrimonio'), ('Cultural heritage and tourism translation' if en else 'Traducción de patrimonio cultural y turismo'),
         ('Interpretation for historic sites, churches and archaeological parks, and content for tours and destinations.' if en else 'Interpretación de sitios históricos, iglesias y parques arqueológicos, y contenido para recorridos y destinos.'),
         (['Heritage site interpretation', 'Guided tour scripts', 'Destination and tour operator content'] if en else ['Interpretación de sitios patrimoniales', 'Guiones de visitas guiadas', 'Contenido de destinos y operadores turísticos'])),
        (('Visitors' if en else 'Visitantes'), ('Visitor information and museum leaflets' if en else 'Información al visitante y folletos de museo'),
         ('The practical texts every visitor reads: leaflets, maps, opening hours, tickets, rules and accessibility information.' if en else 'Los textos prácticos que lee todo visitante: folletos, planos, horarios, entradas, normas e información de accesibilidad.'),
         (['Leaflets, maps and floor plans', 'Tickets, hours and visitor rules', 'Accessibility and safety notices'] if en else ['Folletos, mapas y planos', 'Entradas, horarios y normas', 'Avisos de accesibilidad y seguridad'])),
        (('Digital' if en else 'Digital'), ('Museum websites and apps' if en else 'Webs y apps de museos'),
         ('Websites, online collections, newsletters and social posts, so the visit starts before visitors arrive.' if en else 'Webs, colecciones online, newsletters y redes sociales, para que la visita empiece antes de llegar.'),
         (['Museum websites', 'Online exhibitions', 'Newsletters and social media'] if en else ['Webs de museos', 'Exposiciones online', 'Newsletters y redes sociales'])),
    ])
    s1 = section('bone', 'what', ('What we translate' if en else 'Qué traducimos'), ('From the wall to the audio guide.' if en else 'De la pared a la audioguía.'),
                 ('Translation for museums, galleries and heritage sites.' if en else 'Traducción para museos, galerías y sitios patrimoniales.'), cards)
    s2 = section('ink', 'craft', ('How we work' if en else 'Cómo trabajamos'), ('Written for visitors.' if en else 'Pensado para el visitante.'),
                 ('Texts that read naturally in front of the object.' if en else 'Textos que se leen con naturalidad frente a la obra.'),
                 standards([
                     (('Written for visitors', 'Clear, short sentences that a visitor can take in while standing, without losing the curator’s meaning or tone.') if en else
                      ('Pensado para el visitante', 'Frases claras y breves que se entienden de pie frente a la obra, sin perder el sentido ni el tono del comisario.')),
                     (('The right terms and titles', 'Art history, architecture and archaeology terms are used precisely, and works, artists and places keep their established names in each language.') if en else
                      ('Términos y títulos correctos', 'La terminología de historia del arte, arquitectura y arqueología se usa con precisión, y obras, artistas y lugares mantienen su nombre consagrado en cada idioma.')),
                     (('Fits the panel and the track', 'We work to the character counts of your panels and labels, and keep audio scripts close to the length of each recorded track.') if en else
                      ('Cabe en el panel y en la pista', 'Trabajamos con el número de caracteres de tus paneles y cartelas, y mantenemos los guiones de audio cerca de la duración de cada pista grabada.')),
                 ]))
    s3 = section('bone', 'languages', ('Languages' if en else 'Idiomas'), ('For the visitors you welcome.' if en else 'Para los visitantes que recibes.'),
                 ('In the languages your visitors speak.' if en else 'En los idiomas de tus visitantes.'),
                 prose([('Spanish and English are handled in-house. We also translate museum and heritage content into Italian, French, German and the other languages we work in regularly, and into more than 120 languages through our professional translator network.' if en else
                         'El español y el inglés los trabajamos en nuestro equipo. También traducimos contenido de museos y patrimonio al italiano, francés, alemán y los demás idiomas con los que trabajamos habitualmente, y a más de 120 idiomas a través de nuestra red profesional de traductores.')],
                       (('/languages', 'See all our languages →') if en else ('/idiomas', 'Ver todos nuestros idiomas →'))))
    faqs = [
        (('What files can you work with?', 'Word, Excel and PDF, or text exported from your exhibition design files. We return the translation ready for your designer and flag any line that runs longer than the space allows.') if en else
         ('¿Con qué archivos pueden trabajar?', 'Word, Excel y PDF, o el texto exportado de tus archivos de diseño de la exposición. Te devolvemos la traducción lista para tu diseñador y marcamos cualquier línea que supere el espacio disponible.')),
        (('Do you translate audio guide scripts for recording?', 'Yes. We translate scripts to be spoken, keep each track close to its original length and can mark how names should be pronounced for the voice artist.') if en else
         ('¿Traducen guiones de audioguías para grabar?', 'Sí. Traducimos los guiones para ser locutados, mantenemos cada pista cerca de su duración original y podemos indicar cómo pronunciar los nombres para el locutor.')),
        (('Can you translate an exhibition into several languages at once?', 'Yes. We coordinate all the languages from one set of source texts, so panels, labels and the audio guide say the same thing in every language.') if en else
         ('¿Pueden traducir una exposición a varios idiomas a la vez?', 'Sí. Coordinamos todos los idiomas a partir de un mismo conjunto de textos, para que paneles, cartelas y audioguía digan lo mismo en cada idioma.')),
        (('How are museum projects priced?', 'Usually per word, quoted once we have seen the texts. Send a sample or the full list of panels and labels, and we confirm the price and delivery date in your quotation.') if en else
         ('¿Cómo se presupuestan los proyectos para museos?', 'Normalmente por palabra, con cotización tras ver los textos. Envía una muestra o la lista completa de paneles y cartelas, y te confirmamos precio y plazo en la cotización.')),
    ]
    rel = ([('languages', 'Our languages', 'Spanish, English and twelve more core languages, plus 120+ through our network.'),
            ('content-writing-services', 'Content writing', 'Original content in 14 languages for websites, blogs and campaigns.'),
            ('website-translation-services', 'Website translation & localisation', 'Websites, apps and multilingual SEO.')] if en else
           [('idiomas', 'Nuestros idiomas', 'Español, inglés y doce idiomas principales más, además de más de 120 a través de nuestra red.'),
            ('redaccion-de-contenidos', 'Redacción de contenidos', 'Contenido original en 14 idiomas para webs, blogs y campañas.'),
            ('traduccion-de-paginas-web', 'Traducción de páginas web', 'Webs, apps y SEO multilingüe.')])
    crumb = 'Museum translation' if en else 'Traducción para museos'
    main = pagehead([(('Home' if en else 'Inicio'), home), (crumb, None)], h1, lede) + s1 + s2 + s3 + faq(faqs, lang) + related(lang, rel) + '\n' + start_section(lang) + '\n'
    catalog = (['Museum and exhibition translation', 'Audio guide translation', 'Artwork and painting descriptions', 'Cultural heritage and tourism translation', 'Visitor information and museum leaflets'] if en else
               ['Traducción de museos y exposiciones', 'Traducción de audioguías', 'Descripciones de obras y pinturas', 'Traducción de patrimonio cultural y turismo', 'Información al visitante y folletos de museo'])
    page(lang, slug, other, title, desc, service_graph(slug, lang, title, desc, h1, ('Museum translation' if en else 'Traducción para museos'), catalog, faqs, crumb), main)

# ───────────────────────── Content writing ─────────────────────────
W = {'en': 'content-writing-services', 'es': 'redaccion-de-contenidos'}
def writing(lang):
    en = lang == 'en'; slug, other = W[lang], W['es' if en else 'en']; home = '/' if en else '/es'
    title = ('Content Writing Services in 14 Languages | SP Translations' if en else
             'Redacción de contenidos en 14 idiomas | SP Translations')
    desc = ('Content writing services in 14 languages, including English, Spanish, Italian, French and German: website copy, blog posts and SEO articles, marketing and brand copy, and product descriptions, written from scratch for your audience and market.' if en else
            'Servicios de redacción de contenidos en 14 idiomas, como español, inglés, italiano, francés y alemán: textos para webs, artículos de blog y SEO, textos de marketing y marca, y descripciones de productos, escritos desde cero para tu público y tu mercado.')
    h1 = 'Content writing services' if en else 'Redacción de contenidos'
    lede = ('Original content for websites, blogs, brands and campaigns in English, Spanish, Italian, French, German and nine more languages, written by native writers who know the market and how content is found online.' if en else
            'Contenido original para webs, blogs, marcas y campañas en español, inglés, italiano, francés, alemán y nueve idiomas más, escrito por redactores nativos que conocen el mercado y cómo se encuentra el contenido en internet.')
    cards = types([
        (('Web' if en else 'Web'), ('Website copy' if en else 'Textos para webs'),
         ('Home, about and service pages that explain what you do clearly and lead visitors to get in touch.' if en else 'Páginas de inicio, de empresa y de servicios que explican con claridad lo que haces y llevan al visitante a contactarte.'),
         (['Home and landing pages', 'Service and about pages', 'Calls to action and forms'] if en else ['Páginas de inicio y landing pages', 'Páginas de servicios y de empresa', 'Llamadas a la acción y formularios'])),
        (('Blog' if en else 'Blog'), ('Blog posts and articles' if en else 'Artículos y posts de blog'),
         ('Articles, guides and news that answer your customers’ questions and keep your site fresh.' if en else 'Artículos, guías y noticias que responden a las preguntas de tus clientes y mantienen tu web viva.'),
         (['How-to guides and explainers', 'News and updates', 'Long-form articles'] if en else ['Guías prácticas y explicativas', 'Noticias y novedades', 'Artículos extensos'])),
        (('SEO' if en else 'SEO'), ('SEO content' if en else 'Contenido SEO'),
         ('Content planned around what people actually search, with titles, headings and meta descriptions written to be found.' if en else 'Contenido planificado según lo que la gente busca realmente, con títulos, encabezados y meta descripciones pensados para posicionar.'),
         (['Keyword research by market', 'Meta titles and descriptions', 'SEO landing pages'] if en else ['Investigación de palabras clave por mercado', 'Meta títulos y descripciones', 'Landing pages SEO'])),
        (('Marketing' if en else 'Marketing'), ('Marketing and brand copy' if en else 'Textos de marketing y marca'),
         ('Campaigns, newsletters, social posts and taglines in your brand’s voice.' if en else 'Campañas, newsletters, publicaciones en redes y eslóganes con la voz de tu marca.'),
         (['Email and newsletters', 'Social media posts', 'Taglines and ad copy'] if en else ['Email y newsletters', 'Publicaciones en redes sociales', 'Eslóganes y textos de anuncios'])),
        (('Products' if en else 'Productos'), ('Product and service descriptions' if en else 'Descripciones de productos y servicios'),
         ('Descriptions for online shops, catalogues and brochures that are accurate, consistent and persuasive.' if en else 'Descripciones para tiendas online, catálogos y folletos, precisas, coherentes y persuasivas.'),
         (['E-commerce product pages', 'Catalogues and brochures', 'Company profiles'] if en else ['Fichas de producto de e-commerce', 'Catálogos y folletos', 'Presentaciones de empresa'])),
        (('Multilingual' if en else 'Multilingüe'), ('Multilingual content' if en else 'Contenido multilingüe'),
         ('One brief, written natively in each language you need, so every version reads as an original rather than a translation.' if en else 'Un solo briefing, escrito de forma nativa en cada idioma que necesites, para que cada versión se lea como un original y no como una traducción.'),
         (['Several languages from one brief', 'Spain or Latin American Spanish', 'Consistent message in every language'] if en else ['Varios idiomas desde un briefing', 'Español de España o de Latinoamérica', 'Mismo mensaje en todos los idiomas'])),
    ])
    s1 = section('bone', 'what', ('What we write' if en else 'Qué escribimos'), ('Written from scratch.' if en else 'Escrito desde cero.'),
                 ('Content written for your audience, in their language.' if en else 'Contenido escrito para tu público, en su idioma.'), cards)
    from build import steps_html as steps
    s2 = section('ink', 'process', ('Process' if en else 'Proceso'), ('From brief to publication.' if en else 'Del briefing a la publicación.'),
                 ('How a writing project works.' if en else 'Cómo funciona un proyecto de redacción.'),
                 steps([
                     (('Brief', 'Tell us your audience, goals, tone, keywords and any examples you like. We confirm scope, price and delivery date.') if en else
                      ('Briefing', 'Cuéntanos tu público, objetivos, tono, palabras clave y ejemplos que te gusten. Confirmamos alcance, precio y plazo.')),
                     (('Outline', 'For longer pieces we agree the structure and headings first, so the content goes in the right direction from the start.') if en else
                      ('Esquema', 'Para piezas largas acordamos primero la estructura y los encabezados, para que el contenido vaya en la dirección correcta desde el principio.')),
                     (('Writing', 'The content is written from scratch by a native writer of each language, in your brand’s voice.') if en else
                      ('Redacción', 'Un redactor nativo de cada idioma escribe el contenido desde cero, con la voz de tu marca.')),
                     (('Review and delivery', 'We revise based on your feedback and deliver ready to publish, with headings, meta title and meta description where needed.') if en else
                      ('Revisión y entrega', 'Revisamos según tus comentarios y entregamos el texto listo para publicar, con encabezados, meta título y meta descripción cuando hace falta.')),
                 ]))
    s3 = section('bone', 'seo', ('SEO' if en else 'SEO'), ('Found and read.' if en else 'Encontrado y leído.'),
                 ('Written for people and for search engines.' if en else 'Escrito para personas y para buscadores.'),
                 prose([('Good content answers the question the reader typed. We research the terms people use in each market, which often differ from one language to another, and even between Spain and Latin America, and use them naturally in titles, headings and copy, without stuffing keywords.' if en else
                         'Un buen contenido responde a la pregunta que escribió el lector. Investigamos los términos que se usan en cada mercado, que a menudo cambian de un idioma a otro, e incluso entre España y Latinoamérica, y los usamos con naturalidad en títulos, encabezados y textos, sin forzar palabras clave.'),
                        ('Already have content in one language? We can also <a href="/website-translation-services">translate and localise it</a> instead.' if en else
                         '¿Ya tienes contenido en un idioma? También podemos <a href="/traduccion-de-paginas-web">traducirlo y localizarlo</a>.')]))
    faqs = [
        (('Which languages do you write in?', 'All our core languages: English, Spanish, Italian, French, German, Polish, Romanian, Russian, Portuguese, Turkish, Greek, Dutch, Serbian and Maltese. For Spanish we write for Spain or for Latin America, or for a specific country if your audience is there.') if en else
         ('¿En qué idiomas redactan?', 'En todos nuestros idiomas principales: español, inglés, italiano, francés, alemán, polaco, rumano, ruso, portugués, turco, griego, neerlandés, serbio y maltés. En español escribimos para España o para Latinoamérica, o para un país concreto si tu público está allí.')),
        (('Is the content original?', 'Yes. Every piece is written from scratch for your brief and is never copied from other sites.') if en else
         ('¿El contenido es original?', 'Sí. Cada pieza se escribe desde cero según tu briefing y nunca se copia de otras webs.')),
        (('Can you write the same content in several languages?', 'Yes. From one brief we write each version natively, so every language reads as an original rather than a translation, with the same message.') if en else
         ('¿Pueden escribir el mismo contenido en varios idiomas?', 'Sí. A partir de un briefing escribimos cada versión de forma nativa, para que cada idioma se lea como un original y no como una traducción, con el mismo mensaje.')),
        (('How is content writing priced?', 'Per word or per piece, depending on the project. Send us your brief and we confirm the price and delivery date in your quotation.') if en else
         ('¿Cómo se presupuesta la redacción?', 'Por palabra o por pieza, según el proyecto. Envíanos tu briefing y te confirmamos precio y plazo en la cotización.')),
    ]
    rel = ([('website-translation-services', 'Website translation & localisation', 'Translate the content you already have, with multilingual SEO.'),
            ('museum-translation-services', 'Museum and exhibition translation', 'Exhibition panels, audio guides and visitor information.'),
            ('igaming-translation-services', 'iGaming translation', 'Casino, sportsbook and affiliate content.')] if en else
           [('traduccion-de-paginas-web', 'Traducción de páginas web', 'Traduce el contenido que ya tienes, con SEO multilingüe.'),
            ('traduccion-para-museos', 'Traducción para museos y exposiciones', 'Paneles de exposición, audioguías e información al visitante.'),
            ('traduccion-igaming', 'Traducción para iGaming', 'Contenido de casino, apuestas y afiliación.')])
    crumb = 'Content writing' if en else 'Redacción de contenidos'
    main = pagehead([(('Home' if en else 'Inicio'), home), (crumb, None)], h1, lede) + s1 + s2 + s3 + faq(faqs, lang) + related(lang, rel) + '\n' + start_section(lang) + '\n'
    catalog = (['Website copywriting', 'Blog posts and articles', 'SEO content writing', 'Marketing and brand copy', 'Product and service descriptions', 'Multilingual content in 14 languages'] if en else
               ['Redacción de textos para webs', 'Artículos y posts de blog', 'Redacción de contenido SEO', 'Textos de marketing y marca', 'Descripciones de productos y servicios', 'Contenido multilingüe en 14 idiomas'])
    page(lang, slug, other, title, desc, service_graph(slug, lang, title, desc, h1, ('Content writing' if en else 'Redacción de contenidos'), catalog, faqs, crumb), main)

if __name__ == '__main__':
    for lang in ('en', 'es'):
        museum(lang); writing(lang)
    print('built:', *M.values(), *W.values())
