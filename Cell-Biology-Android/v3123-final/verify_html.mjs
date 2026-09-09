import fs from 'node:fs';
import vm from 'node:vm';

const file = new URL('../app/src/main/assets/www/index.html', import.meta.url);
const html = fs.readFileSync(file, 'utf8');

function requireText(label, pattern) {
  if (!pattern.test(html)) throw new Error(`FAIL ${label}`);
  console.log(`PASS ${label}`);
}

requireText('HTML declares v3.12.3', /CellBiologyApp\s*=\s*\{\s*version:\s*"3\.12\.3"/);
requireText('print footer declares v3.12.3', /Cell Biology Learning Hub, Version 3\.12\.3\./);
requireText('strict supported learner schemas present', /SUPPORTED_SCHEMA_VERSIONS\s*=\s*new Set\(\["1\.0\.0","1\.1\.0","1\.2\.0","1\.3\.0"\]\)/);
requireText('section-aware Android Back handler exposed', /handleAndroidBack/);
requireText('narrow-screen table containment present', /table\.compare-table\{display:block;max-width:100%;overflow-x:auto/);
requireText('Android 7/8 Object.values shim present', /if \(!Object\.values\)/);
requireText('Android 7/8 Object.entries shim present', /if \(!Object\.entries\)/);
requireText('Android 7/8 Object.fromEntries shim present', /if \(!Object\.fromEntries\)/);
if (html.includes('?.')) throw new Error('FAIL optional chaining remains; Android 7/8 WebView cannot parse it');
if (/return\s*\{[^\n}]*\.\.\./.test(html)) throw new Error('FAIL object spread remains in return object');
console.log('PASS Android 7/8 syntax compatibility invariants');
requireText('keyboard search selection state present', /aria-activedescendant/);
requireText('light-theme green contrast repair present', /--accent-green:#306548/);
requireText('global native bridge visibility present', /window\.CellBiologyApp\s*=\s*CellBiologyApp/);
requireText('diagram wording is count-independent', /All Diagram Library entries are original educational schematics bundled with the application/);
requireText('scoped cancer arrow template present', /id="__CBIL_CARROW__"/);
if (/id="carrow"/.test(html) || /url\(#carrow\)/.test(html)) throw new Error('FAIL unscoped carrow reference remains');

if (/version:\s*"3\.10\.0"/.test(html)) throw new Error('FAIL stale app registry 3.10.0 remains');
if (/Version 3\.8\.2\./.test(html)) throw new Error('FAIL stale print version 3.8.2 remains');

const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
if (scripts.length !== 1) throw new Error(`FAIL expected one inline script, found ${scripts.length}`);
new vm.Script(scripts[0], { filename: 'index.inline.js' });
console.log('PASS inline JavaScript parses under Node.js');
console.log('HTML verification complete.');
