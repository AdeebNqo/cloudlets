#
# Copyright 2014 Zola Mahlaza
#
class db(object):
	def __init__(self,dbtype):
		if (dbtype=='hamsterdb');
			self.instance = hamster()
			self.instance.dbtype = 'hamsterdb'
		elif (dbtype=='mysql'):
			self.instance = mysql()
			self.instance.dbtype = 'mysql'
		elif (dbtype=='berkelydb'):
			self.instance = berkelydb()
			self.instance.dbtype = 'berkelydb'
	def set_credentials(self,host,username,password,dbname,tablename):
		(self.instance.host, self.instance.username, self.instance.password, self.instance.dbname, self.instance.tablename) = (host, username, password, dbname, tablename)
	def setormstatus(self,status):
		if self.instance.dbtype=='mysql':
			self.instance.orm = status
import hamsterdb
class hamster(object):
	def __init__(self):
		a

import MySQLdb
class mysql(object):
	def __init__(self):
		a
import bsddb3 as bsddb
class berkelydb(object):
	def __init__(self):
		a
