package com.cloudlet.Javo9;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.example.cloudlet.R;

public class LogInActivity extends Activity implements CProtocolInterface 
{
	private EditText nametextbox = null;
	private Button loginButton = null;
	private Button exitButton = null;
	private CProtocol protocol = null;
	private String username = null;
	private String identifier = null;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_login);
		setTitle("Enter a user name");
		nametextbox = (EditText) findViewById(R.id.nametextbox);
		loginButton = (Button) findViewById(R.id.submitname);

		loginButton.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				username = nametextbox.getText().toString();
				if (username.equals("")) {
					Toast.makeText(getApplicationContext(),
							"Name field is empty", Toast.LENGTH_LONG);
				} else {
					try {
						protocol = CProtocol.getCProtocol();
						protocol.init(getBaseContext());
						protocol.setCloudletAddress("10.10.0.51", 9999);
						String macaddress = protocol.getMacAddress();
						protocol.identifier = username + "|" + macaddress;
						protocol.connectToCloudlet(protocol.identifier);
						protocol.setCProtocolListener(LogInActivity.this);
					} catch (MqttException e) {
						e.printStackTrace();
						// show error connecting dialog
						Toast.makeText(getApplicationContext(),
								"Could not connect", Toast.LENGTH_LONG).show();
					}
				}
			}
		});
		
		exitButton = (Button) findViewById(R.id.quit_app_button);

		exitButton.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				onDestroy();
			}
		});
	}
	
	@Override
	protected void onDestroy() {
		super.onDestroy();
		try {
			protocol.disconnectFromCloudlet();
			finish();
		} catch (NullPointerException e) {
			e.printStackTrace();
		} catch (MqttException e) {
			e.printStackTrace();
		}
		
		android.os.Process.killProcess(android.os.Process.myPid());
	}

	@Override
	public void connectionLost(Throwable arg0) {
		// TODO Auto-generated method stub

	}

	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		Log.d("cloudletXdebug", "0. recieved msg on channel "+arg0);
		if (arg0.equals("server/login/" + protocol.name)) {
			String reply = new String(arg1.getPayload());
			Log.d("cloudletXdebug", reply);
			if (reply.equals("OK")) {
				Intent intent = new Intent(this, ServiceActivity.class);
				startActivity(intent);
			}
			else if (reply.equals("UDUP"))
			{
				Looper.prepare();
				Toast.makeText(getApplicationContext(), "The username is taken.", Toast.LENGTH_LONG).show();
				protocol.disconnectFromCloudlet();
			}
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {

	}
}
