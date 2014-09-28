package com.cloudlet.Javo9;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

import org.json.JSONObject;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.Toast;

import com.example.cloudlet.R;

public class FileChooserActivity extends Activity {
	 private static final String TAG = "FileChooserExampleActivity";
	 private static final int REQUEST_CODE = 6384; // onActivityResult request code
	 
	 FileSharingClient filesharing = null;
	 
	 private boolean fileUploadCheck = true; // Check to see if upload completes without problems.
	 
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
							 Toast.makeText(FileChooserActivity.this,
							 "File Selected: " + path, Toast.LENGTH_LONG).show();
							 // Alternatively, use FileUtils.getFile(Context, Uri)
				             if (path != null && FileUtils.isLocal(path)) {
				            	 final File file = new File(path);
				            	 byte[] b = new byte[(int) file.length()];
				                 try 
				                 {
				                       FileInputStream fis = new FileInputStream(file);
				                       fis.read(b);
				                  } catch (FileNotFoundException e) {
				                	  Log.d("cloudletXdebug", "File Not Found.");
				                	  fileUploadCheck = false;
				                	  e.printStackTrace();
				                  }
				                  catch (IOException e1) {
				                	  Log.d("cloudletXdebug", "Error Reading The File.");
				                	  fileUploadCheck = false;
				                	  e1.printStackTrace();
				                  }
				                 byte[] encodedByteArray = Base64.encode(b, Base64.NO_WRAP);
				                 final String encodedDataStr = new String(encodedByteArray);
				                 new Thread()
				                 {
				                	 public void run()
				                	 {
				                		 JSONObject uploadResponseObj = filesharing.upload("1h", "public", "None", "0", file.getName(), filesharing.getUsername(), encodedDataStr);
				                		 Log.d("cloudletXdebug", "JSONOBJ: "+uploadResponseObj.toString());
				                	 }
				                 }.start();
				             }
						 } catch (Exception e) {
							 fileUploadCheck = false;
							 Log.e("FileSelectorTestActivity", "File select error", e);
						 }
						 
						 if (fileUploadCheck)
						 {
							 Toast.makeText(getApplicationContext(), "Upload successful!",Toast.LENGTH_LONG).show();
						 }
						 else
						 {
							 Toast.makeText(getApplicationContext(), "Upload failed!",Toast.LENGTH_LONG).show();
						 }
					 }
				 }
				 break;
		 }
		 super.onActivityResult(requestCode, resultCode, data);
	 }
}
