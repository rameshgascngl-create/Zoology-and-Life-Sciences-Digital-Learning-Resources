from pathlib import Path
import re,json
ROOT=Path('build-source/Environmental-Sciences-Android')
IDX=ROOT/'app/src/main/assets/index.html'; GR=ROOT/'app/build.gradle'; CAT=ROOT/'app/src/main/assets/book-catalog.json'; MA=ROOT/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java'; META=ROOT/'verification/app-build-metadata.json'; VER=ROOT/'tools/verify_content_integrity.py'
t=IDX.read_text(encoding='utf-8')
# Critical Android bug: preventDefault on toolbar touchend cancels the synthetic click.
t=re.sub(r"\n\s*document\.addEventListener\('touchend',function\(e\)\{\s*if\(e\.target\.closest\?\.\('\.book-toolbar'\)\)e\.preventDefault\(\);\s*\},\{passive:false\}\);\s*","\n",t)
# Remove swipe listeners completely: native vertical WebView scrolling gets exclusive touch handling.
t=re.sub(r"\nconst br=document\.getElementById\('bookReader'\);\nif\(br\)\{.*?\n\}\n</script>","\n</script>",t,count=1,flags=re.S)
# Do not focus/scroll the document on every page render on phones.
t=t.replace("""    p.focus({preventScroll:true});
    document.documentElement.scrollLeft=0;
    document.body.scrollLeft=0;
    if(window.matchMedia('(max-width:700px)').matches){
      window.scrollTo(0,0);
    }else{
      window.scrollTo({top:0,behavior:'smooth'});
    }""","""    document.documentElement.scrollLeft=0;
    document.body.scrollLeft=0;
    if(window.matchMedia('(min-width:701px)').matches) window.scrollTo({top:0,behavior:'smooth'});""")
