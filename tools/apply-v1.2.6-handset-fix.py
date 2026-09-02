from pathlib import Path
import re, json

ROOT=Path('build-source/Environmental-Sciences-Android')
INDEX=ROOT/'app/src/main/assets/index.html'
JAVA=ROOT/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java'
GRADLE=ROOT/'app/build.gradle'
CATALOG=ROOT/'app/src/main/assets/book-catalog.json'
README=ROOT/'README.md'
META=ROOT/'verification/app-build-metadata.json'
VERIFIER=ROOT/'tools/verify_content_integrity.py'

# ---- index.html: compact bounded handset UI + robust language controls ----
t=INDEX.read_text(encoding='utf-8')
t=t.replace('Modular Book Edition v1.2.5','Modular Book Edition v1.2.6')
old='''<div class="book-toolbar">\n<div class="group"><button aria-label="Contents" id="tocBook" type="button">☰ Contents</button>\n<button aria-label="Previous page" id="prevPage" type="button">←</button>\n<button aria-label="Next page" id="nextPage" type="button">→</button>\n<select aria-label="Jump to page" class="hide-mobile" id="pageJump"></select>\n<button id="visualOnlyBtn" title="Focus on figures" type="button">🖼 Visual focus</button></div>\n<div class="group">\n<button onclick="setLang('en')" type="button">English</button>\n<button onclick="setLang('ta')" type="button">தமிழ்</button>\n</div>\n</div>'''
new='''<div class="book-toolbar" role="toolbar" aria-label="Book controls">\n<div class="book-primary-controls">\n<button aria-label="Contents" id="tocBook" type="button"><span aria-hidden="true">☰</span><span class="label">Contents</span></button>\n<button aria-label="Previous page" id="prevPage" type="button">←</button>\n<button aria-label="Next page" id="nextPage" type="button">→</button>\n<button id="visualOnlyBtn" title="Focus on figures" type="button"><span aria-hidden="true">🖼</span><span class="label">Visual</span></button>\n<select aria-label="Jump to page" class="hide-mobile" id="pageJump"></select>\n</div>\n<div class="book-secondary-controls">\n<button id="bookPrivacyBtn" type="button" aria-label="Open privacy policy">Privacy</button>\n<button id="bookLangEn" type="button" aria-pressed="true" lang="en">English</button>\n<button id="bookLangTa" type="button" aria-pressed="false" lang="ta">தமிழ்</button>\n</div>\n</div>'''
if old not in t: raise SystemExit('toolbar markup not found')
t=t.replace(old,new,1)
# remove dynamically appended privacy button from the old first row
t=re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\',\(\)=>\{\s*const tb=document\.querySelector\(\'.book-toolbar \.group\'\);.*?</script>','',t,count=1,flags=re.S)
old_lang="""  var e=document.getElementById('btnEn'),t=document.getElementById('btnTa');
  if(e)e.setAttribute('aria-pressed',x==='en'?'true':'false');
  if(t)t.setAttribute('aria-pressed',x==='ta'?'true':'false');
  document.documentElement.lang=x==='ta'?'ta':'en';
  try{localStorage.setItem('esLang',x)}catch(e){}
}"""
new_lang="""  var e=document.getElementById('btnEn'),t=document.getElementById('btnTa');
  var be=document.getElementById('bookLangEn'),bt=document.getElementById('bookLangTa');
  if(e)e.setAttribute('aria-pressed',x==='en'?'true':'false');
  if(t)t.setAttribute('aria-pressed',x==='ta'?'true':'false');
  if(be)be.setAttribute('aria-pressed',x==='en'?'true':'false');
  if(bt)bt.setAttribute('aria-pressed',x==='ta'?'true':'false');
  document.documentElement.lang=x==='ta'?'ta':'en';
  try{localStorage.setItem('esLang',x)}catch(e){}
  if(document.body.classList.contains('bookmode')) requestAnimationFrame(()=>{document.documentElement.scrollLeft=0;document.body.scrollLeft=0;var p=document.getElementById('bookPage');if(p)p.scrollLeft=0;});
}"""
if old_lang not in t: raise SystemExit('language function block not found')
t=t.replace(old_lang,new_lang,1)
needle="""  if(e.target?.id==='nextPage')showBookPage(bookIndex+1,'next');
  else if(e.target?.id==='prevPage')showBookPage(bookIndex-1,'prev');
  else if(e.target?.id==='exitBook')exitBookMode();"""
replacement="""  const target=e.target?.closest?.('button,select,a')||e.target;
  if(target?.id==='nextPage')showBookPage(bookIndex+1,'next');
  else if(target?.id==='prevPage')showBookPage(bookIndex-1,'prev');
  else if(target?.id==='bookLangEn'){e.preventDefault();setLang('en');}
  else if(target?.id==='bookLangTa'){e.preventDefault();setLang('ta');}
  else if(target?.id==='bookPrivacyBtn'){e.preventDefault();location.href='privacy.html';}
  else if(target?.id==='exitBook')exitBookMode();"""
