package com.cloudlet.Javo9;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import android.webkit.MimeTypeMap;

import com.example.cloudlet.R;

public class FileViewActivity extends Activity
{
	 private static final String TAG = "FileChooserExampleActivity";
	 private static final int REQUEST_CODE = 6384; // onActivityResult request code
	 
	 FileSharingClient filesharing = null;
	 
	 @Override
	 public void onCreate(Bundle savedInstanceState) {
		 super.onCreate(savedInstanceState);
		 // Create a simple button to start the file chooser process
		 Button button = new Button(this);
		 button.setText(R.string.choose_file);
		 button.setOnClickListener(new OnClickListener() {
			 @Override
			 public void onClick(View v) {
				 // Display the file chooser dialog
				 showChooser();
			 }
			 });
		 setContentView(button);
		 filesharing = FileSharingClient.getFileSharingClient();
	 }
	 
	 private void showChooser() {
		// Use the GET_CONTENT intent from the utility class
		Intent target = FileUtils.createGetContentIntent();
		// Create the chooser Intent
		Intent intent = Intent.createChooser(target, getString(R.string.chooser_title));
		try {
		startActivityForResult(intent, REQUEST_CODE);
		} catch (ActivityNotFoundException e) {
			// The reason for the existence of aFileChooser
		}
	} 
	 
	 @Override
	 protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		 switch (requestCode) {
			 case REQUEST_CODE:
				 // If the file selection was successful
				 if (resultCode == RESULT_OK) {
					 if (data != null) {
						 // Get the URI of the selected file
						 final Uri uri = data.getData();
						 Log.d("cloudletXdebug", "Uri = " + uri.toString());
						 try {
							 // Get the file path from the URI
							 final String path = FileUtils.getPath(this, uri);
//							 Toast.makeText(FileViewActivity.this,
//							 "File Selected: " + path, Toast.LENGTH_LONG).show();
							 // Alternatively, use FileUtils.getFile(Context, Uri)
				             if (path != null && FileUtils.isLocal(path)) {
				            	 final File file = new File(path);
//				            	 byte[] b = new byte[(int) file.length()];
//				                 try 
//				                 {
//				                       FileInputStream fis = new FileInputStream(file);
//				                       fis.read(b);
//				                  } catch (FileNotFoundException e) {
//				                	  Log.d("cloudletXdebug", "File Not Found.");
//				                	  fileUploadCheck = false;
//				                	  e.printStackTrace();
//				                  }
//				                  catch (IOException e1) {
//				                	  Log.d("cloudletXdebug", "Error Reading The File.");
//				                	  fileUploadCheck = false;
//				                	  e1.printStackTrace();
//				                  }
//				                 byte[] encodedByteArray = Base64.encode(b, Base64.NO_WRAP);
//				                 final String encodedDataStr = new String(encodedByteArray);
				                 
				                 Intent myIntent = new Intent(android.content.Intent.ACTION_VIEW);
//				                 File file = new File(aFile.getAbsolutePath());
				                 String extension = android.webkit.MimeTypeMap.getFileExtensionFromUrl(Uri.fromFile(file).toString());
				                 String mimetype = android.webkit.MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension);
				                 myIntent.setDataAndType(Uri.fromFile(file),mimetype);
				                 startActivity(myIntent);
				                 
//				                 new Thread()
//				                 {
//				                	 public void run()
//				                	 {
//				                		 JSONObject uploadResponseObj = filesharing.upload("1h", "public", "None", "0", file.getName(), filesharing.getUsername(), encodedDataStr);
//				                		 Log.d("cloudletXdebug", "JSONOBJ: "+uploadResponseObj.toString());
//				                	 }
//				                 }.start();
				             }
						 } catch (Exception e) {
							 Log.e("FileSelectorTestActivity", "File select error", e);
						 }
					 }
				 }
				 break;
		 }
		 super.onActivityResult(requestCode, resultCode, data);
	 }
}
