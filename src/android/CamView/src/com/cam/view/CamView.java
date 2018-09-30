package com.cam.view;

import  android.net.Uri;
import android.util.Log;
import android.app.Activity;

import java.util.List;
import java.util.Arrays;

import android.os.Bundle;
import android.os.Handler;

import android.content.Intent;
import android.content.Context;

import android.widget.Toast;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RelativeLayout.LayoutParams;

import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;

import android.view.View;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View.OnTouchListener;
import android.view.View.OnClickListener;

public class CamView extends Activity implements OnTouchListener {

  private static String ip;
  private static String camPort;
  private static String serverPort;

  private static Client client;
  private static ClientAsyncTask clientAsyncTask;

  private static Button buttonCam;
  private static Button buttonState;

  private static EditText ipAddress;
  private static EditText camPortNumber;
  private static EditText serverPortNumber;
  private static DatabaseHandler db;

  private static String ipAddressDb;
  private static String buttonCamDb;
  private static String buttonStateDb;
  private static String camPortNumberDb;
  private static String serverPortNumberDb;

  private static String sIPAddress  = "";
  private static String sCamPortNumber = "";
  private static String sServerPortNumber = "";

  private static long backPressedTime = 0;

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
    clientAsyncTask = new ClientAsyncTask();
    clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
    buttonCam.setText("Go Live");
  }

  public void onStop() {
    super.onStop();
    if(buttonCam.getText().toString().equals("Live")) {
      clientAsyncTask = new ClientAsyncTask();
      clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
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

    buttonCam   = (Button) findViewById(R.id.buttonCam);
    buttonState = (Button) findViewById(R.id.buttonState);
    ipAddress   = (EditText) findViewById(R.id.editIPAddress);
    camPortNumber    = (EditText) findViewById(R.id.editCamPort);
    serverPortNumber = (EditText) findViewById(R.id.editServerPort);

    db = new DatabaseHandler(CamView.this);

    databaseGetter();

    buttonCam.setText("Go Live");
    buttonState.setText("Stop");

    final Handler handler = new Handler();
    final WebView webView = (WebView) findViewById(R.id.webView);

    buttonCam.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {

        sanityCheck();

        String ipAddress = String.valueOf(sIPAddress); 
        String camPort = String.valueOf(sCamPortNumber);
        String serverPort = String.valueOf(sServerPortNumber);
        final String addr = "http://" + ipAddress + ":" + camPort + "/cam.mjpg";

        clientAsyncTask = new ClientAsyncTask();
        clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "start_monitor");

        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setWebViewClient(new CamViewBrowser());
        handler.postDelayed(new Runnable() {
          public void run() {
            webView.loadUrl(addr);
            buttonCam.setText("Live");
          }
        }, 3000);
      }
    });

    buttonState.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {

        if(buttonCam.getText().toString().equals("Go Live")) {
          Toast.makeText(getApplicationContext(), "Feed isn't live!", Toast.LENGTH_LONG).show();
          return;
        }
        else {
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, serverPortNumberDb, "kill_monitor");
          buttonCam.setText("Go Live");
        }
      }
    });

    serverPortNumber.setOnTouchListener(new OnTouchListener() {
      @Override
      public boolean onTouch(View v, MotionEvent event) {
        return false;
      }
    });

    ipAddress.setOnTouchListener(new OnTouchListener() {
      @Override
      public boolean onTouch(View v, MotionEvent event) {
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
      Log.e("CamView sanityCheck()", "getText() Error => " + e.getMessage(), e);
    }
    try {
      if(String.valueOf(sIPAddress).isEmpty()) {
        Toast.makeText(this,"IP Address cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else if(String.valueOf(sCamPortNumber).isEmpty()) {
        Toast.makeText(this,"Cam port Number cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else if(String.valueOf(sServerPortNumber).isEmpty()) {
        sServerPortNumber = "50050";
      }
      else {
        databaseSetter();
        databaseGetter();
      }
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("CamView sanityCheck()", "isEmpty() Error => " + e.getMessage(), e);
    }
  }

  public void databaseGetter() {

    Log.d("CamView","databaseGetter()");

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

  @Override
  public boolean onTouch(View v, MotionEvent event) {
    return false;
  }


  private class CamViewBrowser extends WebViewClient {
    @Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
      view.loadUrl(url);
      return true;
    }
  }

}
