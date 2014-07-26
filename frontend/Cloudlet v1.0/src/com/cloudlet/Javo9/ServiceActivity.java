package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.MqttClient;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

import com.example.cloudlet.R;

public class ServiceActivity extends Activity{
	public static MqttClient mqttClient = null;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_service);
        
        if (mqttClient!=null){
        	Log.d("Cloudlet", "mqtt object hhas been passed!");
        }
    }
}

