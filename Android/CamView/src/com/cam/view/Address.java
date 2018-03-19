package com.cam.view; 
 
public class Address {
     
  int _id;

  String _ip_address;
  String _port_number;

  public Address() { }
     
  public Address(int id, String ip_address, String port_number) {
      this._ip_address  = ip_address;
      this._port_number = port_number;
  }
     
  public int getID(){
    return this._id;
  }
     
  public void setID(int id){
    this._id = id;
  }

  public String getIPAddress(){
    return this._ip_address;
  }

  public void setIPAddress(String ip_address){
    this._ip_address = ip_address;
  }

  public String getPortNumber(){
    return this._port_number;
  }
     
  public void setPortNumber(String port_number){
    this._port_number = port_number;
  }
     
}
