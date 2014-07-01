package com.cloudlet.installer;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Scanner;

public class NetworkInstaller {
	
	//variables to start and stop the network
	public static int START = 0;
	public static int STOP = 1;
	
	//network credentials
	private String networkname;
	private String networkpassword;
		
	public NetworkInstaller(){
		
	}
	
	/*

	Method for setting name and password of network

	*/
	public void setCredentials(String name, String password) throws IOException{
		System.err.println("FUNCTION: Setting credentials");

		//writing in hostapd main config
		System.err.println("editing /etc/hostapd/hostapd.conf");
		FileOutputStream config = new FileOutputStream("/etc/hostapd/hostapd.conf",false);
		config.write("interface=wlan1\n".getBytes());
		config.write("driver=nl80211\n".getBytes());
		config.write(("ssid="+name+"\n").getBytes());
		config.write("hw_mode=g\n".getBytes());
		config.write("channel=1\n".getBytes());
		/*config.write("macaddr_acl=0\n".getBytes());
		config.write("auth_algs=1\n".getBytes());
		config.write("ignore_broadcast_ssid=0\n".getBytes());
		config.write("wpa=1\n".getBytes());
		config.write(("wpa_passphrase="+password+"\n").getBytes());
		config.write("wpa_key_mgmt=WPA-PSK\n".getBytes());
		config.write("wpa_pairwise=TKIP\n".getBytes());
		config.write("rsn_pairwise=CCMP\n".getBytes());*/
		config.close();
	
		//reading in hostapd conf manager
		System.err.println("editing /etc/default/hostapd");
		FileOutputStream config1 = new FileOutputStream("/etc/default/hostapd",false);
		InputStream i = getClass().getResourceAsStream("/hostapd_manager");
		Scanner hostapdpackagedconfig = new Scanner(i);
		while(hostapdpackagedconfig.hasNextLine()){
			config1.write((hostapdpackagedconfig.nextLine()+"\n").getBytes());
		}
		config1.close();
		hostapdpackagedconfig.close();

		//reading in dhcp-server conf manager
		System.err.println("editing /etc/default/isc-dhcp-server");
		FileOutputStream config2 = new FileOutputStream("/etc/default/isc-dhcp-server",false);
		Scanner dhcppackagedconfig = new Scanner(getClass().getResourceAsStream("/dhcpserver_manager"));
		while(dhcppackagedconfig.hasNextLine()){
			config2.write((dhcppackagedconfig.nextLine()+"\n").getBytes());
		}
		config2.close();
		dhcppackagedconfig.close();


		//writing in main dhcp-server conf
		System.err.println("editing /etc/dhcp/dhcpd.conf");
		FileOutputStream config3 = new FileOutputStream("/etc/dhcp/dhcpd.conf",false);
		Scanner dhcppackagedconfig2 = new Scanner(getClass().getResourceAsStream("/dhcpserver_config"));
		while(dhcppackagedconfig2.hasNextLine()){
			config3.write((dhcppackagedconfig2.nextLine()+"\n").getBytes());
		}
		config3.close();
		dhcppackagedconfig2.close();

		Scanner interfacesconfig = new Scanner(new File("/etc/network/interfaces"));
		boolean exist = false; //var to determine if following lines exist in config file
		String one = "auto wlan1"; 
		String two = "iface wlan1 inet dhcp";
		String currline = interfacesconfig.nextLine();
		String nextline = interfacesconfig.nextLine();
		
		while(true){
			System.err.println("currline: "+currline);
			System.err.println("nextline: "+nextline);
			if (currline.equals(one) && nextline.equals(two)){
				exist = true;
				System.err.println("status: exist");
				break;
			}else{
				if (interfacesconfig.hasNextLine()){
					currline = nextline;
					nextline = interfacesconfig.nextLine();
					System.err.println("status: does not exist");
				}
				else{
					break;
				}
			}
			System.err.println("\n--\t--");
		}
		interfacesconfig.close();
		if (!exist){
			FileOutputStream config4 = new FileOutputStream("/etc/network/interfaces",true);
			config4.write((one+'\n').getBytes());
			config4.write((two+'\n').getBytes());
		}
		System.err.println("Done.");
	}
	/*

	Method for retrieving password and password

	*/
	private void retreiveCredentials() throws FileNotFoundException{
		Scanner config = new Scanner(new File("/etc/hostapd/hostapd.conf"));
		while(config.hasNextLine()){
			String line = config.nextLine();
			if (line.startsWith("ssid")){
				String[] vals = line.split("=");
				networkname = vals[1];
			}else if (line.startsWith("wpa_passphrase")){
				String[] vals = line.split("=");
				networkpassword = vals[1];
			}
		}
		config.close();
	}
	
