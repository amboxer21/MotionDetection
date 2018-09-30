package com.cam.view;

import android.util.Log;

import java.util.List;
import java.util.ArrayList;
 
import android.content.Context;
import android.content.ContentValues;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHandler extends SQLiteOpenHelper {
 
  private static final int DATABASE_VERSION    = 1;
 
  private static final String KEY_ID           = "id";
  private static final String KEY_IP_ADDRESS   = "ip_address";
  private static final String KEY_CAM_PORT_NUMBER    = "cam_port_number";
  private static final String KEY_SERVER_PORT_NUMBER = "Server_port_number";

  private static final String TABLE_ADDRESS = "address";
  private static final String DATABASE_NAME = "url";
 
  public DatabaseHandler(Context context) {
    super(context, DATABASE_NAME, null, DATABASE_VERSION);
  }
 
  @Override
  public void onCreate(SQLiteDatabase db) {
    String CREATE_ADDRESS_TABLE = "CREATE TABLE " + TABLE_ADDRESS + "("
      + KEY_ID + " INTEGER PRIMARY KEY," 
      + KEY_IP_ADDRESS + " TEXT,"
      + KEY_CAM_PORT_NUMBER + " TEXT DEFAULT '5000',"
      + KEY_SERVER_PORT_NUMBER + " TEXT DEFAULT '50050'" + ")";
    db.execSQL(CREATE_ADDRESS_TABLE);
  }
 
  @Override
  public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    db.execSQL("DROP TABLE IF EXISTS " + TABLE_ADDRESS);
    onCreate(db);
  }

  void addAddress(Address address) {
    SQLiteDatabase db = this.getWritableDatabase();
 
    ContentValues values = new ContentValues();
    values.put(KEY_IP_ADDRESS, address.getIPAddress()); 
    values.put(KEY_CAM_PORT_NUMBER, address.getCamPortNumber()); 
    values.put(KEY_SERVER_PORT_NUMBER, address.getServerPortNumber()); 
 
    db.insert(TABLE_ADDRESS, null, values);
    db.close(); 
  }
 
  Address getAddress(int id) {
    SQLiteDatabase db = this.getReadableDatabase();
 
    Cursor cursor = db.query(TABLE_ADDRESS, 
      new String[] {
        KEY_ID, KEY_IP_ADDRESS,
        KEY_CAM_PORT_NUMBER, KEY_SERVER_PORT_NUMBER 
      }, KEY_ID + "=?",
      new String[] { String.valueOf(id) }, null, null, null, null);
      if (cursor != null) {
        cursor.moveToFirst();
      }
 
      Address address = new Address(
        Integer.parseInt(cursor.getString(0)),
        cursor.getString(1), 
        cursor.getString(2),
        cursor.getString(3)
      );
      return address;
  }
     
  public List<Address> getAllAddresses() {

    List<Address> addressList = new ArrayList<Address>();

    String selectQuery = "SELECT  * FROM " + TABLE_ADDRESS;
 
    SQLiteDatabase db  = this.getWritableDatabase();
    Cursor cursor      = db.rawQuery(selectQuery, null);
 
    if (cursor.moveToFirst()) {
      do {
        Address address = new Address();
        address.setID(Integer.parseInt(cursor.getString(0)));
        address.setIPAddress(cursor.getString(1));
        address.setCamPortNumber(cursor.getString(2));
        address.setServerPortNumber(cursor.getString(3));
        addressList.add(address);
      } while (cursor.moveToNext());
    }

    return addressList;
  }
 
  public int updateAddress(Address address) {
    Log.d("CamView","updateAddress(Address address) debug");
    SQLiteDatabase db    = this.getWritableDatabase();
    ContentValues values = new ContentValues();
    values.put(KEY_IP_ADDRESS, address.getIPAddress());
    values.put(KEY_CAM_PORT_NUMBER, address.getCamPortNumber());
    values.put(KEY_SERVER_PORT_NUMBER, address.getServerPortNumber());
 
    return db.update(TABLE_ADDRESS, values, "id = ?",
      new String[] { String.valueOf(address.getID()) });
  }
 
  public void deleteAddress(Address address) {
    SQLiteDatabase db = this.getWritableDatabase();
    db.delete(TABLE_ADDRESS, KEY_ID + " = ?",
      new String[] { String.valueOf(address.getID()) });
    db.close();
  }

  public int getAddressCount() {
    String countQuery = "SELECT  * FROM " + TABLE_ADDRESS;
    Log.d("CamView","countQuery => " + countQuery);
    SQLiteDatabase db = this.getReadableDatabase();
    Cursor cursor = db.rawQuery(countQuery, null);
    cursor.close();
 
    Log.d("CamView","getAddressCount() => " + cursor.getCount());
    return cursor.getCount();
  }
 
}
