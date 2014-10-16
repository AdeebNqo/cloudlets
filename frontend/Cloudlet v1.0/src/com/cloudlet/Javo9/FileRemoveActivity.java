package com.cloudlet.Javo9;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.cloudlet.Javo9.FileDownloadActivity.FileAdapter;
import com.cloudlet.Javo9.FileDownloadActivity.myRunnable;
import com.example.cloudlet.R;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.AdapterView.OnItemClickListener;

public class FileRemoveActivity extends Activity 
{
	ListView fileListView = null;
	ArrayList<String> container = null;
	FileAdapter adapter = null;
	
	FileSharingClient filesharingclient = null;
	CProtocol protocol = null;

	private boolean fileRemoveCheck = true; // Check to see if file was removed from cloudlet without problems.
	
	private ProgressBar spinner;
	private int progressStatus = 0;
	
//	private boolean alreadyCreated = false;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
//		if (!isCreated())
//		{
			super.onCreate(savedInstanceState);
			setContentView(R.layout.activity_file_list);
			setTitle("Tap a file to remove it");
			fileListView = (ListView)findViewById(R.id.filelistX);
			container = new ArrayList<String>();
			adapter = new FileAdapter(getApplicationContext(), R.layout.file, container);
			fileListView.setAdapter(adapter);
			
//			spinner = (ProgressBar)findViewById(R.id.progressBar1);
//			new Thread(new Runnable() 
//			{
//				public void run() 
//				{
//					while (progressStatus < 100) 
//					{
//						progressStatus += 1;
//						// Update the progress bar and display the 
//
//			    /current value in the text view
//			    handler.post(new Runnable() {
//			    public void run() {
//			       progressBar.setProgress(progressStatus);
//			       textView.setText(progressStatus+"/"+progressBar.getMax());
//			    }
//			        });
//			        try {
//			           // Sleep for 200 milliseconds. 
//
//			                         //Just to display the progress slowly
//			           Thread.sleep(200);
//			        } catch (InterruptedException e) {
//			           e.printStackTrace();
//			        }
//			     }
//			  }
//			  }).start();
//			 }
//			if (spinner != null)
//			{
//				spinner.setVisibility(View.GONE);
//			}
			
			Log.d("cloudletXdebug","unpacking intent");
			Intent intent = getIntent();
			String owner = intent.getStringExtra("owner");
			filesharingclient = FileSharingClient.getFileSharingClient();
			protocol = CProtocol.getCProtocol();
			try
			{
				JSONArray array = filesharingclient.files.getJSONArray("files");
				int size = array.length();
				Log.d("cloudletXdebug","found "+size+" files");
				for (int i=0; i<size; ++i)
				{
					 JSONObject obj = array.getJSONObject(i);	
					 String objowner = (String) obj.get("owner");
					 String objFileName = (String) obj.get("filename");
//					 Log.d("cloudletXdebug", "*FILENAME: " + objFileName);
					 Log.d("cloudletXdebug","looking at file owned by "+objowner);
					 Log.d("cloudletXdebug","file owner: "+objowner+", chosen user: "+owner);
//					 if (objowner.equals(owner))
					 {
						 Log.d("cloudletXdebug","adding file to list");
//						 addFile(obj.toString());
						 addFile(objFileName + "|" + objowner + "|" + obj.toString());
					 }
				}
			}
			catch(Exception e)
			{
				e.printStackTrace();
			}
//			alreadyCreated = true;
			fileListView.setOnItemClickListener(new OnItemClickListener()
		    {
				@Override
				public void onItemClick(AdapterView<?> parent, View view, final int position,
						long id) 
				{
					// If file name is selected download the file.
					Object chosenFile = fileListView.getItemAtPosition(position);
					String temp = (String)chosenFile;
					final String filename = temp.split("\\|")[0];
					final String c = temp.split("\\|")[2];
					Log.d("cloudletXdebug", "CSTR: "+c);
					
					final JSONObject jsonObjInput;
					try 
					{
						jsonObjInput = new JSONObject(c);
						
						if (protocol.name.equals(jsonObjInput.getString("owner")))
						{
							filesharingclient.addPosition(position);
							container.remove(position);
			                adapter.notifyDataSetChanged();
			                
							new Thread()
							{
								public void run()
								{
									filesharingclient.remove(protocol.name, filename);
								}
							}.start();
						}
						else
						{
							Toast.makeText(getApplicationContext(), "You are not the file uploader!",Toast.LENGTH_LONG).show();
							fileRemoveCheck = false;
						}
					} 
					catch (JSONException e) 
					{
						fileRemoveCheck = false;
						e.printStackTrace();
					}
					
//					spinner.setVisibility(View.VISIBLE);
//					long startTime = SystemClock.currentThreadTimeMillis();
//					long endTime = startTime + 3000; // Wait for 3 secs.
//					while (SystemClock.currentThreadTimeMillis() < endTime)
//					{
//						// Do nothing...
//					}
//					spinner.setVisibility(View.GONE);
					
					if (fileRemoveCheck)
					{
						Toast.makeText(getApplicationContext(), "File removedl!",Toast.LENGTH_LONG).show();
					}
					else
					{
						Toast.makeText(getApplicationContext(), "Cannot remove file!",Toast.LENGTH_LONG).show();
					}
				}
		    });
//		}
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
    		Log.d("cloudletXdebug","before adapter add" + file);
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

			String[] file = getItem(position).split("\\|");
			Log.d("cloudletXdebug","from inside adapater, user is "+file[0]);
			if (file != null) {
				TextView filename = (TextView) customv.findViewById(R.id.textView1);
				filename.setTextColor(Color.BLACK);
				filename.setText(file[0]);
				
				TextView owner = (TextView) customv.findViewById(R.id.owner);
				owner.setText("Uploaded by "+file[1]);
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
}
