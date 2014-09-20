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
import java.net.SocketAddress;
import java.net.UnknownHostException;
import org.json.*;

import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONStringer;

public class FileSharingClient 
{
	private Socket s;
	private String username;
	private String recvdata;
	private static FileSharingClient instance = null;
	
	public FileSharingClient(String username, String ip, int port)
	{
		try 
		{
			s = new Socket(ip, port);
			// to-do: print who client is connecting to.
			this.username = username;
			this.identify();
			this.recvdata = "";
		} 
		catch (UnknownHostException e) 
		{
			e.printStackTrace();
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
	}
	
	public static FileSharingClient getFileSharingClient(String username, String ip, int port)
	{
		if (instance==null)
		{
			instance = new FileSharingClient(username, ip, port);
			return instance;
		}
		return instance;
	}
	
	/*
	 * Method to id.
	 */
	public void identify()
	{
		String sendString = "{\"action\":\"identify\", \"username\":\"" + username + "\"}";
		JSONObject jsonObj = null;
		
		try 
		{
			jsonObj = new JSONObject(sendString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		this.send(jsonObj);
	}
	
	/*
	 * Method to upload.
	 */
	public void upload(String duration, String access, String accessList,  String compression, String filename, String owner, String objectData)
	{
		if (accessList == null)
		{
			accessList = "";
			String sendString = "{\"duration\":\""+duration+"\", \"access\":\""+access+"\", \"accesslist\":"+accessList+",\"compression\":\""+compression+"\", \"filename\":\""+filename+"\", \"owner\":\""+owner+"\", \"objectdata\":\""+objectData+"\"}";
			JSONObject jsonObj = null;
			
			try 
			{
				jsonObj = new JSONObject(sendString);
			} 
			catch (JSONException e) 
			{
				e.printStackTrace();
			}
			
			this.send(jsonObj);
		}
	}
	
	/*
	 * Method to remove shared files on the cloudlet.
	 */
	public void remove(String owner, String filename)
	{
		String sendString = "{\"action\":\"remove\", \"owner\":\""+owner+"\", \"filename\":\""+filename+"\"}";
		JSONObject jsonObj = null;
		
		try 
		{
			jsonObj = new JSONObject(sendString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		this.send(jsonObj);
	}
	
	/*
	 * Method to download files from the cloudlet.
	 */
	public void download(String owner, String requester, String filename)
	{
		String sendString = "{\"owner\":\""+owner+"\", \"requester\":\""+requester+"\", \"filename\":\""+filename+"\"}";
		JSONObject jsonObj = null;
		
		try 
		{
			jsonObj = new JSONObject(sendString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		this.send(jsonObj);
		JSONObject response = this.recv();
	}
	
	/*
	 * Method to check connection to the cloudlet.
	 */
	public void heartbeat()
	{
		// print 'heartbeat'
		String sendString = "{\"action\":\"heartbeat\"}";
		JSONObject jsonObj = null;
		
		try 
		{
			jsonObj = new JSONObject(sendString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		this.send(jsonObj);
		
		JSONObject response = this.recv();
		try 
		{
			if (response.getString("status").equalsIgnoreCase("OK"))
			{
				// Connecting broken.
				try 
				{
					s.close();
				} 
				catch (IOException e) 
				{
					e.printStackTrace();
				}
			}
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
	}
	
	/*
	 * Method to send file to the cloudlet.
	 */
	public void transfer(String owner, String receiver, String oncloudlet, String filename, String objectData)
	{
		// print 'transfer'
		String sendString = "{\"action\":\"transfer\", \"owner\":\""+owner+"\", \"receiver\":\""+receiver+"\", \"oncloudlet\":\""+oncloudlet+"\", \"filename\":\""+filename+"\", \"objectdata\":\""+objectData+"\"}";
		JSONObject jsonObj = null;
		
		try 
		{
			jsonObj = new JSONObject(sendString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		this.send(jsonObj);
	}
	
	/*
	 * Method to send data.
	 */
	public void send(JSONObject jsonObj)
	{
		String length = jsonObj.length() + "";
		try 
		{
			DataOutputStream dos = new DataOutputStream(s.getOutputStream());
			dos.writeUTF(length);
			
			DataInputStream dis = new DataInputStream(s.getInputStream());
			String response = dis.readUTF();
			if (response.equals("OK"))
			{
				String jsonStr = jsonObj.toString();
				dos.writeUTF(jsonStr);
			}
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
	}
	
	/*
	 * Method to receive data.
	 */
	public JSONObject recv()
	{
		JSONObject data = null;
		int length = 0;
		try 
		{
			DataInputStream dis = new DataInputStream(s.getInputStream());
			length = dis.readInt();
			
			DataOutputStream dos = new DataOutputStream(s.getOutputStream());
			dos.writeUTF("OK");
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
		
		String dataString = "";
		
		if (!recvdata.equals(""))
		{
			dataString += recvdata;
		}
		
		int recvsize = 0;
		
		while (recvsize < length)
		{
			try 
			{
				DataInputStream dis = new DataInputStream(s.getInputStream());
				dataString += dis.readUTF();
				
				if (dataString.length() != 0)
				{
					recvsize += dataString.length();
				}
			} 
			catch (IOException e) 
			{
				e.printStackTrace();
			}
		}
		
		dataString = dataString.substring(0, length);
		JSONObject jsonObj = null;
		try 
		{
			jsonObj = new JSONObject(dataString);
		} 
		catch (JSONException e) 
		{
			e.printStackTrace();
		}
		
		return jsonObj;
	}
}
