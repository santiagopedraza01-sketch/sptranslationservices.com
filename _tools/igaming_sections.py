"""One-off: add the content-types, why-choose-us, translators and order sections to the
iGaming pages (EN/ES), retitle testimonials/related/start, and add two FAQs.
Safe to re-run: each block is skipped if its section id is already on the page."""
import re, json

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') if '&amp;' not in s else s

def types(items):
    out=[]
    for tag,h,p,lis in items:
        out.append(f'''          <article class="type">
            <span class="type__tag">{tag}</span>
            <h3>{h}</h3>
            <p>{p}</p>
            <ul>{''.join(f'<li>{l}</li>' for l in lis)}</ul>
          </article>''')
    return '\n'.join(out)

def section(cls,sid,mark,side,h2,body):
    return f'''<section class="section section--{cls}" id="{sid}">
  <div class="shell spread">
    <div class="spread__index rise">
      <span class="mark">{mark}</span>
      <p>{side}</p>
    </div>
    <div>
      <h2 class="h2 opening rise" style="margin-bottom:clamp(30px,4vw,46px)">{h2}</h2>
{body}
    </div>
  </div>
</section>
'''

def why(items):
    nums=['I','II','III','IV','V','VI','VII','VIII']
    return '      <ol class="why rise">\n'+'\n'.join(
        f'        <li class="why__item"><span class="why__num">{n}</span><div><h3>{h}</h3><p>{p}</p></div></li>' for n,(h,p) in zip(nums,items))+'\n      </ol>'

def langs(title,items,foot):
    lis=''.join(f'<li><a href="{u}">{n}</a></li>' for n,u in items)
    return f'''      <div class="langs rise">
        <h3 class="langs__h">{title}</h3>
        <ul class="langs__list">{lis}</ul>
        <p class="langs__foot">{foot}</p>
      </div>'''

def steps(items):
    return '      <div class="standards rise">\n'+'\n'.join(
        f'<div class="standards__item"><span class="standards__num">{i+1:02d}</span><h3 class="h3">{h}</h3><p>{p}</p></div>' for i,(h,p) in enumerate(items))+'\n      </div>'

