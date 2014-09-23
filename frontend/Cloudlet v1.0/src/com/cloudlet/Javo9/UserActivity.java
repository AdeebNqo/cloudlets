package com.cloudlet.Javo9;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.MenuItem;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import com.example.cloudlet.R;

public class UserActivity extends Activity implements CProtocolInterface 
{
	CProtocol protocol = null;
	ArrayList<String> list = new ArrayList<String>();
	ListView userlist = null;
	StableArrayAdapter adapter = null;
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_user);
		userlist = (ListView) findViewById(R.id.userlist);
	    adapter = new StableArrayAdapter(getBaseContext(), R.layout.user, list);
	    protocol = CProtocol.getCProtocol();
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
		runOnUiThread(new myRunnable(someuser));
    }
    class myRunnable implements Runnable{
    	String someuser;
    	public myRunnable(String someuser){
    		this.someuser = someuser;
    	}
    	public void run(){
    		adapter.add(someuser);
    	}
    }
    
	@Override
	public void connectionLost(Throwable arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void messageArrived(String arg0, MqttMessage arg1) throws Exception {
		if (arg0.equals("client/serviceuserslist/"+protocol.name)){
			addUser(new String(arg1.getPayload()));
		}
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken arg0) {
		// TODO Auto-generated method stub
		
	}
	

	  private class StableArrayAdapter extends ArrayAdapter<String> {

	    HashMap<String, Integer> mIdMap = new HashMap<String, Integer>();

	    public StableArrayAdapter(Context context, int textViewResourceId,
	        List<String> objects) {
	      super(context, textViewResourceId, objects);
	      for (int i = 0; i < objects.size(); ++i) {
	        mIdMap.put(objects.get(i), i);
	      }
	    }

	    @Override
	    public long getItemId(int position) {
	      String item = getItem(position);
	      return mIdMap.get(item);
	    }

	    @Override
	    public boolean hasStableIds() {
	      return true;
	    }

	  }
}
