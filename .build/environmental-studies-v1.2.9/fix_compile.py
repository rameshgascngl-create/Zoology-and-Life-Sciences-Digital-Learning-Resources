from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java'
s=p.read_text(encoding='utf-8')
old='View.LayoutParams lp = webView.getLayoutParams();'
new='android.view.ViewGroup.LayoutParams lp = webView.getLayoutParams();'
if old not in s:
    raise SystemExit('Expected LayoutParams line not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('v1.2.9 compile type corrected')
