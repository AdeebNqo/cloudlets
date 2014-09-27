package com.cloudlet.Javo9;

import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.provider.ContactsContract.CommonDataKinds.Phone;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;

import com.example.cloudlet.R;

public class UserActivity extends Activity implements CProtocolInterface 
{
	CProtocol protocol = null;
	FileSharingClient filesharing = null;
	ArrayList<String> list = new ArrayList<String>();
	ListView userListView = null;
	UserAdapter adapter = null;
	
	Button sync = null;
	Button upload = null;
	
	private boolean alreadyCreated = false;
	private static final int REQUEST_CHOOSER = 6384;
	
	private int syncInterval = 10000; // Sync every 10s.
	private Handler syncHandler = null;
	private Timer timer = null;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		if (!isCreated())
		{
			super.onCreate(savedInstanceState);
			setContentView(R.layout.activity_user);
			userListView = (ListView) findViewById(R.id.userlist);
		    adapter = new UserAdapter(getBaseContext(), R.layout.user, list);
		    userListView.setAdapter(adapter);
		    alreadyCreated = true;
		    
		    syncHandler = new Handler();
		    timer = new Timer();
		    
		    userListView.setOnItemClickListener(new OnItemClickListener()
		    {
				@Override
				public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
						long arg3) {
					Object chosenuser = userListView.getItemAtPosition(arg2);
					String c = (String)chosenuser;
					Log.d("cloudletXdebug","chosen "+c);
					Intent liststarter = new Intent(getApplicationContext(), FileActivity.class);
					Log.d("cloudletXdebug","putting chosen user in intent");
					liststarter.putExtra("owner", c);
					Log.d("cloudletXdebug","starting file activity");
					startActivity(liststarter);
					Log.d("cloudletXdebug","started file activity");
				}
		    });
		    
		    protocol = CProtocol.getCProtocol();
		    protocol.setCProtocolListener(this);
		    filesharing = FileSharingClient.getFileSharingClient();
		    if (filesharing==null){
		    	//retrieving filesharerclient object in future
		    	final Handler handler = new Handler();
		    	handler.postDelayed(new Runnable() {
		    		  @Override
		    		  public void run() {
		    			  filesharing = FileSharingClient.getFileSharingClient();
		    		  }
		    		}, 3000);
		    }
		    try 
		    {
				protocol.requestUsersOnService("file_sharer");
			} 
		    catch (MqttPersistenceException e)
		    {
				e.printStackTrace();
			} 
		    catch (MqttException e) 
			{
				e.printStackTrace();
			}
		    
		    sync = (Button) findViewById(R.id.sync);
		    sync.setOnClickListener(new OnClickListener(){
	
				@Override
				public void onClick(View arg0) {
					new Thread()
					{
						public void run()
						{
							filesharing.sync();
						}
					}.start();
				}
		    	
		    });
		    upload = (Button) findViewById(R.id.upload);
		    upload.setOnClickListener(new OnClickListener(){
	
				@Override
				public void onClick(View arg0) {
					Intent uploadIntent = new Intent(getApplicationContext(), FileChooserActivity.class);
					uploadIntent.setType(Phone.CONTENT_TYPE);
					startActivityForResult(uploadIntent, REQUEST_CHOOSER);
				}
		    	
		    });
		}
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			return true;
		}
		return super.onOptionsItemSelected(item);
	}

	//Method for adding user in listview
	public void addUser(String someuser){
		if (!list.contains(new String(someuser)))
			runOnUiThread(new myRunnable(someuser));
    }
    class myRunnable implements Runnable{
    	String someuser;
    	public myRunnable(String someuser){
    		this.someuser = someuser;
    	}
    	public void run(){
    		Log.d("cloudletXdebug","before adapter add");
    		Log.d("cloudletXdebug",someuser);
    		adapter.add(someuser);
    		Log.d("cloudletXdebug","after adapter add");
    	}
    }
    
	@Override
	public void connectionLost(Throwable arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		Log.d("cloudletXdebug", "3. recieved msg on channel "+arg0);
		Log.d("cloudletXdebug", "client/serviceuserslist/"+protocol.name);
		if (arg0.equals("client/serviceuserslist/"+protocol.name)){
			Log.d("cloudletXdebug", "adding the user");
			addUser(new String(arg1.getPayload()));
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		// TODO Auto-generated method stub
		
	}
	/*
	 * Custom adapter for list of services
	 */
	public class UserAdapter extends ArrayAdapter<String> {
		private Context context;

		public UserAdapter(Context context, int textviewRId) {
			super(context, textviewRId);
			this.context = context;
		}

		public UserAdapter(Context context, int resource, List<String> items) {
			super(context, resource, items);
			this.context = context;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			LayoutInflater inflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			View customv = inflater.inflate(R.layout.user, parent, false);

			String user = getItem(position);
			if (user != null) {
				TextView name = (TextView) customv.findViewById(R.id.usernameXfield);
				name.setText(user);
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
	
//	private void initialiseSync()
//	{
//		//Set the schedule function and rate
//		timer.scheduleAtFixedRate(new TimerTask() {
//
//		    @Override
//		    public void run() {
//		        //Called each time when 10000 milliseconds (10 seconds) (the period parameter)
//		    	new Thread()
//				{
//					public void run()
//					{
//						filesharing.sync();
//					}
//				}.start();
//		    }
//
//		},
//		//Set how long before to start calling the TimerTask (in milliseconds)
//		0,
//		//Set the amount of time between each execution (in milliseconds)
//		10000);
//	}
	
	/*
	 * Method to automatically syncronise the items on the list.
	 */
//	private void initialiseSync()
//	{
//		timerTask = new TimerTask() 
//		{
//			@Override
//			public void run() 
//			{
//				new Thread()
//				{
//					public void run()
//					{
//						filesharing.sync();
//					}
//				}.start();
//			}
//		};
//	}
	
//	Runnable syncStatusChecker = new Runnable() 
//	{
//	    @Override 
//	    public void run() {
//		    updateStatus(); //this function can change value of syncInterval.
//		    syncHandler.postDelayed(syncStatusChecker, syncInterval);
//	    }
//	};
//
//	void startAutoSync() 
//	{
//		syncStatusChecker.run(); 
//	}
//	
//	void stopAutoSync() 
//	{
//		syncHandler.removeCallbacks(syncStatusChecker);
//	}
}
