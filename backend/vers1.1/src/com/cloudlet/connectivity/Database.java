package com.cloudlet.connectivity;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class Database {
	private String username ="";
	private String password = "";
	private String dbname = "";
	private String host = "localhost";
	private int port = 3306;
	
	private Connection con = null;
    private Statement st = null;
    private ResultSet rs = null;
    private String url;
    
	public Database(){
		
	}
	public Database(String db) throws SQLException, ClassNotFoundException{
		if (db.equals("Postgresql")){
			Class.forName("org.postgresql.Driver");
			url = "jdbc:postgresql://"+host+"/"+dbname;
			con = DriverManager.getConnection(url, username, password);
		}
		else if (db.equals("Mysql")){
			Class.forName("com.mysql.jdbc.Driver");
			url = "jdbc:mysql://"+host+":"+port+"/"+dbname;
			con = DriverManager.getConnection(url, username, password);
		}
		else if (db.equals("Sqlite")){
			/*
			 * http://stackoverflow.com/a/593137
			 * 
			 */
			Class.forName("org.sqlite.JDBC");
			con = DriverManager.getConnection("jdbc:sqlite:test.db");
		}
	}
}
