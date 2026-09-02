package edu.gascnagercoil.environmentalsciences;

import android.app.Activity;
import android.annotation.SuppressLint;
import android.graphics.Color;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Toast;

import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView webView;
    private ScrollView scrollView;
    private WebViewAssetLoader assetLoader;
    private Button visualButton;
    private static final String HOME="https://appassets.androidplatform.net/assets/index.html";
    private static final String PRIVACY="https://appassets.androidplatform.net/assets/privacy.html";

    @SuppressLint({"SetJavaScriptEnabled","JavascriptInterface"})
    @Override protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        if(android.os.Build.VERSION.SDK_INT>=30)getWindow().setDecorFitsSystemWindows(true);
        getWindow().setStatusBarColor(Color.rgb(31,101,82));

        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(Color.rgb(255,253,248));
        LinearLayout controls=new LinearLayout(this); controls.setOrientation(LinearLayout.VERTICAL); controls.setPadding(dp(5),dp(5),dp(5),dp(5)); controls.setBackgroundColor(Color.rgb(248,251,249));
        root.addView(controls,new LinearLayout.LayoutParams(-1,-2));
        LinearLayout row1=makeRow(),row2=makeRow(); controls.addView(row1,new LinearLayout.LayoutParams(-1,dp(48))); controls.addView(row2,new LinearLayout.LayoutParams(-1,dp(48)));

        Button contents=makeButton("☰ Contents"),prev=makeButton("←"),next=makeButton("→"); visualButton=makeButton("▣ Visual");
        addWeighted(row1,contents,1.55f); addWeighted(row1,prev,.55f); addWeighted(row1,next,.55f); addWeighted(row1,visualButton,1.15f);
        Button privacy=makeButton("Privacy"),english=makeButton("English"),tamil=makeButton("தமிழ்");
        addWeighted(row2,privacy,1f); addWeighted(row2,english,1f); addWeighted(row2,tamil,1f);

        scrollView=new ScrollView(this); scrollView.setFillViewport(false); scrollView.setSmoothScrollingEnabled(true); scrollView.setVerticalScrollBarEnabled(true); scrollView.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);
        webView=new WebView(this); webView.setBackgroundColor(Color.rgb(255,253,248)); webView.setVerticalScrollBarEnabled(false); webView.setHorizontalScrollBarEnabled(false); webView.setOverScrollMode(View.OVER_SCROLL_NEVER); webView.setNestedScrollingEnabled(false);
        scrollView.addView(webView,new ScrollView.LayoutParams(-1,dp(900)));
        root.addView(scrollView,new LinearLayout.LayoutParams(-1,0,1f)); setContentView(root);

        assetLoader=new WebViewAssetLoader.Builder().addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this)).build();
        WebSettings s=webView.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(false); s.setAllowContentAccess(false); s.setAllowFileAccessFromFileURLs(false); s.setAllowUniversalAccessFromFileURLs(false); s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW); s.setBuiltInZoomControls(false); s.setDisplayZoomControls(false); s.setSupportZoom(false); s.setLoadWithOverviewMode(false); s.setUseWideViewPort(false); s.setTextZoom(100);
        WebView.setWebContentsDebuggingEnabled(false);
        webView.addJavascriptInterface(new HostBridge(),"AndroidHost");
        webView.setWebViewClient(new WebViewClient(){
            @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest r){return assetLoader.shouldInterceptRequest(r.getUrl());}
            @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){String u=r.getUrl().toString();return !u.startsWith("https://appassets.androidplatform.net/assets/");}
            @Override public void onPageFinished(WebView v,String url){super.onPageFinished(v,url); if(HOME.equals(url)) js("(async()=>{await enterBookMode();reportAndroidContentHeight();})();",true); else requestHeight();}
        });

        contents.setOnClickListener(v->js("(async()=>{await loadCatalog();if(!document.body.classList.contains('bookmode'))await enterBookMode();const i=BOOK_CATALOG.findIndex(x=>x.key==='front-2');if(i>=0)await showBookPage(i,'none');reportAndroidContentHeight();})();",true));
        prev.setOnClickListener(v->js("(async()=>{if(!document.body.classList.contains('bookmode'))await enterBookMode();await showBookPage(Math.max(0,bookIndex-1),'none');reportAndroidContentHeight();})();",true));
        next.setOnClickListener(v->js("(async()=>{if(!document.body.classList.contains('bookmode'))await enterBookMode();await showBookPage(Math.min(BOOK_CATALOG.length-1,bookIndex+1),'none');reportAndroidContentHeight();})();",true));
        privacy.setOnClickListener(v->{visualButton.setText("▣ Visual");webView.loadUrl(PRIVACY);scrollView.scrollTo(0,0);});
        english.setOnClickListener(v->js("setLang('en');reportAndroidContentHeight();",true));
        tamil.setOnClickListener(v->js("setLang('ta');reportAndroidContentHeight();",true));
        visualButton.setOnClickListener(v->webView.evaluateJavascript("(function(){try{return toggleVisualFocusNative();}catch(e){return 'error';}})();",result->{
            String r=result==null?"":result.replace("\\\"","").replace("\"","");
            if("none".equals(r)){Toast.makeText(this,"No visual on this page",Toast.LENGTH_SHORT).show();return;}
            visualButton.setText("on".equals(r)?"▣ Full":"▣ Visual"); requestHeight(); scrollView.scrollTo(0,0);
        }));

        if(savedInstanceState==null)webView.loadUrl(HOME);else webView.restoreState(savedInstanceState);
    }

    private class HostBridge{
        @JavascriptInterface public void setContentHeight(final int cssPx){runOnUiThread(()->{
            if(webView==null)return; int px=Math.max(dp(300),Math.round(cssPx*getResources().getDisplayMetrics().density));
            View.LayoutParams lp=webView.getLayoutParams(); if(lp.height!=px){lp.height=px;webView.setLayoutParams(lp);} });}
    }
    private void requestHeight(){webView.postDelayed(()->js("reportAndroidContentHeight();"),80);}
    private LinearLayout makeRow(){LinearLayout r=new LinearLayout(this);r.setOrientation(LinearLayout.HORIZONTAL);r.setGravity(Gravity.CENTER_VERTICAL);return r;}
    private Button makeButton(String t){Button b=new Button(this);b.setText(t);b.setAllCaps(false);b.setTextSize(TypedValue.COMPLEX_UNIT_SP,15);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(dp(4),0,dp(4),0);return b;}
    private void addWeighted(LinearLayout row,View v,float w){LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-1,w);lp.setMargins(dp(2),dp(2),dp(2),dp(2));row.addView(v,lp);}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private void js(String code){js(code,false);} private void js(String code,boolean top){webView.evaluateJavascript("(function(){try{"+code+"}catch(e){console.error(e);}})();",x->{requestHeight();if(top)scrollView.post(()->scrollView.scrollTo(0,0));});}
    @Override protected void onSaveInstanceState(Bundle out){webView.saveState(out);super.onSaveInstanceState(out);}
    private void handleBackNavigation(){if(webView==null){finish();return;}if(!HOME.equals(webView.getUrl())){webView.loadUrl(HOME);return;}webView.evaluateJavascript("(function(){try{return !!(window.handleAppBack&&window.handleAppBack());}catch(e){return false;}})();",v->{if(!"true".equals(v))finish();});}
    @SuppressWarnings("deprecation") @Override public void onBackPressed(){handleBackNavigation();}
    @Override protected void onDestroy(){if(webView!=null){webView.removeJavascriptInterface("AndroidHost");webView.stopLoading();webView.setWebViewClient(null);webView.destroy();webView=null;}super.onDestroy();}
}
