from pathlib import Path
from bs4 import BeautifulSoup, Tag
import re, json, hashlib, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
A=ROOT/'app/src/main/assets'; UNITS=A/'units'

def pop_first(nodes,pred):
    for i,x in enumerate(nodes):
        if pred(x): return nodes.pop(i)
    return None

def txt(x): return x.get_text(' ',strip=True)

def pair(soup,en,ta,role):
    if not en or not ta: return False
    if not isinstance(ta,list): ta=[ta]
    p=soup.new_tag('section',attrs={'class':['bilingual-pair'],'data-pair-role':role})
    en.wrap(p)
    for n in ta: p.append(n)
    return True

for f in sorted(UNITS.glob('unit-*.html')):
    soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    changed=False
    for a in soup.select('article.lesson'):
        tb=a.find('section',class_='ta-block',recursive=False)
        if not tb: continue
        nodes=[x.extract() for x in tb.find_all(recursive=False) if isinstance(x,Tag)]
        tb.decompose()
        learning=pop_first(nodes,lambda x:'கற்றல் விளைவ' in txt(x))
        key=pop_first(nodes,lambda x:'முக்கிய சொற' in txt(x))
        apply=pop_first(nodes,lambda x:'சிந்தித்துப்' in txt(x) or 'சிந்தித்து' in txt(x))
        summary=pop_first(nodes,lambda x:'கருத்தின் சாரம்' in txt(x))
        depth=[]
        for i,x in enumerate(list(nodes)):
            if 'ஆழமான புரிதல்' in txt(x):
                x=nodes.pop(i);depth=[x]
                if i<len(nodes) and nodes[i].name=='p': depth.append(nodes.pop(i))
                break
        pair(soup,a.find('div',class_='goals',recursive=False),learning,'learning-outcome')
        pair(soup,a.find('div',class_='keyterms',recursive=False),key,'key-terms')
        pair(soup,a.find('div',class_='apply',recursive=False),apply,'think-apply')
        pair(soup,a.find('div',class_='summary',recursive=False),summary,'summary')
        pair(soup,a.find('section',class_='depth-extension',recursive=False),depth,'depth')
        direct=[x for x in a.find_all(recursive=False) if isinstance(x,Tag)]
        enparas=[x for x in direct if x.name=='p']
        taparas=[x for x in nodes if x.name=='p' and not (x.get('class') or [])]
        for en,ta in zip(enparas,taparas):
            if ta in nodes: nodes.remove(ta)
            pair(soup,en,ta,'explanation')
        direct=[x for x in a.find_all(recursive=False) if isinstance(x,Tag)]
        visual=[]
        for x in direct:
            if x.name=='h3' or 'bilingual-pair' in (x.get('class') or []): continue
            cls=set(x.get('class') or [])
            if x.name in {'figure','table'} or cls & {'naturalplate','explainer','visual','databox','compare','example','didyou','cause','memory','level','explain','authoritybox','law-facts','examnote','chemnamebox'}:
                visual.append(x)
        while nodes and visual:
            en=visual.pop(0); group=[nodes.pop(0)]
            while nodes and len(group)<4:
                cls=set(nodes[0].get('class') or [])
                if 'ta-title' in cls or 'caption' in cls or 'ta-figure-group' in cls: group.append(nodes.pop(0))
                else: break
            pair(soup,en,group,'visual-or-feature')
        if nodes:
            en=soup.new_tag('div',attrs={'class':['en-only','bilingual-anchor']});en.string='Related explanation'
            p=soup.new_tag('section',attrs={'class':['bilingual-pair'],'data-pair-role':'supplemental'});p.append(en)
            for n in nodes:p.append(n)
            a.append(p)
        changed=True
    if changed:f.write_text(str(soup),encoding='utf-8')

idx=A/'index.html'; html=idx.read_text(encoding='utf-8')
markers=['/* ===== v1.2.5 mobile reader / page-turn reliability ===== */','/* ===== v1.3.0 Android handset layout: definitive mobile rules ===== */','/* ===== v1.3.0 conservative Android WebView reader =====','/* ===== v1.3.0 native-control Android reader ===== */','/* ===== v1.3.0 native-scroll authoritative handset layer ===== */']
def rmblock(text,marker):
    start=text.find(marker)
    if start<0:return text
    media=text.find('@media',start)
    if media<0:return text
    brace=text.find('{',media);depth=0
    for i in range(brace,len(text)):
        if text[i]=='{':depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return text[:start]+text[i+1:]
    return text