css='''
/* ===== v1.2.7 conservative Android WebView reader ===== */
@media(max-width:700px){
 html,body{width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;min-height:100%!important;overflow-x:hidden!important;overflow-y:visible!important;touch-action:auto!important}
 body.bookmode{position:static!important;height:auto!important;min-height:100%!important;overflow:visible!important;touch-action:auto!important}
 body.bookmode #bookReader,body.bookmode .book-shell,body.bookmode .book-stage{position:static!important;display:block!important;width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;min-height:0!important;max-height:none!important;margin:0!important;padding:0!important;overflow:visible!important;contain:none!important;transform:none!important;perspective:none!important;touch-action:auto!important}
 body.bookmode .book-toolbar{position:static!important;display:block!important;width:100%!important;max-width:100%!important;margin:0!important;padding:6px!important;background:#f8fbf9!important;border:0!important;border-bottom:1px solid #d7e1dc!important;border-radius:0!important;box-shadow:none!important;overflow:visible!important;transform:none!important;touch-action:auto!important}
 .book-primary-controls,.book-secondary-controls{display:grid!important;width:100%!important;max-width:100%!important;min-width:0!important;gap:5px!important;margin:0!important}
 .book-primary-controls{grid-template-columns:minmax(0,1.5fr) 44px 44px minmax(0,1.1fr)!important}.book-secondary-controls{grid-template-columns:repeat(3,minmax(0,1fr))!important;margin-top:5px!important}.book-primary-controls #pageJump{display:none!important}
 body.bookmode .book-toolbar button{display:block!important;width:100%!important;min-width:0!important;max-width:100%!important;height:42px!important;min-height:42px!important;padding:6px 5px!important;margin:0!important;border-radius:8px!important;font-size:13px!important;line-height:1.1!important;white-space:normal!important;overflow:visible!important;text-overflow:clip!important;touch-action:auto!important;pointer-events:auto!important}
 body.bookmode .book-toolbar button[aria-pressed="true"]{background:#1f6552!important;color:#fff!important;border-color:#1f6552!important}
 body.bookmode .book-page{position:static!important;display:block!important;width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;min-height:0!important;max-height:none!important;margin:0!important;padding:20px 14px 64px!important;border:0!important;border-radius:0!important;box-shadow:none!important;transform:none!important;overflow:visible!important;contain:none!important;touch-action:auto!important;pointer-events:auto!important}
 body.bookmode .book-page::before{display:none!important}body.bookmode .book-page *{box-sizing:border-box;max-width:100%}
 body.bookmode .book-page p,body.bookmode .book-page li,body.bookmode .book-page h1,body.bookmode .book-page h2,body.bookmode .book-page h3,body.bookmode .book-page h4,body.bookmode .book-page h5{white-space:normal!important;overflow-wrap:break-word!important;word-break:normal!important}
 body.bookmode .book-page img,body.bookmode .book-page svg,body.bookmode .book-page canvas,body.bookmode .book-page video{display:block!important;width:auto!important;max-width:100%!important;height:auto!important}
 body.bookmode .book-page .naturalplate svg,body.bookmode .book-page .explainer svg,body.bookmode .book-page .ta-figure-card svg{width:100%!important;min-height:0!important;max-height:none!important}
 body.bookmode .fact-table{display:block!important;width:100%!important;max-width:100%!important;overflow-x:auto!important;-webkit-overflow-scrolling:touch!important}
 body.bookmode .book-page.turn-next,body.bookmode .book-page.turn-prev{animation:none!important}.book-hint{display:none!important}
}
@media(max-width:380px){.book-primary-controls{grid-template-columns:minmax(0,1.35fr) 40px 40px minmax(0,1fr)!important}body.bookmode .book-toolbar button{font-size:12px!important;min-height:40px!important;height:40px!important;padding:4px!important}body.bookmode .book-page{padding-left:11px!important;padding-right:11px!important}}
'''
t=t.replace('</style><meta content="#1f6552"',css+'\n</style><meta content="#1f6552"',1)
# Explicit click binding with no touch handlers.
extra='''<script>(function(){function b(id,fn){const e=document.getElementById(id);if(!e||e.dataset.bound127)return;e.dataset.bound127='1';e.addEventListener('click',function(ev){ev.stopPropagation();fn();},false)}function init(){b('bookLangEn',()=>setLang('en'));b('bookLangTa',()=>setLang('ta'));b('prevPage',()=>showBookPage(bookIndex-1,'prev'));b('nextPage',()=>showBookPage(bookIndex+1,'next'));b('bookPrivacyBtn',()=>location.href='privacy.html')}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init()})();</script>'''
t=t.replace('</body>',extra+'\n</body>')
t=t.replace('v1.2.6','v1.2.7'); IDX.write_text(t,encoding='utf-8')
g=GR.read_text();g=g.replace('versionCode 10206','versionCode 10207').replace("versionName '1.2.6'","versionName '1.2.7'");GR.write_text(g)
c=json.loads(CAT.read_text());c['version']='1.2.7';CAT.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
j=MA.read_text();j=j.replace('settings.setLoadWithOverviewMode(false);','settings.setLoadWithOverviewMode(true);').replace('settings.setUseWideViewPort(false);','settings.setUseWideViewPort(true);');MA.write_text(j)
meta=json.loads(META.read_text());meta.update(version_name='1.2.7',version_code=10207,app_version='1.2.7',content_revision='v1.2.7 conservative Android WebView interaction/scroll correction; educational content unchanged',content_revision_manifest='verification/content-revision-manifest-v1.2.7.json');META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
m=json.loads((ROOT/'verification/content-revision-manifest-v1.2.6.json').read_text());m['release']='1.2.7';m['previous_release']='1.2.6';m['purpose']='Remove Android touch cancellation and restore native WebView scrolling.';m['content_change']=False;m['reader_changes']=['Remove toolbar touchend preventDefault that cancels Android click synthesis','Remove swipe handlers so WebView owns vertical touch scrolling','Use normal-flow non-sticky mobile toolbar','Remove mobile transform/containment/touch-action overrides','Bind language/navigation with ordinary click events','Enable wide viewport/overview scaling'];(ROOT/'verification/content-revision-manifest-v1.2.7.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
v=VER.read_text().replace('content-revision-manifest-v1.2.6.json','content-revision-manifest-v1.2.7.json').replace("'1.2.6'","'1.2.7'").replace('versionCode 10206','versionCode 10207').replace('v1.2.6 Android handset layout correction with unchanged verified educational content','v1.2.7 conservative Android WebView correction with unchanged verified educational content');VER.write_text(v)
assert "closest?.('.book-toolbar'))e.preventDefault" not in t
assert "br.addEventListener('touchstart'" not in t
assert "br.addEventListener('touchend'" not in t
print('v1.2.7 patch applied')