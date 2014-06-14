/*

Copyright 2014 Zola 'AdeebNqo' Mahlaza

This class is for managing the network.

http://www.gnu.org/licenses/gpl-3.0.txt

*/

import java.io.FileOutputStream;
import java.io.RandomAccessFile;
import java.util.Scanner;
import java.io.InputStream;
import java.io.File;
import java.io.IOException;
import java.io.FileNotFoundException;

public class NetworkManager{
	//variables to start and stop the network
	public static int START = 0;
	public static int STOP = 1;
		
	//network credentials
	private String networkname;
	private String networkpassword;

	public NetworkManager(){

	}
	/*

	Method for setting name and password of network

	*/
	public void setCredentials(String name, String password) throws IOException{
		System.err.println("Setting credentials");

		//writing in hostapd main config
		FileOutputStream config = new FileOutputStream("/etc/hostapd/hostapd.conf",false);
		config.write("interface=wlan0".getBytes());
		config.write("driver=nl80211".getBytes());
		config.write(("ssid="+name).getBytes());
		config.write("hw_mode=g".getBytes());
		config.write("channel=1".getBytes());
		config.write("macaddr_acl=0".getBytes());
		config.write("auth_algs=1".getBytes());
		config.write("ignore_broadcast_ssid=0".getBytes());
		config.write("wpa=3".getBytes());
		config.write(("wpa_passphrase="+password).getBytes());
		config.write("wpa_key_mgmt=WPA-PSK".getBytes());
		config.write("wpa_pairwise=TKIP".getBytes());
		config.write("rsn_pairwise=CCMP".getBytes());
		config.close();
	
		//reading in hostapd conf manager
		FileOutputStream config1 = new FileOutputStream("/etc/default/hostapd",false);
		Scanner hostapdpackagedconfig = new Scanner(new File(System.getProperty("user.dir")+"/config","hostapd_manager"));
		while(hostapdpackagedconfig.hasNextLine()){
			config1.write(hostapdpackagedconfig.nextLine().getBytes());
		}
		config1.close();

		//reading in dhcp-server conf manager
		FileOutputStream config2 = new FileOutputStream("/etc/default/isc-dhcp-server",false);
		Scanner dhcppackagedconfig = new Scanner(new File(System.getProperty("user.dir")+"/config","dhcpserver_manager"));
		while(dhcppackagedconfig.hasNextLine()){
			config2.write(dhcppackagedconfig.nextLine().getBytes());
		}
		config2.close();


		//writing in main dhcp-server conf
		FileOutputStream config3 = new FileOutputStream("/etc/dhcp/dhcpd.conf",false);
		Scanner dhcppackagedconfig2 = new Scanner(new File(System.getProperty("user.dir")+"/config","dhcpserver_config"));
		while(dhcppackagedconfig2.hasNextLine()){
			config3.write(dhcppackagedconfig2.nextLine().getBytes());
		}
		config3.close();

		Scanner interfacesconfig = new Scanner(new File("/etc/network/interfaces"));
		boolean add = true; int count = 0; boolean stop = false;
		String one = "auto wlan0"; 
		String two = "iface wlan0 inet static";
		String three = "address 10.10.0.1";
		String four = "netmask 255.255.255.0";
		while(interfacesconfig.hasNextLine() && !stop){
			String line = interfacesconfig.nextLine();
			switch(count){
				case 0:
					if (line.equals(one)){
						++count;
					}
					break;
				case 1:
					if (line.equals(two)){
						++count;
					}
					else{
						count = 0;					
					}
					break;
				case 2:
					if (line.equals(three)){
						++count;
					}
					else{
						count = 0;					
					}
					break;
				case 4:
					if (line.equals(four)){
						stop = true;
						add = false;
					}
					else{
						count = 0;
					}
					break;
			}
		}
		if (add){
			FileOutputStream config4 = new FileOutputStream("/etc/network/interfaces",true);
			config4.write(one.getBytes());
			config4.write(two.getBytes());
			config4.write(three.getBytes());
			config4.write(four.getBytes());
			config4.close();
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
		if (status==NetworkManager.START){
			System.err.println("Starting network...");
		}
		else{
			System.err.println("Stopping network...");
		}


		String stringstatus = (status==NetworkManager.START) ? "start" : "stop";

		//checking if isc-dhcp-server and hostapd are installed
		boolean hostapdinstallstatus = isInstalled("hostapd");
		boolean dhcpinstallstatus = isInstalled("isc-dhcp-server");
		if (hostapdinstallstatus && dhcpinstallstatus){
			/*
			Starting/Stopping services
			*/
			InputStream[] dhcpresponse = run("sudo service isc-dhcp-server "+stringstatus);
			InputStream[] hostapdresponse = run("sudo service hostapd "+stringstatus);
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
		if (installedLine.endsWith(" (none)")){
			return false;
		}
		return true;
	}
	/*
	
	Method for running unix command
	@return Outpout and Error streams, respectively.
	*/
	public InputStream[] run(String cmd) throws IOException{
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
	class MissingApplicationException extends Exception{
		public MissingApplicationException(String msg){
			super(msg);
		}
		public MissingApplicationException(String message, Throwable throwable) {
			super(message, throwable);
		}
	}
}
