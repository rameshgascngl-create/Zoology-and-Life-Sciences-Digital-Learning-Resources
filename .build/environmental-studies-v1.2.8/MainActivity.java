package edu.gascnagercoil.environmentalsciences;

import android.app.Activity;
import android.annotation.SuppressLint;
import android.graphics.Color;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;

import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView webView;
    private WebViewAssetLoader assetLoader;
    private static final String HOME = "https://appassets.androidplatform.net/assets/index.html";
    private static final String PRIVACY = "https://appassets.androidplatform.net/assets/privacy.html";

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (android.os.Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(true);
        getWindow().setStatusBarColor(Color.rgb(31,101,82));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(255,253,248));

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.VERTICAL);
        controls.setPadding(dp(5), dp(5), dp(5), dp(5));
        controls.setBackgroundColor(Color.rgb(248,251,249));
        root.addView(controls, new LinearLayout.LayoutParams(-1, -2));

        LinearLayout row1 = makeRow();
        LinearLayout row2 = makeRow();
        controls.addView(row1, new LinearLayout.LayoutParams(-1, dp(48)));
        controls.addView(row2, new LinearLayout.LayoutParams(-1, dp(48)));

        Button contents = makeButton("☰ Contents");
        Button prev = makeButton("←");
        Button next = makeButton("→");
        Button visual = makeButton("▣ Visual");
        addWeighted(row1, contents, 1.55f); addWeighted(row1, prev, .55f); addWeighted(row1, next, .55f); addWeighted(row1, visual, 1.15f);

        Button privacy = makeButton("Privacy");
        Button english = makeButton("English");
        Button tamil = makeButton("தமிழ்");
        addWeighted(row2, privacy, 1f); addWeighted(row2, english, 1f); addWeighted(row2, tamil, 1f);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(255,253,248));
        webView.setVerticalScrollBarEnabled(true);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);
        webView.setNestedScrollingEnabled(true);
        root.addView(webView, new LinearLayout.LayoutParams(-1, 0, 1f));
        setContentView(root);

        assetLoader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setSupportMultipleWindows(false);
        s.setJavaScriptCanOpenWindowsAutomatically(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setLoadWithOverviewMode(false);
        s.setUseWideViewPort(false);
        s.setTextZoom(100);
        WebView.setWebContentsDebuggingEnabled(false);

        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                return !url.startsWith("https://appassets.androidplatform.net/assets/");
            }
            @Override public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (HOME.equals(url)) {
                    js("(async()=>{try{await enterBookMode();}catch(e){console.error(e)}})();");
                }
            }
        });

        contents.setOnClickListener(v -> js("(async()=>{await loadCatalog();if(!document.body.classList.contains('bookmode'))await enterBookMode();const i=BOOK_CATALOG.findIndex(x=>x.key==='front-2');if(i>=0)showBookPage(i,'none');})();", true));
        prev.setOnClickListener(v -> js("if(!document.body.classList.contains('bookmode'))enterBookMode();showBookPage(Math.max(0,bookIndex-1),'none');", true));
        next.setOnClickListener(v -> js("if(!document.body.classList.contains('bookmode'))enterBookMode();showBookPage(Math.min(BOOK_CATALOG.length-1,bookIndex+1),'none');", true));
        visual.setOnClickListener(v -> js("document.body.classList.toggle('visual-focus');"));
        privacy.setOnClickListener(v -> webView.loadUrl(PRIVACY));
        english.setOnClickListener(v -> js("setLang('en');"));
        tamil.setOnClickListener(v -> js("setLang('ta');"));

        if (savedInstanceState == null) webView.loadUrl(HOME);
        else webView.restoreState(savedInstanceState);
    }

    private LinearLayout makeRow() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        return row;
    }

    private Button makeButton(String label) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        b.setMinWidth(0);
        b.setMinimumWidth(0);
        b.setPadding(dp(4), 0, dp(4), 0);
        return b;
    }

    private void addWeighted(LinearLayout row, View view, float weight) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -1, weight);
        lp.setMargins(dp(2), dp(2), dp(2), dp(2));
        row.addView(view, lp);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void js(String code) { js(code, false); }

    private void js(String code, boolean resetTop) {
        webView.evaluateJavascript("(function(){try{" + code + "}catch(e){console.error(e);}})();", value -> {
            if (resetTop) webView.postDelayed(() -> webView.scrollTo(0, 0), 60);
        });
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    private void handleBackNavigation() {
        if (webView == null) { finish(); return; }
        if (!HOME.equals(webView.getUrl())) { webView.loadUrl(HOME); return; }
        webView.evaluateJavascript("(function(){try{return !!(window.handleAppBack&&window.handleAppBack());}catch(e){return false;}})();", value -> {
            if (!"true".equals(value)) {
                if (webView.canGoBack()) webView.goBack(); else finish();
            }
        });
    }

    @SuppressWarnings("deprecation")
    @Override public void onBackPressed() { handleBackNavigation(); }

    @Override protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.setWebViewClient(null);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
