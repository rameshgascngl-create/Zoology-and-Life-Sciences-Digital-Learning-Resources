from pathlib import Path
from bs4 import BeautifulSoup,Tag
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();A=root/'app/src/main/assets';V=root/'verification';errs=[]
M=json.loads((V/'content-revision-manifest-v1.3.0.json').read_text(encoding='utf-8'))
lt=mt=0
for item in M['units']:
 p=A/'units'/item['file'];b=p.read_bytes();s=BeautifulSoup(b,'html.parser')
 if hashlib.sha256(b).hexdigest()!=item['sha256']:errs.append('hash '+item['file'])
 if len(b)!=item['bytes']:errs.append('bytes '+item['file'])
 lessons=s.select('article.lesson');mcqs=s.select('.mcq');lt+=len(lessons);mt+=len(mcqs)
 if len(lessons)!=item['lessons']:errs.append('lessons '+item['file'])
 if len(mcqs)!=item['mcqs']:errs.append('mcqs '+item['file'])
 for a in lessons:
  tb=a.find('section',class_='ta-block',recursive=False);lid=a.get('id')
  if not tb:errs.append('missing Tamil block '+str(lid));continue
  direct=[x for x in a.find_all(recursive=False) if isinstance(x,Tag)]
  if not direct or direct[-1] is not tb:errs.append('language ordering '+str(lid))
  for t in a.find_all(class_='ta'):
   if t is tb or tb in t.parents:continue
   errs.append('interleaved Tamil '+str(lid));break
  en=' '.join(x.get_text(' ',strip=True) for x in direct if x is not tb);ta=tb.get_text(' ',strip=True);ew,tw=len(en.split()),len(ta.split())
  if ew<120 or tw<100 or ew+tw<300:errs.append(f'academic depth {lid} EN={ew} TA={tw}')
 for q in mcqs:
  if not q.select_one('p .en') or not q.select_one('p .ta') or len(q.select('label .ta'))!=4:errs.append('bilingual mcq '+item['file']);break
 r=s.select_one('.review ol')
 if not r or len(r.find_all('li',recursive=False))!=len(lessons):errs.append('review completeness '+item['file'])
cat=json.loads((A/'book-catalog.json').read_text(encoding='utf-8'))
if cat.get('version')!='1.3.0' or len(cat.get('pages',[]))!=80:errs.append('catalog')
bg=(root/'app/build.gradle').read_text(encoding='utf-8')
if "versionName '1.3.0'" not in bg or 'versionCode 10300' not in bg:errs.append('gradle version')
if lt!=46:errs.append('lesson total '+str(lt))
if mt!=58:errs.append('mcq total '+str(mt))
if 'android.permission.INTERNET' in (root/'app/src/main/AndroidManifest.xml').read_text():errs.append('internet permission')
idx=(A/'index.html').read_text(encoding='utf-8');java=(root/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java').read_text(encoding='utf-8')
for needle,label in [("const page=document.getElementById('bookPage')",'visible-page height source'),('Math.max(page.scrollHeight,page.offsetHeight,r.height)','visible-page height'),("document.body.classList.contains('bookmode')&&page",'bookmode height guard')]:
 if needle not in idx:errs.append(label)
for needle,label in [('new ScrollView(this)','native ScrollView'),('setNestedScrollingEnabled(false)','WebView nested scrolling'),('showBookPage(Math.min(BOOK_CATALOG.length-1,bookIndex+1)','next navigation'),('showBookPage(Math.max(0,bookIndex-1)','previous navigation'),('toggleVisualFocusNative()','visual action')]:
 if needle not in java:errs.append(label)
if errs:print('VERIFY FAIL: '+'; '.join(errs));sys.exit(1)
print('VERIFY PASS: v1.3.0 46-lesson academic depth, English-first/Tamil-second ordering, 58 bilingual MCQs, unit hashes, catalog, native navigation, visual action and visible-page scrolling invariants verified.')
