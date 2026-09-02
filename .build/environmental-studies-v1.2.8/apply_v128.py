from pathlib import Path
import json,re,shutil

root=Path('.')
idx=root/'app/src/main/assets/index.html'
text=idx.read_text(encoding='utf-8')

# Remove the Android-hostile toolbar touch cancellation and swipe listeners if present.
text=re.sub(r"\n\s*document\.addEventListener\('touchend',function\(e\)\{\s*if\(e\.target\.closest\?\.\('\.book-toolbar'\)\)e\.preventDefault\(\);\s*\},\{passive:false\}\);\s*","\n",text)
text=re.sub(r"\nconst br=document\.getElementById\('bookReader'\);\nif\(br\)\{.*?\n\}\n</script>","\n</script>",text,count=1,flags=re.S)

css='''\n/* ===== v1.2.8 native-control Android reader ===== */\n@media(max-width:700px){\n  body.bookmode .book-toolbar{display:none!important}\n  body.bookmode #bookReader,body.bookmode .book-shell,body.bookmode .book-stage,body.bookmode .book-page{\n    position:static!important;width:100%!important;max-width:100%!important;min-width:0!important;\n    height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;\n    transform:none!important;contain:none!important;touch-action:auto!important;\n  }\n  html,body,body.bookmode{overflow-x:hidden!important;overflow-y:auto!important;height:auto!important;min-height:100%!important;touch-action:auto!important}\n  body.bookmode .book-page{padding:18px 14px 64px!important;margin:0!important;border:0!important;box-shadow:none!important}\n  body.bookmode .book-page *{box-sizing:border-box;max-width:100%}\n  body.bookmode .book-page img,body.bookmode .book-page svg,body.bookmode .book-page canvas,body.bookmode .book-page video{max-width:100%!important;height:auto!important}\n  .figure-lightbox:not(.open){pointer-events:none!important}\n  .book-hint{display:none!important}\n}\n'''
text=text.replace('</style><meta content="#1f6552"',css+'\n</style><meta content="#1f6552"',1)
text=text.replace('v1.2.5','v1.2.8')
idx.write_text(text,encoding='utf-8')

# Replace Android host with native control-bar implementation.
src=Path('../../.build/environmental-studies-v1.2.8/MainActivity.java')
dst=root/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java'
shutil.copyfile(src,dst)

# Version metadata.
gradle=root/'app/build.gradle'
g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 10208',g)
g=re.sub(r"versionName\s+'[^']+'","versionName '1.2.8'",g)
gradle.write_text(g,encoding='utf-8')

catalog=root/'app/src/main/assets/book-catalog.json'
cat=json.loads(catalog.read_text(encoding='utf-8'));cat['version']='1.2.8'
catalog.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

meta_path=root/'verification/app-build-metadata.json'
meta=json.loads(meta_path.read_text(encoding='utf-8'))
meta['version_name']='1.2.8';meta['version_code']=10208;meta['app_version']='1.2.8'
meta['content_revision']='v1.2.8 native Android control bar and WebView scrolling correction; educational content unchanged'
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Reuse unchanged unit hashes in a v1.2.8 release manifest.
prev=root/'verification/content-revision-manifest-v1.2.5.json'
m=json.loads(prev.read_text(encoding='utf-8'))
m['release']='1.2.8';m['previous_release']='1.2.5';m['content_change']=False
m['purpose']='Move critical controls out of HTML into native Android UI and restore plain WebView scrolling.'
m['reader_changes']=['Native Android two-row control bar','HTML book toolbar hidden on phones','Contents/Prev/Next/Visual/Privacy/English/Tamil handled natively','WebView occupies remaining screen height and scrolls natively','HTML touch interception removed for primary reader interaction']
new_manifest=root/'verification/content-revision-manifest-v1.2.8.json'
new_manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
meta=json.loads(meta_path.read_text(encoding='utf-8'));meta['content_revision_manifest']='verification/content-revision-manifest-v1.2.8.json';meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

ver=root/'tools/verify_content_integrity.py'
v=ver.read_text(encoding='utf-8')
v=v.replace('content-revision-manifest-v1.2.5.json','content-revision-manifest-v1.2.8.json')
v=v.replace("'1.2.5'","'1.2.8'")
v=v.replace('versionCode 10205','versionCode 10208')
v=v.replace('v1.2.5','v1.2.8')
ver.write_text(v,encoding='utf-8')

# Build-time assertions for the exact failure class.
assert "body.bookmode .book-toolbar{display:none!important}" in text
assert "touchend',function(e)" not in text or "book-toolbar" not in text[text.find("touchend',function(e)"):text.find("touchend',function(e)")+180]
assert 'setOnClickListener' in dst.read_text(encoding='utf-8')
assert "Button tamil = makeButton(\"தமிழ்\")" in dst.read_text(encoding='utf-8')
assert 'setUseWideViewPort(false)' in dst.read_text(encoding='utf-8')
print('v1.2.8 native controls patch applied')
