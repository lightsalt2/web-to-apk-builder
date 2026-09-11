import os, re, html, urllib.request, urllib.parse
from pathlib import Path

url = os.environ.get('APP_URL','').strip()
app_name = os.environ.get('APP_NAME','').strip()[:60]
package_name = os.environ.get('PACKAGE_NAME','').strip()
icon_url = os.environ.get('ICON_URL','').strip()

if not re.fullmatch(r'https://[^\s]+', url):
    raise SystemExit('APP_URL must start with https://')
if not app_name:
    raise SystemExit('APP_NAME is required')
if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+', package_name):
    raise SystemExit('Invalid PACKAGE_NAME')

# Update start URL in Java source.
java_path = Path('app/src/main/java/com/hymnbox/video/MainActivity.java')
text = java_path.read_text(encoding='utf-8')
escaped_url = url.replace('\\', '\\\\').replace('"', '\\"')
text = re.sub(r'private static final String START_URL = ".*?";',
              f'private static final String START_URL = "{escaped_url}";', text)
java_path.write_text(text, encoding='utf-8')

# Update applicationId only; namespace/source package stay fixed.
gradle_path = Path('app/build.gradle.kts')
gradle = gradle_path.read_text(encoding='utf-8')
gradle = re.sub(r'applicationId = ".*?"', f'applicationId = "{package_name}"', gradle)
gradle_path.write_text(gradle, encoding='utf-8')

# Update visible app name.
strings_path = Path('app/src/main/res/values/strings.xml')
strings_path.write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    f'    <string name="app_name">{html.escape(app_name)}</string>\n'
    '</resources>\n', encoding='utf-8')

# Optional custom icon. Percent-encode Korean/non-ASCII path characters first.
if icon_url:
    parts = urllib.parse.urlsplit(icon_url)
    safe_path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe='/:%@!$&\'()*+,;=-._~')
    safe_query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe='=&?/:;%+,-._~')
    encoded_icon_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment))
    request = urllib.request.Request(encoded_icon_url, headers={'User-Agent': 'WebToAPKBuilder/2.0'})
    with urllib.request.urlopen(request, timeout=30) as response, open('/tmp/app-icon', 'wb') as output:
        output.write(response.read())

    from PIL import Image
    img = Image.open('/tmp/app-icon').convert('RGBA')
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((512,512))
    out_dir = Path('app/src/main/res/drawable')
    out_dir.mkdir(parents=True, exist_ok=True)
    icon_path = out_dir / 'generated_icon.png'
    img.save(icon_path)
    manifest_path = Path('app/src/main/AndroidManifest.xml')
    manifest = manifest_path.read_text(encoding='utf-8')
    if 'android:icon=' not in manifest:
        manifest = manifest.replace('<application\n', '<application\n        android:icon="@drawable/generated_icon"\n', 1)
    manifest_path.write_text(manifest, encoding='utf-8')

print('Configured build:', app_name, url, package_name)
