package com.cloudlet.connectivity;


public interface ConnectionChangeListener {
	int CONNECTED = 1;
	int DISCONNECTED  = 0;
	public void connectionchange(int status, ConnectionHandler s, String ip);
}
