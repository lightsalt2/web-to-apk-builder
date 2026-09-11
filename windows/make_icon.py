import os
import io
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, UnidentifiedImageError

u = os.environ.get('ICON_URL', '').strip()
if not u:
    print('No custom icon supplied; using default app icon.')
    raise SystemExit(0)

try:
    p = urllib.parse.urlsplit(u)
    path = urllib.parse.quote(urllib.parse.unquote(p.path), safe="/:%@!$&'()*+,;=-._~")
    query = urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&?/:;%+,-._~')
    enc = urllib.parse.urlunsplit((p.scheme, p.netloc, path, query, p.fragment))

    req = urllib.request.Request(
        enc,
        headers={
            'User-Agent': 'Mozilla/5.0 WebToAPKBuilder/3.1',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        content_type = (r.headers.get('Content-Type') or '').lower()
        data = r.read()

    if not data:
        raise ValueError('Downloaded icon file is empty')

    # Try to decode from memory regardless of extension/content type.
    img = Image.open(io.BytesIO(data)).convert('RGBA')
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((256, 256))
    img.save(
        'windows/app.ico',
        format='ICO',
        sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
    )
    print(f'Custom icon created successfully. Content-Type: {content_type or "unknown"}')

except Exception as e:
    # Icon failure must never stop the Windows app build.
    print(f'WARNING: custom icon could not be processed: {e}')
    print('Continuing with default app icon.')
    try:
        Path('windows/app.ico').unlink(missing_ok=True)
    except Exception:
        pass
    raise SystemExit(0)
