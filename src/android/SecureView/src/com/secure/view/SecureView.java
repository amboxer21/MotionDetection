package com.secure.view;

import android.net.Uri;
import android.util.Log;
import android.app.Activity;
import android.graphics.Color;

import java.util.List;
import java.util.Arrays;

import android.os.Bundle;
import android.os.Handler;

import android.content.Intent;
import android.content.Context;

import android.widget.Toast;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.ToggleButton;
import android.widget.RelativeLayout;
import android.widget.RelativeLayout.LayoutParams;

import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;

import android.view.View;
import android.view.KeyEvent;
import android.view.ViewGroup;
import android.view.MotionEvent;
import android.view.SurfaceView;
import android.view.SurfaceHolder;
import android.view.View.OnTouchListener;
import android.view.View.OnClickListener;

public class SecureView extends Activity implements OnTouchListener, SurfaceHolder.Callback {

  private static String ip;
  private static String camPort;
  private static String serverPort;

  private static Client client;
  private static ClientAsyncTask clientAsyncTask;

  private SurfaceView surfaceView;
  private SurfaceHolder surfaceHolder;

  private static TextView textView;
  private static ToggleButton buttonCam;
  private static ToggleButton buttonRecord;

  private static EditText ipAddress;
  private static EditText camPortNumber;
  private static EditText serverPortNumber;
  private static DatabaseHandler db;

  private static String ipAddressDb;
  private static String buttonCamDb;
  private static String buttonRecordDb;
  private static String camPortNumberDb;
  private static String serverPortNumberDb;

  private static String sIPAddress  = "";
  private static String sCamPortNumber = "";
  private static String sServerPortNumber = "";

  private static int mCounter = 0;
  private static int wCounter = 0;
  private static long backPressedTime = 0;
  private static boolean Kill_monitor_string_sent = false;

  @Override
  public void onBackPressed() {
    long mTime = System.currentTimeMillis();
    if(mTime - backPressedTime > 2000) {
      backPressedTime = mTime;
      Toast.makeText(this, "Press back again to close app.", Toast.LENGTH_SHORT).show();
    }
    else {
      super.onBackPressed();
      Intent intent = new Intent(Intent.ACTION_MAIN);
      intent.addCategory(Intent.CATEGORY_HOME);
      startActivity(intent);
    }
  }

  @Override
  public void onResume() {
    super.onResume();
  }

  @Override
  public void onPause() {
    super.onPause();
  }

  public void onStop() {
    super.onStop();
    buttonCam.setChecked(false);
    if(textView.getText().toString().equals("Live Feed")) {
      /*clientAsyncTask = new ClientAsyncTask();
      clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "stop_recording");*/
      clientAsyncTask = new ClientAsyncTask();
      clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
      textView.setText("Dead Feed");
      buttonRecord.setText("Record");
      textView.setTextColor(Color.parseColor("#ff0000"));
    }
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
  } 

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    textView     = (TextView) findViewById(R.id.textView);
    buttonCam    = (ToggleButton) findViewById(R.id.buttonCam);
    ipAddress    = (EditText) findViewById(R.id.editIPAddress);
    buttonRecord = (ToggleButton) findViewById(R.id.buttonRecord);
    camPortNumber    = (EditText) findViewById(R.id.editCamPort);
    serverPortNumber = (EditText) findViewById(R.id.editServerPort);

    db = new DatabaseHandler(SecureView.this);

    databaseGetter();

    wCounter = 1;
    mCounter = 1;

    RelativeLayout mRelativeLayoutMain = (RelativeLayout) findViewById(R.id.secureView);
    mRelativeLayoutMain.setOnTouchListener(this);

    surfaceView = (SurfaceView)findViewById(R.id.preview);
    surfaceHolder = surfaceView.getHolder();
    surfaceHolder.addCallback(this);
    surfaceHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

    buttonCam.setChecked(false);
    buttonRecord.setText("Record");
    textView.setText("Dead Feed");
    textView.setTextColor(Color.parseColor("#ff0000"));

    final Handler handler = new Handler();
    final WebView webView = (WebView) findViewById(R.id.webView);

