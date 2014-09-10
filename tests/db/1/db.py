#
# Copyright 2014 Zola Mahlaza
#
class db(object):
	def __init__(self,dbtype):
		if (dbtype=='mysql'):
			self.instance = mysql()
			self.instance.dbtype = 'mysql'
		elif (dbtype=='berkelydb'):
			self.instance = berkelydb()
			self.instance.dbtype = 'berkelydb'
	def set_credentials(self,host,username,password,dbname,tablename):
		(self.instance.host, self.instance.username, self.instance.password, self.instance.dbname, self.instance.tablename) = (host, username, password, dbname, tablename)
	def connect(self):
		self.instance.connect()
	def insert(self,key,data):
		self.instance.insert(key,data)
	def get(self,key):
		return self.instance.get(key)
import MySQLdb
class mysql(object):
	def connect(self):
		self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.dbname)
		self.cur = self.db.cursor()
	def insert(self,key,data):
		print('INSERT into {0} (id, data) values ({1}, {2})'.format(self.tablename, key, data))
		self.cur.execute('INSERT into {0} (id, data) values ({1}, {2})'.format(self.tablename, key, data))
		self.db.commit()
	def get(self,key):
		self.cur.execute('SELECT * FROM {0} where id={1}'.format(self.tablename, key))
		return cur.fetchall()
import bsddb3 as bsddb
class berkelydb(object):
	def connect(self):
		self.db = bsddb.db.DB()
		self.db.open(self.dbname, None, bsddb.db.DB_HASH, bsddb.db.DB_CREATE)
		self.cur = self.db.cursor()
	def insert(self,key,data):
		self.db.put(key,data)
	def get(self,key):
		return self.db.get(key)
