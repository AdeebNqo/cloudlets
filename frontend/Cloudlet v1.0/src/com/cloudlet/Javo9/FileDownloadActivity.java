package com.cloudlet.Javo9;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Environment;
import android.util.Base64;
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
import android.widget.Toast;

import com.example.cloudlet.R;

public class FileDownloadActivity extends Activity 
{
	ListView fileListView = null;
	ArrayList<String> container = null;
	FileAdapter adapter = null;
	
	FileSharingClient filesharingclient = null;
	CProtocol protocol = null;

	private boolean fileDownloadCheck = true; // Check to see if download completes without problems.
	
//	private boolean alreadyCreated = false;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
//		if (!isCreated())
//		{
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
			try
			{
				JSONArray array = filesharingclient.files.getJSONArray("files");
				int size = array.length();
				Log.d("cloudletXdebug","found "+size+" files");
				for (int i=0; i<size; ++i)
				{
					 JSONObject obj = array.getJSONObject(i);	
					 String objowner = (String) obj.get("owner");
					 Log.d("cloudletXdebug","looking at file owned by "+objowner);
					 Log.d("cloudletXdebug","file owner: "+objowner+", chosen user: "+owner);
//					 if (objowner.equals(owner))
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
//			alreadyCreated = true;
			fileListView.setOnItemClickListener(new OnItemClickListener()
		    {
				@Override
				public void onItemClick(AdapterView<?> parent, View view, int position,
						long id) 
				{
					// If file name is selected download the file.
					Object chosenFile = fileListView.getItemAtPosition(position);
					final String c = (String)chosenFile;
					Log.d("cloudletXdebug", "CSTR: "+c);
					final JSONObject jsonObjInput;
					try 
					{
						jsonObjInput = new JSONObject(c);
						new Thread()
						{
							public void run()
							{
								try 
								{
									JSONObject jsonObjOutput = filesharingclient.download(jsonObjInput.getString("owner"), protocol.name, jsonObjInput.getString("filename"));
									Log.d("cloudletXdebug", "DOWNLOAD: "+jsonObjOutput.toString());
									
									String encodedDataStr = jsonObjOutput.getString("objectdata");
									Log.d("cloudletXdebug", "FILENAME: "+jsonObjInput.getString("filename"));
									byte[] decodedByteArray = Base64.decode(encodedDataStr, Base64.NO_WRAP); // this is the file in a byte array.
									File fileDirectory = getAlbumStorageDir("Cloudlet Downloads");
									try 
									{
										writeFile(decodedByteArray, fileDirectory, jsonObjInput.getString("filename"));
									} 
									catch (IOException e) 
									{
										fileDownloadCheck = false;
										e.printStackTrace();
									}
								} 
								catch (JSONException e) 
								{
									fileDownloadCheck = false;
									e.printStackTrace();
								}
							}
						}.start();
					} 
					catch (JSONException e) 
					{
						fileDownloadCheck = false;
						e.printStackTrace();
					}
					
					if (fileDownloadCheck)
					{
						Toast.makeText(getApplicationContext(), "Download successful!",Toast.LENGTH_LONG).show();
					}
					else
					{
						Toast.makeText(getApplicationContext(), "Download failed!",Toast.LENGTH_LONG).show();
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

			String file = getItem(position);
			Log.d("cloudletXdebug","from inside adapater, user is "+file);
			if (file != null) {
				TextView filename = (TextView) customv.findViewById(R.id.textView1);
				filename.setTextColor(Color.BLACK);
				filename.setText(file);
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
	 * Method to write data onto a File object.
	 */
	public void writeFile(byte[] data, File fileDirectory, String fileName) throws IOException
	{
		File file = new File(fileDirectory.getPath(), fileName);
		FileOutputStream out = new FileOutputStream(file);
		out.write(data);
		out.close();
	}
	
	/*
	 * Method to get the storage directory of a picture file.
	 */
	public File getAlbumStorageDir(String albumName) {
	    // Get the directory for the user's public pictures directory. 
	    File file = new File(Environment.getExternalStoragePublicDirectory(
	            Environment.DIRECTORY_DOWNLOADS), albumName);
	    if (!file.mkdirs()) {
	        Log.d("cloudletXdebug", "Directory not created");
	    }
	    return file;
	}
	
	/* 
	 * Checks if external storage is available for read and write
	 */
	public boolean isExternalStorageWritable() {
	    String state = Environment.getExternalStorageState();
	    if (Environment.MEDIA_MOUNTED.equals(state)) {
	        return true;
	    }
	    return false;
	}

	/* 
	 * Checks if external storage is available to at least read 
	 */
	public boolean isExternalStorageReadable() {
	    String state = Environment.getExternalStorageState();
	    if (Environment.MEDIA_MOUNTED.equals(state) ||
	        Environment.MEDIA_MOUNTED_READ_ONLY.equals(state)) {
	        return true;
	    }
	    return false;
	}
	
	/*
	 * Method to check if this activity was created before within this session.
	 */
//	private boolean isCreated()
//	{
//		return alreadyCreated;
//	}
}