	/*

	Method for getting password

	*/
	public String getPassword() throws FileNotFoundException{
		if (networkpassword!=null && networkpassword.equals("\\s+")){
			retreiveCredentials();
		}
		return networkpassword;
	}
	/*
	
	Method for getting network name

	*/
	public String getNetworkName() throws FileNotFoundException{
		if (networkname!=null && networkname.equals("\\s+")){
			retreiveCredentials();
		}
		return networkname;
	}
	/*

	Method for changing network status
	
	*/
	public boolean setStatus(int status) throws IOException,MissingApplicationException{
		if (status==NetworkInstaller.START){
			System.err.println("Starting network...");
		}
		else{
			System.err.println("Stopping network...");
		}


		String stringstatus = (status==NetworkInstaller.START) ? "start" : "stop";

		//checking if isc-dhcp-server and hostapd are installed
		boolean hostapdinstallstatus = isInstalled("hostapd");
		boolean dhcpinstallstatus = isInstalled("isc-dhcp-server");
		if (hostapdinstallstatus && dhcpinstallstatus){
			/*
			Starting/Stopping services
			*/
			InputStream[] dhcpresponse = run("sudo service isc-dhcp-server "+stringstatus);
			InputStream[] hostapdresponse = run("sudo service hostapd "+stringstatus);
			System.err.println("--dhcp server--");
			for (InputStream in: dhcpresponse){
				byte[] bytes = new byte[1024];
				while((in.read(bytes))!=-1){
					String r = new String(bytes,"UTF-8");
					System.err.println(r);
					if (r.startsWith("start: Job is already running:")){
						run("sudo service isc-dhcp-server restart");
					}
					
				}
			}
			System.err.println("--hostapd--");
			for (InputStream in: hostapdresponse){
				byte[] bytes = new byte[1024];
				while((in.read(bytes))!=-1){
					String r = new String(bytes,"UTF-8");
					System.err.println(r);
					if (r.startsWith("start: Job is already running:")){
						run("sudo service hostapd restart");
					}
				}
			}
			return true; //ToDo: check if starting was successful.
		}
		else{
			System.err.println("hostapd and isc-dhcp-server are not installed.");
			throw new MissingApplicationException("Missing application: hostapd and/or isc-dhcp-server");
		}
	}
	/*
	
	Method for checking if application is installed

	*/
	public boolean isInstalled(String appname) throws IOException{
		InputStream[] response = run("apt-cache policy "+appname);
		Scanner input = new Scanner(response[0]);
		input.nextLine();
		String installedLine = input.nextLine();
		input.close();
		if (installedLine.endsWith(" (none)")){
			return false;
		}
		return true;
	}
	/*
	
	Method for running unix command
	@return Outpout and Error streams, respectively.
	*/
	private InputStream[] run(String cmd) throws IOException{
		ProcessBuilder procBuilder = new ProcessBuilder(cmd.split("\\s+"));
		Process proc = procBuilder.start();
		//Output of the cmd
		InputStream out = proc.getInputStream();
		//Errors of the cmd
		InputStream in = proc.getErrorStream();
		InputStream[] streams = {out, in};
		return streams;			
	}

	/*

	Exception for indicating that there's an application that
	is supposed to be installed but is missing.

	*/
	public class MissingApplicationException extends Exception{
		private static final long serialVersionUID = 1L;
		public MissingApplicationException(String msg){
			super(msg);
		}
		public MissingApplicationException(String message, Throwable throwable) {
			super(message, throwable);
		}
	}
}
