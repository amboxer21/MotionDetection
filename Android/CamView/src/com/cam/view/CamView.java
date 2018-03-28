package com.cam.view;

import android.util.Log;
import android.os.Bundle;
import android.app.Activity;

import java.util.List;
import java.util.Arrays;

import android.content.Intent;
import android.content.Context;

import android.widget.Toast;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RelativeLayout.LayoutParams;

import android.webkit.WebView;
import android.webkit.WebViewClient;

import android.view.View;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View.OnTouchListener;
import android.view.View.OnClickListener;

public class CamView extends Activity implements OnTouchListener {

  private WebView webView;

  private static Client client;

  private static Button button;
  private static EditText ipAddress;
  private static EditText portNumber;
  private static DatabaseHandler db;

  private static String ipAddressDb;
  private static String portNumberDb;

  private static String sIPAddress  = "";
  private static String sPortNumber = "";

  private static long backPressedTime = 0;

  @Override
  public void onBackPressed() {

    button.setVisibility(View.VISIBLE);

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
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    button     = (Button) findViewById(R.id.button);
    portNumber = (EditText) findViewById(R.id.editPort);
    ipAddress  = (EditText) findViewById(R.id.editIPAddress);

    db = new DatabaseHandler(CamView.this);
    getSetDatabaseInfo(0);

    webView    = (WebView) findViewById(R.id.webView);

    webView.setVerticalScrollBarEnabled(false);
    webView.setHorizontalScrollBarEnabled(false);
    webView.setWebViewClient(new CamViewBrowser());
  
    String ip   = String.valueOf(ipAddressDb);
    String port = String.valueOf(portNumberDb);
    final String addr = "http://" + ip + ":" + port + "/cam.mjpg";

    webView.loadUrl(addr);

    /*client = new Client("192.168.1.177", 9486, "onn");  
    client.sendDataWithString();*/

    button.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {
        sanityCheck();
        String ip   = String.valueOf(sIPAddress);
        String port = String.valueOf(sPortNumber);
        String addr = "http://" + ip + ":" + port + "/cam.mjpg";
        webView.setVerticalScrollBarEnabled(false);
        webView.setHorizontalScrollBarEnabled(false);
        webView.setWebViewClient(new CamViewBrowser());
        webView.loadUrl(addr);
      }
    });

    portNumber.setOnTouchListener(new OnTouchListener() {
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
      sPortNumber = portNumber.getText().toString();
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("CamView sanityCheck()", "getText() Error => " + e.getMessage(), e);
    }
    try {
      if(sIPAddress.isEmpty()) {
        Toast.makeText(this,"IP Address cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else if(sPortNumber.isEmpty()) {
        Toast.makeText(this,"Port Number cannot be empty.", Toast.LENGTH_SHORT).show();
        return;
      }
      else {
        getSetDatabaseInfo(1);
      }
    }
    catch(Exception e) {
      e.printStackTrace();
      Log.e("CamView sanityCheck()", "isEmpty() Error => " + e.getMessage(), e);
    }
  }

  public void getSetDatabaseInfo(int action) {

    List<Address> address = db.getAllAddresses();

    if(address == null) {
      return;
    }

    for(Address url : address) {
      ipAddressDb  = url.getIPAddress();
      portNumberDb = url.getPortNumber();
    }

    switch(action) {
      case 0:
        if(ipAddressDb != null) {
          ipAddress.setText(ipAddressDb);
          portNumber.setText(portNumberDb);
        }
        break;
      case 1:
        if(ipAddressDb != null) {
          Log.d("CamView","getSetDatabaseInfo() case 1 - if ipAddressDb != null");
          db.updateAddress(new Address(1,sIPAddress,sPortNumber));
        }
        else {
          Log.d("CamView","getSetDatabaseInfo() case 1 - else");
          db.addAddress(new Address(1,sIPAddress,sPortNumber));
        }
        break;
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
