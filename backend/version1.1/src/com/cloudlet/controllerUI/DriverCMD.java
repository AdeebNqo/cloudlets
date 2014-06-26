package com.cloudlet.controllerUI;

import java.io.IOException;
import java.util.Scanner;

import com.cloudlet.connectivity.Server;
import com.cloudlet.installer.NetworkInstaller;
import com.cloudlet.installer.NetworkInstaller.MissingApplicationException;

public class DriverCMD {
	public static void main(String[] args) throws IOException,
			MissingApplicationException {
		
		Scanner input = new Scanner(System.in);
		NetworkInstaller ni = new NetworkInstaller();
		Server server = new Server();
		
		System.out
				.println("1. Cloudlet server installation.\n2.Run cloudlet server.\n3. Stop running cloudlet");
		int choice = input.nextInt();
		switch (choice) {
			case 1:
				boolean gotocase2 = false;
				boolean hostapdinstallstatus = ni.isInstalled("hostapd");
				boolean dhcpinstallstatus = ni.isInstalled("isc-dhcp-server");
				if (hostapdinstallstatus && dhcpinstallstatus) {
					System.out.println("Enter ssid/network name/cloudlet name:");
					String ssid = input.next();
					System.out.println("Enter password:");
					String password = input.next();
					ni.setCredentials(ssid, password);
					System.err.println("Credentials set");
					gotocase2 = true;
				} else if (dhcpinstallstatus) {
					System.err
							.println("hostapd is not installed. Please install it using `sudo apt-get install hostapd`.");
				} else if (hostapdinstallstatus) {
					System.err
							.println("isc-dhcp-server is not installed. Please install it using `sudo apt-get install isc-dhcp-server`.");
				} else {
					System.err
							.println("Neither hostapd nor isc-dhcp-server is installed. Please install those packages to continue.");
				}
				if (!gotocase2){
					break;
				}
			case 2:
				System.err.println("case2 first line");
				ni.setStatus(NetworkInstaller.START);
				System.err.println("case2 before server start");
				server.start();
				System.err.println("server started..");
				break;
			case 3:
				server.stop();
				ni.setStatus(NetworkInstaller.STOP);
			default:
				System.err.println("Exiting UI...");
		}
		input.close();
	}
}
