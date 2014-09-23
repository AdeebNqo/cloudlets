package com.cloudlet.Javo9;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.example.cloudlet.R;

public class ServiceActivity extends Activity implements CProtocolInterface{

	CProtocol protocol = null;
	ArrayList<String> list = new ArrayList<String>();
	ServiceAdapter adapter = null;
	String identifier = null;
	String username = null;
	FileSharingClient filesharingclient = null;
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
	    setContentView(R.layout.activity_service);
	    final ListView servicelist = (ListView) findViewById(R.id.servicelist);
	    adapter = new ServiceAdapter(this, R.layout.service, list);
	    servicelist.setAdapter(adapter);
		protocol = CProtocol.getCProtocol();
		protocol.setCProtocolListener(ServiceActivity.this);
		try {
			protocol.requestAvailableServices();
		} catch (MqttPersistenceException e1) {
			e1.printStackTrace();
		} catch (MqttException e1) {
			e1.printStackTrace();
		}
    	servicelist.setOnItemClickListener(new OnItemClickListener(){

			@Override
			public void onItemClick(AdapterView<?> parent, View view,
					int position, long id) {
				String chosenservice = servicelist.getItemAtPosition(position).toString();
				String[] items = chosenservice.split(";");
				String name = items[0].split("=")[1];
				try {
					protocol.requestService(identifier,name);
				} catch (MqttPersistenceException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (MqttException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
    	});
    	Log.d("cloudletXdebug", "last line of oncreate");
    }
	@Override
	protected void onDestroy() {
		// TODO Auto-generated method stub
		try {
			protocol.disconnectFromCloudlet();
		} catch (NullPointerException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (MqttException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		super.onDestroy();
	}
    /*
     * Method for adding service to the list of
     * services which will be displayed
     */
    public void addService(String service){
    	runOnUiThread(new myRunnable(service));
    }
    class myRunnable implements Runnable{
    	String service;
    	public myRunnable(String service){
    		this.service = service;
    	}
    	public void run(){
    		adapter.add(service);
    	}
    }
    
	@Override
	public void connectionLost(Throwable arg0) {
		//Toast.makeText(getApplicationContext(), "Connection lost: "+arg0.getMessage(), Toast.LENGTH_LONG).show();
	}
	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		String msg = new String(arg1.getPayload());
		Log.d("cloudletXdebug", arg0);
		if (arg0.equals("client/service")){
			addService(msg);
			int i = msg.indexOf("=");
			String serviceName = msg.substring(i+1);
			protocol.subscribeServiceChannel(serviceName);
		}
		else if (Pattern.matches("client/service_request/.*/"+identifier+"/recvIP", arg0)){
			String[] vals = new String(arg1.getPayload()).split("\\|");
			String servicename = vals[0];
			String[] portandip = vals[1].split(":");
			String ip = portandip[0];
			String port = portandip[1];
			if (servicename.endsWith("file_sharer")){
				filesharingclient = FileSharingClient.getFileSharingClient(username, ip , Integer.parseInt(port));
				Intent intent = new Intent(this, UserActivity.class);
				startActivity(intent);
			}
		}
	}
	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		//Toast.makeText(getApplicationContext(), "Delivered msg", Toast.LENGTH_SHORT).show();
	}
	/*
	 * Custom adapter for list of services
	 */
	public class ServiceAdapter extends ArrayAdapter<String>{
		private Context context;
		public ServiceAdapter(Context context, int textviewRId){
			super(context, textviewRId);
			this.context = context;
		}
		public ServiceAdapter(Context context, int resource, List<String> items){
			super(context, resource, items);
			this.context = context;
		}
		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			View customv = inflater.inflate(R.layout.service, parent, false);
			
			String service = getItem(position);
			String[] services = service.split(";");
			if (service!=null){
				TextView name = (TextView) customv.findViewById(R.id.name);
				TextView description = (TextView) customv.findViewById(R.id.description);
				TextView authors = (TextView) customv.findViewById(R.id.authors);
				TextView website = (TextView) customv.findViewById(R.id.website);
				TextView copyright = (TextView) customv.findViewById(R.id.copyright);
				TextView version = (TextView) customv.findViewById(R.id.version);
				
				
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
}