from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
p=root/'app/src/main/java/edu/gascnagercoil/environmentalsciences/MainActivity.java'
j=p.read_text(encoding='utf-8')

# Clarify visual control regardless of whether the source uses a local or field variable.
j=j.replace('▣ Visual','▣ Figures')

# Add an explicit bilingual button if the earlier exact-form patch did not match.
if 'makeButton("EN+TA")' not in j:
    # Handle separate declaration form.
    pat=r'(Button\s+tamil\s*=\s*makeButton\("தமிழ்"\)\s*;)'
    if re.search(pat,j):
        j=re.sub(pat,r'\1\n        Button both = makeButton("EN+TA");',j,count=1)
    else:
        # Handle a combined Button declaration ending in tamil=makeButton(...);
        pat=r'(Button\s+privacy\s*=.*?tamil\s*=\s*makeButton\("தமிழ்"\)\s*;)'
        m=re.search(pat,j,re.S)
        if m:
            repl=m.group(1)[:-1]+',both=makeButton("EN+TA");'
            j=j[:m.start()]+repl+j[m.end():]
        else:
            raise SystemExit('Unable to locate Tamil button declaration')

if 'addWeighted(row2,both' not in j:
    m=re.search(r'(addWeighted\(row2\s*,\s*tamil\s*,\s*[^;]+;)',j)
    if not m: raise SystemExit('Unable to locate Tamil row2 weighting')
    j=j[:m.end()]+ '\n        addWeighted(row2,both,1f);' + j[m.end():]

if "setLang('both')" not in j:
    m=re.search(r'(tamil\.setOnClickListener\([^;]+;)',j)
    if not m: raise SystemExit('Unable to locate Tamil click listener')
    # Preserve whichever js helper signature the current source uses.
    if 'reportAndroidContentHeight' in m.group(1):
        line='\n        both.setOnClickListener(v->js("setLang(\'both\');reportAndroidContentHeight();",true));'
    else:
        line='\n        both.setOnClickListener(v -> js("setLang(\'both\');"));'
    j=j[:m.end()]+line+j[m.end():]

# Document the existing local height bridge without changing its callable surface.
if 'SECURITY INVARIANT' not in j and 'private final class HostBridge' in j:
    j=j.replace('    private final class HostBridge{','''    /**\n     * Narrow local-content bridge. SECURITY INVARIANT:\n     * Keep this interface limited to primitive, non-sensitive UI sizing data.\n     * Do not add file, network, credential, intent, storage or arbitrary-command methods.\n     */\n    private final class HostBridge{''')

p.write_text(j,encoding='utf-8')

# Fail closed if the intended native controls did not materialize.
for token in ('new ScrollView(this)','setNestedScrollingEnabled(false)','makeButton("EN+TA")','▣ Figures','@JavascriptInterface'):
    if token not in j: raise SystemExit('Missing Android invariant: '+token)
if j.count('@JavascriptInterface')!=1: raise SystemExit('Unexpected JavascriptInterface count')
print('v1.3.1 native controls PASS')
