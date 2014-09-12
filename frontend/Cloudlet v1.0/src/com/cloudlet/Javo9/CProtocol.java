/*
 * Class to handle the connecting and requesting of services from the cloudlet using the new protocol.
 * Jarvis Mutakha(mtkjar001)
 * September 2014.
 */

package com.cloudlet.Javo9;

import java.util.List;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import android.content.Context;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiConfiguration;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;

public class CProtocol implements MqttCallback{
	private WifiManager manager=null;
	private Context appContext = null;
	private CProtocol instance = null;
	private String cloudletAddress = null;
	private MqttClient mqttClient = null ;
	private MemoryPersistence persistence = new MemoryPersistence();
	
	public CProtocol getCProtocol(){
		if (instance==null){
			instance = new CProtocol();
			return instance;
		}
		return instance;
	}
	/*
	 * Initializing the context in which the
	 * CProtocol will operate.
	 */
	public void init(Context appContext){
		instance.appContext = appContext;
	}
	/*
	 * Method for setting IP and Port of cloudlet
	 */
	public void setCloudletAddress(String ip, int port){
		instance.cloudletAddress = "tcp://"+ip+":"+port;
	}
	/*
	 * Method for connecting to a specified WiFi network.
	 * 
	 */
	public void connectToWiFi(String ssid, String password)
	{
		instance.manager = (WifiManager) instance.appContext.getSystemService(Context.WIFI_SERVICE);
		List<ScanResult> networks = manager.getScanResults();
		for (ScanResult network: networks){
			if (network.SSID.equals(ssid)){
				WifiConfiguration wc = new WifiConfiguration();
				wc.SSID = network.SSID;
				wc.BSSID = network.BSSID;
				wc.status = WifiConfiguration.Status.ENABLED;
			    wc.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.TKIP);
			    wc.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.CCMP);
			    wc.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK);
			    wc.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.TKIP);
			    wc.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.CCMP);
			    wc.allowedProtocols.set(WifiConfiguration.Protocol.RSN);
				int netID = manager.addNetwork(wc);
				manager.enableNetwork(netID, true);
			}
		}
	}
	/*
	 * Method for connecting to a cloudlet
	 */
	public void connectToCloudlet(String identifier) throws MqttException{
		new Connector().execute(identifier);
	}
	private class Connector extends AsyncTask<String, Void, Void>{

		@Override
		protected Void doInBackground(String... params) {
			try{
				String identifier = params[0];
				instance.mqttClient = new MqttClient(instance.cloudletAddress, identifier, persistence);
				MqttConnectOptions connOpts = new MqttConnectOptions();
		        connOpts.setCleanSession(true);
		        mqttClient.connect();
		        mqttClient.subscribe("client/connecteduser"); //connected users will be broadcasted here
	            mqttClient.subscribe("client/service"); //available services will be broadcasted here
	            mqttClient.subscribe("client/service_request/"+identifier);
	            mqttClient.subscribe("client/service_request/+/"+identifier+"/recvIP");
			}catch(MqttException e){
				e.printStackTrace();
			}
			return null;
		}
	
	}
	
	
	/*
	 * Method for retrieving the mac address
	 */
	public String getMacAddress(){
		WifiInfo info = instance.manager.getConnectionInfo();
		String address = info.getMacAddress();
		return address;
	}
	
	@Override
	public void connectionLost(Throwable arg0) {
		// TODO Auto-generated method stub
		
	}
	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		// TODO Auto-generated method stub
		
	}
	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		// TODO Auto-generated method stub
		
	}
}
