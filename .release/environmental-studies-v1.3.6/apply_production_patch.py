#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BUILD = ROOT / 'app/build.gradle'
MANIFEST = ROOT / 'app/src/main/AndroidManifest.xml'

EXPECTED = {
    BUILD: 'fcf79ca44264f4c99976383068f9c3c4a0af7ad3567c79d1aa30a85e0120d8aa',
    MANIFEST: '2cad4fbc606a72bcbdb313be95fe7e4650b9fda4d8dc4a57282f765264d65378',
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for path, expected in EXPECTED.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f'REFUSE: unexpected frozen source for {path}: {actual} != {expected}')

build = BUILD.read_text(encoding='utf-8')
anchor = "plugins { id 'com.android.application' }\n\n"
signing_prelude = """plugins { id 'com.android.application' }

def releaseStorePath = System.getenv('ENVSCI_KEYSTORE_PATH')
def releaseStorePassword = System.getenv('ENVSCI_KEYSTORE_PASSWORD')
def releaseKeyAlias = System.getenv('ENVSCI_KEY_ALIAS')
def releaseKeyPassword = System.getenv('ENVSCI_KEY_PASSWORD')
def hasReleaseSigning = [releaseStorePath, releaseStorePassword, releaseKeyAlias, releaseKeyPassword]
        .every { it != null && !it.isBlank() }

"""
if build.count(anchor) != 1:
    raise SystemExit('REFUSE: Gradle plugin anchor not unique')
build = build.replace(anchor, signing_prelude, 1)

old_block = """    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
"""
new_block = """    signingConfigs {
        if (hasReleaseSigning) {
            release {
                storeFile file(releaseStorePath)
                storePassword releaseStorePassword
                keyAlias releaseKeyAlias
                keyPassword releaseKeyPassword
                enableV2Signing true
                enableV3Signing true
            }
        }
    }

    buildTypes {
        release {
            debuggable false
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            if (hasReleaseSigning) {
                signingConfig signingConfigs.release
            }
        }
    }
"""
if build.count(old_block) != 1:
    raise SystemExit('REFUSE: expected release buildTypes block not found exactly once')
build = build.replace(old_block, new_block, 1)
BUILD.write_text(build, encoding='utf-8')

manifest = MANIFEST.read_text(encoding='utf-8')
if manifest.count('android:allowBackup="true"') != 1:
    raise SystemExit('REFUSE: expected allowBackup=true not found exactly once')
manifest = manifest.replace('android:allowBackup="true"', 'android:allowBackup="false"', 1)
for line in [
    '        android:dataExtractionRules="@xml/data_extraction_rules"\n',
    '        android:fullBackupContent="@xml/backup_rules"\n',
]:
    if manifest.count(line) != 1:
        raise SystemExit(f'REFUSE: expected manifest backup rule line not found exactly once: {line.strip()}')
    manifest = manifest.replace(line, '', 1)
MANIFEST.write_text(manifest, encoding='utf-8')

print('PASS: applied production-only Gradle signing/debuggable and manifest backup corrections')
print(f'patched app/build.gradle sha256={sha256(BUILD)}')
print(f'patched AndroidManifest.xml sha256={sha256(MANIFEST)}')