for m in markers: html=rmblock(html,m)
css='''\n/* ===== v1.3.1 authoritative Android handset reader =====\n   Android native controls own navigation and the parent ScrollView owns vertical scrolling.\n   WebView pagination, swipe gestures, transforms and sticky HTML reader chrome are intentionally disabled on phones.\n*/\n@media(max-width:700px){\n html,body{width:100%!important;max-width:100%!important;overflow-x:hidden!important}\n body.bookmode{overflow-x:hidden!important;overflow-y:visible!important}\n body.bookmode .book-shell,body.bookmode .book-stage,body.bookmode .book-page{width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;transform:none!important;perspective:none!important;contain:none!important;position:static!important}\n body.bookmode .book-toolbar{display:none!important}\n body.bookmode .book-page{padding:14px 12px 18px!important;margin:0!important}\n body.bookmode .book-page-number{position:static!important;right:auto!important;bottom:auto!important;text-align:center!important;margin:24px 0 0!important}\n body.bookmode img,body.bookmode svg,body.bookmode canvas,body.bookmode table{max-width:100%!important;height:auto}\n .bilingual-pair{display:block;margin:0 0 12px}\n .depth-extension{margin-top:20px;padding-top:12px;border-top:1px solid var(--line)}\n}\n'''
pos=html.find('</style>');html=html[:pos]+css+html[pos:]
html=html.replace("function setLang(x){\n  x=(x==='ta')?'ta':'en';\n  document.body.classList.remove('enonly','taonly');\n  document.body.classList.add(x==='ta'?'taonly':'enonly');","function setLang(x){\n  x=(x==='ta'||x==='both')?x:'en';\n  document.body.classList.remove('enonly','taonly','bothlang');\n  if(x==='ta')document.body.classList.add('taonly');\n  else if(x==='en')document.body.classList.add('enonly');\n  else document.body.classList.add('bothlang');")
html=html.replace("  if(be)be.setAttribute('aria-pressed',x==='en'?'true':'false');\n  if(bt)bt.setAttribute('aria-pressed',x==='ta'?'true':'false');","  if(be)be.setAttribute('aria-pressed',x==='en'?'true':'false');\n  if(bt)bt.setAttribute('aria-pressed',x==='ta'?'true':'false');\n  var bb=document.getElementById('bookLangBoth');\n  if(bb)bb.setAttribute('aria-pressed',x==='both'?'true':'false');")
html=html.replace('v1.3.0','v1.3.1')
idx.write_text(html,encoding='utf-8')

java=ROOT/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java';j=java.read_text(encoding='utf-8')
j=j.replace('visualButton=makeButton("▣ Visual");','visualButton=makeButton("▣ Figures");')
j=j.replace('Button privacy=makeButton("Privacy"),english=makeButton("English"),tamil=makeButton("தமிழ்");\n        addWeighted(row2,privacy,1f); addWeighted(row2,english,1f); addWeighted(row2,tamil,1f);','Button privacy=makeButton("Privacy"),english=makeButton("English"),tamil=makeButton("தமிழ்"),both=makeButton("EN+TA");\n        addWeighted(row2,privacy,1f); addWeighted(row2,english,1f); addWeighted(row2,tamil,1f); addWeighted(row2,both,1f);')
j=j.replace("        tamil.setOnClickListener(v->js(\"setLang('ta');reportAndroidContentHeight();\",true));","        tamil.setOnClickListener(v->js(\"setLang('ta');reportAndroidContentHeight();\",true));\n        both.setOnClickListener(v->js(\"setLang('both');reportAndroidContentHeight();\",true));")
j=j.replace('    private final class HostBridge{','''    /**\n     * Narrow local-content bridge. SECURITY INVARIANT:\n     * Keep this interface minimal. Only primitive, non-sensitive UI sizing data may cross it.\n     * Do not add file, network, credential, intent, storage or arbitrary-command methods.\n     * The WebView is restricted to the appassets local origin and the app has no INTERNET permission.\n     */\n    private final class HostBridge{''')
java.write_text(j,encoding='utf-8')

bg=ROOT/'app/build.gradle';g=bg.read_text(encoding='utf-8').replace('versionCode 10300','versionCode 10301').replace("versionName '1.3.0'","versionName '1.3.1'");bg.write_text(g,encoding='utf-8')
catp=A/'book-catalog.json';cat=json.loads(catp.read_text(encoding='utf-8'));cat['version']='1.3.1';catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

