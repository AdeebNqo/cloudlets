package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;

public class FileSharingDB {
	private Socket socket;
	private DataOutputStream output = null;
	private DataInputStream input = null;
	
	private static FileSharingDB instance = null;
	public FileSharingDB(){
		socket = null;
	}
	public static FileSharingDB getInstance(){
		if(instance == null){
			instance = new FileSharingDB();
			return instance;
		}
		return instance;
	}
	public void setSocket(Socket sock){
		instance.socket = sock;
	}
	public Socket getSocket(){
		return instance.socket;
	}
	public void setDataInputStream(DataInputStream input){
		instance.input = input;
	}
	public DataInputStream getDataInputStream(){
		return instance.input;
	}
	public void setDataOutputStream(DataOutputStream output){
		instance.output = output;
	}
	public DataOutputStream getDataOutputStream(){
		return instance.output;
	}
}
