"""Animate a still into a seamless, silent background loop with Higgsfield (Seedance 2.0 image-to-video).

Run from the site root:
  python3 _tools/gen_video.py <still.jpg> <out-name> "<motion prompt>" [seconds=8] [resolution=1080p]
Uploads the still, asks for a clip that starts AND ends on that frame (so it loops without a jump),
downloads it and writes web versions: img/hero/<out-name>.mp4 (1920 wide) and <out-name>-720.mp4,
H.264, no audio, faststart. Needs the Higgsfield credentials used by gen_image.py, and the
imageio-ffmpeg package (bundled ffmpeg) for the compression step.
Cost: Seedance 2.0 1080p ≈ $0.43 per second of video (check with the /estimate endpoint).
"""
import json, os, subprocess, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from gen_image import hf_auth, http, HF_API

MODEL = 'bytedance/seedance-2.0/image-to-video'

def upload(path, auth):
    up = http(f'{HF_API}/files/generate-upload-url', {'content_type': 'image/jpeg'}, auth)
    req = urllib.request.Request(up['upload_url'], data=open(path, 'rb').read(), method='PUT', headers=up.get('upload_headers', {'Content-Type': 'image/jpeg'}))
    urllib.request.urlopen(req, timeout=120).read()
    return up['public_url']

def generate(still, prompt, seconds, res):
    auth = hf_auth()
    url = upload(still, auth)
    body = {'image_url': url, 'end_image_url': url, 'prompt': prompt, 'duration': seconds, 'resolution': res, 'generate_audio': False}
    sub = http(f'{HF_API}/{MODEL}', body, {**auth, 'Idempotency-Key': str(uuid.uuid4())})
    status_url = sub.get('status_url') or f'{HF_API}/requests/{sub["request_id"]}/status'
    for i in range(180):                                  # up to ~15 minutes
        time.sleep(5)
        st = http(status_url, headers=auth)
        if st.get('status') == 'completed': return http(st['video']['url'], timeout=300)
        if st.get('status') in ('failed', 'nsfw', 'canceled'): sys.exit(f'Higgsfield request {st.get("status")}: {st.get("error", "")}')
    sys.exit(f'Still running after 15 minutes: {status_url}')

def encode(raw_path, out, width, crf):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-y', '-loglevel', 'error', '-i', raw_path, '-an', '-vf', f'scale={width}:-2:flags=lanczos,fps=25',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)

if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    still, name, prompt = sys.argv[1:4]
    seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    res = sys.argv[5] if len(sys.argv) > 5 else '1080p'
    raw = generate(still, prompt, seconds, res)
    os.makedirs('img/hero', exist_ok=True)
    raw_path = f'/tmp/{name}-raw.mp4'; open(raw_path, 'wb').write(raw)
    encode(raw_path, f'img/hero/{name}.mp4', 1920, 26)
    encode(raw_path, f'img/hero/{name}-720.mp4', 1280, 28)
    for f in (f'img/hero/{name}.mp4', f'img/hero/{name}-720.mp4'): print(f, os.path.getsize(f) // 1024, 'KB')