(ROOT/'README.md').write_text('''# Environmental Studies Android — v1.3.1\n\nOffline bilingual undergraduate Environmental Studies textbook for Android.\n\n- Package: `edu.gascnagercoil.environmentalsciences`\n- versionName: `1.3.1`\n- versionCode: `10301`\n- minSdk 24; compileSdk/targetSdk 36\n- 9 modular unit files, 46 lessons, 58 bilingual MCQs, 80 reader pages\n- Local loading via `WebViewAssetLoader`; no INTERNET permission\n- Native Android navigation controls + native `ScrollView` handset reader\n- Language modes: English, தமிழ், EN+TA\n\n## Reader architecture\nAndroid handset navigation is native and the parent `ScrollView` owns vertical scrolling. The WebView renders bundled educational content only. Transform-based WebView pagination and swipe page-turning are intentionally disabled on phone-width layouts. A narrowly scoped `JavascriptInterface` reports rendered content height to Android; its only permitted responsibility is primitive UI sizing. See `docs/adr/0001-native-handset-reader.md`.\n\n## Bilingual pedagogy\nv1.3.1 restores semantic English–Tamil pairing. Tamil is no longer collected into one terminal lesson block. English-only, Tamil-only and EN+TA modes are presentation choices over the same paired source.\n\n## Verification\n```bash\npython tools/verify_content_integrity.py\ngradle --no-daemon clean lint test assembleDebug bundleRelease\n```\nThe verifier checks 46 lessons, 58 bilingual MCQs, catalog resolution, academic depth, paired bilingual DOM structure, Android reader invariants, version synchronization and absence of INTERNET permission.\n\n## Release notes — v1.3.1\n- consolidated superseded handset-reader CSS into one authoritative block;\n- restored paired bilingual lesson structure and added EN+TA mode;\n- retained native Android navigation and native vertical scrolling;\n- clarified `Visual` control as `Figures`;\n- documented and constrained the JS↔Android height bridge;\n- replaced stale verifier usage with one canonical v1.3.1-aware verifier;\n- synchronized README/build/catalog metadata;\n- incorporated the final v1.3.0 source audit into the release decision record.\n\nSigning credentials are intentionally not included.\n''',encoding='utf-8')

adr=ROOT/'docs/adr/0001-native-handset-reader.md';adr.parent.mkdir(parents=True,exist_ok=True);adr.write_text('''# ADR 0001 — Native handset reader with paired bilingual content\n\n**Status:** Accepted  \n**Release:** v1.3.1  \n**Date:** 2026-09-02\n\n## Context\nEarlier releases attempted transform-based pagination, swipe page turns and HTML reader controls inside Android WebView. Real-device testing repeatedly exposed clipped controls, lost clicks, horizontal displacement and unreliable vertical scrolling. v1.3.0 moved navigation to native Android controls and vertical scrolling to a native `ScrollView`. The final v1.3.0 audit also identified stale CI verifier wiring, README version drift and a terminal Tamil-block restructuring that weakened bilingual contextual anchoring.\n\n## Decision\n1. Android handset navigation is native.\n2. Vertical scrolling is owned by native `ScrollView`.\n3. WebView is a local content renderer hosted from `appassets.androidplatform.net`.\n4. One authoritative phone CSS layer replaces accumulated reader experiments.\n5. Educational source preserves semantic English–Tamil pairing; language mode changes visibility, not source order.\n6. `AndroidHost` is restricted to primitive content-height reporting only.\n7. Any future bridge method requires explicit security review.\n8. CI uses one canonical version-aware verifier.\n\n## Consequences\nThis trades animated page turns for predictable handset behaviour and maintainability. The bridge adds a small attack surface, mitigated by API 24+, local-origin-only loading, blocked external navigation, no INTERNET permission and one primitive sizing method.\n''',encoding='utf-8')

