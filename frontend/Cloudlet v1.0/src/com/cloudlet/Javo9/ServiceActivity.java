package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;
import java.util.LinkedList;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.TextView;

import com.example.cloudlet.R;

public class ServiceActivity extends Activity{
	public static MqttClient mqttClient = null;
	

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_service);
      
    }
    
    class ConnectToService extends AsyncTask<String, Void, Integer>
    {

		LinkedList<String> files = new LinkedList<String>();
		Socket socket = null;
		DataInputStream is;
		DataOutputStream os;
		
		@Override
		protected Integer doInBackground(String... params) {
			try
			{
				String ip = params[0];
				if (ip.equals("127.0.0.1"))
					ip = "10.10.0.5";
				
				String port = params[1];
				socket = new Socket(ip, Integer.parseInt(port));
				is = new DataInputStream(socket.getInputStream());
				os = new DataOutputStream(socket.getOutputStream());
				String macAddr = Client.getInstance().info.getMacAddress();
				os.writeUTF("connect " + macAddr);
				
				Log.d("Cloudlet", "abt 2rid connect response");
				if(is.readUTF().equals("OK"))
				{
					os.writeUTF("numfiles");
					Log.d("Cloudlet", "requested num files");
					int numFiles = Integer.parseInt(is.readUTF());
					os.writeUTF("OK");
					
					
					Log.d("Cloudlet", "available files: "+numFiles);
					for (int i = 0; i < numFiles; ++i)
					{
						Log.d("Cloudlet", "attempting to read file details");
						String fileDetails = is.readUTF();
						files.add(fileDetails);
						os.writeUTF("OK");
					}
					Log.d("Cloudlet", "after loop");
					
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
}