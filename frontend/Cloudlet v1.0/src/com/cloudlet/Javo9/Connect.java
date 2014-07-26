package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

import com.example.cloudlet.R;

public class Connect extends Activity 
{
	
	//wifi state related vars
	WifiManager manager = null;
	WifiInfo info = null;
	
	//mqtt broker related vars
	private String brokerIP = "10.10.0.5";
	private int brokerPort = 9999;
	private String brokerAddress = "tcp://"+brokerIP+":"+brokerPort;
	private String deviceType = "client";
	MemoryPersistence persistence = new MemoryPersistence();
	MqttClient mqttClient = null ;
	
	//ui vars
	TextView statustext;
	
	Client myclient = Client.getInstance();
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
	@SuppressLint("NewApi")
	class Connector extends AsyncTask<Void, Void, Integer>{

		@Override
		protected Integer doInBackground(Void... params) {
			try {
				//Log.v("Cloudlet", "Atempyinh to vonnect");
				mqttClient = new MqttClient(brokerAddress, deviceType, persistence);
				MqttConnectOptions connOpts = new MqttConnectOptions();
	            connOpts.setCleanSession(true);
	            mqttClient.connect();
	            //Log.v("Cloudlet", "Connected!");
	            mqttClient.subscribe("client/connect"); //client connection here
	            mqttClient.subscribe("client/disconnect"); //client disconnects here
	            mqttClient.subscribe("server/connecteduser"); //connected users will be broadcasted here
	            mqttClient.subscribe("server/service"); //requested service list will be broadcasted here
	            
	            //Log.v("Cloudlet", "subscribed to channnels!");
	            //sending "connect MAC-address" string
	            String macaddress = info.getMacAddress();
	            String connectString = "connect "+macaddress;
	            MqttMessage message = new MqttMessage(connectString.getBytes());
	            mqttClient.publish("client/connect", message);
	            Log.v("Cloudlet", ""+(mqttClient instanceof java.io.Serializable));
	            return 0;
			} catch (MqttException e) {
				Log.v("Cloudlet", e.getMessage());
				Log.v("Cloudlet", "caused by "+e.getCause());
				e.printStackTrace();
				return 1;
			}
		}

	    @Override
	    protected void onPostExecute(Integer connectStatus) {
	    	if (connectStatus==0){
	    		Intent intent = new Intent(Connect.this, ServiceActivity.class);
	    		myclient.setMqttClient(mqttClient);
	    		myclient.setInfo(info);
	        	startActivity(intent);
	    	}
	    	else{
	    		String connectionfail = getResources().getString(R.string.connectionfailed_text);
	    		statustext.setText(connectionfail);
	    	}
	    }
	}
}