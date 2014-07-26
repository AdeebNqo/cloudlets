package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.MqttClient;

public class Client{
	public MqttClient client;
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
}