C = {}
C['en'] = dict(
 f='igaming-translation-services.html', quote='/#quote',
 wa='https://wa.me/35679066398?text=Hello%2C%20I%20would%20like%20a%20quote%20for%20an%20iGaming%20translation%20project.',
 types=('warm','content-types','Content we translate','Every touchpoint a player sees.','Trusted to translate every type of iGaming content.',[
  ('Product','iGaming websites and apps','Your whole front end, from the lobby and cashier to account settings, localised in the file formats your developers already use. Variables, HTML tags and character limits stay intact, so strings drop straight back into the build.',['Lobby, navigation and promotion pages','Registration, KYC and cashier flows','iOS and Android strings: JSON, XLIFF, PO, CSV']),
  ('Studios','Slot games','Game rules, paytables, feature names and in-game messages translated so the mechanics are crystal clear and the theme still feels exciting, within tight UI space and the wording test labs expect.',['Rules, paytables and help screens','Bonus rounds, features and symbol names','Win messages and in-game UI']),
  ('SEO','Casino and sports betting SEO content','Native-language articles and landing pages built around what players in each market actually search for. We research local keywords instead of translating English ones, and write content that ranks and converts.',['Local keyword research and mapping','Casino, slot and betting guides','Meta titles, descriptions and headings']),
  ('Affiliates','Affiliate SEO content','Operator reviews, bonus pages and comparison tables for affiliates who need volume and quality in many markets at once, written to each market’s advertising rules.',['Casino and bookmaker reviews and toplists','Bonus, payment method and app pages','Regular content refreshes at scale']),
  ('Reviews','Slot reviews and descriptions','Slot reviews and short game descriptions that explain RTP, volatility, features and max win accurately, in a voice your players actually want to read.',['In-depth slot reviews','Short lobby and provider descriptions','Accurate RTP, volatility and feature data']),
  ('CRM','Player communication','Emails, push notifications, SMS and support replies that sound like your brand in every language, and stay clear about bonus terms and safer gambling.',['Welcome, retention and VIP journeys','Push, SMS and in-app messages','Help centre articles and support macros']),
  ('Marketing','Marketing materials and press releases','Campaigns, sponsorship news and press releases transcreated for each market, so your headline lands as well in Milan or São Paulo as it does in London.',['Press releases and announcements','Ads, banners and social posts','Sales decks and trade show materials']),
  ('Compliance','Terms, policies and safer gambling','Terms and conditions, bonus rules, privacy policies and responsible gambling pages translated precisely, using the terminology each regulator expects.',['T&amp;Cs, bonus and wagering rules','Responsible and safer gambling pages','KYC, AML and privacy policies']),
 ]),
 why=('bone','why','Why SP Translations','What you get from day one.','Why choose SP Translations as your iGaming translation agency?',[
  ('Based in Malta, the home of iGaming','We work in the same ecosystem as MGA-licensed operators, studios and affiliates, so we understand your products, your release cycles and your regulators.'),
  ('Human translation by native speakers','Every word is translated and reviewed by people, never published as raw machine output. Translators work only into their native language and know the sector’s terminology and slang.'),
  ('Easy ordering, no portal needed','Send files through the quote form, by email or on WhatsApp. You get a clear quotation, usually within a few working hours, and we fit around your tools and workflow.'),
  ('A dedicated contact for every client','One person looks after your account, glossary and deadlines across every language, so you never have to explain a brief twice.'),
  ('Competitive, transparent pricing','Rates start at €0.1 per word, with every project quoted in writing before work starts. Repeated and updated content is priced accordingly, so there are no surprises on the invoice.'),
  ('Fast turnaround for launches','Standard projects in 24–48 hours, with priority same-day or overnight delivery for launches, promotions and urgent fixes, subject to availability.'),
  ('Security and confidentiality','NDAs on request, confidential file handling and access limited to the translators on your project. Unreleased games and promotions stay private.'),
  ('Regulatory compliance','Compliance and responsible gambling text uses each market’s established terminology, and we flag wording that needs a local version. <a href="#markets">See the markets we cover</a>.'),
 ]),
 tr=('bone','translators','Our translators','Native speakers who know the sector.','Meet our experienced iGaming translators.',
  '''      <div class="prose rise" style="margin-bottom:clamp(30px,4vw,46px)">
        <p>Behind every project is a team of native-speaking translators who know iGaming from the inside. They know the difference between a free bet and a bet credit, between RTP and volatility, and between a bonus page that converts and one that breaks the advertising rules. Projects are led by our founder, Santiago Pedraza Castillo, and each language is handled by a specialist who translates only into their mother tongue.</p>
      </div>''',
  [('Sector specialists','Translators matched to your vertical: casino, sportsbook, affiliate SEO, game rules or compliance.'),
   ('Native in every market','Including Spanish for Spain and each Latin American market, and Portuguese for Brazil.'),
   ('Consistent over time','The same translators stay on your account, working from your glossary and style guide.')],
  ('iGaming languages we cover most often',[('English','/website-translation-services'),('Spanish','/igaming-translation-latam'),('Italian','/italian-translation-malta'),('French','/french-translation-malta'),('German','/german-translation-malta'),('Polish','/polish-translation-malta'),('Romanian','/romanian-translation-malta'),('Russian','/russian-translation-malta'),('Portuguese','/portuguese-translation-malta'),('Turkish','/turkish-translation-malta'),('Greek','/greek-translation-malta'),('Dutch','/dutch-translation-malta'),('Serbian','/serbian-translation-malta'),('Maltese','/maltese-translation-malta')],
   'Need another market? <strong>120+ more languages</strong> through our translator network. <a href="/translators">Meet the team →</a>')),
 order=('warm','order','Order now','Three steps to localised content.','Order iGaming translations now.',[
  ('Send your files','Upload files, share a link to your site or describe the project. Any format works: XLIFF, JSON, Excel, Word or a CMS export.'),
  ('Get your quotation','A clear price and delivery date, usually within a few working hours. Free and with no obligation.'),
  ('Receive and go live','Translated, reviewed files returned ready to import, with updates handled whenever your content changes.')],
  'Request a quote','Message on WhatsApp'),
 testimonials_h2=('What iGaming clients say.','Why clients love working with us.'),
 related=('<span class="mark">Keep reading</span>','<span class="mark">Featured articles</span>'),
 start=(r'<p><strong>Ready to start\?</strong>.*?</p>','<p><strong>Kickstart your project today.</strong> Send your files or a link to your site and receive a fixed quotation, with no obligation.</p>'),
 faqs=[('Do you use machine translation?','No. Every iGaming text is translated and reviewed by native-speaking professionals. If you already have machine-translated content, we can post-edit it to publishing quality, and we tell you honestly when a rewrite is the better option.'),
       ('Can you write original iGaming SEO content, not just translate it?','Yes. We write native-language casino, slot and betting content from scratch, based on local keyword research, in all our core languages. See <a href="/content-writing-services">content writing</a>.')],
 recolor={'verticals':'bone','localise':'warm','testimonials':'bone','latam':'warm','faq':'bone','related':'warm'},
)
C['es'] = dict(
 f='traduccion-igaming.html', quote='/es#quote',
 wa='https://wa.me/35679066398?text=Hola%2C%20me%20gustar%C3%ADa%20solicitar%20una%20cotizaci%C3%B3n%20para%20un%20proyecto%20de%20iGaming.',
 types=('warm','content-types','Contenido que traducimos','Cada punto de contacto con el jugador.','Confían en nosotros para traducir todo tipo de contenido de iGaming.',[
  ('Producto','Webs y apps de iGaming','Todo tu front end, del lobby y el cajero a la configuración de la cuenta, localizado en los formatos que ya usan tus desarrolladores. Variables, etiquetas HTML y límites de caracteres se mantienen intactos, para que los textos vuelvan directamente al build.',['Lobby, navegación y páginas de promociones','Registro, KYC y flujos de cajero','Textos de iOS y Android: JSON, XLIFF, PO, CSV']),
  ('Estudios','Tragamonedas','Reglas, tablas de pagos, nombres de funciones y mensajes del juego traducidos para que la mecánica quede clarísima y la temática siga emocionando, dentro del espacio de la interfaz y con la terminología que esperan los laboratorios.',['Reglas, tablas de pagos y pantallas de ayuda','Rondas de bonificación, funciones y símbolos','Mensajes de premio e interfaz del juego']),
  ('SEO','Contenido SEO de casino y apuestas deportivas','Artículos y landing pages en el idioma nativo, construidos en torno a lo que los jugadores de cada mercado buscan de verdad. Investigamos palabras clave locales en lugar de traducir las inglesas, y escribimos contenido que posiciona y convierte.',['Investigación y mapeo de palabras clave locales','Guías de casino, tragamonedas y apuestas','Meta títulos, descripciones y encabezados']),
  ('Afiliados','Contenido SEO para afiliados','Reseñas de operadores, páginas de bonos y tablas comparativas para afiliados que necesitan volumen y calidad en muchos mercados a la vez, según las normas de publicidad de cada uno.',['Reseñas y rankings de casinos y casas de apuestas','Páginas de bonos, métodos de pago y apps','Actualizaciones periódicas de contenido a escala']),
  ('Reseñas','Reseñas y descripciones de tragamonedas','Reseñas de tragamonedas y descripciones breves que explican con precisión el RTP, la volatilidad, las funciones y el premio máximo, con una voz que tus jugadores quieran leer.',['Reseñas completas de tragamonedas','Descripciones breves para lobby y proveedores','Datos precisos de RTP, volatilidad y funciones']),
  ('CRM','Comunicación con jugadores','Emails, notificaciones push, SMS y respuestas de soporte que suenan a tu marca en cada idioma y son claros sobre los términos de los bonos y el juego seguro.',['Recorridos de bienvenida, retención y VIP','Push, SMS y mensajes in-app','Artículos del centro de ayuda y macros de soporte']),
  ('Marketing','Materiales de marketing y notas de prensa','Campañas, patrocinios y notas de prensa transcreados para cada mercado, para que tu titular funcione igual de bien en Ciudad de México o São Paulo que en Madrid.',['Notas de prensa y anuncios','Anuncios, banners y redes sociales','Presentaciones comerciales y material para ferias']),
  ('Cumplimiento','Términos, políticas y juego seguro','Términos y condiciones, reglas de bonos, políticas de privacidad y páginas de juego responsable traducidos con precisión, con la terminología que espera cada regulador.',['T&amp;C, reglas de bonos y rollover','Páginas de juego responsable y seguro','Políticas de KYC, AML y privacidad']),
 ]),
 why=('bone','why','Por qué SP Translations','Lo que obtienes desde el primer día.','¿Por qué elegir SP Translations como agencia de traducción para iGaming?',[
  ('En Malta, la casa del iGaming','Trabajamos en el mismo ecosistema que los operadores, estudios y afiliados con licencia de la MGA, así que entendemos tus productos, tus ciclos de lanzamiento y a tus reguladores.'),
  ('Traducción humana por nativos','Cada palabra la traducen y revisan personas; nunca publicamos traducción automática sin revisar. Los traductores trabajan solo hacia su lengua materna y conocen la terminología y la jerga del sector.'),
  ('Pedidos fáciles, sin portales','Envía tus archivos con el formulario de cotización, por email o por WhatsApp. Recibes una cotización clara, normalmente en pocas horas laborables, y nos adaptamos a tus herramientas y flujo de trabajo.'),
  ('Un contacto dedicado para cada cliente','Una sola persona gestiona tu cuenta, tu glosario y tus plazos en todos los idiomas, para que nunca tengas que explicar un encargo dos veces.'),
  ('Precios competitivos y transparentes','Tarifas desde 0,1 € por palabra y cada proyecto cotizado por escrito antes de empezar. El contenido repetido o actualizado se tarifica en consecuencia, sin sorpresas en la factura.'),
  ('Entregas rápidas para lanzamientos','Proyectos estándar en 24–48 horas, y entrega prioritaria el mismo día o durante la noche para lanzamientos, promociones y correcciones urgentes, según disponibilidad.'),
  ('Seguridad y confidencialidad','NDA bajo petición, tratamiento confidencial de los archivos y acceso limitado a los traductores de tu proyecto. Los juegos y promociones sin lanzar se quedan en privado.'),
  ('Cumplimiento normativo','Los textos de cumplimiento y juego responsable usan la terminología establecida en cada mercado, y señalamos lo que necesita una versión local. <a href="#markets">Ver los mercados que cubrimos</a>.'),
 ]),
 tr=('bone','translators','Nuestros traductores','Nativos que conocen el sector.','Conoce a nuestros traductores expertos en iGaming.',
  '''      <div class="prose rise" style="margin-bottom:clamp(30px,4vw,46px)">
        <p>Detrás de cada proyecto hay un equipo de traductores nativos que conocen el iGaming desde dentro. Saben la diferencia entre una apuesta gratis y un crédito de apuesta, entre el RTP y la volatilidad, y entre una página de bonos que convierte y otra que incumple las normas de publicidad. Los proyectos los dirige nuestro fundador, Santiago Pedraza Castillo, y cada idioma lo trabaja un especialista que solo traduce hacia su lengua materna.</p>
      </div>''',
  [('Especialistas del sector','Traductores asignados según tu vertical: casino, apuestas deportivas, SEO de afiliados, reglas de juego o cumplimiento.'),
   ('Nativos en cada mercado','Incluido español para España y cada mercado latinoamericano, y portugués para Brasil.'),
   ('Constancia en el tiempo','Los mismos traductores se quedan en tu cuenta y trabajan con tu glosario y tu guía de estilo.')],
  ('Idiomas de iGaming que más trabajamos',[('Inglés','/traduccion-de-paginas-web'),('Español','/traduccion-igaming-latinoamerica'),('Italiano','/traduccion-italiano-malta'),('Francés','/traduccion-frances-malta'),('Alemán','/traduccion-aleman-malta'),('Polaco','/traduccion-polaco-malta'),('Rumano','/traduccion-rumano-malta'),('Ruso','/traduccion-ruso-malta'),('Portugués','/traduccion-portugues-malta'),('Turco','/traduccion-turco-malta'),('Griego','/traduccion-griego-malta'),('Neerlandés','/traduccion-neerlandes-malta'),('Serbio','/traduccion-serbio-malta'),('Maltés','/traduccion-maltes-malta')],
   '¿Necesitas otro mercado? <strong>Más de 120 idiomas</strong> a través de nuestra red de traductores. <a href="/traductores">Conoce al equipo →</a>')),
 order=('warm','order','Haz tu pedido','Tres pasos hacia el contenido localizado.','Encarga ya tus traducciones de iGaming.',[
  ('Envía tus archivos','Sube los archivos, comparte el enlace de tu web o describe el proyecto. Cualquier formato sirve: XLIFF, JSON, Excel, Word o una exportación de tu CMS.'),
  ('Recibe tu cotización','Precio y plazo de entrega claros, normalmente en pocas horas laborables. Gratis y sin compromiso.'),
  ('Recibe y publica','Archivos traducidos y revisados, listos para importar, y actualizaciones cada vez que cambie tu contenido.')],
  'Solicitar una cotización','Escribir por WhatsApp'),
 testimonials_h2=None,
 related=('<span class="mark">Sigue leyendo</span>','<span class="mark">Artículos destacados</span>'),
 start=(r'<p><strong>¿Lista tu documentación\?</strong>.*?</p>','<p><strong>Da el primer paso hoy.</strong> Envíanos tus archivos o el enlace de tu web y recibe una cotización fija, sin compromiso.</p>'),
 faqs=[('¿Usan traducción automática?','No. Todo el contenido de iGaming lo traducen y revisan profesionales nativos. Si ya tienes contenido traducido automáticamente, podemos poseditarlo hasta calidad de publicación, y te decimos con sinceridad cuándo conviene más reescribirlo.'),
       ('¿Pueden redactar contenido SEO original de iGaming, no solo traducirlo?','Sí. Redactamos desde cero contenido de casino, tragamonedas y apuestas en el idioma nativo, a partir de una investigación de palabras clave local, en todos nuestros idiomas principales. Consulta <a href="/redaccion-de-contenidos">redacción de contenidos</a>.')],
 recolor={'verticals':'bone','localise':'warm'},
)

