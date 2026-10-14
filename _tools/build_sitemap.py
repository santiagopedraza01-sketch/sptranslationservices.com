"""Rebuild the XML sitemaps (Yoast-style index + page and guide sitemaps).

Run from the site root:  python3 _tools/build_sitemap.py
- sitemap.xml        index of the sitemaps below (robots.txt points here)
- page-sitemap.xml   home, service, company and legal pages
- post-sitemap.xml   guides
Each URL's <lastmod> is the time of the last git commit that touched the page
(or now, if it has uncommitted changes). Entries are listed in the order the
pages were first published, oldest first, with the two home pages at the top. main-sitemap.xsl renders them as a table in a
browser. The _tools folder is not published (Jekyll skips folders starting with _).
"""
import glob, os, re, subprocess
from datetime import datetime, timezone

BASE = 'https://sptranslationservices.com'
XSL = '<?xml-stylesheet type="text/xsl" href="/main-sitemap.xsl"?>'

def lastmod(path):
    dirty = subprocess.run(['git', 'status', '--porcelain', '--', path], capture_output=True, text=True).stdout.strip()
    iso = None if dirty else subprocess.run(['git', 'log', '-1', '--format=%cI', '--', path], capture_output=True, text=True).stdout.strip()
    dt = datetime.fromisoformat(iso) if iso else datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0)

def created(path):
    out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%cI', '--', path], capture_output=True, text=True).stdout.split()
    return datetime.fromisoformat(out[-1]).astimezone(timezone.utc) if out else datetime.now(timezone.utc)

def fmt(dt): return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')

def page_info(path):
    s = open(path, encoding='utf-8').read()
    loc = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
    alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', s)
    imgs = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', s):
        if 'crest' in src or src.startswith('data:'): continue
        u = src if src.startswith('http') else f'{BASE}/{src.lstrip("/")}'
        if u not in imgs: imgs.append(u)
    return dict(loc=loc, alts=alts, imgs=imgs, mod=lastmod(path), born=created(path))

def urlset(entries):
    out = ['<?xml version="1.0" encoding="UTF-8"?>', XSL,
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
           '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for e in entries:
        out += ['  <url>', f'    <loc>{e["loc"]}</loc>', f'    <lastmod>{fmt(e["mod"])}</lastmod>']
        out += [f'    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in e['alts']]
        out += [f'    <image:image><image:loc>{i}</image:loc></image:image>' for i in e['imgs']]
        out.append('  </url>')
    out.append('</urlset>')
    return '\n'.join(out) + '\n'

pages = sorted(f for f in glob.glob('*.html') if f != 'testimonials-admin.html')
info = [page_info(f) for f in pages]
is_guide = lambda e: re.search(r'/(guide|guia)-', e['loc'])
homes = [f'{BASE}/', f'{BASE}/en']
order = lambda e: (e['loc'] not in homes, homes.index(e['loc']) if e['loc'] in homes else 0, e['born'], e['loc'])
groups = {'page-sitemap.xml': sorted([e for e in info if not is_guide(e)], key=order),
          'post-sitemap.xml': sorted([e for e in info if is_guide(e)], key=order)}

index = ['<?xml version="1.0" encoding="UTF-8"?>', XSL,
         '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for name, entries in groups.items():
    open(name, 'w', encoding='utf-8').write(urlset(entries))
    index += ['  <sitemap>', f'    <loc>{BASE}/{name}</loc>',
              f'    <lastmod>{fmt(max(e["mod"] for e in entries))}</lastmod>', '  </sitemap>']
    print(f'{name}: {len(entries)} URLs')
index.append('</sitemapindex>')
open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(index) + '\n')
