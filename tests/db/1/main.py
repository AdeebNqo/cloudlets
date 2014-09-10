import ConfigParser
from db import db

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#retrieving configuration
numtimes = int(config.get('DEFAULT','numtimes'))
action = config.get('DEFAULT','action')
testdb = config.get('DEFAULT','db')

key = config.get('DEFAULT','key')
data = config.get('DEFAULT','data')
useblob = config.get('DEFAULT','useblob')

host = config.get('dbconfig','host')
username = config.get('dbconfig','username')
password = config.get('dbconfig','password')
tablename = config.get('dbconfig','tablename')
dbname = config.get('dbconfig','dbname')
dbnameBerkely = config.get('berkelydb','dbname')

mysqluseorm = config.get('mysql','orm')

#getting which dbs are to be tested
if testdb=='all':
	testdb = 'mysql,berkelydb'
testdbs = testdb.split(',')
#getting which actions are to be executed
actions = action.split(',')

#testing each selected db
for currdb in testdbs:
	somedb = db(currdb)
	if currdb == 'berkelydb':
		somedb.set_credentials(host,username,password,dbnameBerkely,tablename)
	else:
		somedb.set_credentials(host,username,password,dbname,tablename)
	somedb.connect()
	for i in range(numtimes):
		for someaction in actions:
			if someaction=='insert':
				somedb.insert(key,data)
			elif someaction=='get':
				somedb.get(key)