if needle not in t: raise SystemExit('book click handler not found')
t=t.replace(needle,replacement,1)
t=t.replace("""  br.addEventListener('touchstart',e=>{
    touchX=e.changedTouches[0].screenX;touchY=e.changedTouches[0].screenY
  },{passive:true});""","""  br.addEventListener('touchstart',e=>{
    if(e.target.closest?.('.book-toolbar')){touchX=null;touchY=null;return;}
    touchX=e.changedTouches[0].screenX;touchY=e.changedTouches[0].screenY
  },{passive:true});""",1)
t=t.replace("if(Math.abs(dx)>90&&Math.abs(dx)>Math.abs(dy)*1.8)","if(Math.abs(dx)>90&&Math.abs(dx)>Math.abs(dy)*1.8)",1) if "Math.abs(dx)>90" in t else t.replace("if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.25)","if(Math.abs(dx)>90&&Math.abs(dx)>Math.abs(dy)*1.8)",1)
css=r'''
/* ===== v1.2.6 Android handset layout: definitive mobile rules ===== */
*,*::before,*::after{box-sizing:border-box}
html{width:100%;min-width:0;overflow-x:hidden;scroll-behavior:auto}
body{width:100%;min-width:0;max-width:100%;margin:0;overflow-x:hidden!important;overflow-y:auto!important;-webkit-overflow-scrolling:touch;touch-action:pan-y}
body.bookmode{position:static!important;height:auto!important;min-height:100%!important;overflow-y:auto!important;overflow-x:hidden!important}
body.bookmode #bookReader{width:100%;max-width:100%;min-width:0;margin:0!important;padding:0!important;overflow:visible!important}
body.bookmode .book-toolbar{box-sizing:border-box;left:auto;right:auto;width:100%;max-width:100%;min-width:0;margin:0!important}
.book-primary-controls,.book-secondary-controls{min-width:0}
@media(max-width:700px){
 body.bookmode{background:#fffdf8!important}
 body.bookmode .book-toolbar{position:sticky!important;top:0!important;z-index:1000!important;display:grid!important;grid-template-rows:auto auto!important;grid-template-columns:1fr!important;gap:4px!important;padding:5px 6px 6px!important;background:#f8fbf9!important;border:0!important;border-bottom:1px solid #d7e1dc!important;border-radius:0!important;box-shadow:0 2px 8px rgba(20,55,44,.08)!important;overflow:visible!important;transform:none!important}
 .book-primary-controls{display:grid!important;grid-template-columns:minmax(88px,1.35fr) 42px 42px minmax(82px,1.2fr)!important;gap:4px!important;width:100%!important;max-width:100%!important;align-items:stretch!important}
 .book-primary-controls #pageJump{display:none!important}
 .book-secondary-controls{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:4px!important;width:100%!important;max-width:100%!important}
 body.bookmode .book-toolbar button{display:flex!important;align-items:center!important;justify-content:center!important;gap:4px!important;width:100%!important;min-width:0!important;max-width:100%!important;height:38px!important;min-height:38px!important;padding:4px 6px!important;margin:0!important;border-radius:9px!important;font-size:13px!important;line-height:1.05!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;touch-action:manipulation!important}
 body.bookmode .book-toolbar button[aria-pressed="true"]{background:#1f6552!important;color:#fff!important;border-color:#1f6552!important}
 body.bookmode .book-toolbar .label{display:inline!important}
 body.bookmode .book-stage{display:block!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:0!important;margin:0!important;padding:0!important;overflow:visible!important;perspective:none!important;contain:none!important;transform:none!important}
 body.bookmode .book-page{display:block!important;position:relative!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:0!important;height:auto!important;max-height:none!important;margin:0!important;padding:22px 14px 58px!important;border:0!important;border-radius:0!important;box-shadow:none!important;transform:none!important;overflow-x:hidden!important;overflow-y:visible!important;contain:none!important;touch-action:pan-y!important}
 body.bookmode .book-page::before{display:none!important}
 body.bookmode .book-page *{max-width:100%}
 body.bookmode .book-page p,body.bookmode .book-page li,body.bookmode .book-page h1,body.bookmode .book-page h2,body.bookmode .book-page h3,body.bookmode .book-page h4,body.bookmode .book-page h5{overflow-wrap:anywhere;word-break:normal;white-space:normal}
 body.bookmode .book-page img,body.bookmode .book-page svg,body.bookmode .book-page video,body.bookmode .book-page canvas{width:100%!important;max-width:100%!important;height:auto!important}
 body.bookmode .book-page .naturalplate svg,body.bookmode .book-page .explainer svg,body.bookmode .book-page .ta-figure-card svg{min-height:0!important;max-height:none!important;aspect-ratio:auto!important}
 body.bookmode .fact-table{display:block!important;width:100%!important;max-width:100%!important;overflow-x:auto!important;touch-action:pan-x pan-y!important}
 body.bookmode .book-page.turn-next,body.bookmode .book-page.turn-prev{animation:phonePageFade .14s ease-out both!important}
 @keyframes phonePageFade{from{opacity:.68}to{opacity:1}}
}
@media(max-width:380px){.book-primary-controls{grid-template-columns:minmax(78px,1.25fr) 38px 38px minmax(72px,1.1fr)!important}body.bookmode .book-toolbar button{height:36px!important;min-height:36px!important;font-size:12px!important;padding:3px 4px!important}body.bookmode .book-page{padding-left:11px!important;padding-right:11px!important}}
'''
marker='</style><meta content="#1f6552"'
pos=t.find(marker)
if pos<0: raise SystemExit('head style marker not found')
t=t[:pos]+css+'\n'+t[pos:]
INDEX.write_text(t,encoding='utf-8')

