# Invertebrate Virtual Laboratory v1.0.3 — APK build evidence

Source archive: `InvertebrateLab_1.0.3_android_project.zip`

- Source ZIP SHA-256: `5535afc6b0f23e14601ee570350edbb39fb7c28376e76e2c31565d4fe58b33be`
- Package: `com.gasczoology.invertebratelab`
- versionName: `1.0.3`
- versionCode: `103`
- minSdk: `24`
- targetSdk: `36`
- compileSdk: `36`
- GitHub builder branch base commit: `c4e014a36e19901acc7b9830a3a87454c3f157ec`
- GitHub builder-kit workflow run: `34618241674` — success
- GitHub Build Tools 34 workflow run: `34618806929` — success

## Build result

- Debug APK assembly: PASS
- Release APK assembly: PASS
- Final distribution APK: `InvertebrateLab-1.0.3.apk`
- Final APK SHA-256: `4c284187356f31d4d817de8ed47c4f0114c5f1f758e92ee3ac18f939530f1781`
- ZIP alignment: PASS
- APK Signature Scheme v2: PASS
- APK Signature Scheme v3: PASS
- Production signer certificate SHA-256: `2a686a2016789329f6abc91eb262b860163448599073801036291ea74847cd24`
- Signer DN: `CN=GASC Zoology, OU=Zoology, O=GASC Nagercoil, L=Nagercoil, ST=Tamil Nadu, C=IN`

## Security checks

- Release debuggable flag: absent
- `android.permission.INTERNET`: absent
- Camera permission: absent
- Broad external-storage permissions: absent
- Web content uses `WebViewAssetLoader`
- `addJavascriptInterface`: not used
- File access flags remain disabled in the supplied source

## Build notes

AGP 8.7.3 emits a compatibility warning because it was tested through compileSdk 35 while this source targets compileSdk 36. The build nevertheless completes successfully. Android Lint was not completed in the local offline build because the GitHub-generated Gradle cache did not contain `com.android.tools.lint:lint-gradle:31.7.3`; this was an unavailable lint-engine dependency, not a source compilation failure.

The production upload key created for this first signed release must be retained for future updates to the same package unless Play App Signing changes the signing workflow.
