package in.gov.tn.gascngl.zoology.cellbiology;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.Until;

import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

@RunWith(AndroidJUnit4.class)
public class MainActivitySmokeTest {
    private static final String PKG = "in.gov.tn.gascngl.zoology.cellbiology";
    private static final long JS_TIMEOUT_SECONDS = 15;
    private static final long UI_TIMEOUT_MS = 8_000;

    @After
    public void restoreDeviceWindow() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        try { device.executeShellCommand("wm size reset"); } catch (Exception ignored) {}
        try { device.executeShellCommand("wm density reset"); } catch (Exception ignored) {}
        try { device.setOrientationNatural(); } catch (Exception ignored) {}
        device.pressBack();
    }

    @Test
    public void launchesOfflineHardenedWebView() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            AtomicReference<WebView> ref = new AtomicReference<>();
            scenario.onActivity(activity -> {
                WebView webView = findWebView(activity.findViewById(android.R.id.content));
                assertNotNull(webView);
                ref.set(webView);
                assertTrue(webView.getSettings().getJavaScriptEnabled());
                assertTrue(webView.getSettings().getDomStorageEnabled());
                assertFalse(webView.getSettings().getAllowFileAccess());
                assertFalse(webView.getSettings().getAllowFileAccessFromFileURLs());
                assertFalse(webView.getSettings().getAllowUniversalAccessFromFileURLs());
                assertEquals(android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW,
                        webView.getSettings().getMixedContentMode());

                try {
                    PackageInfo info = activity.getPackageManager().getPackageInfo(
                            activity.getPackageName(), PackageManager.GET_PERMISSIONS);
                    String[] permissions = info.requestedPermissions == null ? new String[0] : info.requestedPermissions;
                    assertFalse(Arrays.asList(permissions).contains(Manifest.permission.INTERNET));
                    assertTrue(activity.getApplicationInfo().targetSdkVersion >= 36);
                } catch (PackageManager.NameNotFoundException error) {
                    throw new AssertionError(error);
                }
            });
            waitForAppBoot(ref.get());
            assertTrue(unquote(eval(ref.get(), "location.href")).startsWith("https://appassets.androidplatform.net/"));
        }
    }

    @Test
    public void bootTamilThemeAndResponsiveLayout() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        applyRequestedFormFactor(device);
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));
            assertTrue(jsBool(web, "document.body.innerText.length > 1000"));

            eval(web, "document.getElementById('theme-toggle-btn').click(); true");
            assertEquals("dark", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));
            eval(web, "document.getElementById('theme-toggle-btn').click(); true");
            assertEquals("light", unquote(eval(web, "document.documentElement.getAttribute('data-theme')")));

            eval(web, "if(document.documentElement.lang!=='en'){document.getElementById('lang-toggle-btn').click();} document.getElementById('lang-toggle-btn').click(); true");
            assertEquals("ta", unquote(eval(web, "document.documentElement.lang")));
            assertTrue(jsBool(web, "/[\\u0B80-\\u0BFF]/.test(document.body.innerText)"));
            assertTrue(jsBool(web, "document.documentElement.scrollWidth <= window.innerWidth + 1"));
        }
    }

    @Test
    public void nativeBackReturnsToPreviousSection() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            eval(web, "document.querySelector('[data-action=\"nav\"][data-nav=\"readiness-report\"]').click(); true");
            assertTrue(jsBool(web, "document.body.innerText.indexOf('Readiness')>=0"));

            if (Build.VERSION.SDK_INT >= 33) {
                int w = device.getDisplayWidth();
                int h = device.getDisplayHeight();
                device.swipe(2, h / 2, Math.max(220, w / 2), h / 2, 24);
            } else {
                device.pressBack();
            }
            Thread.sleep(900);
            assertEquals(PKG, device.getCurrentPackageName());
            assertFalse(jsBool(web, "document.body.innerText.indexOf('Readiness Report')>=0 && document.querySelector('[data-section=\"readiness-report\"]')"));
        }
    }

    @Test
    public void printFlowOpensAndroidPrintUi() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            eval(web, "document.querySelector('[data-action=\"nav\"][data-nav=\"print-centre\"]').click(); true");
            eval(web, "document.querySelector('[data-action=\"print-unit\"]').click(); true");
            boolean printUi = device.wait(Until.hasObject(By.pkg("com.android.printspooler").depth(0)), UI_TIMEOUT_MS)
                    || device.wait(Until.hasObject(By.textContains("Print")), 2_000);
            assertTrue("Android Print UI did not appear", printUi);
            device.pressBack();
        }
    }

    @Test
    public void exportFlowOpensCreateDocumentPicker() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            eval(web, "document.querySelector('[data-action=\"nav\"][data-nav=\"progress-history\"]').click(); true");
            eval(web, "document.querySelector('[data-action=\"export-progress\"]').click(); true");
            assertTrue("Create-document picker did not open", waitForExternalSystemUi(device));
            device.pressBack();
        }
    }

    @Test
    public void importFlowOpensOpenDocumentPicker() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            eval(web, "document.querySelector('[data-action=\"nav\"][data-nav=\"progress-history\"]').click(); true");
            eval(web, "document.querySelector('input[data-action=\"import-progress\"]').click(); true");
            assertTrue("Open-document picker did not open", waitForExternalSystemUi(device));
            device.pressBack();
        }
    }

    @Test
    public void persistencePhase1StoresMarker() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            eval(web, "localStorage.setItem('cbil-ci-persist','survives-force-stop'); localStorage.getItem('cbil-ci-persist')");
            assertEquals("survives-force-stop", unquote(eval(web, "localStorage.getItem('cbil-ci-persist')")));
        }
    }

    @Test
    public void persistencePhase2ReadsMarker() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            WebView web = captureWebView(scenario);
            waitForAppBoot(web);
            assertEquals("survives-force-stop", unquote(eval(web, "localStorage.getItem('cbil-ci-persist')")));
            eval(web, "localStorage.removeItem('cbil-ci-persist'); true");
        }
    }

    private static void applyRequestedFormFactor(UiDevice device) throws Exception {
        Context ctx = InstrumentationRegistry.getInstrumentation().getTargetContext();
        String size = InstrumentationRegistry.getArguments().getString("cbilSize", "");
        String density = InstrumentationRegistry.getArguments().getString("cbilDensity", "");
        String orientation = InstrumentationRegistry.getArguments().getString("cbilOrientation", "portrait");
        if (!size.isEmpty()) device.executeShellCommand("wm size " + size);
        if (!density.isEmpty()) device.executeShellCommand("wm density " + density);
        if ("landscape".equals(orientation)) device.setOrientationLeft(); else device.setOrientationNatural();
        device.waitForIdle();
    }

    private static boolean waitForExternalSystemUi(UiDevice device) throws Exception {
        long end = System.currentTimeMillis() + UI_TIMEOUT_MS;
        while (System.currentTimeMillis() < end) {
            String current = device.getCurrentPackageName();
            if (current != null && !PKG.equals(current) && !current.endsWith(".test")) return true;
            Thread.sleep(200);
        }
        return false;
    }

    private static WebView captureWebView(ActivityScenario<MainActivity> scenario) {
        AtomicReference<WebView> ref = new AtomicReference<>();
        scenario.onActivity(activity -> ref.set(findWebView(activity.findViewById(android.R.id.content))));
        assertNotNull(ref.get());
        return ref.get();
    }

    private static void waitForAppBoot(WebView web) {
        long end = System.currentTimeMillis() + 15_000;
        while (System.currentTimeMillis() < end) {
            try {
                if (jsBool(web, "document.readyState==='complete' && !!window.CellBiologyApp && !!window.CellBiologyApp.UI && document.body.innerText.length>500")) return;
            } catch (AssertionError ignored) {}
            try { Thread.sleep(200); } catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
        throw new AssertionError("Cell Biology HTML did not boot within timeout");
    }

    private static boolean jsBool(WebView web, String expression) {
        return "true".equals(eval(web, "Boolean(" + expression + ")"));
    }

    private static String eval(WebView web, String js) {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<String> result = new AtomicReference<>();
        InstrumentationRegistry.getInstrumentation().runOnMainSync(() ->
                web.evaluateJavascript(js, value -> { result.set(value); latch.countDown(); }));
        try {
            if (!latch.await(JS_TIMEOUT_SECONDS, TimeUnit.SECONDS)) throw new AssertionError("JavaScript evaluation timed out: " + js);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new AssertionError(e);
        }
        return result.get();
    }

    private static String unquote(String value) {
        if (value == null || "null".equals(value)) return null;
        if (value.length() >= 2 && value.startsWith("\"") && value.endsWith("\"")) {
            return value.substring(1, value.length() - 1)
                    .replace("\\n", "\n")
                    .replace("\\\"", "\"")
                    .replace("\\\\", "\\");
        }
        return value;
    }

    private static WebView findWebView(View view) {
        if (view instanceof WebView) return (WebView) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                WebView found = findWebView(group.getChildAt(i));
                if (found != null) return found;
            }
        }
        return null;
    }
}
