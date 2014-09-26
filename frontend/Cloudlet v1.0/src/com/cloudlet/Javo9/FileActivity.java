package com.cloudlet.Javo9;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.AdapterView.OnItemClickListener;

import com.example.cloudlet.R;

public class FileActivity extends Activity 
{
	ListView fileListView = null;
	ArrayList<String> container = null;
	FileAdapter adapter = null;
	
	FileSharingClient filesharingclient = null;
	CProtocol protocol = null;
	
	private boolean alreadyCreated = false;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		if (!isCreated())
		{
			alreadyCreated = true;
			super.onCreate(savedInstanceState);
			setContentView(R.layout.activity_file_list);
			
			fileListView = (ListView)findViewById(R.id.filelistX);
			container = new ArrayList<String>();
			adapter = new FileAdapter(getApplicationContext(), R.layout.file, container);
			fileListView.setAdapter(adapter);
			
			Log.d("cloudletXdebug","unpacking intent");
			Intent intent = getIntent();
			String owner = intent.getStringExtra("owner");
			filesharingclient = FileSharingClient.getFileSharingClient();
			protocol = CProtocol.getCProtocol();
			Log.d("cloudletXdebug","owner is not mobile phone");
			try
			{
				JSONArray array = filesharingclient.files.getJSONArray("files");
				int size = array.length();
				for (int i=0; i<size; ++i)
				{
					 JSONObject obj = array.getJSONObject(i);	
					 String objowner = (String) obj.get("owner");
					 Log.d("cloudletXdebug","looking at file owned by "+objowner);
					 Log.d("cloudletXdebug","file owner: "+objowner+", chosen user: "+owner);
					 if (objowner.equals(owner))
					 {
						 Log.d("cloudletXdebug","adding file to list");
						 addFile(obj.toString());
					 }
				}
			}
			catch(Exception e)
			{
				e.printStackTrace();
			}
			
			fileListView.setOnItemClickListener(new OnItemClickListener()
		    {
				@Override
				public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
						long arg3) 
				{
					// If file name is selected download the file.
					String fileName = 
					Object chosenFile = fileListView.getItemAtPosition(arg2);
					String c = (String)chosenFile;
					filesharingclient.download(c, protocol.name, filename)
				}
		    });
		}
	}
	
	/*
	 * Method to add file name to the screen.
	 */
	public void addFile(String file){
		runOnUiThread(new myRunnable(file));
    }
    class myRunnable implements Runnable{
    	String file;
    	public myRunnable(String file){
    		this.file = file;
    	}
    	public void run(){
    		Log.d("cloudletXdebug","before adapter add");
    		Log.d("cloudletXdebug",file);
    		//adapter.add(someuser);
    		container.add(file);
    		adapter.notifyDataSetChanged();
    		Log.d("cloudletXdebug","after adapter add");
    	}
    }
    
	/*
	 * Custom adapter for list of files.
	 */
	public class FileAdapter extends ArrayAdapter<String> {
		private Context context;

		public FileAdapter(Context context, int textviewRId) {
			super(context, textviewRId);
			this.context = context;
		}

		public FileAdapter(Context context, int resource, List<String> items) {
			super(context, resource, items);
			this.context = context;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			LayoutInflater inflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			View customv = inflater.inflate(R.layout.file, parent, false);

			String user = getItem(position);
			Log.d("cloudletXdebug","from inside adapater, user is "+user);
			if (user != null) {
				TextView filename = (TextView) customv.findViewById(R.id.textView1);
				filename.setText(user);
			}
			return customv;
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
	
	/*
	 * Method to check if this activity was created before within this session.
	 */
	private boolean isCreated()
	{
		return alreadyCreated;
	}
}
