package com.cloudlet.Javo9;


import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import com.example.cloudlet.R;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

public class Connect extends Activity 
{
	
	//wifi state related vars
	WifiManager manager = null;
	WifiInfo info = null;
	
	//mqtt broker related vars
	private String brokerIP = "10.10.0.2";
	private int brokerPort = 9999;
	private String brokerAddress = "tcp://"+brokerIP+":"+brokerPort;
	private String deviceType = "client";
	MemoryPersistence persistence = new MemoryPersistence();
	MqttClient sampleClient = null ;
	
	//ui vars
	TextView statustext;
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.connect_screen);
		statustext = (TextView) findViewById(R.id.statustext);
		manager = (WifiManager) getSystemService(Context.WIFI_SERVICE);
		info = manager.getConnectionInfo();
		
		new Connector().execute();
	}
	
	//Class to connect to mqtt broker on the background
	class Connector extends AsyncTask<Void, Void, Integer>{

		@Override
		protected Integer doInBackground(Void... params) {
			try {
				sampleClient = new MqttClient(brokerAddress, deviceType, persistence);
				MqttConnectOptions connOpts = new MqttConnectOptions();
	            connOpts.setCleanSession(true);
	            sampleClient.subscribe("client/connect"); //client connection here
	            sampleClient.subscribe("client/disconnect"); //client disconnects here
	            sampleClient.subscribe("server/connecteduser"); //connected users will be broadcasted here
	            sampleClient.subscribe("servers/service"); //requested service list will be broadcasted here
	            
	            //sending "connect MAC-address" string
	            String macaddress = info.getMacAddress();
	            String connectString = "connect "+macaddress;
	            MqttMessage message = new MqttMessage(connectString.getBytes());
	            sampleClient.publish("client/connect", message);
	            return 0;
			} catch (MqttException e) {
				e.printStackTrace();
				return 1;
			}
		}
		
	    @Override
	    protected void onPostExecute(Integer connectStatus) {
	    	if (connectStatus==0){
	    		Intent intent = new Intent(Connect.this, ServiceActivity.class);
	        	startActivity(intent);
	    	}
	    	else{
	    		String connectionfail = getResources().getString(R.string.connectionfailed_text);
	    		statustext.setText(connectionfail);
	    	}
	    }
	}
}