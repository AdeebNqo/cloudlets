import ConfigParser
from db import db
import datetime
import cProfile
import base64

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#retrieving configuration
numtimes = int(config.get('DEFAULT','numtimes'))
action = config.get('DEFAULT','action')
testdb = config.get('DEFAULT','db')

key = config.get('DEFAULT','key')
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

datastring = base64.b64encode(open('audio0.mp3','r').read())
data = datastring
keyval = 'teststring'

class DatabaseTest(object):
	def __init__(self,dbtype):
		self.somedb = db(dbtype)
		if dbtype == 'berkelydb':
			self.somedb.set_credentials(host,username,password,dbnameBerkely,tablename)
		else:
			self.somedb.set_credentials(host,username,password,dbname,tablename)
		self.somedb.connect()
	def test_insert(self):
		cProfile.runctx('self.reallytest_insert()', globals(), locals())
	def reallytest_insert(self):
		self.somedb.insert(('id','objectdata',), (keyval, data,))
	def test_get(self):
		cProfile.runctx('self.reallytest_get()', globals(), locals())
	def reallytest_get(self):
		self.somedb.get(keyval)
	def test_update(self):
		cProfile.runctx('self.reallytest_update()', globals(), locals())
	def reallytest_update(self):
		self.somedb.update(keyval, ('id','objectdata',), (keyval, data,))
if __name__=='__main__':
	for dbtype in testdbs:
		dbX = DatabaseTest(dbtype)
		dbX.test_insert()
		dbX.test_get()
		dbX.test_update()
