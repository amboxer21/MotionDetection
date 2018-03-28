package com.cam.view;

import android.os.AsyncTask;

class ClientAsyncTask extends AsyncTask<String, String, String> {

  private Exception exception;
  private static Client client;

  protected String doInBackground(String... params) {
    try {
      String ip           = params[0];
      String serverPort   = params[1];
      String serverAction = params[2];
      client = new Client(ip,Integer.valueOf(serverPort),serverAction);
      client.sendDataWithString();
      return null;
    } 
    catch(Exception e) {
      this.exception = e;
      return null;
    }
  }

  @Override
  protected void onPostExecute(String result) { }

  @Override
  protected void onPreExecute() { }

  @Override
  protected void onProgressUpdate(String... text) { }

}
