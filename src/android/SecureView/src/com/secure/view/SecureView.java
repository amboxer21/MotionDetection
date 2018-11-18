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
      clientAsyncTask = new ClientAsyncTask();
      clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "stop_recording");
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

        sanityCheck();

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
          }, 3000);
        }
        else if(textView.getText().toString() == "Live Feed") {
          textView.setText("Dead Feed");
          buttonRecord.setText("Record");
          textView.setTextColor(Color.parseColor("#ff0000"));
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "stop_recording");
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
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
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "start_recording");
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

  public void sanityCheck() {

    try {
      sIPAddress  = ipAddress.getText().toString();
      sCamPortNumber = camPortNumber.getText().toString();
      sServerPortNumber = serverPortNumber.getText().toString();
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("SecureView sanityCheck()", "getText() Error => " + e.getMessage(), e);
    }
    try {
      if(String.valueOf(sIPAddress).isEmpty()) {
        buttonCam.setChecked(false);
        Toast.makeText(this,"IP Address cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else if(String.valueOf(sCamPortNumber).isEmpty()) {
        buttonCam.setChecked(false);
        Toast.makeText(this,"Cam port number cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else if(String.valueOf(sServerPortNumber).isEmpty()) {
        buttonCam.setChecked(false);
        Toast.makeText(this,"Server port number cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else {
        databaseSetter();
        databaseGetter();
      }
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("SecureView sanityCheck()", "isEmpty() Error => " + e.getMessage(), e);
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
