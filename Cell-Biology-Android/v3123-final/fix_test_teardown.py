#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
p = root / 'app/src/androidTest/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivitySmokeTest.java'
s = p.read_text(encoding='utf-8')
old = '''        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {\n            WebView web = captureWebView(scenario);\n            waitForAppBoot(web);\n            assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));\n            assertTrue(jsBool(web, "document.body.innerText.length > 1000"));\n\n            eval(web, "document.getElementById('theme-toggle-btn').click(); true");\n            assertEquals("dark", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));\n            eval(web, "document.getElementById('theme-toggle-btn').click(); true");\n            assertEquals("light", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));\n\n            eval(web, "if(document.documentElement.lang!=='en'){document.getElementById('lang-toggle-btn').click();} document.getElementById('lang-toggle-btn').click(); true");\n            assertEquals("ta", unquote(eval(web, "document.documentElement.lang")));\n            assertTrue(jsBool(web, "/[\\\\u0B80-\\\\u0BFF]/.test(document.body.innerText)"));\n            assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));\n        }\n'''
new = '''        ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class);\n        WebView web = captureWebView(scenario);\n        waitForAppBoot(web);\n        assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));\n        assertTrue(jsBool(web, "document.body.innerText.length > 1000"));\n\n        eval(web, "document.getElementById('theme-toggle-btn').click(); true");\n        assertEquals("dark", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));\n        eval(web, "document.getElementById('theme-toggle-btn').click(); true");\n        assertEquals("light", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));\n\n        eval(web, "if(document.documentElement.lang!=='en'){document.getElementById('lang-toggle-btn').click();} document.getElementById('lang-toggle-btn').click(); true");\n        assertEquals("ta", unquote(eval(web, "document.documentElement.lang")));\n        assertTrue(jsBool(web, "/[\\\\u0B80-\\\\u0BFF]/.test(document.body.innerText)"));\n        assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));\n        // Android 7/8 ActivityScenario.close() can hang in PAUSED after wm-size/orientation changes.\n        // Finish explicitly without asserting DESTROYED; each harness invocation is isolated.\n        scenario.onActivity(activity -> activity.finish());\n'''
if old not in s:
    if 'ActivityScenario.close() can hang in PAUSED' in s:
        print('test teardown fix already present')
    else:
        raise SystemExit('responsive-layout teardown block not found')
else:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
print('test_sha256', hashlib.sha256(p.read_bytes()).hexdigest())
