import ConfigParser
from db import db
import datetime

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#retrieving configuration
numtimes = int(config.get('DEFAULT','numtimes'))
action = config.get('DEFAULT','action')
testdb = config.get('DEFAULT','db')

keys = config.get('DEFAULT','key')
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
	print('testing db: {}'.format(currdb))
	somedb = db(currdb)
	if currdb == 'berkelydb':
		somedb.set_credentials(host,username,password,dbnameBerkely,tablename)
	else:
		somedb.set_credentials(host,username,password,dbname,tablename)
	somedb.connect()
	inserttime = 0
	retrievetime = 0
	updatetime = 0
	for i in range(numtimes):
		for someaction in actions:
			if someaction=='insert':
				start = datetime.datetime.now()
				somedb.insert(tuple(keys.split(',')),tuple(data.split(',')))
				diff = datetime.datetime.now()-start
				inserttime += diff.total_seconds()
			elif someaction=='get':
				start = datetime.datetime.now()
				somedb.get(data.split(',')[0])
				diff = datetime.datetime.now()-start
				retrievetime += diff.total_seconds()
			elif someaction=='update':
				start = datetime.datetime.now()
				somedb.update('anele#data.mp3',('access',),('private',))
				diff = datetime.datetime.now()-start
				updatetime += diff.total_seconds()
	print('Number of runs: {}'.format(numtimes))
	print('Insert time: {} seconds'.format(inserttime))
	print('Retrieve time: {} seconds'.format(retrievetime))
	print('Update time: {} seconds'.format(updatetime))
	print('\n')
