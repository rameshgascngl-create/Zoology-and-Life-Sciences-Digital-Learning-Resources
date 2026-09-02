from pathlib import Path
from bs4 import BeautifulSoup, Tag
import base64,zlib,json,re,hashlib,sys

root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parents[2]
payload=(repo/'.build/environmental-studies-v1.3.0/expansions.zlib.b64').read_text().strip()
D=json.loads(zlib.decompress(base64.b64decode(payload)).decode('utf-8'))
units=root/'app/src/main/assets/units'

for f in sorted(units.glob('unit-*.html')):
    soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    dirty=False
    for lid,pair in D.items():
        en,ta=pair
        a=soup.find('article',id=lid)
        if a and not a.find('section',class_='depth-extension'):
            sec=soup.new_tag('section',attrs={'class':'depth-extension'})
            h=soup.new_tag('h4',attrs={'class':'en-only'});h.string='Deeper understanding';sec.append(h)
            p=soup.new_tag('p',attrs={'class':'en-only'});p.string=en;sec.append(p)
            ht=soup.new_tag('h4',attrs={'class':'ta'});ht.string='ஆழமான புரிதல்';sec.append(ht)
            pt=soup.new_tag('p',attrs={'class':'ta'});pt.string=ta;sec.append(pt)
            a.append(sec);dirty=True
    for a in soup.select('article.lesson'):
        tb=a.find('section',class_='ta-block',recursive=False)
        if tb is None:
            tb=soup.new_tag('section',attrs={'class':['ta-block','ta']});a.append(tb)
        for el in list(a.find_all(class_='ta')):
            if el is tb or tb in el.parents: continue
            el.attrs.pop('style',None);tb.append(el.extract());dirty=True
        direct=[x for x in a.find_all(recursive=False) if isinstance(x,Tag)]
        if tb in direct:
            pos=direct.index(tb)
            for c in direct[pos+1:]: tb.insert_before(c.extract());dirty=True
        direct=[x for x in a.find_all(recursive=False) if isinstance(x,Tag)]
        if not direct or direct[-1] is not tb:
            tb.extract();a.append(tb);dirty=True
    if dirty: f.write_text(str(soup),encoding='utf-8')

idx=root/'app/src/main/assets/index.html'
html=idx.read_text(encoding='utf-8').replace('v1.2.9','v1.3.0')
m=re.search(r'function reportAndroidContentHeight\(\)\{[\s\S]*?\n\}',html)
if not m: raise RuntimeError('reportAndroidContentHeight not found')
new="""function reportAndroidContentHeight(){
  try{
    if(window.AndroidHost&&typeof window.AndroidHost.setContentHeight==='function'){
      requestAnimationFrame(()=>requestAnimationFrame(()=>{
        const page=document.getElementById('bookPage');
        let h=0;
        if(document.body.classList.contains('bookmode')&&page){
          const r=page.getBoundingClientRect();
          h=Math.ceil(Math.max(page.scrollHeight,page.offsetHeight,r.height));
        }else{
          h=Math.ceil(Math.max(document.documentElement.scrollHeight,document.body.scrollHeight));
        }
        window.AndroidHost.setContentHeight(Math.max(1,h));
      }));
    }
  }catch(e){}
}"""
html=html[:m.start()]+new+html[m.end():]
html+='\n<style>@media(max-width:700px){.book-page-number{position:static!important;right:auto!important;bottom:auto!important;text-align:center!important;margin:24px 0 0!important}.depth-extension{margin-top:22px;padding-top:12px;border-top:1px solid #d8e1dc}.depth-extension h4{color:#174f42;margin:10px 0 8px}}</style>\n'
idx.write_text(html,encoding='utf-8')

bg=root/'app/build.gradle'
g=bg.read_text(encoding='utf-8').replace('versionCode 10209','versionCode 10300').replace("versionName '1.2.9'","versionName '1.3.0'")
bg.write_text(g,encoding='utf-8')
catp=root/'app/src/main/assets/book-catalog.json';cat=json.loads(catp.read_text(encoding='utf-8'));cat['version']='1.3.0';catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'release':'1.3.0','previous_release':'1.2.9','purpose':'Academic depth expansion, English-first/Tamil-second normalization, visible-page height correction.','content_change':True,'expanded_lessons':sorted(D),'ordering_rule':'Complete English/common lesson content precedes one final Tamil block.','depth_gate':'Each lesson >=120 English words, >=100 Tamil words, >=300 combined words.','units':[]}
for f in sorted(units.glob('unit-*.html')):
    s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    manifest['units'].append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':len(f.read_bytes()),'lessons':len(s.select('article.lesson')),'mcqs':len(s.select('.mcq'))})
(root/'verification/content-revision-manifest-v1.3.0.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
meta=root/'verification/app-build-metadata.json';md=json.loads(meta.read_text(encoding='utf-8'));md.update({'version_name':'1.3.0','version_code':10300,'app_version':'1.3.0','content_revision':'v1.3.0 academic depth reconstruction and visible-page height correction','content_revision_manifest':'verification/content-revision-manifest-v1.3.0.json'});meta.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
