#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, sys

if len(sys.argv) != 3:
    raise SystemExit('usage: apply_icon_v3124.py <project-root> <icon-b64>')

project = Path(sys.argv[1]).resolve()
payload = Path(sys.argv[2]).resolve()
res = project / 'app/src/main/res'

raw = base64.b64decode(payload.read_text(encoding='utf-8').strip(), validate=True)
expected_icon_sha = 'eee78833c0b3bc651819c016470bb0b97dd86e2ce63a9bb532cb3375fa139025'
actual_icon_sha = hashlib.sha256(raw).hexdigest()
if actual_icon_sha != expected_icon_sha:
    raise SystemExit(f'icon SHA mismatch: {actual_icon_sha}')
if len(raw) != 10414 or raw[:4] != b'RIFF' or raw[8:12] != b'WEBP':
    raise SystemExit('icon payload is not the expected WebP')

nodpi = res / 'drawable-nodpi'
nodpi.mkdir(parents=True, exist_ok=True)
icon = nodpi / 'cell_app_icon.webp'
icon.write_bytes(raw)

transparent = res / 'drawable/ic_launcher_foreground_transparent.xml'
transparent.write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android"\n    android:width="108dp"\n    android:height="108dp"\n    android:viewportWidth="108"\n    android:viewportHeight="108">\n    <path android:fillColor="#00000000" android:pathData="M0,0h108v108h-108z"/>\n</vector>\n''', encoding='utf-8')

legacy = '''<bitmap xmlns:android="http://schemas.android.com/apk/res/android"\n    android:src="@drawable/cell_app_icon"\n    android:gravity="fill" />\n'''
adaptive = '''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@drawable/cell_app_icon" />\n    <foreground android:drawable="@drawable/ic_launcher_foreground_transparent" />\n</adaptive-icon>\n'''

base = res / 'mipmap-anydpi'
base.mkdir(parents=True, exist_ok=True)
(base / 'ic_launcher.xml').write_text(legacy, encoding='utf-8')
(base / 'ic_launcher_round.xml').write_text(legacy, encoding='utf-8')
for qual in ('mipmap-anydpi-v26', 'mipmap-anydpi-v33'):
    d = res / qual
    d.mkdir(parents=True, exist_ok=True)
    (d / 'ic_launcher.xml').write_text(adaptive, encoding='utf-8')
    (d / 'ic_launcher_round.xml').write_text(adaptive, encoding='utf-8')

build = project / 'app/build.gradle.kts'
s = build.read_text(encoding='utf-8')
if 'versionCode = 31203' not in s or 'versionName = "3.12.3"' not in s:
    raise SystemExit('expected v3.12.3 Gradle metadata not found')
s = s.replace('versionCode = 31203', 'versionCode = 31204', 1)
s = s.replace('versionName = "3.12.3"', 'versionName = "3.12.4"', 1)
build.write_text(s, encoding='utf-8')

metadata_test = project / 'app/src/test/java/in/gov/tn/gascngl/zoology/cellbiology/ReleaseMetadataTest.java'
if metadata_test.exists():
    t = metadata_test.read_text(encoding='utf-8')
    t = t.replace('31203', '31204').replace('3.12.3', '3.12.4')
    metadata_test.write_text(t, encoding='utf-8')

html = project / 'app/src/main/assets/www/index.html'
h = html.read_text(encoding='utf-8')
if '3.12.3' not in h:
    raise SystemExit('v3.12.3 identity not found in HTML')
h = h.replace('3.12.3', '3.12.4')
html.write_text(h, encoding='utf-8')

print('icon_sha256', actual_icon_sha)
print('icon_bytes', len(raw))
print('html_sha256', hashlib.sha256(html.read_bytes()).hexdigest())
print('v3.12.4 launcher icon applied')