aud=ROOT/'docs/audits/v1.3.0-final-source-audit.md';aud.parent.mkdir(parents=True,exist_ok=True);aud.write_text('''# Audit incorporated: v1.3.0 — Real Source (Final)\n\n## Confirmed findings\n- v1.3.0-aware verifier passed while the legacy verifier was stale.\n- CI still invoked the stale verifier, creating a build blocker in the source workflow.\n- Native Android controls + `ScrollView` are a deliberate architecture pivot away from fragile WebView pagination.\n- The height-reporting `JavascriptInterface` is an acceptable narrowly scoped trade-off under the local-only security model, but must not grow casually.\n- README version metadata had drifted across releases.\n- `tools/requirements.txt` correctly pins BeautifulSoup and CI installs it.\n- Dynamic artifact naming from Gradle metadata is the preferred self-updating pattern.\n- `enableOnBackInvokedCallback=true`, absence of INTERNET permission and non-edge-to-edge handling remain appropriate.\n- The `Visual` feature existed but its label was insufficiently descriptive.\n\n## v1.3.1 actions\nAll blocking and maintainability findings above are corrected. The earlier APK audit's bilingual-pedagogy concern is also corrected by restoring semantic English–Tamil pairing and adding explicit EN+TA mode.\n''',encoding='utf-8')

ver=ROOT/'tools/verify_content_integrity.py';ver.write_text(r'''from pathlib import Path
from bs4 import BeautifulSoup
import json,sys
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'app/src/main/assets';errs=[];L=M=0
for p in sorted((A/'units').glob('unit-*.html')):
 s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser');ls=s.select('article.lesson');qs=s.select('.mcq');L+=len(ls);M+=len(qs)
 for a in ls:
  if a.find('section',class_='ta-block',recursive=False):errs.append(f'terminal Tamil block {a.get("id")}')
  pairs=a.select(':scope > section.bilingual-pair');roles={x.get('data-pair-role') for x in pairs}
  if len(pairs)<4:errs.append(f'paired structure {a.get("id")}')
  for req in ('learning-outcome','key-terms','think-apply','summary'):
   if req not in roles:errs.append(f'missing pair {req} {a.get("id")}')
  if len(a.get_text(' ',strip=True).split())<300:errs.append(f'academic depth {a.get("id")}')
 for q in qs:
  if not q.select_one('p .en') or not q.select_one('p .ta') or len(q.select('label .ta'))!=4:errs.append(f'bilingual mcq {p.name}');break
cat=json.loads((A/'book-catalog.json').read_text(encoding='utf-8'))
if cat.get('version')!='1.3.1' or len(cat.get('pages',[]))!=80:errs.append('catalog/version')
bg=(ROOT/'app/build.gradle').read_text(encoding='utf-8');rd=(ROOT/'README.md').read_text(encoding='utf-8');idx=(A/'index.html').read_text(encoding='utf-8');java=(ROOT/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java').read_text(encoding='utf-8');man=(ROOT/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
if "versionName '1.3.1'" not in bg or 'versionCode 10301' not in bg:errs.append('gradle version')
if 'v1.3.1' not in rd or 'versionCode: `10301`' not in rd:errs.append('README version')
if idx.count('v1.3.1 authoritative Android handset reader')!=1:errs.append('authoritative mobile CSS')
for stale in ('v1.2.5 mobile reader / page-turn reliability','v1.3.0 conservative Android WebView reader','v1.3.0 native-control Android reader','v1.3.0 native-scroll authoritative handset layer'):
 if stale in idx:errs.append('stale CSS '+stale)
if "x==='ta'||x==='both'" not in idx:errs.append('EN+TA mode')
for tok in ('new ScrollView(this)','setNestedScrollingEnabled(false)','makeButton("EN+TA")','makeButton("▣ Figures")','@JavascriptInterface'):
 if tok not in java:errs.append('android invariant '+tok)
if java.count('@JavascriptInterface')!=1:errs.append('bridge method count')
if 'android.permission.INTERNET' in man:errs.append('INTERNET permission')
if L!=46:errs.append(f'lesson total {L}')
if M!=58:errs.append(f'mcq total {M}')
if errs:print('VERIFY FAIL: '+'; '.join(errs));sys.exit(1)
print('VERIFY PASS: v1.3.1 paired bilingual pedagogy, 46-lesson depth, 58 bilingual MCQs, single handset CSS architecture, native ScrollView controls, narrow JS bridge and synchronized release metadata verified.')
''',encoding='utf-8')
stale=ROOT/'tools/verify_content_integrity_v130.py'
if stale.exists():stale.unlink()
manifest={'release':'1.3.1','previous_release':'1.3.0','content_change':True,'purpose':'Audit-driven maintainability, bilingual pedagogy and CI correction.','units':[]}
for f in sorted(UNITS.glob('unit-*.html')):
 s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser');manifest['units'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':len(f.read_bytes()),'lessons':len(s.select('article.lesson')),'mcqs':len(s.select('.mcq'))})
(ROOT/'verification/content-revision-manifest-v1.3.1.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Applied v1.3.1 audit corrections')