    buttonCam.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {

        buttonCam.setChecked(false);

        if(passedSanityCheck()) {
        
          buttonCam.setChecked(true);

          databaseSetter();
          databaseGetter();

          if(textView.getText().toString() == "Dead Feed") {
            String sIPAddress2 = String.valueOf(sIPAddress); 
            String camPort = String.valueOf(sCamPortNumber);
            String serverPort = String.valueOf(sServerPortNumber);
            final String addr = "http://" + sIPAddress2 + ":" + camPort + "/cam.mjpg";
  
            clientAsyncTask = new ClientAsyncTask();
            clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "start_monitor");

            webView.setVerticalScrollBarEnabled(false);
            webView.setHorizontalScrollBarEnabled(false);
            webView.getSettings().setUseWideViewPort(true);
            webView.getSettings().setJavaScriptEnabled(true);
            webView.getSettings().setLoadWithOverviewMode(true);
            webView.setWebViewClient(new SecureViewBrowser());
            webView.setBackgroundColor(Color.parseColor("#ffffff"));
            handler.postDelayed(new Runnable() {
              public void run() {
                textView.setText("Live Feed");
                textView.setTextColor(Color.parseColor("#00ff55"));
                webView.loadUrl(addr);
              }
            }, 6000);
          }
          else if(textView.getText().toString() == "Live Feed") {
            textView.setText("Dead Feed");
            buttonRecord.setText("Record");
            textView.setTextColor(Color.parseColor("#ff0000"));
            /*clientAsyncTask = new ClientAsyncTask();
            clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "stop_recording");*/
            clientAsyncTask = new ClientAsyncTask();
            clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
          }
        }
      }
    });

    buttonRecord.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {
        if(textView.getText().toString() == "Dead Feed") {
          Toast.makeText(getApplicationContext(), "Feed is not live.", Toast.LENGTH_LONG).show();
        }
        else if(buttonCam.getText().toString() == "Record") { 
          /*clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "start_recording");*/
          buttonRecord.setText("Recording");
        }
        else {
          buttonRecord.setText("Recording");
        }
      }
    });

    webView.setOnTouchListener(new OnTouchListener() {
      @Override
      public boolean onTouch(View v, MotionEvent event) {
        if(event.getAction() == MotionEvent.ACTION_DOWN) {
          wCounter++;
        }
        if((wCounter % 2) == 0) {
          ipAddress.setVisibility(View.VISIBLE);
          buttonCam.setVisibility(View.VISIBLE);
          buttonRecord.setVisibility(View.VISIBLE);
          camPortNumber.setVisibility(View.VISIBLE);
          serverPortNumber.setVisibility(View.VISIBLE);
        }
        else {
          ipAddress.setVisibility(View.INVISIBLE);
          buttonCam.setVisibility(View.INVISIBLE);
          buttonRecord.setVisibility(View.INVISIBLE);
          camPortNumber.setVisibility(View.INVISIBLE);
          serverPortNumber.setVisibility(View.INVISIBLE);
        }
        return false;
      }
    });

  }

  public boolean passedSanityCheck() {

    try {
      sIPAddress  = ipAddress.getText().toString();
      sCamPortNumber = camPortNumber.getText().toString();
      sServerPortNumber = serverPortNumber.getText().toString();
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("SecureView passedSanityCheck()", "getText() Error => " + e.getMessage(), e);
      return false;
    }
    try {
      if(String.valueOf(sIPAddress).isEmpty()) {
        Toast.makeText(this,"IP Address cannot be empty.", Toast.LENGTH_SHORT).show();
        return false;
      }
      else if(String.valueOf(sCamPortNumber).isEmpty()) {
        Toast.makeText(this,"Cam port number cannot be empty.", Toast.LENGTH_SHORT).show();
        return false;
      }
      else if(String.valueOf(sServerPortNumber).isEmpty()) {
        Toast.makeText(this,"Server port number cannot be empty.", Toast.LENGTH_SHORT).show();
        return false;
      }
      else {
        return true;
      }
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("SecureView passedSanityCheck()", "isEmpty() Error => " + e.getMessage(), e);
      return false;
    }
  }

  public void databaseGetter() {

    Log.d("SecureView","databaseGetter()");

    List<Address> address = db.getAllAddresses();

    if(address == null) {
      return;
    }

    for(Address url : address) {
      ipAddressDb  = url.getIPAddress();
      camPortNumberDb = url.getCamPortNumber();
      serverPortNumberDb = url.getServerPortNumber();

      ip = String.valueOf(ipAddressDb);
      camPort = String.valueOf(camPortNumberDb);
      serverPort = String.valueOf(serverPortNumberDb);

      ipAddress.setText(ip);

      if(camPort == null) {
        camPortNumber.setText("5000");
        serverPortNumber.setText("50050");
      }
      else {
        camPortNumber.setText(camPort);
        serverPortNumber.setText(serverPort);
      }
    }
  }

  public void databaseSetter() {

    if(ipAddressDb != null) {
      db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber));
    }
    else {
      db.addAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber));
    }
  }

  private class SecureViewBrowser extends WebViewClient {
    @Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
      view.loadUrl(url);
      return true;
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
      handleError(errorCode,view);
    }

    @Override
    public void onReceivedError(WebView view, WebResourceRequest req, WebResourceError rerr) {
      onReceivedError(view, rerr.getErrorCode(),rerr.getDescription().toString(),req.getUrl().toString());
    }

    public void handleError(int errorCode, WebView view) {

      String message = null;

      if(errorCode == WebViewClient.ERROR_AUTHENTICATION) {
        message = "User authentication failed on server";
      }
      else if (errorCode == WebViewClient.ERROR_TIMEOUT) {
        message = "The server is taking too much time to communicate. Try again later.";
      }
      else if (errorCode == WebViewClient.ERROR_TOO_MANY_REQUESTS) {
        message = "Too many requests during this load";
      }
      else if (errorCode == WebViewClient.ERROR_UNKNOWN) {
        message = "Generic error";
      }
      else if (errorCode == WebViewClient.ERROR_BAD_URL) {
        message = "Check entered URL..";
      }
      else if (errorCode == WebViewClient.ERROR_CONNECT) {
        message = "Failed to connect to the server";
      }
      else if (errorCode == WebViewClient.ERROR_FAILED_SSL_HANDSHAKE) {
        message = "Failed to perform SSL handshake";
      }
      else if (errorCode == WebViewClient.ERROR_HOST_LOOKUP) {
        message = "Server or proxy hostname lookup failed";
      }
      else if (errorCode == WebViewClient.ERROR_PROXY_AUTHENTICATION) {
        message = "User authentication failed on proxy";
      }
      else if (errorCode == WebViewClient.ERROR_REDIRECT_LOOP) {
        message = "Too many redirects";
      }
      else if (errorCode == WebViewClient.ERROR_UNSUPPORTED_AUTH_SCHEME) {
        message = "Unsupported authentication scheme (not basic or digest)";
      }
      else if (errorCode == WebViewClient.ERROR_UNSUPPORTED_SCHEME) {
        message = "unsupported scheme";
      }
      else if (errorCode == WebViewClient.ERROR_FILE) {
        message = "Generic file error";
      }
      else if (errorCode == WebViewClient.ERROR_FILE_NOT_FOUND) {
        message = "File not found";
      }
      else if (errorCode == WebViewClient.ERROR_IO) {
        message = "The server failed to communicate. Try again later.";
      }
      if (message != null) {
        buttonCam.setChecked(false);
        textView.setText("Dead Feed");
        textView.setTextColor(Color.parseColor("#ff0000"));
        Toast.makeText(getApplicationContext(), "" + message, Toast.LENGTH_LONG).show();
      }
    }
  }

  public boolean onTouch(View v, MotionEvent event) {
    mCounter++;
    if((mCounter % 2) == 0) {
      ipAddress.setVisibility(View.VISIBLE);
      buttonCam.setVisibility(View.VISIBLE);
      buttonRecord.setVisibility(View.VISIBLE);
      camPortNumber.setVisibility(View.VISIBLE);
      serverPortNumber.setVisibility(View.VISIBLE);
    }
    else {
      ipAddress.setVisibility(View.INVISIBLE);
      buttonCam.setVisibility(View.INVISIBLE);
      buttonRecord.setVisibility(View.INVISIBLE);
      camPortNumber.setVisibility(View.INVISIBLE);
      serverPortNumber.setVisibility(View.INVISIBLE);
    }

    return false;
  }

  public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) { }

  public void surfaceCreated(SurfaceHolder holder) { }

  public void surfaceDestroyed(SurfaceHolder holder) { }

}
