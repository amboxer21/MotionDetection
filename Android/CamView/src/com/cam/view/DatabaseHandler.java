package com.cam.view;

import java.util.List;
import java.util.ArrayList;
 
import android.content.Context;
import android.content.ContentValues;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHandler extends SQLiteOpenHelper {
 
  private static final int DATABASE_VERSION   = 1;
 
  private static final String KEY_ID          = "id";
  private static final String KEY_IP_ADDRESS  = "ip_address";
  private static final String KEY_PORT_NUMBER = "port_number";

  private static final String TABLE_ADDRESS   = "address";
  private static final String DATABASE_NAME   = "url";
 
  public DatabaseHandler(Context context) {
    super(context, DATABASE_NAME, null, DATABASE_VERSION);
  }
 
  @Override
  public void onCreate(SQLiteDatabase db) {
    String CREATE_ADDRESS_TABLE = "CREATE TABLE " + TABLE_ADDRESS + "("
      + KEY_ID + " INTEGER PRIMARY KEY," 
      + KEY_IP_ADDRESS + " TEXT,"
      + KEY_PORT_NUMBER + " TEXT" + ")";
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
    values.put(KEY_PORT_NUMBER, address.getPortNumber()); 
 
    db.insert(TABLE_ADDRESS, null, values);
    db.close(); 
  }
 
  Address getAddress(int id) {
    SQLiteDatabase db = this.getReadableDatabase();
 
    Cursor cursor = db.query(TABLE_ADDRESS, 
      new String[] { KEY_ID, KEY_IP_ADDRESS, KEY_PORT_NUMBER }, KEY_ID + "=?",
      new String[] { String.valueOf(id) }, null, null, null, null);
      if (cursor != null) {
        cursor.moveToFirst();
      }
 
      Address address = new Address(Integer.parseInt(cursor.getString(0)),
        cursor.getString(1), 
        cursor.getString(2));

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
        address.setPortNumber(cursor.getString(2));
        addressList.add(address);
      } while (cursor.moveToNext());
    }
 
    return addressList;
  }
 
  public int updateAddress(Address address) {
    SQLiteDatabase db    = this.getWritableDatabase();
    ContentValues values = new ContentValues();
    values.put(KEY_IP_ADDRESS, address.getIPAddress());
    values.put(KEY_PORT_NUMBER, address.getPortNumber());
 
    return db.update(TABLE_ADDRESS, values, KEY_ID + " = ?",
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
    SQLiteDatabase db = this.getReadableDatabase();
    Cursor cursor = db.rawQuery(countQuery, null);
    cursor.close();
 
    return cursor.getCount();
  }
 
}
