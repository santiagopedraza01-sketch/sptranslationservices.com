"""Generate a blog hero image and save it web-ready.

Run from the site root:
  python3 _tools/gen_image.py <slug> "<prompt>"            (Higgsfield, default)
  python3 _tools/gen_image.py <slug> "<prompt>" --gemini   (Google Gemini instead)
  python3 _tools/gen_image.py <slug> "<prompt>" --card     (bright 3:2 blog-card thumbnail → img/blog/cards/<slug>.jpg;
                                                             use the English slug — the Spanish version shares it)
Saves img/blog/<slug>.jpg (2000×1125) and img/blog/<slug>-sm.jpg (1000×562), and records the image in
_tools/blog/posts/<slug>.json ("hero_image"), so build_post.py shows it faded behind the headline.

Credentials are never stored in the repo:
- Higgsfield (https://higgsfield.ai, model Recraft V4.1 Pro, 2K, 16:9): a key ID + secret from
  console.higgsfield.ai. Read from HF_KEY ("KEY_ID:KEY_SECRET"), or HF_API_KEY_ID + HF_API_KEY_SECRET,
  or on this Mac from the keychain: service "higgsfield.io", accounts "key-id" and "api-key".
  Model override: HF_IMAGE_MODEL (an endpoint id such as "higgsfield-ai/soul/cinema").
- Gemini: GEMINI_API_KEY, or ~/.config/sp-translations/gemini-key. Needs billing on the key's project.

House style is added to every prompt: editorial photograph, natural light, navy and warm brass tones,
space for the headline, and no text, logos, flags, readable stamps or recognisable people.
"""
import base64, io, json, os, subprocess, sys, time, uuid, urllib.request, urllib.error

STYLE = ('Editorial photograph for the hero of a professional translation agency blog article. '
         'Natural light, shallow depth of field, calm and premium, muted deep-navy and warm brass tones, '
         'wide 16:9 composition with quieter empty space on the left for a headline. '
         'No text, no lettering, no logos, no flags, no official seals or stamps that could be read, '
         'no recognisable real people or faces. Subject: ')
CARD_STYLE = ('Bright, premium editorial photograph used as a blog article thumbnail for a high-end translation agency. '
              'Warm natural daylight, shallow depth of field, clean and uncluttered, cohesive palette of warm wood, cream paper, '
              'deep navy and brushed brass accents, subject centred. No text or lettering, no logos, no flags, no readable stamps, '
              'no recognisable people or faces. Subject: ')
UA = 'Mozilla/5.0 (compatible; sptranslationservices-images/1.0)'

