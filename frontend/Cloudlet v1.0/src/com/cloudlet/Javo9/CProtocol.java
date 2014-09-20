/*
 * Class to handle the connecting and requesting of services from the cloudlet using the new protocol.
 * Jarvis Mutakha(mtkjar001)
 * September 2014.
 */

package com.cloudlet.Javo9;

import java.util.LinkedList;
import java.util.List;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import android.content.Context;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiConfiguration;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.util.Log;

public class CProtocol implements MqttCallback{
	private WifiManager manager=null;
	private Context appContext = null;
	private static CProtocol instance = null;
	private String cloudletAddress = null;
	private MqttClient mqttClient = null ;
	private MemoryPersistence persistence = new MemoryPersistence();
	int i = 0;
	LinkedList<CProtocolInterface> cprotocollisteners = new LinkedList<CProtocolInterface>();
	
	public static CProtocol getCProtocol(){
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
		this.appContext = appContext;
		manager = (WifiManager) appContext.getSystemService(Context.WIFI_SERVICE);
	}
	/*
	 * Method for setting IP and Port of cloudlet
	 */
	public void setCloudletAddress(String ip, int port){
		cloudletAddress = "tcp://"+ip+":"+port;
	}
	/*
	 * Method for connecting to a specified WiFi network.
	 * 
	 */
	public void connectToWiFi(String ssid, String password)
	{
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
		String[] vals = identifier.split("\\|");
		//Log.d("cloudletXdebug", "mqttClient creation failed");
		String name = vals[0].substring(0, 6);
		identifier = name +"|"+ vals[1];
		new Connector().execute(identifier);
	}
	
	public void subscribeServiceChannel(String servicename) throws MqttException
	{
		mqttClient.subscribe("client/servicename/"+servicename, 1);
	}
	
	/*
	 * Method for disconnecting from cloudlet
	 */
	public void disconnectFromCloudlet() throws MqttException, NullPointerException{
		if (mqttClient==null){
			throw new NullPointerException("Mqtt Client is null.");
		}else{
			mqttClient.disconnect();
		}
	}
	private class Connector extends AsyncTask<String, Void, Void>{
		@Override
		protected Void doInBackground(String... params) {
			try{
				String identifier = params[0];
				Log.d("cloudletXdebug", identifier);
				Log.d("cloudletXdebug", cloudletAddress);
				mqttClient = new MqttClient(cloudletAddress, identifier, persistence);
				mqttClient.setCallback(CProtocol.this);
				MqttConnectOptions connOpts = new MqttConnectOptions();
		        connOpts.setCleanSession(true);
		        mqttClient.connect();
		        mqttClient.subscribe("client/connecteduser"); //connected users will be broadcasted here
	            mqttClient.subscribe("client/service"); //available services will be broadcasted here
	            mqttClient.subscribe("client/service_request/"+identifier);
	            mqttClient.subscribe("client/service_request/+/"+identifier+"/recvIP");
	            Log.d("cloudletXdebug", "done with connecting and subscribing");
			}catch(MqttException e){
				Log.d("cloudletXdebug", "mqttClient creation failed");
				//e.printStackTrace();
			}
			return null;
		}

		@Override
		protected void onPostExecute(Void result) {
			try {
				CProtocol.this.requestAvailableServices();;
			} catch (MqttPersistenceException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (MqttException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			super.onPostExecute(result);
		}
	}
	
	/*
	 * Method for requesting list of users using a service.
	 */
	public void requestUsersOnService(String channel) throws MqttPersistenceException, MqttException
	{
		MqttMessage msg = new MqttMessage("file_sharing".getBytes());
		mqttClient.publish(channel, msg);
	}
	
	/*
	 * Method for requesting connected users
	 */
	public void requestConnectedUsers() throws MqttPersistenceException, MqttException{
		MqttMessage msg = new MqttMessage("hello".getBytes());
		mqttClient.publish("server/connectedusers", msg);
	}
	/*
	 * Method for requesting available services
	 */
	public void requestAvailableServices() throws MqttPersistenceException, MqttException{
		MqttMessage msg = new MqttMessage("world".getBytes());
		mqttClient.publish("server/servicelist", msg);
	}
	
	/*
	 * Method for requesting a service
	 */
	public void requestService(String identifier, String servicename) throws MqttPersistenceException, MqttException{
		MqttMessage msg = new MqttMessage((identifier+";"+servicename).getBytes());
		mqttClient.publish("server/useservice", msg);
	}
	/*
	 * Method for advertising clients' services
	 */
	public void advertizeServices(String servicesString) throws MqttPersistenceException, MqttException{
		MqttMessage msg = new MqttMessage(servicesString.getBytes());
		mqttClient.publish("server/service", msg);
	}
	/*
	 * Method for retrieving the mac address
	 */
	public String getMacAddress(){
		WifiInfo info = manager.getConnectionInfo();
		String address = info.getMacAddress();
		return address;
	}
	/*
	 * 
	 */
	public void setCProtocolListener(CProtocolInterface somereceiver){
		cprotocollisteners.add(somereceiver);
	}
	
	@Override
	public void connectionLost(Throwable arg0) {
		Log.d("cloudletXdebug", "the connection has been lost: "+arg0.getMessage());
		for (CProtocolInterface somereceiver: cprotocollisteners){
			somereceiver.connectionLost(arg0);
		}
		arg0.printStackTrace();
	}
	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		Log.d("cloudletXdebug", "msg delivered");
		for (CProtocolInterface somereceiver: cprotocollisteners){
			somereceiver.deliveryComplete(arg0);
		}
	}
	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		Log.d("cloudletXdebug", "msg has been received");
		for (CProtocolInterface somereceiver: cprotocollisteners){
			somereceiver.messageArrived(arg0, arg1);
		}
	}
}
