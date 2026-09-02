from pathlib import Path
import sys,json

root=Path(sys.argv[1])
idx=root/'app/src/main/assets/index.html'
text=idx.read_text(encoding='utf-8')

# v1.2.9 bug: bookIndex is declared with top-level `let`, not as window.bookIndex.
# The Android height/index bridge therefore kept reporting zero. Native Forward
# consequently evaluated zero + one and reopened the Contents page.
old="AndroidHost.pageRendered(Number(window.bookIndex||0),h);"
new="AndroidHost.pageRendered(Number((typeof bookIndex==='number'?bookIndex:0)),h);"
if old not in text:
    raise SystemExit('expected stale window.bookIndex bridge not found')
text=text.replace(old,new,1)

if 'Number(window.bookIndex||0)' in text:
    raise SystemExit('stale window.bookIndex bridge remains')
if "typeof bookIndex==='number'?bookIndex" not in text:
    raise SystemExit('real lexical bookIndex bridge was not installed')

text=text.replace('v1.2.9','v1.2.10')
idx.write_text(text,encoding='utf-8')

gradle=root/'app/build.gradle'
g=gradle.read_text(encoding='utf-8')
g=g.replace('versionCode 10209','versionCode 10210')
g=g.replace("versionName '1.2.9'","versionName '1.2.10'")
gradle.write_text(g,encoding='utf-8')

catalog=root/'app/src/main/assets/book-catalog.json'
c=json.loads(catalog.read_text(encoding='utf-8'))
c['version']='1.2.10'
catalog.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

prev=root/'verification/content-revision-manifest-v1.2.9.json'
new_manifest=root/'verification/content-revision-manifest-v1.2.10.json'
m=json.loads(prev.read_text(encoding='utf-8'))
m['release']='1.2.10'
m['previous_release']='1.2.9'
m['purpose']='Fix Android native Previous/Next page-index synchronization.'
m['content_change']=False
m['reader_changes']=[
    'Report lexical bookIndex through AndroidHost instead of nonexistent window.bookIndex',
    'Native Next/Previous now advance from the actual currently displayed page'
]
new_manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

meta=root/'verification/app-build-metadata.json'
md=json.loads(meta.read_text(encoding='utf-8'))
md['version_name']='1.2.10'
md['version_code']=10210
md['app_version']='1.2.10'
md['content_revision']='v1.2.10 native page-index synchronization correction; educational unit payloads unchanged'
md['content_revision_manifest']='verification/content-revision-manifest-v1.2.10.json'
meta.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

ver=root/'tools/verify_content_integrity.py'
v=ver.read_text(encoding='utf-8')
v=v.replace('content-revision-manifest-v1.2.9.json','content-revision-manifest-v1.2.10.json')
v=v.replace("'1.2.9'","'1.2.10'")
v=v.replace('versionCode 10209','versionCode 10210')
v=v.replace('v1.2.9','v1.2.10')
ver.write_text(v,encoding='utf-8')

print('v1.2.10 navigation sync patch applied')
