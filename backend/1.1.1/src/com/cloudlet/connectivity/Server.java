package com.cloudlet.connectivity;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;

public class Server implements ConnectionChangeListener{
	private int START = 0;
	private int STOP = 1;
	
	private int running = 0;
	private HashMap<String, ConnectionHandler> connectedUsers = new HashMap<String, ConnectionHandler>();
	private ServerSocket sSocket;
	
	public Server(){
		
	}
	public void run() throws IOException{
		sSocket = new ServerSocket(9090);
		(new Thread(){
			public void run(){
				while(running == START){
					try{
						System.err.println("waiting for connection...");
						Socket s = sSocket.accept();
						
						ConnectionHandler handler = new ConnectionHandler(s);
						
						Thread  worker = new Thread(handler);
						worker.start();
						
						handler.addListener(Server.this);
						connectionchange(ConnectionChangeListener.CONNECTED,  handler, s.getInetAddress().toString());
						System.err.println("connection accepted...");
						
					}catch(IOException e){
						e.printStackTrace();
					}
				}
			}
		}).start();
	}
	
	public void start() throws IOException{
			running = START;
			run();
			System.err.println("start() returning");
	}
	public void stop(){
		running = STOP;
	}
	
	public void connectionchange(int status, ConnectionHandler handler, String ip) {
		if (ConnectionChangeListener.CONNECTED == status){
			connectedUsers.put(ip, handler);
		}else if (ConnectionChangeListener.DISCONNECTED == status){
			connectedUsers.remove(ip);
		}
	}
}