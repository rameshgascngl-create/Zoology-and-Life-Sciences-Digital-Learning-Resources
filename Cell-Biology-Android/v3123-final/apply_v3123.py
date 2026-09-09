#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
htmlp = root / 'app/src/main/assets/www/index.html'
if not htmlp.exists():
    raise SystemExit(f'project root invalid: {root}')

s = htmlp.read_text(encoding='utf-8')
# Identity + release note.
s = s.replace('Android/mobile remediation — v3.12.2', 'Android/mobile remediation — v3.12.3')
s = s.replace('version: "3.12.2"', 'version: "3.12.3"')
s = s.replace(
    'Android-remediation release 3.12.2 adds narrow-screen overflow containment, stronger light-theme contrast, keyboard-operable search results, strict learner-state import validation, and section-aware Android Back navigation while preserving the locked scientific lesson corpus.',
    'Android-remediation release 3.12.3 preserves the v3.12.2 layout, accessibility, learner-state and Back-navigation fixes and adds Android 7/8 WebView compatibility by removing unsupported modern JavaScript syntax and providing narrowly scoped ES compatibility shims, while preserving the locked scientific lesson corpus.'
)
s = s.replace('Cell Biology Learning Hub, Version 3.12.2.', 'Cell Biology Learning Hub, Version 3.12.3.')

# Android 7/8 WebView (Chrome 51/61-era) compatibility.
needle = '"use strict";\n'
poly = '''"use strict";\n/* Android 7/8 WebView compatibility: Chrome 51-era WebView lacks Object.values, Object.entries and Object.fromEntries. */\nif (!Object.values) Object.values = function(obj){ return Object.keys(obj).map(function(k){ return obj[k]; }); };\nif (!Object.entries) Object.entries = function(obj){ return Object.keys(obj).map(function(k){ return [k, obj[k]]; }); };\nif (!Object.fromEntries) Object.fromEntries = function(iterable){ var out = {}; iterable.forEach(function(pair){ out[pair[0]] = pair[1]; }); return out; };\n'''
if 'Android 7/8 WebView compatibility:' not in s:
    if needle not in s: raise SystemExit('strict marker missing')
    s = s.replace(needle, poly, 1)
s = s.replace('unit: ontology.topics.find(t=>t.id===c.parentTopic)?.unit || null,', 'unit: ((ontology.topics.find(t=>t.id===c.parentTopic) || {}).unit) || null,')
s = s.replace('const d=EXAM_PRACTICE[unit]; const title=ONTOLOGY.units.find(u=>u.id===unit)?.title||unit;', 'const d=EXAM_PRACTICE[unit]; const title=((ONTOLOGY.units.find(u=>u.id===unit)||{}).title)||unit;')
s = s.replace('return { unit: u.id, title: u.title, ...r };', 'return Object.assign({ unit: u.id, title: u.title }, r);')
s = s.replace('const all=[...(deep.keyConcepts||[]),...(deep.shortNotes||[]),...(topic.subtopics||[])];', 'const all=[].concat(deep.keyConcepts||[], deep.shortNotes||[], topic.subtopics||[]);')
s = s.replace('const height = Math.max(...Object.values(pos).map(p=>p.y)) + 60;', 'const height = Math.max.apply(null, Object.values(pos).map(p=>p.y)) + 60;')
htmlp.write_text(s, encoding='utf-8')

# Release metadata + docs/tools, preserving forensic APK baseline.
for p in root.rglob('*'):
    if not p.is_file() or 'provenance' in p.parts or p == htmlp:
        continue
    if p.suffix.lower() not in {'.md','.json','.java','.kts','.mjs','.py','.yml','.yaml','.txt'}:
        continue
    try: t = p.read_text(encoding='utf-8')
    except UnicodeDecodeError: continue
    nt = t.replace('3.12.2','3.12.3').replace('31202','31203')
    if p.name == 'README.md': nt = nt.replace('`versionCode`: `31201`','`versionCode`: `31203`')
    if p.name == 'ReleaseMetadataTest.java': nt = nt.replace('releaseMetadataMatchesV3121','releaseMetadataMatchesV3123')
    if nt != t: p.write_text(nt, encoding='utf-8')

# Correct verifier regex literals (plain version replacement does not alter escaped regex text).
p = root / 'tools/verify_html.mjs'
t = p.read_text(encoding='utf-8')
t = t.replace('/CellBiologyApp\\s*=\\s*\\{\\s*version:\\s*"3\\.12\\.2"/', '/CellBiologyApp\\s*=\\s*\\{\\s*version:\\s*"3\\.12\\.3"/')
t = t.replace('/Cell Biology Learning Hub, Version 3\\.12\\.2\\./', '/Cell Biology Learning Hub, Version 3\\.12\\.3\\./')
legacy = """requireText('Android 7/8 Object.values shim present', /if \\(!Object\\.values\\)/);\nrequireText('Android 7/8 Object.entries shim present', /if \\(!Object\\.entries\\)/);\nrequireText('Android 7/8 Object.fromEntries shim present', /if \\(!Object\\.fromEntries\\)/);\nif (html.includes('?.')) throw new Error('FAIL optional chaining remains; Android 7/8 WebView cannot parse it');\nif (/return\\s*\\{[^\\n}]*\\.\\.\\./.test(html)) throw new Error('FAIL object spread remains in return object');\nconsole.log('PASS Android 7/8 syntax compatibility invariants');\n"""
anchor = "requireText('narrow-screen table containment present', /table\\.compare-table\\{display:block;max-width:100%;overflow-x:auto/);\n"
if 'Android 7/8 syntax compatibility invariants' not in t:
    if anchor not in t: raise SystemExit('verify_html anchor missing')
    t = t.replace(anchor, anchor + legacy)
