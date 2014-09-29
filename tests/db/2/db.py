#
# Copyright 2014 Zola Mahlaza
#
class db(object):
	def __init__(self,dbtype):
		if (dbtype=='mysql'):
			self.instance = mysql()
			self.instance.dbtype = 'mysql'
		elif (dbtype=='berkeleydb'):
			self.instance = berkeleydb()
			self.instance.dbtype = 'berkeleydb'
	def set_credentials(self,host,username,password,dbname,tablename):
		(self.instance.host, self.instance.username, self.instance.password, self.instance.dbname, self.instance.tablename) = (host, username, password, dbname, tablename)
	def connect(self):
		self.instance.connect()
	def insert(self,key,data):
		self.instance.insert(key,data)
	def get(self,key):
		return self.instance.get(key)
	def delete(self, key):
		return self.instance.delete(key)
	def getpublicfiles(self):
		return self.instance.getpublicfiles()
	def getsharedfiles(self, requester):
		return self.instance.getsharedfiles(requester)
	def cleandata(self):
		self.instance.cleandata()
import MySQLdb
class mysql(object):
	def connect(self):
		self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=str(self.password), db=self.dbname)
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
			values = values + "\""+data[i]+"\""
			if (i!=length-1):
				string = string+','
				values = values+','
		string = string+')'
		values = values+')'
		self.cur.execute('INSERT INTO {0} {1} VALUES {2};'.format(self.tablename, string, values))
		self.db.commit()
	'''
	This method only takes the identifier used for each db item.
	The argument is a dictionary. {name:value}
	'''
	def get(self,key):
		self.cur.execute("SELECT * FROM {0} where {1}=\"{2}\"".format(self.tablename, key.keys()[0], key.values()[0]))
		return self.cur.fetchone()
	def update(self, key, keys, data):
		length = len(keys)
		updatestring = ''
		for i in range(length):
			updatestring = updatestring+keys[i]+'='+data[i]
			if (i!=length-1):
				updatestring=updatestring+','
		self.cur.execute('UPDATE {0} SET {1} where \"{2}\"=\"{3}\"'.format(self.tablename, updatestring, key.keys()[0], key.values()[0]))
		self.cur.commit()
	# Method for deleting item from database
	def delete(self, key):
		try:
			self.cur.execute("DELETE FROM {0} where {1}=\"{2}\"".format(self.tablename, key.keys()[0], key.values()[0]))
			self.db.commit()
			return 0
		except:
			self.db.rollback()
			return 1
	# Method for getting public files
	def getpublicfiles(self):
		self.cur.execute("SELECT * FROM {0} where access=\"public\"".format(self.tablename))
		return self.cur.fetchall()
	# Method for getting all shared file
	def getsharedfiles(self, requester):
		cmd = "SELECT * FROM "+self.tablename+" where NOT (access=\"public\") AND accesslist LIKE \"%"+requester+"%\""
		self.cur.execute(cmd)
		return self.cur.fetchall()
	def cleandata(self):
		cmd = "DELETE FROM {}".format(self.tablename)
		self.cur.execute(cmd)
		self.db.commit()
import bsddb3 as bsddb
class berkeleydb(object):
	def connect(self):
		self.db = bsddb.db.DB()
		self.db.open(self.dbname, None, bsddb.db.DB_HASH, bsddb.db.DB_CREATE)
		self.cur = self.db.cursor()
	def insert(self,keys,data):
		self.db.put(data[0],'?'.join(data))
	def get(self,key):
		val = self.db.get(key['id'])
		return tuple(val.split('?'))
	def update(self, key, keys, data):
		vals = self.get(key)
		length = len(keys)
		for i in range(length):
			val = keys[i]
			if (val=='id'):
				vals[0] = data[i]
			elif (val=='access'):
				vals[1] = data[i]
			elif (val=='filename'):
				vals[2] = data[i]
			elif (val=='owner'):
				vals[3] = data[i]
			elif (val=='accesslist'):
				vals[4] = data[i]
			elif (val=='compression'):
				vals[5] = data[i]
		self.insert(key,vals)
	def delete(self, key):
		try:
			self.db.delete(key['id'])
			return 0
		except Exception,e:
			traceback.print_exc()
			return 1
	def getpublicfiles(self):
		returnval = []
		rec = self.cur.first()
		while rec:
			vals = tuple(rec[1].split('?'))
			if (vals[1]=='public'):
				returnval.append(vals)
			rec = self.cur.next()
		self.cur = self.db.cursor()
		return returnval
	def getsharedfiles(self, requester):
		returnval = []
		rec = self.cur.first()
		while rec:
			vals = tuple(rec[1].split('?'))
			if (requester in vals[4]):
				returnval.append(vals)
			rec = self.cur.next()
		self.cur = self.db.cursor()
		return returnval
	def cleandata(self):
		try:
			os.remove('{1}/{0}.db'.format(self.dbname,os.path.dirname(__file__)))
			self.connect()
		except Exception,e:
			pass
			#traceback.print_exc()
