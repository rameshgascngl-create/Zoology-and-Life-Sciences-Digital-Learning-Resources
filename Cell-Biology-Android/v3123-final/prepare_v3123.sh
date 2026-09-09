#!/usr/bin/env bash
set -euo pipefail
ROOT="$GITHUB_WORKSPACE"
WORK="$ROOT/Cell-Biology-Android/work-v3123"
PROJECT="$WORK/CellBiologyAndroid-v3.12.3"

cd "$ROOT"
test "$(find Cell-Biology-Android/source-parts -maxdepth 1 -name 'part-*.b64' | wc -l)" -eq 18
cat Cell-Biology-Android/source-parts/part-*.b64 | base64 --decode > /tmp/cellbio-v3121.tar.xz
echo 'c33c32242d9fffeff167f19f073d8335292eba3f042b199ad2fc055fd2cdfe0c  /tmp/cellbio-v3121.tar.xz' | sha256sum -c -

test "$(find Cell-Biology-Android/v3122-patch -maxdepth 1 -name 'p*.b64' | wc -l)" -eq 5
cat Cell-Biology-Android/v3122-patch/p*.b64 | base64 --decode > /tmp/cellbio-v3122-patch.xz
echo '010f87b9bc05f2e57852246aa3070878379fa1eb981bf861b3b4110705722216  /tmp/cellbio-v3122-patch.xz' | sha256sum -c -
xz -dc /tmp/cellbio-v3122-patch.xz > /tmp/cellbio-v3122.patch

python - <<'PY'
from pathlib import Path
import re
data=Path('/tmp/cellbio-v3122.patch').read_text()
sections=re.split(r'(?=^diff --git )', data, flags=re.M)
native='diff --git a/app/src/main/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivity.java b/app/src/main/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivity.java'
kept=[s for s in sections if not s.startswith(native)]
if len(kept)==len(sections): raise SystemExit('native diff section not found')
Path('/tmp/cellbio-v3122-nonnative.patch').write_text(''.join(kept))
PY

rm -rf "$WORK"
mkdir -p "$WORK"
tar -xJf /tmp/cellbio-v3121.tar.xz -C "$WORK"
mv "$WORK/CellBiologyAndroid-v3.12.1" "$PROJECT"
cd "$PROJECT"
patch --dry-run -p1 < /tmp/cellbio-v3122-nonnative.patch
patch -p1 < /tmp/cellbio-v3122-nonnative.patch

echo 'c87925c055a766072f617e92e92ce0714e3897285d4cb1447ff5fcc41908ba5c  Cell-Biology-Android/v3122-final/MainActivity.java' | (cd "$ROOT" && sha256sum -c -)
echo 'aa397faaed1d599899af9a6b99ed1980a3f8a8367270f33df970373176e9d7fc  Cell-Biology-Android/v3122-final/MainActivitySmokeTest.java' | (cd "$ROOT" && sha256sum -c -)
cp "$ROOT/Cell-Biology-Android/v3122-final/MainActivity.java" app/src/main/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivity.java
rm -f app/src/androidTest/java/in/gov/tn/gascngl/zoology/cellbiology/DeviceValidationTest.java
cp "$ROOT/Cell-Biology-Android/v3122-final/MainActivitySmokeTest.java" app/src/androidTest/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivitySmokeTest.java

python - <<'PY'
from pathlib import Path
styles=Path('app/src/main/res/values/styles.xml')
styles.write_text(styles.read_text().replace('        <item name="android:windowLightNavigationBar">true</item>\n',''))
v27=Path('app/src/main/res/values-v27'); v27.mkdir(parents=True, exist_ok=True)
(v27/'styles.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.CellBiology" parent="android:style/Theme.Material.Light.NoActionBar">
        <item name="android:windowLightNavigationBar">true</item>
    </style>
</resources>
''')
PY
rm -f gradle/wrapper/gradle-wrapper.jar

echo '8ef3044ddef1ca0bc1251d489fc63cd6905f8b22b8f154849ff190310e1059e4  Cell-Biology-Android/v3123-final/apply_v3123.py' | (cd "$ROOT" && sha256sum -c -)
python "$ROOT/Cell-Biology-Android/v3123-final/apply_v3123.py" "$PROJECT"

echo '4b1e3a26f46729615bf0bb77339d3902cb2084333f60b203300a4d9eda78a119  Cell-Biology-Android/v3123-final/fix_test_teardown.py' | (cd "$ROOT" && sha256sum -c -)
python "$ROOT/Cell-Biology-Android/v3123-final/fix_test_teardown.py" "$PROJECT"

mkdir -p tools
echo '198ecb6a35f07d07d1dc268b4b18258919222a55ef7c236a61f0d17fb8f73292  Cell-Biology-Android/v3123-final/verify_canonical.py' | (cd "$ROOT" && sha256sum -c -)
echo '7497c036718bbb57fa259ede1f97c1ad291864f51f47509b327aa494eb5028ca  Cell-Biology-Android/v3123-final/verify_html.mjs' | (cd "$ROOT" && sha256sum -c -)
cp "$ROOT/Cell-Biology-Android/v3123-final/verify_canonical.py" tools/verify_canonical.py
cp "$ROOT/Cell-Biology-Android/v3123-final/verify_html.mjs" tools/verify_html.mjs

echo '68b58282c497b7450b1d261873458e0c8528f31cf94e05d026e83c0cee167519  app/src/main/assets/www/index.html' | sha256sum -c -
echo '2fa75e1062391b901c9bab9441f5df308eef69189d18d52729cb48f243973eee  app/src/androidTest/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivitySmokeTest.java' | sha256sum -c -
echo 'c87925c055a766072f617e92e92ce0714e3897285d4cb1447ff5fcc41908ba5c  app/src/main/java/in/gov/tn/gascngl/zoology/cellbiology/MainActivity.java' | sha256sum -c -
grep -q 'versionName = "3.12.3"' app/build.gradle.kts
grep -q 'versionCode = 31203' app/build.gradle.kts
! grep -qF '?.' app/src/main/assets/www/index.html
! grep -q 'id="carrow"' app/src/main/assets/www/index.html
! grep -q 'url(#carrow)' app/src/main/assets/www/index.html
! grep -q 'All 26 Diagram Library entries' app/src/main/assets/www/index.html
python tools/verify_canonical.py
node tools/verify_html.mjs

echo "CANONICAL_V3123_READY=$PROJECT"
