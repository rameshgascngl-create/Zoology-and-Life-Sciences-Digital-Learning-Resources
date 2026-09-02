"""Apply the narrowly scoped v1.3.2 Privacy-footer revision to v1.3.1."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(sys.argv[1]).resolve()
ASSETS = ROOT / 'app/src/main/assets'
PRIVACY_SHA = '8a692f37a158095f514fd6474479321e2b954b1f36274159cd0091273c9855c6'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def replace_once(text, old, new):
    assert text.count(old) == 1, f'Expected exactly one occurrence: {old!r}'
    return text.replace(old, new, 1)

privacy_path = ASSETS / 'privacy.html'
assert sha(privacy_path) == PRIVACY_SHA, 'Unexpected privacy-policy baseline; review before applying'
preserved = [ASSETS / 'index.html', *sorted((ASSETS / 'units').glob('unit-*.html')),
             ROOT / 'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java']
before = {str(p.relative_to(ROOT)): sha(p) for p in preserved}
privacy = privacy_path.read_text(encoding='utf-8')
style = '''
.privacy-credit{margin-top:32px;padding:20px 0 0;border-top:1px solid #ccdcd4;text-align:center;font-size:.875rem;line-height:1.6;overflow-wrap:anywhere}
.privacy-credit p{margin:0}.privacy-credit strong{font-weight:600}
'''
footer = '''
<footer id="privacyFooter" class="privacy-credit" lang="en">
<p><strong>R.Ramesh</strong><br>Department of Zoology<br>Government Arts and Science College<br>Nagercoil, Tamil Nadu</p>
</footer>
'''
# Native ScrollView needs the actual content bottom, not the WebView's own
# viewport height. Keep the same existing primitive-only Android interface.
height_script = '''
<script>
let privacyHeightFrame=0;
function reportAndroidContentHeight(){
  if(!window.AndroidHost||typeof window.AndroidHost.setContentHeight!=='function')return;
  cancelAnimationFrame(privacyHeightFrame);
  privacyHeightFrame=requestAnimationFrame(function(){
    const footer=document.getElementById('privacyFooter');
    if(!footer)return;
    const padding=parseFloat(getComputedStyle(document.body).paddingBottom)||0;
    const height=Math.ceil(footer.getBoundingClientRect().bottom+window.scrollY+padding);
    if(Number.isFinite(height)&&height>0)window.AndroidHost.setContentHeight(height);
  });
}
window.addEventListener('load',reportAndroidContentHeight);
window.addEventListener('resize',reportAndroidContentHeight);
if(document.fonts)document.fonts.ready.then(reportAndroidContentHeight);
</script>
'''
privacy = replace_once(privacy, '</style>', style + '</style>')
privacy = replace_once(privacy, '</body>', footer + height_script + '</body>')
privacy_path.write_text(privacy, encoding='utf-8')

gradle_path = ROOT / 'app/build.gradle'
gradle = replace_once(gradle_path.read_text(), "versionName '1.3.1'", "versionName '1.3.2'")
gradle = replace_once(gradle, 'versionCode 10301', 'versionCode 10302')
gradle_path.write_text(gradle)
catalog_path = ASSETS / 'book-catalog.json'
catalog_path.write_text(replace_once(catalog_path.read_text(), '"version": "1.3.1"', '"version": "1.3.2"'))
readme_path = ROOT / 'README.md'
readme = replace_once(readme_path.read_text(), '# Environmental Studies Android — v1.3.1', '# Environmental Studies Android — v1.3.2')
readme = replace_once(readme, '- versionName: `1.3.1`', '- versionName: `1.3.2`')
readme = replace_once(readme, '- versionCode: `10301`', '- versionCode: `10302`')
readme += '\n## Release notes — v1.3.2\n\nName and institutional details added only to the Privacy page footer, without a role title. All nine unit files, the textbook reader and Android activity are byte-identical to v1.3.1. Privacy-page height reporting keeps the footer reachable in the native ScrollView.\n'
readme_path.write_text(readme)

verifier_path = ROOT / 'tools/verify_content_integrity.py'
verifier = verifier_path.read_text()
for old, new in [
    ("cat.get('version')!='1.3.1'", "cat.get('version')!='1.3.2'"),
    ("versionName '1.3.1'", "versionName '1.3.2'"),
    ('versionCode 10301', 'versionCode 10302'),
    ("if 'v1.3.1' not in ", "if '# Environmental Studies Android — v1.3.2' not in "),
    ('versionCode: `10301`', 'versionCode: `10302`'),
    ('VERIFY PASS: v1.3.1 ', 'VERIFY PASS: v1.3.2 '),
]:
    verifier = replace_once(verifier, old, new)
footer_check = '''import hashlib
readme=(ROOT/'README.md').read_text(encoding='utf-8')
privacy=BeautifulSoup((A/'privacy.html').read_text(encoding='utf-8'),'html.parser')
footer=privacy.select('footer#privacyFooter')
if len(footer)!=1 or footer[0].get_text(' ',strip=True)!='R.Ramesh Department of Zoology Government Arts and Science College Nagercoil, Tamil Nadu': errs.append('Privacy footer identity')
if 'versionName: `1.3.2`' not in readme: errs.append('README versionName')
revision=json.loads((ROOT/'verification/content-revision-manifest-v1.3.2.json').read_text())
for path,expected in revision['preserved_files'].items():
 if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected: errs.append('preserved content '+path)
if hashlib.sha256((A/'privacy.html').read_bytes()).hexdigest()!=revision['privacy_sha256']: errs.append('Privacy content hash')
'''
verifier = replace_once(verifier, 'if errs:', footer_check + 'if errs:')
verifier_path.write_text(verifier)

meta_path = ROOT / 'verification/app-build-metadata.json'
meta = json.loads(meta_path.read_text())
meta.update(version_name='1.3.2', version_code=10302, app_version='1.3.2',
            content_revision='v1.3.2 Privacy footer; educational content unchanged from v1.3.1',
            content_revision_manifest='verification/content-revision-manifest-v1.3.2.json')
meta_path.write_text(json.dumps(meta, indent=2)+'\n')
revision = dict(release='1.3.2', previous_release='1.3.1', educational_content_changed=False,
                purpose='Name and institutional details in Privacy footer only; no role title.',
                previous_privacy_sha256=PRIVACY_SHA, privacy_sha256=sha(privacy_path), preserved_files=before)
(ROOT / 'verification/content-revision-manifest-v1.3.2.json').write_text(json.dumps(revision, indent=2)+'\n')
assert all(sha(ROOT / path) == digest for path, digest in before.items())
print('PRIVACY FOOTER PASS: requested identity; no role title; 11 content/activity files unchanged; v1.3.2 / 10302')
