"""Generate a blog hero image with Google Gemini and save it web-ready.

Run from the site root:
  python3 _tools/gen_image.py <slug> "<prompt>"
Saves img/blog/<slug>.jpg (2000px wide, ~16:9) and img/blog/<slug>-sm.jpg (1000px), and records
the image in _tools/blog/posts/<slug>.json ("hero_image"), so build_post.py shows it in the hero.

The API key is read from the GEMINI_API_KEY environment variable, or from the file
~/.config/sp-translations/gemini-key (one line, nothing else). It is never stored in the repo.
Model: GEMINI_IMAGE_MODEL env var, else the first image-capable Gemini model the key can use.

House style is added to every prompt: editorial photograph, natural light, muted navy and warm brass
tones, no text, no logos, no flags, no identifiable real people or official seals.
"""
import base64, io, json, os, sys, urllib.request

API = 'https://generativelanguage.googleapis.com/v1beta'
PREFERRED = ['gemini-3-pro-image', 'gemini-3.1-flash-image', 'gemini-2.5-flash-image']   # best quality first
STYLE = ('Editorial photograph for the hero of a professional translation agency blog article. '
         'Natural light, shallow depth of field, calm and premium, muted deep-navy and warm brass tones, '
         'wide 16:9 composition with empty space on the left for a headline. '
         'No text, no lettering, no logos, no flags, no official seals or stamps that could be read, '
         'no recognisable real people or faces. Subject: ')

def key():
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    p = os.path.expanduser('~/.config/sp-translations/gemini-key')
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit('No Gemini API key: set GEMINI_API_KEY or create ~/.config/sp-translations/gemini-key')
    return k

def call(url, body=None, k=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
    with urllib.request.urlopen(req, timeout=180) as r: return json.load(r)

def pick_model(k):
    if os.environ.get('GEMINI_IMAGE_MODEL'): return os.environ['GEMINI_IMAGE_MODEL']
    models = call(f'{API}/models?pageSize=200', k=k).get('models', [])
    names = [m['name'].split('/')[-1] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
    image = [n for n in names if 'image' in n and 'gemini' in n]
    if not image: sys.exit('This key has no image-capable Gemini model. Models: ' + ', '.join(names))
    for pref in PREFERRED:
        if pref in image: return pref
    return sorted(image, key=lambda n: ('preview' in n, 'lite' in n, n))[0]

def generate(prompt, k):
    model = pick_model(k)
    body = {'contents': [{'parts': [{'text': STYLE + prompt}]}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '16:9'}}}
    try:
        out = call(f'{API}/models/{model}:generateContent', body, k)
    except urllib.error.HTTPError as e:
        if e.code == 400:   # older models don't take imageConfig
            body['generationConfig'] = {'responseModalities': ['TEXT', 'IMAGE']}
            out = call(f'{API}/models/{model}:generateContent', body, k)
        else:
            sys.exit(f'Gemini error {e.code}: {e.read().decode()[:500]}')
    for c in out.get('candidates', []):
        for part in c.get('content', {}).get('parts', []):
            data = part.get('inlineData') or part.get('inline_data')
            if data: return base64.b64decode(data['data']), model
    sys.exit('Gemini returned no image: ' + json.dumps(out)[:600])

def save(raw, slug):
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w, h = im.size; target = 16 / 9
    if w / h > target:   # crop to 16:9
        nw = int(h * target); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    elif w / h < target:
        nh = int(w / target); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    os.makedirs('img/blog', exist_ok=True)
    big = im.resize((2000, 1125), Image.LANCZOS); big.save(f'img/blog/{slug}.jpg', quality=74, optimize=True, progressive=True)
    im.resize((1000, 562), Image.LANCZOS).save(f'img/blog/{slug}-sm.jpg', quality=72, optimize=True, progressive=True)
    return f'img/blog/{slug}.jpg'

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    slug, prompt = sys.argv[1], sys.argv[2]
    k = key()
    raw, model = generate(prompt, k)
    path = save(raw, slug)
    src = f'_tools/blog/posts/{slug}.json'
    if os.path.exists(src):
        d = json.load(open(src, encoding='utf-8'))
        for p in d.values():
            p['hero_image'] = {'src': '/' + path, 'small': f'/img/blog/{slug}-sm.jpg', 'prompt': prompt, 'model': model}
        json.dump(d, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{path} ({os.path.getsize(path)//1024} KB) from {model}')
