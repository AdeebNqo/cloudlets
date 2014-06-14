/*

Copyright 2014 Zola 'AdeebNqo' Mahlaza

Class for handling network services.

http://www.gnu.org/licenses/gpl-3.0.txt

*/
public class Driver{
	public static void main(String[] args){
		try{
			NetworkManager service = new NetworkManager();
			service.setStatus(NetworkManager.STOP);
			service.setCredentials("cloudlet-test","12345");
			service.setStatus(NetworkManager.START);
			System.err.println("Login credentials: name("+service.getNetworkName()+"), password( "+service.getPassword()+")");
		}catch(Exception e){
			e.printStackTrace();
		}
	}
}
