package com.cloudlet.connectivity;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

public class ConnectionHandler implements Runnable{
	
	private List<ConnectionChangeListener> listeners = new ArrayList<ConnectionChangeListener>();
	private Socket socket = null;
	private InputStream in = null;
	private OutputStream out = null;
	
	private int CONNECTION_TIME = 10;
	
    public void addListener(ConnectionChangeListener toAdd) {
        listeners.add(toAdd);
    }
    
	public ConnectionHandler(Socket socket) throws IOException{
		this.socket = socket;
		
		in = socket.getInputStream();
		out = socket.getOutputStream();
		
		checkConnection();
		
	}
	public void checkConnection(){
		//checking the life of the connection
		Timer timer = new Timer();
		timer.scheduleAtFixedRate(new TimerTask() {
			  @Override
			  public void run() {
				  //send data
				  
				  //wait for 60 sec
				  
				  //if no response, connection is dead.
				  //else do nothing as everything is well
			  }
			}, CONNECTION_TIME*60*1000, CONNECTION_TIME*60*1000);
	}
	public void run(){
		if (socket != null){
			
		}
	}
}
