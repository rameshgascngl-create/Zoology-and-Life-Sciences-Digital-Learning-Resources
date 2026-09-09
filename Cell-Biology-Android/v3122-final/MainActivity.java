package in.gov.tn.gascngl.zoology.cellbiology;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.res.Configuration;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintManager;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.JavascriptInterface;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.webkit.WebViewAssetLoader;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String LOCAL_HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + LOCAL_HOST + "/assets/www/index.html";
    private static final int REQUEST_OPEN_JSON = 1001;
    private static final int REQUEST_SAVE_JSON = 1002;
    private static final int MAX_JSON_BYTES = 5 * 1024 * 1024;
    private static final int LIGHT_PAPER = 0xFFF1F0E4;
    private static final int DARK_PAPER = 0xFF101716;

    private FrameLayout rootView;
    private WebView webView;
    private ValueCallback<Uri[]> fileChooserCallback;
    private String pendingExportJson;
    private volatile boolean webBackHandleable;
    private boolean darkUi;

    @Override protected void onCreate(@Nullable Bundle state) {
        super.onCreate(state);
        configureSystemBarsAndInsets();
        configureWebView();
        registerBackHandler();
        if (state == null || webView.restoreState(state) == null) webView.loadUrl(START_URL);
    }

    private void configureSystemBarsAndInsets() {
        rootView = new FrameLayout(this);
        rootView.setBackgroundColor(LIGHT_PAPER);
        rootView.setLayoutParams(new ViewGroup.LayoutParams(-1, -1));
        setContentView(rootView);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            getWindow().setStatusBarColor(Color.TRANSPARENT);
            getWindow().setNavigationBarColor(Color.TRANSPARENT);
            getWindow().setDecorFitsSystemWindows(false);
            applySystemBarsAppearance(false);
            rootView.setOnApplyWindowInsetsListener((view, insets) -> {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                android.graphics.Insets ime = insets.getInsets(WindowInsets.Type.ime());
                view.setPadding(bars.left, bars.top, bars.right, Math.max(bars.bottom, ime.bottom));
                return insets;
            });
            rootView.requestApplyInsets();
        }
    }

    private void applySystemBarsAppearance(boolean dark) {
        darkUi = dark;
        int bg = dark ? DARK_PAPER : LIGHT_PAPER;
        if (rootView != null) rootView.setBackgroundColor(bg);
        if (webView != null) webView.setBackgroundColor(bg);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                int mask = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(dark ? 0 : mask, mask);
            }
        } else {
            int flags = dark ? 0 : (View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | (Build.VERSION.SDK_INT >= 26 ? View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR : 0));
            getWindow().getDecorView().setSystemUiVisibility(flags);
        }
    }

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    private void configureWebView() {
        webView = new WebView(this);
        webView.setBackgroundColor(LIGHT_PAPER);
        rootView.addView(webView, new FrameLayout.LayoutParams(-1, -1));
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setAllowContentAccess(true);
        s.setJavaScriptCanOpenWindowsAutomatically(false);
        s.setSupportMultipleWindows(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        WebView.setWebContentsDebuggingEnabled((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);

        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this)).build();
        webView.setWebViewClient(new WebViewClient() {
            @Nullable @Override public WebResourceResponse shouldInterceptRequest(@NonNull WebView v, @NonNull WebResourceRequest r) { return loader.shouldInterceptRequest(r.getUrl()); }
            @Nullable @SuppressWarnings("deprecation") @Override public WebResourceResponse shouldInterceptRequest(@NonNull WebView v, @NonNull String u) { return loader.shouldInterceptRequest(Uri.parse(u)); }
            @Override public boolean shouldOverrideUrlLoading(@NonNull WebView v, @NonNull WebResourceRequest r) { return routeNavigation(r.getUrl()); }
            @SuppressWarnings("deprecation") @Override public boolean shouldOverrideUrlLoading(@NonNull WebView v, @NonNull String u) { return routeNavigation(Uri.parse(u)); }
            @Override public void onReceivedError(@NonNull WebView v, @NonNull WebResourceRequest r, @NonNull WebResourceError e) {
                if (r.isForMainFrame()) Toast.makeText(MainActivity.this, "The learning app could not load. Please reopen it.", Toast.LENGTH_LONG).show();
                super.onReceivedError(v, r, e);
            }
            @Override public boolean onRenderProcessGone(@NonNull WebView v, @NonNull RenderProcessGoneDetail d) {
                destroyWebView(); Toast.makeText(MainActivity.this, "Android WebView restarted after a renderer problem.", Toast.LENGTH_LONG).show(); recreate(); return true;
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
                fileChooserCallback = cb;
                Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/json");
                try { startActivityForResult(i, REQUEST_OPEN_JSON); return true; }
                catch (Exception ex) { fileChooserCallback = null; Toast.makeText(MainActivity.this, "No compatible file picker is available.", Toast.LENGTH_LONG).show(); return false; }
            }
        });
        webView.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
    }

    private boolean isTrustedUrl(@Nullable String value) {
        if (value == null) return false;
        Uri u = Uri.parse(value);
        return "https".equalsIgnoreCase(u.getScheme()) && LOCAL_HOST.equalsIgnoreCase(u.getHost());
    }

    private boolean routeNavigation(Uri uri) {
        if (uri == null) return true;
        if ("https".equalsIgnoreCase(uri.getScheme()) && LOCAL_HOST.equalsIgnoreCase(uri.getHost())) return false;
        if ("http".equalsIgnoreCase(uri.getScheme()) || "https".equalsIgnoreCase(uri.getScheme())) {
            try { startActivity(new Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE)); }
            catch (Exception ex) { Toast.makeText(this, "No browser is available for this link.", Toast.LENGTH_SHORT).show(); }
        }
        return true;
    }

    private void registerBackHandler() {
        if (Build.VERSION.SDK_INT >= 33) getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::handleBack);
    }
    @Override @SuppressWarnings("deprecation") @SuppressLint("GestureBackNavigation") public void onBackPressed() { if (Build.VERSION.SDK_INT < 33) handleBack(); else super.onBackPressed(); }
    private void handleBack() {
        if (webView == null) { moveTaskToBack(true); return; }
        if (!webBackHandleable && !webView.canGoBack()) { moveTaskToBack(true); return; }
        webView.evaluateJavascript("(function(){try{if(window.CellBiologyApp&&CellBiologyApp.UI&&typeof CellBiologyApp.UI.handleAndroidBack==='function')return CellBiologyApp.UI.handleAndroidBack();}catch(e){}return 'unhandled';})()", value -> {
            if (!"\"handled\"".equals(value)) { if (webView != null && webView.canGoBack()) webView.goBack(); else moveTaskToBack(true); }
        });
    }

    @Override protected void onSaveInstanceState(@NonNull Bundle out) { if (webView != null) webView.saveState(out); super.onSaveInstanceState(out); }

    @Override protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_OPEN_JSON) {
            if (fileChooserCallback == null) return;
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null && uriWithinJsonLimit(data.getData())) result = new Uri[]{data.getData()};
            else if (resultCode == RESULT_OK) Toast.makeText(this, "Selected JSON exceeds the 5 MB limit.", Toast.LENGTH_LONG).show();
            fileChooserCallback.onReceiveValue(result); fileChooserCallback = null; return;
        }
        if (requestCode == REQUEST_SAVE_JSON) {
            String json = pendingExportJson; pendingExportJson = null;
            if (resultCode != RESULT_OK || data == null || data.getData() == null || json == null) return;
            try (OutputStream out = getContentResolver().openOutputStream(data.getData(), "wt")) {
                if (out == null) throw new IllegalStateException("Unable to open selected file");
                out.write(json.getBytes(StandardCharsets.UTF_8)); out.flush(); Toast.makeText(this, "Progress exported.", Toast.LENGTH_SHORT).show();
            } catch (Exception ex) { Toast.makeText(this, "Progress export failed.", Toast.LENGTH_LONG).show(); }
        }
    }

    private boolean uriWithinJsonLimit(Uri uri) {
        try (ParcelFileDescriptor pfd = getContentResolver().openFileDescriptor(uri, "r")) {
            if (pfd == null) return false;
            long size = pfd.getStatSize();
            return size < 0 || size <= MAX_JSON_BYTES;
        } catch (Exception e) { return false; }
    }

    private void destroyWebView() {
        if (fileChooserCallback != null) { fileChooserCallback.onReceiveValue(null); fileChooserCallback = null; }
        if (webView != null) { webView.removeJavascriptInterface("AndroidBridge"); webView.stopLoading(); webView.setWebChromeClient(null); webView.setWebViewClient(null); if (webView.getParent() instanceof ViewGroup) ((ViewGroup)webView.getParent()).removeView(webView); webView.destroy(); webView = null; }
    }
    @Override protected void onDestroy() { destroyWebView(); super.onDestroy(); }

    public final class AndroidBridge {
        private void withTrustedPage(Runnable action) {
            runOnUiThread(() -> { if (webView != null && isTrustedUrl(webView.getUrl())) action.run(); });
        }
        @JavascriptInterface public void saveProgressJson(String json) {
            if (json == null || json.trim().isEmpty() || json.getBytes(StandardCharsets.UTF_8).length > MAX_JSON_BYTES) return;
            withTrustedPage(() -> {
                pendingExportJson = json;
                Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/json").putExtra(Intent.EXTRA_TITLE, "cbil-progress.json");
                try { startActivityForResult(i, REQUEST_SAVE_JSON); }
                catch (Exception ex) { pendingExportJson = null; Toast.makeText(MainActivity.this, "No compatible save location picker is available.", Toast.LENGTH_LONG).show(); }
            });
        }
        @JavascriptInterface public void printPage(String jobTitle) {
            withTrustedPage(() -> {
                if (webView == null) return;
                String title = (jobTitle == null || jobTitle.trim().isEmpty()) ? "Cell Biology Learning Hub" : jobTitle.trim();
                PrintManager pm = (PrintManager)getSystemService(Context.PRINT_SERVICE);
                PrintDocumentAdapter adapter = webView.createPrintDocumentAdapter(title);
                pm.print(title, adapter, new PrintAttributes.Builder().build());
            });
        }
        @JavascriptInterface public void setSystemUiDark(boolean dark) { withTrustedPage(() -> applySystemBarsAppearance(dark)); }
        @JavascriptInterface public void setUiLocale(String language) {
            withTrustedPage(() -> {
                if (!"ta".equals(language) && !"en".equals(language)) return;
                Locale locale = Locale.forLanguageTag("ta".equals(language) ? "ta-IN" : "en-IN");
                Configuration c = new Configuration(getResources().getConfiguration());
                c.setLocale(locale);
                getResources().updateConfiguration(c, getResources().getDisplayMetrics());
            });
        }
        @JavascriptInterface public void setWebBackHandleable(boolean handleable) { withTrustedPage(() -> webBackHandleable = handleable); }
    }
}
