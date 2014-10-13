package com.cloudlet.Javo9;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.example.cloudlet.R;

public class ServiceActivity extends Activity implements CProtocolInterface {

	CProtocol protocol = null;
	ArrayList<String> list = new ArrayList<String>();
	ServiceAdapter adapter = null;
	String identifier = null;
	String username = null;
	FileSharingClient filesharingclient = null;
	private boolean alreadyCreated = false;

	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		if (!isCreated())
		{
			super.onCreate(savedInstanceState);
			setContentView(R.layout.activity_service);
			final ListView servicelist = (ListView) findViewById(R.id.servicelist);
			
			//creating adapter
			if (adapter==null){
				adapter = new ServiceAdapter(this, R.layout.service, list);
				servicelist.setAdapter(adapter);
			}
			
			//retrieving protocol class
			if (protocol==null){
				protocol = CProtocol.getCProtocol();
				protocol.setCProtocolListener(ServiceActivity.this);
				try {
					protocol.requestAvailableServices();
				} catch (MqttPersistenceException e1) {
					e1.printStackTrace();
				} catch (MqttException e1) {
					e1.printStackTrace();
				}
			}
			
			alreadyCreated = true;
			
			servicelist.setOnItemClickListener(new OnItemClickListener() 
			{
				@Override
				public void onItemClick(AdapterView<?> parent, View view,
						int position, long id) {
					if (filesharingclient == null) {
						String chosenservice = servicelist.getItemAtPosition(
								position).toString();
						String[] items = chosenservice.split(";");
						String name = items[0].split("=")[1];
						try 
						{
								//try
							//	{
									while(protocol.subscribed==false){}
									Log.d("cloudletXdebug", "THREAD SLEEP started!");
									//Thread.sleep((long)5.0);
								//} 
//								catch (InterruptedException e) 
//								{
//									Log.d("cloudletXdebug", "THREAD SLEEP FAILED!");
//									e.printStackTrace();
//								}
							
							protocol.requestService(protocol.identifier, name);
						} 
						catch (MqttPersistenceException e) {
							e.printStackTrace();
						} 
						catch (MqttException e) {
							e.printStackTrace();
						}
					} else {
						// start file sharing activity
						Intent intent = new Intent(ServiceActivity.this, UserActivity.class);
						startActivity(intent);
					}
				}
			});
		}
	}

	/*
	 * Method for adding service to the list of services which will be displayed
	 */
	public void addService(String service) {
		if (!list.contains(new String(service)))
			runOnUiThread(new myRunnable(service));
	}

	class myRunnable implements Runnable {
		String service;

		public myRunnable(String service) {
			this.service = service;
		}

		public void run() {
			adapter.add(service);
		}
	}

	@Override
	public void connectionLost(Throwable arg0) {
		// Toast.makeText(getApplicationContext(),
		// "Connection lost: "+arg0.getMessage(), Toast.LENGTH_LONG).show();
	}

	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		String msg = new String(arg1.getPayload());
		Log.d("cloudletXdebug", "1. recieved msg on channel "+arg0);
		if (arg0.equals("client/service/" + protocol.name)) {
			addService(msg);
		}else if (arg0.equals("client/service_request/recvIP")){
			Log.d("cloudletXdebug","recieved ip and port");
			String[] vals = new String(arg1.getPayload()).split("\\|");
			if (vals[3].equals(protocol.macaddress)){
				String[] portandip = vals[1].split(":");
				final String ip = portandip[0];
				final String port = portandip[1];
				String[] param = {ip, port};
				FileSharingClientConnector filesharingconnector = new FileSharingClientConnector(this);
				filesharingconnector.execute(param);
			}
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		// Toast.makeText(getApplicationContext(), "Delivered msg",
		// Toast.LENGTH_SHORT).show();
	}

	/*
	 * Custom adapter for list of services
	 */
	public class ServiceAdapter extends ArrayAdapter<String> {
		private Context context;

		public ServiceAdapter(Context context, int textviewRId) {
			super(context, textviewRId);
			this.context = context;
		}

		public ServiceAdapter(Context context, int resource, List<String> items) {
			super(context, resource, items);
			this.context = context;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			LayoutInflater inflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			View customv = inflater.inflate(R.layout.service, parent, false);

			String service = getItem(position);
			String[] services = service.split(";");
			if (service != null) {
				TextView name = (TextView) customv.findViewById(R.id.name);
				TextView description = (TextView) customv
						.findViewById(R.id.description);
				TextView authors = (TextView) customv
						.findViewById(R.id.authors);
				TextView website = (TextView) customv
						.findViewById(R.id.website);
				TextView copyright = (TextView) customv
						.findViewById(R.id.copyright);
				TextView version = (TextView) customv
						.findViewById(R.id.version);

				name.setText(services[0].split("=")[1]);
				version.setText(services[1].split("=")[1]);
				description.setText(services[2].split("=")[1]);
				authors.setText(services[3].split("=")[1]);
				copyright.setText(services[4].split("=")[1]);
				website.setText(services[5].split("=")[1]);
			}
			return customv;
		}
	}
	
	/*
	 * Method to check if this activity was created before within this session.
	 */
	private boolean isCreated()
	{
		return alreadyCreated;
	}
	
	/*
	 * Class for connecting to file sharing client
	 */
	private class FileSharingClientConnector extends AsyncTask<String, Void, Void> {

		ProgressDialog dialog;
		public FileSharingClientConnector(Activity activity){
//			Looper.prepare();
//			this.dialog = new ProgressDialog(activity);
		}
		protected void onPreExecute() {
//			dialog.setTitle("Requesting file sharer");
//			dialog.setMessage("Please wait...");
			//dialog.show();
		}
		@Override
		protected Void doInBackground(String... params) {
			String ip = params[0];
			int port = Integer.parseInt(params[1]);
			
			filesharingclient = FileSharingClient.getFileSharingClient(
					protocol.name, ip, port);
			Log.d("cloudletXdebug", "done creating filesharingclient");
			return null;
		}
		protected void onPostExecute(Void result) {
			Intent intent = new Intent(ServiceActivity.this, UserActivity.class);
			startActivity(intent);
		}
	}
	
	@Override
	public void onBackPressed() 
	{
	  finish();
	}
}