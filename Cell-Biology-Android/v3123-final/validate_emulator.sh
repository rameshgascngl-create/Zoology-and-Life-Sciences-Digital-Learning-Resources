#!/usr/bin/env bash
set -euo pipefail
API="$1"
cd "$GITHUB_WORKSPACE"
mkdir -p validation-output
cleanup() {
  adb exec-out screencap -p > "validation-output/failure-api-${API}.png" 2>/dev/null || true
  adb logcat -d > "validation-output/logcat-api-${API}.txt" 2>/dev/null || true
}
trap cleanup EXIT
APP_APK=$(find artifacts/app -name '*.apk' -print -quit)
TEST_APK=$(find artifacts/test -name '*.apk' -print -quit)
test -n "$APP_APK"; test -n "$TEST_APK"
sha256sum "$APP_APK" "$TEST_APK" | tee "validation-output/apk-sha256-api-${API}.txt"
adb shell getprop ro.build.version.release | tee "validation-output/android-release-api-${API}.txt"
adb shell getprop ro.build.version.sdk | tee "validation-output/android-sdk-api-${API}.txt"
adb install -r "$APP_APK"
adb install -r "$TEST_APK"
PKG=in.gov.tn.gascngl.zoology.cellbiology
TESTPKG=in.gov.tn.gascngl.zoology.cellbiology.test
RUNNER=androidx.test.runner.AndroidJUnitRunner
CLASS=in.gov.tn.gascngl.zoology.cellbiology.MainActivitySmokeTest
adb shell pm list instrumentation | tee "validation-output/instrumentation-api-${API}.txt"
if [ "$API" -ge 33 ]; then
  adb shell cmd overlay enable-exclusive --category com.android.internal.systemui.navbar.gestural || adb shell cmd overlay enable com.android.internal.systemui.navbar.gestural || true
  adb shell cmd overlay list | grep -i navbar | tee "validation-output/navbar-api-${API}.txt" || true
fi
run_test() {
  METHOD="$1"; shift
  OUT="validation-output/api-${API}-${METHOD}-$(date +%s%N).txt"
  echo "===== API ${API} :: ${METHOD} $* ====="
  set +e
  adb shell am instrument -w -r "$@" -e class "$CLASS#$METHOD" "$TESTPKG/$RUNNER" | tee "$OUT"
  RC=${PIPESTATUS[0]}
  set -e
  if [ "$RC" -ne 0 ] || grep -q 'FAILURES!!!' "$OUT" || ! grep -Eq 'OK \(1 test\)|INSTRUMENTATION_CODE: -1' "$OUT"; then
    echo "FAILED: ${METHOD} on API ${API}" | tee -a "$OUT"
    return 1
  fi
  echo "PASSED: ${METHOD} on API ${API}" | tee -a "$OUT"
}
run_test launchesOfflineHardenedWebView
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 360x800 -e cbilDensity 320 -e cbilOrientation portrait
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 800x360 -e cbilDensity 320 -e cbilOrientation landscape
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 600x960 -e cbilDensity 160 -e cbilOrientation portrait
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 960x600 -e cbilDensity 160 -e cbilOrientation landscape
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 800x1280 -e cbilDensity 160 -e cbilOrientation portrait
run_test bootTamilThemeAndResponsiveLayout -e cbilSize 1280x800 -e cbilDensity 160 -e cbilOrientation landscape
run_test nativeBackReturnsToPreviousSection
run_test printFlowOpensAndroidPrintUi
run_test exportFlowOpensCreateDocumentPicker
run_test importFlowOpensOpenDocumentPicker
run_test persistencePhase1StoresMarker
adb shell am force-stop "$PKG"
sleep 1
run_test persistencePhase2ReadsMarker
adb exec-out screencap -p > "validation-output/final-api-${API}.png" || true
adb logcat -d > "validation-output/logcat-api-${API}.txt" || true
trap - EXIT
echo "ALL VALIDATIONS PASSED ON API ${API}" | tee "validation-output/PASS-api-${API}.txt"
