from pathlib import Path
import re,hashlib,json
p=Path(__file__).resolve().parents[1]
s=(p/'app/src/main/assets/www/index.html').read_text(encoding='utf-8')
assert '3.12.3' in s
assert 'All 26 Diagram Library entries' not in s
assert 'id="carrow"' not in s
assert 'url(#carrow)' not in s
assert 'diagramSvgInstance' in s
assert 'id="__CBIL_CARROW__"' in s
assert s.count('url(#__CBIL_CARROW__)') == 4
assert 'Multi-API emulator validation is part of the release gate' in s
print('canonical HTML checks PASS', hashlib.sha256(s.encode()).hexdigest())
