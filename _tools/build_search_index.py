"""Rebuild search-index.json for the site search (search.js).

Run from the site root:  python3 _tools/build_search_index.py
One entry for each page (title, description, H1, opening text) and one for each
section with an id and a heading, so a search for "prices" can land on /en#fees.
The quote, review and contact forms are left out. Run it after adding or editing pages.
"""
import glob, html, json, re

BASE = 'https://sptranslationservices.com'
SKIP = {'testimonials-admin.html'}

def clean(s):
    s = re.sub(r'<(script|style|svg|form|datalist|select|noscript)\b.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

entries = []
for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    s = open(f, encoding='utf-8').read()
    lang = re.search(r'<html lang="(\w+)"', s).group(1)
    url = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
    path = url.replace(BASE, '') or '/'
    title = clean(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    title = re.split(r'\s+[|—]\s+SP Translations', title)[0].strip()
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    main = s[s.index('<main'):s.index('</main>')]
    main = re.sub(r'<p class="crumb">.*?</p>', ' ', main, flags=re.S)       # breadcrumbs add noise to snippets
    h1 = clean(re.search(r'<h1[^>]*>(.*?)</h1>', main, re.S).group(1))
    sections = re.findall(r'<section\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</section>', main, re.S)
    first_text = clean(sections[0][1])[:400] if sections else ''
    entries.append(dict(page=path, url=path, lang=lang, title=h1 or title, heading='', section=False,
                        description=desc, text=first_text))
    for sid, body in sections:
        if sid in ('top', 'instruct', 'reviews', 'start', 'related'): continue
        h2 = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S)
        mark = re.search(r'<span class="mark">(.*?)</span>', body, re.S)
        if not (h2 or mark): continue
        h2 = clean(h2.group(1)) if h2 else ''
        mark = re.sub(r'^\d+\s*[—-]\s*', '', clean(mark.group(1))) if mark else ''
        if mark.lower() in ('guide', 'guía'): mark = ''      # a guide's body: label it by its H2 instead
        text = clean(body)
        if mark and text.startswith(clean(re.search(r'<span class="mark">(.*?)</span>', body, re.S).group(1))):
            text = text[len(clean(re.search(r'<span class="mark">(.*?)</span>', body, re.S).group(1))):].strip()
        if len(text) < 40: continue
        if not (mark or h2): continue
        entries.append(dict(page=path, url=f'{path}#{sid}', lang=lang, title=h1 or title, heading=mark or h2,
                            sub=h2 if mark else '', section=True, description='', text=text[:3000]))

json.dump(entries, open('search-index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'search-index.json: {len(entries)} entries from {len({e["page"] for e in entries})} pages')
