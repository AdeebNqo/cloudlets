package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.TextView;

import com.example.cloudlet.R;
import com.fima.cardsui.objects.CardStack;
import com.fima.cardsui.objects.RecyclableCard;
import com.fima.cardsui.views.CardUI;

public class ServiceActivity extends Activity{
	public static MqttClient mqttClient = null;
	private CardUI cardui;
	

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_service);
        
        mqttClient = Client.getInstance().getMqttClient();
        mqttClient.setCallback(new ServerCallback());
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

        cardui.refresh();
    }
    
    class ConnectToService extends AsyncTask<String, Void, Integer>
    {

		@Override
		protected Integer doInBackground(String... params) {
			try
			{
				String ip = params[0];
				if (ip.equals("127.0.0.1"))
					ip = "10.10.0.5";
				
				String port = params[1];
				Socket socket = new Socket(ip, Integer.parseInt(port));
				DataInputStream is = new DataInputStream(socket.getInputStream());
				DataOutputStream os = new DataOutputStream(socket.getOutputStream());
				String macAddr = Client.getInstance().info.getMacAddress();
				os.writeUTF("connect " + macAddr);
				
				Log.d("Cloudlet", "abt 2rid connect response");
				if(is.readUTF().equals("OK"))
				{
					Log.d("Cloudlet", "abt 2requested num files");
					os.writeUTF("numfiles");
					Log.d("Cloudlet", "requested num files");
					int numFiles = is.readInt();
					os.writeUTF("OK");
					
					
					for (int i = 0; i < numFiles; ++i)
					{
						String fileDetails = is.readUTF();
						Log.d("Cloudlet", fileDetails);
						os.writeUTF("OK");
					}
					
					return 0;
				}
				
				
				return 1;
			}
			catch (Exception e)
			{
				e.printStackTrace();
				return 1;
			}
		}
    	
    }
    
	class ServerCallback implements MqttCallback{

		@Override
		public void connectionLost(Throwable arg0) {
			// TODO Auto-generated method stub
			Log.d("Cloudlet","connection lost");
		}

		@Override
		public void deliveryComplete(IMqttDeliveryToken arg0) {
			// TODO Auto-generated method stub
			Log.d("Cloudlet","delivery complete");
		}

		@Override
		public void messageArrived(String arg0, MqttMessage arg1)
				throws Exception {
			// TODO Auto-generated method stub
			if (arg0.equals("server/service")){
				String service = new String(arg1.getPayload());
				final String[] items = service.split("-");
				ServiceCard serviceCard = new ServiceCard(items[0], items[1], R.drawable.card);
				cardui.addCard(serviceCard);
				serviceCard.setOnClickListener(new OnClickListener(){

					@Override
					public void onClick(View arg0) {
						/*
						 * How to connect to a service
						 * 
						 * 1. Create socket to ip=items[2], port=items[3]
						 * 2. send "connect <mac address>" via socket
						 * 3. send string "numfiles" via socket
						 * 4. read socket for num of files accessible
						 * 5. send "OK" via socket
						 * 6. for numfiles times	
						 *		6.1 read file details
						 *		6.2 send "OK" via socket
						 */
						Log.d("Cloudlet", "test1");
						new ConnectToService().execute(items[2] ,  items[3]);
						Log.d("Cloudlet", "test2");
					}
					
				});
			}
		}
		
	}
	class ServiceCard extends RecyclableCard{
		public ServiceCard(String title, String descr, int image){
			super(title, descr, image);
		}
		@Override
		protected void applyTo(View convertView) {
			((TextView)(convertView.findViewById(R.id.title))).setText(this.title);
			((TextView)(convertView.findViewById(R.id.description))).setText(this.desc);
		}

		@Override
		protected int getCardLayoutId() {
			return R.layout.card_ex;
		}
	}
}