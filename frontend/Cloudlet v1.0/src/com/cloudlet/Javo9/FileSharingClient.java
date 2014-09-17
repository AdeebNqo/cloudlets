package com.cloudlet.Javo9;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.UnknownHostException;

public class FileSharingClient 
{
	private Socket s;
	private String username;
	private String recvdata;
	
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
	
	public void identify()
	{
		String sendString = "{\"action\":\"identify\", \"username\":\"" + username + "\"}";
		this.send(sendString);
	}
	
	public void upload(String duration, String access, String accessList,  String compression, String filename, String owner, String objectData)
	{
		if (accessList == null)
		{
			accessList = "";
			String sendString = "{\"duration\":\""+duration+"\", \"access\":\""+access+"\", \"accesslist\":"+accessList+",\"compression\":\""+compression+"\", \"filename\":\""+filename+"\", \"owner\":\""+owner+"\", \"objectdata\":\""+objectData+"\"}";
			this.send(sendString);
		}
	}
	
	public void remove(String owner, String filename)
	{
		String sendString = "{\"action\":\"remove\", \"owner\":\""+owner+"\", \"filename\":\""+filename+"\"}";
		this.send(sendString);
	}
	
	public void download(String owner, String requester, String filename)
	{
		String sendString = "{\"owner\":\""+owner+"\", \"requester\":\""+requester+"\", \"filename\":\""+filename+"\"}";
		this.send(sendString);
		// json obj from recv()
	}
	
	public void heartbeat()
	{
		// print 'heartbeat'
		String sendString = "{\"action\":\"heartbeat\"}";
		this.send(sendString);
		// response from recv()
		
	}
	
	public void transfer(String owner, String receiver, String oncloudlet, String filename, String objectData)
	{
		// print 'transfer'
		String sendString = "{\"action\":\"transfer\", \"owner\":\""+owner+"\", \"receiver\":\""+receiver+"\", \"oncloudlet\":\""+oncloudlet+"\", \"filename\":\""+filename+"\", \"objectdata\":\""+objectData+"\"}";
		this.send(sendString);
	}
	
	public void send(String str)
	{
		String length = str.length() + "";
		try 
		{
			DataOutputStream dos = new DataOutputStream(s.getOutputStream());
			dos.writeUTF(length);
			
			DataInputStream dis = new DataInputStream(s.getInputStream());
			String response = dis.readUTF();
			if (response == "OK")
			{
				dos.writeUTF(str);
			}
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
	}
	
	public void recv()
	{
		try 
		{
			DataInputStream dis = new DataInputStream(s.getInputStream());
			int length = dis.readInt();
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
	}
}