def http(url, body=None, headers=None, method=None, timeout=120):
    h = {'User-Agent': UA, **(headers or {})}
    if body is not None: h['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        return json.loads(data) if 'json' in r.headers.get('Content-Type', '') else data

def keychain(service, account):
    try: return subprocess.run(['security', 'find-generic-password', '-s', service, '-a', account, '-w'],
                               capture_output=True, text=True, check=True).stdout.strip()
    except Exception: return ''

# ── Higgsfield ──
HF_API = 'https://api.higgsfield.ai'
HF_MODEL = os.environ.get('HF_IMAGE_MODEL', 'recraft/v4.1/pro/text-to-image')
PALETTE = [[17, 29, 44], [27, 42, 62], [142, 114, 67], [196, 172, 128], [245, 242, 237]]   # site navy, brass, bone

def hf_auth():
    combo = os.environ.get('HF_KEY', '')
    kid, sec = (combo.split(':', 1) + [''])[:2] if combo else (os.environ.get('HF_API_KEY_ID', ''), os.environ.get('HF_API_KEY_SECRET', ''))
    kid = kid or keychain('higgsfield.io', 'key-id') or keychain('higgsfield.io', 'api-key-id'); sec = sec or keychain('higgsfield.io', 'api-key')
    if not (kid and sec): sys.exit('Higgsfield needs a key ID and secret: set HF_KEY="ID:SECRET" or add both to the keychain (see the docstring).')
    return {'Authorization': f'Key {kid}:{sec}'}

def higgsfield(prompt, card=False):
    auth = hf_auth()
    body = {'prompt': (CARD_STYLE if card else STYLE) + prompt, 'aspect_ratio': '3:2' if card else '16:9'}
    if 'recraft' in HF_MODEL: body.update(resolution='2k', output_format='jpg', colors=[{'rgb': c} for c in PALETTE])
    else: body.update(resolution='1080p', batch_size=1)
    try:
        sub = http(f'{HF_API}/{HF_MODEL}', body, {**auth, 'Idempotency-Key': str(uuid.uuid4())})
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        sys.exit(f'Higgsfield error {e.code}: ' + ('invalid credentials' if e.code == 401 else 'insufficient balance' if e.code == 403 else msg))
    status_url = sub.get('status_url') or f'{HF_API}/requests/{sub["request_id"]}/status'
    for i in range(90):                                  # up to ~6 minutes
        time.sleep(2 if i < 5 else 4)
        st = http(status_url, headers=auth)
        if st.get('status') == 'completed':
            return http(st['images'][0]['url'], timeout=180), HF_MODEL
        if st.get('status') in ('failed', 'nsfw', 'canceled'):
            sys.exit(f'Higgsfield request {st.get("status")}: {st.get("error", "")}')
    sys.exit(f'Higgsfield request still running after 6 minutes: {status_url}')

# ── Gemini (fallback) ──
GEMINI_API = 'https://generativelanguage.googleapis.com/v1beta'
PREFERRED = ['gemini-3-pro-image', 'gemini-3.1-flash-image', 'gemini-2.5-flash-image']

def gemini(prompt):
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    p = os.path.expanduser('~/.config/sp-translations/gemini-key')
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit('No Gemini API key.')
    h = {'x-goog-api-key': k}
    names = [m['name'].split('/')[-1] for m in http(f'{GEMINI_API}/models?pageSize=200', headers=h).get('models', [])]
    model = os.environ.get('GEMINI_IMAGE_MODEL') or next((m for m in PREFERRED if m in names), None)
    if not model: sys.exit('No image-capable Gemini model for this key.')
    body = {'contents': [{'parts': [{'text': STYLE + prompt}]}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '16:9'}}}
    try: out = http(f'{GEMINI_API}/models/{model}:generateContent', body, h, timeout=180)
    except urllib.error.HTTPError as e: sys.exit(f'Gemini error {e.code}: {e.read().decode()[:300]}')
    for c in out.get('candidates', []):
        for part in c.get('content', {}).get('parts', []):
            d = part.get('inlineData') or part.get('inline_data')
            if d: return base64.b64decode(d['data']), model
    sys.exit('Gemini returned no image.')

def save_card(raw, key):
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w, h = im.size; t = 1.5
    if w / h > t: nw = int(h * t); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    elif w / h < t: nh = int(w / t); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    os.makedirs('img/blog/cards', exist_ok=True)
    im.resize((1200, 800), Image.LANCZOS).save(f'img/blog/cards/{key}.jpg', quality=78, optimize=True, progressive=True)
    im.resize((600, 400), Image.LANCZOS).save(f'img/blog/cards/{key}-sm.jpg', quality=76, optimize=True, progressive=True)
    return f'img/blog/cards/{key}.jpg'

def save(raw, slug, outdir='img/blog'):
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w, h = im.size; target = 16 / 9
    if w / h > target: nw = int(h * target); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    elif w / h < target: nh = int(w / target); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    os.makedirs(outdir, exist_ok=True)
    im.resize((2000, 1125), Image.LANCZOS).save(f'{outdir}/{slug}.jpg', quality=74, optimize=True, progressive=True)
    im.resize((1000, 562), Image.LANCZOS).save(f'{outdir}/{slug}-sm.jpg', quality=72, optimize=True, progressive=True)
    return f'{outdir}/{slug}.jpg'

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) < 2: sys.exit(__doc__)
    slug, prompt = args[0], args[1]
    if '--card' in sys.argv:   # blog card thumbnail: img/blog/cards/<english-slug>.jpg, used by build_blog.py
        raw, model = higgsfield(prompt, card=True)
        print(save_card(raw, slug), 'from', model); sys.exit(0)
    raw, model = (gemini if '--gemini' in sys.argv else higgsfield)(prompt)
    path = save(raw, slug)
    src = f'_tools/blog/posts/{slug}.json'
    if os.path.exists(src):
        d = json.load(open(src, encoding='utf-8'))
        for p in d.values():
            p['hero_image'] = {'src': '/' + path, 'small': f'/img/blog/{slug}-sm.jpg', 'prompt': prompt, 'model': model}
        json.dump(d, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{path} ({os.path.getsize(path) // 1024} KB) from {model}')
