"""Submit new and updated pages to Ralfy Index (https://ralfyindex.com) for Google indexing.

Runs in GitHub Actions on every push to main (.github/workflows/ralfy-index.yml), after GitHub Pages
has published the commit. Can also be run by hand from the site root:
  python3 _tools/ralfy_submit.py --range <before> <after>   pages changed between two commits
  python3 _tools/ralfy_submit.py --all                      every URL in the sitemaps
  python3 _tools/ralfy_submit.py --urls <url> [<url> …]     specific URLs
  add --dry-run to list the URLs without submitting, --instant for Ralfy's instant mode (more credits)

API key: RALFY_API_KEY environment variable (a GitHub Actions secret). Never commit it.
Which pages count: root *.html and blog/**/index.html, by their <link rel="canonical"> URL.
Skipped: noindex pages (redirect stubs such as /en, /guides, /guias), testimonials-admin.html, and
anything outside the site. Only URLs that answer 200 on the live site are submitted.
"""
import json, os, re, subprocess, sys, time, urllib.request, urllib.error

API = 'https://api.ralfyindex.com'
BASE = 'https://sptranslationservices.com'
SKIP = {'testimonials-admin.html'}

def page_file(path):
    return (path.endswith('.html') and '/' not in path and path not in SKIP) or re.fullmatch(r'blog/(.+/)?index\.html', path)

def canonical(path, rev='HEAD'):
    try: s = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError: return None          # deleted in this push
    if re.search(r'name="robots" content="noindex', s): return None
    m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    return m.group(1) if m and m.group(1).startswith(BASE) else None

def changed(before, after):
    if not before or set(before) == {'0'}: before = f'{after}~1'
    out = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=AMR', before, after], capture_output=True, text=True, check=True).stdout
    urls = []
    for f in out.split():
        if page_file(f):
            u = canonical(f, after)
            if u and u not in urls: urls.append(u)
    return urls

def sitemap_urls():
    urls = []
    for f in ('page-sitemap.xml', 'post-sitemap.xml'):
        if os.path.exists(f): urls += re.findall(r'<loc>([^<]+)</loc>', open(f, encoding='utf-8').read())
    return urls

def live(u, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(u, method='GET', headers={'User-Agent': 'sp-translations-ralfy-submit'})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200 and r.geturl().rstrip('/') == u.rstrip('/'): return True
        except urllib.error.HTTPError as e:
            if e.code != 404: print(f'  {u}: HTTP {e.code}')
        except Exception as e:
            print(f'  {u}: {e}')
        time.sleep(15)
    return False

def call(endpoint, body):
    req = urllib.request.Request(API + endpoint, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except Exception: return {'status': 'error', 'message': f'HTTP {e.code}'}

if __name__ == '__main__':
    a = sys.argv[1:]
    dry, instant = '--dry-run' in a, '--instant' in a or os.environ.get('RALFY_INSTANT') == '1'
    if '--range' in a: i = a.index('--range'); urls = changed(a[i + 1], a[i + 2])
    elif '--all' in a: urls = sitemap_urls()
    elif '--urls' in a: urls = [u for u in a[a.index('--urls') + 1:] if u.startswith('http')]
    else: sys.exit(__doc__)

    if not urls: print('No new or updated pages to submit.'); sys.exit(0)
    print(f'{len(urls)} page(s) to submit:'); [print('  ' + u) for u in urls]
    if dry: sys.exit(0)

    ok = [u for u in urls if live(u)]
    for u in set(urls) - set(ok): print(f'  skipped (not live yet): {u}')
    if not ok: sys.exit('Nothing is live to submit.')

    key = os.environ.get('RALFY_API_KEY', '').strip()
    if not key:   # not configured yet: warn, don't fail every deploy
        print('::warning::RALFY_API_KEY is not set, so nothing was submitted. Add it under Settings → Secrets and variables → Actions.')
        sys.exit(0)
    sha = (os.environ.get('GITHUB_SHA') or subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout)[:7]
    name = f'sptranslationservices.com {time.strftime("%Y-%m-%d %H:%M", time.gmtime())} {sha}'.strip()
    res = call('/project', {'apikey': key, 'projectName': name, 'urls': ok, 'instantIndex': 1 if instant else 0})
    print('Ralfy Index:', json.dumps({k: v for k, v in res.items() if k != 'apikey'}))
    bal = call('/balance', {'apikey': key})
    if 'balance' in bal: print(f'Credits left: {bal["balance"]}')
    if res.get('errorCode') or str(res.get('status', '')).lower() in ('error', 'fail', 'failed'):
        sys.exit(f'Submission failed: {res.get("message") or res}')
    print(f'Submitted {len(ok)} URL(s) as project "{name}" ({"instant" if instant else "regular"} mode).')
