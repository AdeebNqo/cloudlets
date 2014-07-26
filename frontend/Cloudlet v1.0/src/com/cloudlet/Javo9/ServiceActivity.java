package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import com.example.cloudlet.R;
import com.fima.cardsui.objects.CardStack;
import com.fima.cardsui.views.CardUI;

public class ServiceActivity extends Activity{
	public static MqttClient mqttClient = null;
	private CardUI cardui;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_service);
        
        mqttClient = Client.getInstance().getMqttClient();
        
        cardui = (CardUI) findViewById(R.id.cardsview);
        cardui.setSwipeable(true);
        
        CardStack stack= new CardStack(); 
        stack.setTitle(getResources().getString(R.string.service_text));
        cardui.addStack(stack);
        
        MqttMessage msg = new MqttMessage("ufck that btch".getBytes());
        try {
			mqttClient.publish("client/servicelist",msg);
		} catch (MqttPersistenceException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (MqttException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

    }
}

