package com.cam.view; 
 
public class Address {
     
  int _id;

  String _ip_address;
  String _cam_port_number;
  String _server_port_number;

  public Address() { }
     
  public Address(int id, String ip_address, String cam_port_number, String server_port_number) {
      this._id = id;
      this._ip_address  = ip_address;
      this._cam_port_number = cam_port_number;
      this._server_port_number = server_port_number;
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

  public String getCamPortNumber(){
    return this._cam_port_number;
  }
     
  public void setCamPortNumber(String cam_port_number){
    this._cam_port_number = cam_port_number;
  }

  public String getServerPortNumber(){
    return this._server_port_number;
  }

  public void setServerPortNumber(String server_port_number){
    this._server_port_number = server_port_number;
  }
     
}