def strip(h): return re.sub(r'<[^>]+>','',h)

for lang,c in C.items():
    f=c['f']; s=open(f,encoding='utf-8').read()
    def before(sid,block):
        global s
        if f'id="{block[1]}"' in block[0] and False: pass
    # recolour existing sections
    for sid,cls in c['recolor'].items():
        s=re.sub(rf'<section class="section section--\w+" id="{sid}">',f'<section class="section section--{cls}" id="{sid}">',s)
    # content types: after #content
    t=c['types']
    if 'id="content-types"' not in s:
        sec=section(t[0],t[1],t[2],t[3],t[4],'      <div class="types types--2 rise">\n'+types(t[5])+'\n      </div>')
        s=s.replace('<section class="section section--bone" id="verticals">',sec+'<section class="section section--bone" id="verticals">',1)
    # why: before #markets
    w=c['why']
    if 'id="why"' not in s:
        sec=section(w[0],w[1],w[2],w[3],w[4],why(w[5]))
        s=re.sub(r'(<section class="section section--\w+" id="markets">)',lambda m:sec+m.group(1),s,count=1)
    # translators + order: after #process
    tr=c['tr']; o=c['order']
    if 'id="translators"' not in s:
        body=tr[5]+'\n      <div class="standards rise" style="margin-bottom:clamp(30px,4vw,46px)">\n'+'\n'.join(
            f'<div class="standards__item"><span class="standards__num">{n}</span><h3 class="h3">{h}</h3><p>{p}</p></div>' for n,(h,p) in zip(['I','II','III'],tr[6]))+'\n      </div>\n'+langs(tr[7][0],tr[7][1],tr[7][2])
        sec=section(tr[0],tr[1],tr[2],tr[3],tr[4],body)
        btns=f'''      <p class="rise" style="display:flex;flex-wrap:wrap;gap:12px;margin-top:clamp(30px,4vw,46px)">
        <a class="btn btn--ink" href="{c['quote']}">{o[6]}<span class="btn__arrow" aria-hidden="true"></span></a>
        <a class="btn btn--line" href="{c['wa']}" target="_blank" rel="noopener">{o[7]}</a>
      </p>'''
        sec+=section(o[0],o[1],o[2],o[3],o[4],steps(o[5])+'\n'+btns)
        i=s.index('id="process"'); j=s.index('</section>',i)+len('</section>\n')
        s=s[:j]+sec+s[j:]
    if c['testimonials_h2']:
        s=s.replace(c['testimonials_h2'][0],c['testimonials_h2'][1])
    s=s.replace(*c['related'])
    s=re.sub(c['start'][0],c['start'][1],s,count=1,flags=re.S)
    # FAQs: html + JSON-LD
    for q,a in c['faqs']:
        if q in s: continue
        i=s.index('<div class="questions">'); j=s.index('\n      </div>',i)
        s=s[:j]+f'\n        <details>\n          <summary>{q}</summary>\n          <p>{a}</p>\n        </details>'+s[j:]
        k=s.index('"mainEntity": [',s.index('"@type": "FAQPage"')); depth=0
        p=s.index('[',k)
        for x in range(p,len(s)):
            if s[x]=='[': depth+=1
            elif s[x]==']':
                depth-=1
                if depth==0: end=x; break
        last=s.rstrip()[:0]
        item=',\n        {\n          "@type": "Question",\n          "name": '+json.dumps(q,ensure_ascii=False)+',\n          "acceptedAnswer": {\n            "@type": "Answer",\n            "text": '+json.dumps(strip(a),ensure_ascii=False)+'\n          }\n        }'
        body=s[p:end].rstrip()
        s=s[:p]+body+item+'\n      '+s[end:]
    open(f,'w',encoding='utf-8').write(s)
    print(f,'ok')