# ---- Android host: stop edge-to-edge overlap and preserve vertical scrolling ----
s=JAVA.read_text(encoding='utf-8')
s=s.replace('import android.view.WindowInsets;\n','')
s=s.replace('''        Window window = getWindow();
        if (android.os.Build.VERSION.SDK_INT >= 30) window.setDecorFitsSystemWindows(false);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(255,253,248));
        webView.setFitsSystemWindows(false);
        webView.setOnApplyWindowInsetsListener((v, insets) -> {
            if (android.os.Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                v.setPadding(bars.left, bars.top, bars.right, bars.bottom);
                return WindowInsets.CONSUMED;
            }
            return insets;
        });''','''        Window window = getWindow();
        if (android.os.Build.VERSION.SDK_INT >= 30) window.setDecorFitsSystemWindows(true);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(255,253,248));
        webView.setFitsSystemWindows(true);
        webView.setVerticalScrollBarEnabled(true);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);''')
s=s.replace('''        settings.setCacheMode(WebSettings.LOAD_DEFAULT);''','''        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);''')
JAVA.write_text(s,encoding='utf-8')

# ---- release metadata ----
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+10205','versionCode 10206',g);g=re.sub(r"versionName\s+'1\.2\.5'","versionName '1.2.6'",g);GRADLE.write_text(g,encoding='utf-8')
cat=json.loads(CATALOG.read_text(encoding='utf-8'));cat['version']='1.2.6';CATALOG.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
meta=json.loads(META.read_text(encoding='utf-8'));meta.update(version_name='1.2.6',version_code=10206,app_version='1.2.6',content_revision='v1.2.6 Android handset layout/system-bar/scroll/language-control correction; educational unit payloads unchanged',content_revision_manifest='verification/content-revision-manifest-v1.2.6.json');META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prev=ROOT/'verification/content-revision-manifest-v1.2.5.json';m=json.loads(prev.read_text(encoding='utf-8'));m['release']='1.2.6';m['previous_release']='1.2.5';m['purpose']='Android handset safe-area, compact toolbar, language-control, overflow and vertical-scroll correction.';m['content_change']=False;m['reader_changes']=['Use Android system-bar-safe layout instead of edge-to-edge WebView padding consumption','Compact two-row phone toolbar fully bounded to viewport','Explicit book-mode English/Tamil buttons with aria state and delegated handlers','Normal vertical document scrolling; no reader-stage containment/clipping','Disable horizontal WebView scrollbar and bound all page/media content to viewport','Make swipe page navigation more conservative so vertical scrolling wins','Keep phone page transitions as a short non-geometric fade'];(ROOT/'verification/content-revision-manifest-v1.2.6.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=VERIFIER.read_text(encoding='utf-8').replace('content-revision-manifest-v1.2.5.json','content-revision-manifest-v1.2.6.json').replace("'1.2.5'","'1.2.6'").replace('versionCode 10205','versionCode 10206').replace('v1.2.5 mobile reader correction with unchanged verified educational content','v1.2.6 Android handset layout correction with unchanged verified educational content');VERIFIER.write_text(v,encoding='utf-8')
r=README.read_text(encoding='utf-8').replace('versionName: `1.2.5`','versionName: `1.2.6`').replace('versionCode: `10205`','versionCode: `10206`').replace('content-revision-manifest-v1.2.5.json','content-revision-manifest-v1.2.6.json').replace('v1.2.5 hashes','v1.2.6 hashes');r+='\n\n## v1.2.6 handset layout correction\n\nDevice-confirmed fix for system-bar overlap, clipped reader toolbar, unreliable language controls, horizontal page overflow and vertical scrolling on Android phones. Educational unit content is unchanged.\n';README.write_text(r,encoding='utf-8')
print('v1.2.6 patch applied')
