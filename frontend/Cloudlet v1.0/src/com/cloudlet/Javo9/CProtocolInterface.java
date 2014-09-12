/*
 * Interface class for the CProtocol.
 */
package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public interface CProtocolInterface {
	public void connectionLost(Throwable arg0);
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception;
	public void deliveryComplete(IMqttDeliveryToken arg0);
}
