/*

Copyright 2014 Zola 'AdeebNqo' Mahlaza

Class for handling network services.

http://www.gnu.org/licenses/gpl-3.0.txt

*/
public class Driver{
	public static void main(String[] args){
		try{
			NetworkService service = new NetworkService();
			service.startNetwork();
		}catch(Exception e){

		}
	}
}
