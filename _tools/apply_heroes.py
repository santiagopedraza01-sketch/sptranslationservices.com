"""Hero images on every page except the home pages — see _tools/heroes.json.

Run from the site root:
  python3 _tools/apply_heroes.py --generate   create any missing images in img/hero/ (Higgsfield, ~$0.21 each)
  python3 _tools/apply_heroes.py              add/refresh the images in the pages' heroes (no API calls)
Re-run the second form after rebuilding pages with langgen/servicegen/build_blog, which start from
plain page shells. Each image sits faded behind the headline (.pagehead__bg, styles.css), and becomes
the page's og:image when the page still uses the default social image.
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))

BASE = 'https://sptranslationservices.com'
CFG = json.load(open('_tools/heroes.json', encoding='utf-8'))
HEROES = {k: v for k, v in CFG.items() if not k.startswith('_')}

def generate(key):
    import gen_image
    if os.path.exists(f'img/hero/{key}.jpg'): return f'{key}: exists'
    raw, model = gen_image.higgsfield(HEROES[key]['prompt'])
    gen_image.save(raw, key, 'img/hero')
    return f'{key}: generated ({os.path.getsize(f"img/hero/{key}.jpg") // 1024} KB)'

def safe_generate(key):
    try: return generate(key)
    except BaseException as e: return f'{key}: FAILED {str(e)[:200]}'   # gen_image exits on API errors

def apply(key, page):
    s = open(page, encoding='utf-8').read(); o = s
    tag = (f'<img class="pagehead__bg" src="/img/hero/{key}.jpg" srcset="/img/hero/{key}-sm.jpg 1000w, /img/hero/{key}.jpg 2000w" '
           f'sizes="(max-width:900px) 100vw, 70vw" alt="" width="2000" height="1125" fetchpriority="high">')
    s = re.sub(r'\n  <img class="pagehead__bg" src="/img/hero/[^"]+"[^>]*>', '', s)          # ours, from a previous run
    m = re.search(r'<section class="pagehead([^"]*)" id="top">', s)
    if not m or 'pagehead--photo' in m.group(1): return f'{page}: skipped'
    cls = m.group(1) if 'pagehead--bg' in m.group(1) else m.group(1) + ' pagehead--bg'
    s = s[:m.start()] + f'<section class="pagehead{cls}" id="top">\n  {tag}' + s[m.end():]
    s = s.replace(f'<meta property="og:image" content="{BASE}/img/og-image.jpg">', f'<meta property="og:image" content="{BASE}/img/hero/{key}.jpg">')
    if s != o: open(page, 'w', encoding='utf-8').write(s); return f'{page}: updated'
    return f'{page}: unchanged'

if __name__ == '__main__':
    if '--generate' in sys.argv:
        with ThreadPoolExecutor(4) as ex:
            for line in ex.map(safe_generate, HEROES):
                print(line, flush=True)
    missing = [k for k in HEROES if not os.path.exists(f'img/hero/{k}.jpg')]
    if missing: print('No image yet for:', ', '.join(missing), '(run with --generate)')
    for k, v in HEROES.items():
        if k in missing: continue
        for p in v['pages']:
            if os.path.exists(p): r = apply(k, p); print(r) if 'updated' in r else None
