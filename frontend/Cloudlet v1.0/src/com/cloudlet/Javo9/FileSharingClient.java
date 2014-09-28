/*
 * Class to handle file sharing service on the client side.
 * Jarvis Mutakha (MTKJAR001).
 * September 2014.
 */

package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;

import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

public class FileSharingClient {
	private Socket s;
	private String username;
	private String recvdata;
	private static FileSharingClient instance = null;

	DataOutputStream dos;
	DataInputStream dis;

	JSONObject files = null;
	
	public FileSharingClient(String username, String ip, int port) {
		try {
			Log.d("cloudletXdebug", "socket creating");
			s = new Socket(ip, port);
			Log.d("cloudletXdebug", "socket created");
			dos = new DataOutputStream(s.getOutputStream());
			dis = new DataInputStream(s.getInputStream());
			// to-do: print who client is connecting to.
			this.username = username;
			Log.d("cloudletXdebug", "filesharing: identifying");
			this.identify();
			Log.d("cloudletXdebug", "filesharing: done identifying");
			this.recvdata = "";
		} catch (UnknownHostException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		files = getaccessiblefiles(username);
		Log.d("cloudletXdebug", files.toString());
	}

	public static FileSharingClient getFileSharingClient() {
		return instance;
	}

	public static FileSharingClient getFileSharingClient(String username,
			String ip, int port) {
		if (instance == null) {
			instance = new FileSharingClient(username, ip, port);
			return instance;
		}
		return instance;
	}
	
	public void sync(){
		files = getaccessiblefiles(username);
	}

	/*
	 * Accessors.
	 */
	public String getUsername()
	{
		return username;
	}
	
	/*
	 * Method for determining if client is connected
	 */
	public boolean isConnected() {
		try {
			return heartbeat();
		} catch (Exception e) {
			return false;
		}
	}

	/*
	 * Method to id.
	 */
	public void identify() {
		String sendString = "{\"action\":\"identify\", \"username\":\""
				+ username + "\"}";
		Log.d("cloudletXdebug", "sending "+sendString);
		this.send(sendString);
	}

	/*
	 * Method to upload.
	 */
	public JSONObject upload(String duration, String access, String accessList,
		String compression, String filename, String owner, String objectData) 
	{
		String sendString = "{\"action\":\"upload\", \"duration\":\"" + duration
				+ "\", \"access\":\"" + access + "\", \"accesslist\":\""
				+ accessList + "\",\"compression\":\"" + compression
				+ "\", \"filename\":\"" + filename + "\", \"owner\":\""
				+ owner + "\", \"objectdata\":\"" + objectData + "\"}";
		Log.d("cloudletXdebug", objectData);
		Log.d("cloudletXdebug", sendString);
		this.send(sendString);
		
		return this.recv();
	}
	/*
	 * Method for retrieving accessible files
	 */
	public JSONObject getaccessiblefiles(String name){
		String jsonstring = "{\"action\":\"getfiles\", \"requester\":\""+name+"\"}";
		send(jsonstring);
		
		return this.recv();
	}
	/*
	 * Method to remove shared files on the cloudlet.
	 */
	public void remove(String owner, String filename) {
		String sendString = "{\"action\":\"remove\", \"owner\":\"" + owner
				+ "\", \"filename\":\"" + filename + "\"}";
		this.send(sendString);
		recv();
	}

	/*
	 * Method to download files from the cloudlet.
	 */
	public JSONObject download(String owner, String requester, String filename) {
		String sendString = "{\"owner\":\"" + owner + "\", \"requester\":\""
				+ requester + "\", \"filename\":\"" + filename + "\"}";

		this.send(sendString);
		
		return this.recv();
	}

	/*
	 * Method to check connection to the cloudlet.
	 */
	public boolean heartbeat() {
		// print 'heartbeat'
		String sendString = "{\"action\":\"heartbeat\"}";
		this.send(sendString);

		JSONObject response = this.recv();
		try {
			if (response.getString("status").equalsIgnoreCase("OK")) {
				return true;
			}
		} catch (JSONException e) {
			e.printStackTrace();
		}
		return false;
	}

	/*
	 * Method to send file to the cloudlet.
	 */
	public void transfer(String owner, String receiver, String oncloudlet,
		String filename, String objectData) {
		String sendString = "{\"action\":\"transfer\", \"owner\":\"" + owner
				+ "\", \"receiver\":\"" + receiver + "\", \"oncloudlet\":\""
				+ oncloudlet + "\", \"filename\":\"" + filename
				+ "\", \"objectdata\":\"" + objectData + "\"}";
		this.send(sendString);
		recv();
	}
	/*
	 * Method to send data.
	 */
	public void send(String data) {
		try {
			Log.d("cloudletXdebug", "DATA.LENGTH: "+data.length());
			dos.writeBytes(data.length() + "");
			byte[] ok = new byte[2];
			dis.read(ok);
			String response = new String(ok);
			if (response.equals("OK")) {
				dos.writeBytes(data);
				dos.flush();
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/*
	 * Method to receive data.
	 */
	public JSONObject recv() {
		int length = -1;
		try{
			Log.d("cloudletXdebug","attempting to read");
			String lengthX = "";
			byte[] size = new byte[dis.available()];
			while (true){
				dis.read(size);
				String tmp = new String(size);
				lengthX += tmp;
				if (lengthX!=""){
					length = Integer.parseInt(lengthX);
					break;
				}
				size = new byte[dis.available()];
			}
			Log.d("cloudletXdebug","expecting "+length+" bytes");
			
			//sending ok response
			dos.write("OK".getBytes());
			//reading data
			int recvsize = 0; //received bytes
			String data = "";
			while (recvsize < length){
				int available = dis.available();
				recvsize += available;
				byte[] aval = new byte[available];
				dis.read(aval);
				data += new String(aval);
				Log.d("cloudletXdebug", "received "+recvsize+" bytes at this point");
			}
			Log.d("cloudletXdebug","received "+data);
			JSONObject obj = new JSONObject(data);
			return obj;
		}catch(Exception e){
			e.printStackTrace();
		}
		return null;
	}
}
