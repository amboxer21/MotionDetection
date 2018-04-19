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
  private static Button buttonLive;

  private static EditText ipAddress;
  private static EditText camPortNumber;
  private static EditText serverPortNumber;
  private static DatabaseHandler db;

  private static String buttonCamDb;
  private static String ipAddressDb;
  private static String buttonLiveDb;
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
    clientAsyncTask.execute(ipAddressDb, "50050", "kill_monitor");
    //buttonCam.setText("Stop");
    buttonLive.setText("Go Live");
  }

  public void onStop() {
    super.onStop();
    clientAsyncTask = new ClientAsyncTask();
    clientAsyncTask.execute(ipAddressDb, "50050", "kill_monitor");
    //buttonCam.setText("Stop");
    buttonLive.setText("Go Live");
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
    clientAsyncTask = new ClientAsyncTask();
    clientAsyncTask.execute(ipAddressDb, "50050", "kill_monitor");
    //buttonCam.setText("Stop");
    buttonLive.setText("Go Live");
  } 

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    buttonCam = (Button) findViewById(R.id.buttonCam);
    buttonLive = (Button) findViewById(R.id.buttonLive);
    ipAddress = (EditText) findViewById(R.id.editIPAddress);
    camPortNumber = (EditText) findViewById(R.id.editCamPort);
    serverPortNumber = (EditText) findViewById(R.id.editServerPort);

    db = new DatabaseHandler(CamView.this);

    databaseGetter();

    if(!String.valueOf(buttonCamDb).isEmpty() && String.valueOf(buttonCamDb).equals("Stop")) {
      buttonCam.setText("Start");
    }
    else if(!String.valueOf(buttonCamDb).isEmpty()) {
      buttonCam.setText("Stop");
    }

    final Handler handler = new Handler();
    final WebView webView = (WebView) findViewById(R.id.webView);

    buttonLive.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {

        sanityCheck("buttonLive");

        String ip = String.valueOf(sIPAddress);
        String camPort = String.valueOf(sCamPortNumber);
        String serverPort = String.valueOf(sServerPortNumber);
        final String addr = "http://" + ip + ":" + camPort + "/cam.mjpg";

        clientAsyncTask = new ClientAsyncTask();
        clientAsyncTask.execute(ipAddressDb, "50050", "start_monitor");

        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setWebViewClient(new CamViewBrowser());
        handler.postDelayed(new Runnable() {
          public void run() {
            webView.loadUrl(addr);
            buttonLive.setText("Live");
          }
        }, 4000);
      }
    });

    buttonCam.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {

        sanityCheck("buttonCam");

        if(buttonLive.getText().toString().equals("Live")) {
          Toast.makeText(getApplicationContext(), "Cannot stop MotionDetection while Live!", Toast.LENGTH_LONG).show();
          return;
        }
        else if(String.valueOf(buttonCamDb).equals("Stop")) {
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, "50050", "start_motion");
          buttonCam.setText("Stop");
        }
        else if(String.valueOf(buttonCamDb).equals("Start")) {
          clientAsyncTask = new ClientAsyncTask();
          clientAsyncTask.execute(ipAddressDb, "50050", "kill_motion");
          buttonCam.setText("Start");
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

  public void sanityCheck(String button_name) {

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
        Toast.makeText(this,"Server port Number cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else {
        databaseGetter();
        databaseSetter(button_name);
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
      buttonCamDb = url.getCamState();
      Log.d("CamView","databaseGetter() url.getIPAddress() => " + String.valueOf(url.getIPAddress()));
      Log.d("CamView","databaseGetter() url.getCamPortNumber() => " + String.valueOf(url.getCamPortNumber()));
      Log.d("CamView","databaseGetter() url.getServerPortNumber() => " + String.valueOf(url.getServerPortNumber()));
      Log.d("CamView","databaseGetter() url.getCamState() => " + String.valueOf(url.getCamState()));

      ip = String.valueOf(ipAddressDb);
      camPort = String.valueOf(camPortNumberDb);
      serverPort = String.valueOf(serverPortNumberDb);

      ipAddress.setText(ip);
      camPortNumber.setText(camPort);
      serverPortNumber.setText(serverPort);
    }
  }

  public void databaseSetter(String button_name) {

    if(ipAddressDb != null) {
      Log.d("CamView","getSetDatabaseInfo() ipAddressDb != null");
      if(String.valueOf(buttonCamDb).equals("Start")) {
        Log.d("CamView","databaseSetter() if(buttonCamDb.equals('Start')))");
        if(button_name.equals("buttonCam")) {
          Log.d("CamView","databaseSetter() button_name.equals('buttonCam')");
          db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"Stop"));
        }
        else {
          Log.d("CamView","databaseSetter() !button_name.equals('buttonCam')");
          db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"none"));
        }
      }
      else if(String.valueOf(buttonCamDb).equals("Stop")) {
        Log.d("CamView","databaseSetter() else if(buttonCamDb.equals('Stop'))");
        if(button_name.equals("buttonCam")) {
          Log.d("CamView","databaseSetter() button_name.equals('buttonCam')");
          db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"Start"));
        }
        else {
          Log.d("CamView","databaseSetter() !button_name.equals('buttonCam')");
          db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"none"));
        }
      }
      else {
        Log.d("CamView","databaseSetter() else");
        db.updateAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"none"));
      }
    }
    else {
      Log.d("CamView","databaseSetter() ipAddressDb == null");
      db.addAddress(new Address(1,sIPAddress,sCamPortNumber,sServerPortNumber,"Start"));
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
