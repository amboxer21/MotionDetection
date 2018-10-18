package com.secure.view;

import java.io.PrintWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.ByteArrayOutputStream;

import java.net.Socket;
import java.net.InetAddress;
import java.net.UnknownHostException;

import android.util.Log;

public class Client { 

  public static int serverPort;

  public static String serverAction;
	public static String serverAddress;

	public static Socket socket;
  public static OutputStream out;
	public static PrintWriter pWriter; 
 
  public Client(String addr, int port, String action) {
    serverPort     = port;
    serverAddress  = addr;
    serverAction   = action;
  }

  public void sendDataWithString() {

    try {
      socket  = new Socket(serverAddress, serverPort);

      pWriter = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));
      pWriter.write(serverAction);

      pWriter.flush();
      pWriter.close();
      Log.d("SecureView", "pWriter: " + pWriter);
    }
    catch(IOException e) {
      Log.d("SecureView", "sendDataWithString() " + e.toString());
      e.printStackTrace();
    }

  }

}
