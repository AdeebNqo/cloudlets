import java.net.Socket;
import java.net.ServerSocket;
import java.io.IOException;
public class Server{
	public static void main(String[] args){
		try{
			ServerSocket sSocket = new ServerSocket(9090);
			while(true){
				System.err.println("waiting...");
				Socket s = sSocket.accept();
				System.err.println("accepted...");
			}
		}catch(IOException e){
			e.printStackTrace();
		}
	}
}
