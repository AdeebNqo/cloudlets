/*

Copyright 2014 Zola 'AdeebNqo' Mahlaza

This class is for managing the network.

http://www.gnu.org/licenses/gpl-3.0.txt

*/
public class NetworkManager{
	//variables to start and stop the network
	public static int START = 0;
	public static int STOP = 1;

	public NetworkManager(){

	}
	/*

	Method for changing network status

	*/
	public void setStatus(int status){
		String status = (status==START) ? "start" : "stop";

		//checking if isc-dhcp-server and hostapd are installed
		boolean hostapdinstallstatus = isInstalled("hostapd");
		boolean dhcpinstallstatus = isInstalled("isc-dhcp-server");
		if (hostapdinstallstatus && dhcpinstallstatus){
			/*
			Starting services
			*/
			InputStream[] dhcpresponse = run("sudo service isc-dhcp-server "+status);
			InputStream[] hostapdresponse = run("sudo service hostapd "+status);
			return true; //ToDo: check if starting was successful.
		}
		else{
			System.err.println("hostapd and isc-dhcp-server are not installed.");
			throw new MissingApplicationException("Missing application: hostapd and/or isc-dhcp-server");
		}
		return false;
	}
	/*
	
	Method for checking if application is installed

	*/
	public boolean isInstalled(String appname){
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
	public InputStream[] run(String cmd){
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
