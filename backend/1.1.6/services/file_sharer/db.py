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
	'''
	This method takes in two tuples. The first tuple contains
	a list of the names of the columns. The second contains a
	list of values of the columns.
	'''
	def insert(self,keys,data):
		length = len(keys)
		#creating strings for the keys and values
		string = '('
		values = '('
		for i in range(length):
			string = string + keys[i]
			values = values + data[i]
			if (i!=length-1):
				string = string+','
				values = values+','
		string = string+')'
		values = values+')'
		print('INSERT INTO {0} {1} VALUES {2};'.format(self.tablename, string, values))
		self.cur.execute('INSERT INTO {0} {1} VALUES {2};'.format(self.tablename, string, values))
		self.db.commit()
	'''
	This method only takes the identifier used for each db item.
	The argument is a dictionary. {name:value}
	'''
	def get(self,key):
		self.cur.execute('SELECT * FROM {0} where {1}={2}'.format(self.tablename, key.keys()[0], key.values()[0]))
		return cur.fetchall()
	def update(self, key, keys, data):
		length = len(keys)
		updatestring = ''
		for i in range(length):
			updatestring = updatestring+keys[i]+'='+data[i]
			if (i!=length-1):
				updatestring=updatestring+','
		self.cur.execute('UPDATE {0} SET {1} where {2}={3}'.format(self.tablename, updatestring, key.keys()[0], key.values()[0]))
		self.cur.commit()
import bsddb3 as bsddb
class berkelydb(object):
	def connect(self):
		self.db = bsddb.db.DB()
		self.db.open(self.dbname, None, bsddb.db.DB_HASH, bsddb.db.DB_CREATE)
		self.cur = self.db.cursor()
	def insert(self,key,data):
		self.db.put(key,data)
	def get(self,keys):
		return self.db.get(key)
