import os
import urllib.parse
import urllib.request
from PIL import Image

u = os.environ.get('ICON_URL', '').strip()
if not u:
    raise SystemExit(0)

p = urllib.parse.urlsplit(u)
path = urllib.parse.quote(urllib.parse.unquote(p.path), safe="/:%@!$&'()*+,;=-._~")
query = urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&?/:;%+,-._~')
enc = urllib.parse.urlunsplit((p.scheme, p.netloc, path, query, p.fragment))

req = urllib.request.Request(enc, headers={'User-Agent': 'WebToAPKBuilder/3.0'})
with urllib.request.urlopen(req, timeout=30) as r, open('windows/app-icon', 'wb') as f:
    f.write(r.read())

img = Image.open('windows/app-icon').convert('RGBA')
side = min(img.size)
left = (img.width - side) // 2
top = (img.height - side) // 2
img = img.crop((left, top, left + side, top + side)).resize((256, 256))
img.save(
    'windows/app.ico',
    format='ICO',
    sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
)
