package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.net.Socket;
import java.util.LinkedList;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemLongClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import com.example.cloudlet.R;

public class FileListActivity extends Activity {

	private Socket socket = null;
	private DataOutputStream output = null;
	private DataInputStream input = null;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_file_list);

		socket = FileSharingDB.getInstance().getSocket();
		input = FileSharingDB.getInstance().getDataInputStream();
		output = FileSharingDB.getInstance().getDataOutputStream();
		
		//Intent intent = 
		LinkedList<String> items = new LinkedList<String>();
		Bundle extras = getIntent().getExtras();
		int numfiles = extras.getInt("numfiles");
		
		for (int i=0; i<numfiles; ++i){
			String file = extras.getString("file"+i);
			items.add(file);
			Log.d("Cloudlet", "added "+file);
		}
		final ListView lv = (ListView) findViewById(R.id.filelist);
		ArrayAdapter<String> arrayAdapter = new ArrayAdapter<String>(
                this,
                android.R.layout.simple_list_item_1,
                items );

        lv.setAdapter(arrayAdapter);
        lv.setOnItemLongClickListener(new OnItemLongClickListener(){

			@Override
			public boolean onItemLongClick(AdapterView<?> parent, View view,
					int position, long id) {
				String str=lv.getItemAtPosition(position).toString();
				String[] vals = str.split(" ");
				Toast.makeText(getApplicationContext(), vals[1], Toast.LENGTH_SHORT).show();
				Log.d("Cloudlet", "After toast");
				String[] pathsplit = vals[1].split("/");
				new FileDownloader().execute(vals[1], pathsplit[pathsplit.length-1]);
				Log.d("Cloudlet", "Started file downloader");
				return false;
			}
        });
	}

	class FileDownloader extends AsyncTask<String, Void, String>{
		String filename;
		@Override
		protected void onPostExecute(String result) {
			// TODO Auto-generated method stub
			super.onPostExecute(result);
			Toast.makeText(getApplicationContext(), filename+" downloaded.", Toast.LENGTH_LONG).show();
		}

		@Override
		protected String doInBackground(String... params) {
			try {
				Log.d("Cloudlet", "attempting to download file");
				String hash = params[0];
				filename = params[1];
				output.writeUTF("download "+hash);
				String dataresponse = input.readUTF();
				output.writeUTF("OK");
				double filesize = Double.parseDouble(dataresponse.split(" ")[1]);
				byte[] data = new byte[(int) Math.ceil(filesize)];
				input.readFully(data, 0, (int) Math.floor(filesize));
				Log.d("Cloudlet", "Before writing to file");
				File file = new File(getApplicationContext().getFilesDir(), filename);
				FileOutputStream stream = new FileOutputStream(file);;
				stream.write(data);
				stream.close();
				Log.d("Cloudlet",getApplicationContext().getFilesDir().getAbsolutePath());
				Log.d("Cloudlet", "wrote to file");
				output.writeUTF("OK");

			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				return null;
			}
			return null;
		}
		
	}
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {

		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.file_list, menu);
		return true;
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

	/**
	 * A placeholder fragment containing a simple view.
	 */
	public static class PlaceholderFragment extends Fragment {

		public PlaceholderFragment() {
		}

		@Override
		public View onCreateView(LayoutInflater inflater, ViewGroup container,
				Bundle savedInstanceState) {
			View rootView = inflater.inflate(R.layout.fragment_file_list,
					container, false);
			return rootView;
		}
	}

}
