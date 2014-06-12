/*

Copyright 2014 Zola 'AdeebNqo' Mahlaza

Class for handling network services.

http://www.gnu.org/licenses/gpl-3.0.txt

*/
public class NetworkService{

	public NetworkService(){
		
	}

	/*
	____________________________________
	Method for starting network service
	____________________________________
	*/
	public boolean startNetwork(){
		//checking if isc-dhcp-server and hostapd are installed
		boolean hostapdinstallstatus = isInstalled("hostapd");
		boolean dhcpinstallstatus = isInstalled("isc-dhcp-server");
		if (hostapdinstallstatus && dhcpinstallstatus){
			/*
			Starting services
			*/
			InputStream[] dhcpresponse = run("sudo service isc-dhcp-server start");
			InputStream[] hostapdresponse = run("sudo service hostapd start");
		}
		else{
			throw new Exception("Missing application: hostapd and/or isc-dhcp-server");
		}
	}
	/*
	
	Method for checking if application is installed

	*/
	public boolean isInstalled(String appname){
		InputStream[] response = run("apt-cache policy "+appname);
		Scanner input = new Scanner(reponse[0]);
		input.nextLine();
		String installedLine = input.nextLine();
		if (installedLine.endsWith(" (none)")){
			return false;
		}
		return true;
	}
	/*
	
	Method for running unix command

	*/
	public InputStream[] run(String cmd) throws Exception{
		ProcessBuilder procBuilder = new ProcessBuilder(cmd.split("\\s+"));
		procBuilder.directory(new File(working_directory));
		Process proc = procBuilder.start();//Runtime.getRuntime().exec(cmd);
		//Output of the cmd
		InputStream out = proc.getInputStream();
		//Errors of the cmd
		InputStream in = proc.getErrorStream();
		InputStream[] streams = {out, in};
		return streams;			
	} 
	/*
	
	Method for running piped unix command
	@note This is reused from https://github.com/AdeebNqo/JBa-h

	*/
	public InputStream run_piped(String cmd){
		int last_pos =0;
		Vector<String> commands = new Vector<String>();
		int string_length = cmd.length();
		//spliting up the commands
		for (int i=0;i<string_length;i++){
			if (cmd.charAt(i)=='|'){
				String sub = cmd.substring(last_pos,i);
				last_pos = i;
				commands.add(sub);
			}
		}
		//running the actual commands
		commands.add(cmd.substring(last_pos+1));
		commands.trimToSize();
		ProcessBuilder proc=null;//defining the process outside the loop so that we can can get the results afterwards
		InputStream results = null;
		for (String cur_string:commands){
			cur_string = (cur_string.replaceAll("\\s+"," "));
			cur_string = cur_string.replaceAll("^\\s+","");
			try{
				//formatting the command
				if (cur_string.contains("ls")){
					String[] str = cur_string.split("\\s+");
					if (str.length==1){
						//if cmd is just ls
						cur_string = "ls "+working_directory;
					}
					else if (str.length==2 && str[1].startsWith("-")){
						//ls and flags only, no dir given
						cur_string=cur_string+" "+working_directory;
					}
					else if (str.length==2){
						//no flags given
						if (!str[1].startsWith("/home")){
							//if not full path
							cur_string = "ls "+working_directory+"/"+str[1];
						}
					}
					else if (str.length==3){
						if (!str[1].startsWith("/home")){
		                                	//if not full path
		                                	cur_string = str[0]+" "+str[1]+" "+working_directory+"/"+str[2];
		                        	}
					}
				}
				//starting the 'current' process--running the next cmd on the list of pipes
				proc = new ProcessBuilder(cur_string.split("\\s"));
				Process p = proc.start();
				if (results!=null){
					BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
					Scanner results_reader = new Scanner(results);
					while(results_reader.hasNextLine()){
						writer.write(results_reader.nextLine());
						writer.newLine();
					}
					writer.close();
					results_reader.close();
				}
				p.waitFor();
				results = p.getInputStream();

			}catch(Exception e){
				e.printStackTrace();
			}
		}
	
		//printing final output of the piped cmd
		//<here>
		return results;
	}
	
}
