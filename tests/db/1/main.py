import ConfigParser
from db import db

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#retrieving configuration
numtimes = config['DEFAULT']['numtimes']
action = config['DEFAULT']['action']
testdb = config['DEFAULT']['db']

host = config['dbconfig']['host']
username = config['dbconfig']['username']
password = config['dbconfig']['password']
tablename = config['dbconfig']['tablename']
dbname = config['dbconfig']['dbname']

mysqluseorm = config['mysql']['orm']

#getting which dbs are to be tested
if testdb=='all':
	testdb = 'hamsterdb,mysql,berkelydb'
testdbs = testdb.split()

#testing each selected db
for currdb in testdbs:
	somedb = db(currdb)
	somedb.set_credentials(host,username,password,dbname,tablename)
