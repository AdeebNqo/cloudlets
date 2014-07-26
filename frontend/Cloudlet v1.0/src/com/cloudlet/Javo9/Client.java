package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.MqttClient;

import android.net.wifi.WifiInfo;

public class Client{
	public MqttClient client;
	public WifiInfo info;
	private static Client instance = null;
	
	public Client(){
		client = null;
	}
	
	public static Client getInstance(){
		if (instance == null){
			instance = new Client();
		}
		return instance;
	}
	
	public void setMqttClient(MqttClient someclient){
		instance.client = someclient;
	}
	
	public MqttClient getMqttClient(){
		return instance.client;
	}
	
	public WifiInfo getInfo()
	{
		return info;
	}
	
	public void setInfo(WifiInfo i)
	{
		info = i;
	}
}