p.write_text(t, encoding='utf-8')

# Instrumentation: longer legacy boot allowance + genuine physical import-control tap.
p = root / 'app/src/androidTest/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivitySmokeTest.java'
t = p.read_text(encoding='utf-8')
if 'import androidx.test.uiautomator.UiObject2;' not in t:
    t = t.replace('import androidx.test.uiautomator.UiDevice;', 'import androidx.test.uiautomator.UiDevice;\nimport androidx.test.uiautomator.UiObject2;')
t = t.replace('private static final long JS_TIMEOUT_SECONDS = 15;', 'private static final long JS_TIMEOUT_SECONDS = 30;')
t = t.replace('long end = System.currentTimeMillis() + 15_000;', 'long end = System.currentTimeMillis() + 30_000;')
old = '''            eval(web, "document.querySelector('[data-action=\\"nav\\"][data-nav=\\"progress-history\\"]').click(); true");\n            eval(web, "document.querySelector('input[data-action=\\"import-progress\\"]').click(); true");\n            assertTrue("Open-document picker did not open", waitForExternalSystemUi(device));'''
new = '''            eval(web, "document.querySelector('[data-action=\\"nav\\"][data-nav=\\"progress-history\\"]').click(); true");\n            Thread.sleep(500);\n            UiObject2 importControl = device.wait(Until.findObject(By.textContains("Import progress")), UI_TIMEOUT_MS);\n            if (importControl != null) {\n                importControl.click();\n            } else {\n                tapDomElementPhysically(web, device, "input[data-action=\\"import-progress\\"]");\n            }\n            assertTrue("Open-document picker did not open after a physical Import-control tap", waitForExternalSystemUi(device));'''
if old in t:
    t = t.replace(old, new)
elif 'Open-document picker did not open after a physical Import-control tap' not in t:
    raise SystemExit('import test block missing')
helper = '''\n    private static void tapDomElementPhysically(WebView web, UiDevice device, String selector) {\n        String js = "(function(){var e=document.querySelector('" + selector.replace("'", "\\\\'") + "');"\n                + "if(!e)return '';var t=e.closest('label')||e;var r=t.getBoundingClientRect();"\n                + "return [r.left,r.top,r.width,r.height,window.devicePixelRatio||1].join(',');})()";\n        String data = unquote(eval(web, js));\n        assertNotNull("Import control DOM rectangle unavailable", data);\n        String[] parts = data.split(",");\n        assertTrue("Invalid Import control DOM rectangle: " + data, parts.length == 5);\n        double left = Double.parseDouble(parts[0]);\n        double top = Double.parseDouble(parts[1]);\n        double width = Double.parseDouble(parts[2]);\n        double height = Double.parseDouble(parts[3]);\n        double dpr = Double.parseDouble(parts[4]);\n        int[] location = new int[2];\n        InstrumentationRegistry.getInstrumentation().runOnMainSync(() -> web.getLocationOnScreen(location));\n        int x = location[0] + (int)Math.round((left + width / 2.0) * dpr);\n        int y = location[1] + (int)Math.round((top + height / 2.0) * dpr);\n        assertTrue("Physical tap on Import control failed", device.click(x, y));\n    }\n'''
marker = '\n    private static boolean waitForExternalSystemUi(UiDevice device) throws Exception {'
if 'private static void tapDomElementPhysically' not in t:
    if marker not in t: raise SystemExit('helper insertion marker missing')
    t = t.replace(marker, helper + marker)
p.write_text(t, encoding='utf-8')

# Provenance records the exact repaired HTML, while retaining exact original-APK hashes.
prov = root / 'PROVENANCE.json'
html = htmlp.read_bytes()
if prov.exists():
    data = json.loads(prov.read_text(encoding='utf-8'))
else:
    data = {
        'source_apk': 'CellBiologyLearningHub-3.12.1-release.apk',
        'source_apk_sha256': '4cbbee4cff9875c4a63a5b246672366d2c8817cdbc008b35e0abbba81eebf624',
        'source_apk_html_sha256': 'c13b9f839246b3d5e9e2cf4c3cf42154368494cbf96e2d4933a803e6c92e74bf',
        'provenance_note': 'Canonical maintenance tree reconstructed from the audited APK-derived baseline; original APK hashes retained for traceability.'
    }
data['patched_html_sha256'] = hashlib.sha256(html).hexdigest()
data['patched_html_bytes'] = len(html)
data['canonical_version'] = '3.12.3'
data['canonical_version_code'] = 31203
prov.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('v3.12.3 compatibility patch applied')
print('html_sha256', hashlib.sha256(html).hexdigest())
