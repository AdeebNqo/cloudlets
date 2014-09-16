package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Toast;

import com.example.cloudlet.R;

public class ServiceActivity extends Activity implements CProtocolInterface{

	CProtocol protocol = null;
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
	    setContentView(R.layout.activity_service);
    	try{
			protocol = CProtocol.getCProtocol();
			protocol.init(getBaseContext());
			protocol.setCloudletAddress("10.10.0.51", 9999);
			//protocol.connectToWiFi("CloudletX", "none");
			String macaddress = protocol.getMacAddress();
			protocol.connectToCloudlet("clientandroid|"+macaddress);
    	}catch(MqttException e){
    		e.printStackTrace();
    		//show error connecting dialog
    		Toast.makeText(getApplicationContext(), "Could not connect", Toast.LENGTH_LONG).show();
    	}
    }
    
	@Override
	public void connectionLost(Throwable arg0) {
		Toast.makeText(getApplicationContext(), "Connection lost", Toast.LENGTH_LONG).show();
	}
	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		String msg = new String(arg1.getPayload());
		Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_LONG).show();
	}
	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		Toast.makeText(getApplicationContext(), "Delivered msg", Toast.LENGTH_SHORT).show();
	}
}