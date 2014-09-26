#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# File sharing service
#
# "Any sufficiently advanced bug is indistinguishable from a feature."
# -Bruce Brown
#
import socket
import json
import os
import threading
import shutil
import traceback
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
		print('INSERT INTO {0}{1} VALUES {2};'.format(self.tablename, string, values))
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
class berkelydb(object):
	def connect(self):
		self.db = bsddb.db.DB()
		self.db.open(self.dbname, None, bsddb.db.DB_HASH, bsddb.db.DB_CREATE)
		self.cur = self.db.cursor()
	def insert(self,key,data):
		self.db.put(key,data)
	def get(self,keys):
		return self.db.get(key)
	def cleandata(self):
		os.remove('{}.db'.format(self.dbname))
		self.connect()

class file_sharer():
	def __init__(self):
		self.currdb = db('mysql')
		self.currdb.set_credentials('localhost', 'root', 101, 'cloudletX', 'files')
		self.currdb.connect()
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind(('10.10.0.51', 0))
		self.sockt.listen(1)
		self.users = {}
		self.curd = os.path.dirname(__file__)
		try:
			#cleaning database
			self.currdb.cleandata()
			#cleaning folders
			dirs = [x[0] for x in os.walk(directory)]
			for DIR in dirs:
				shutil.rmtree(DIR)
		except:
			traceback.print_exc()
	def start(self):
		print('starting')
		t = threading.Thread(target=self.wait_connections)
		t.daemon = True
		t.start()
	def wait_connections(self):
		while True:
			conn, addr = self.sockt.accept()
			self.handle(conn, addr)
	def handle(self, somesocket, address):
		try:
			data = ''
			lastend = None
			while True:
				length = somesocket.recv(1024)
				if (length!='' or length!=None):
					dosomething = False
					try:
						length = int(length)
						dosomething = True
					except:
						pass
					if (dosomething):
						somesocket.sendall('OK')
						if (lastend!=None):
							data=data+lastend
							lastend = None
						data = data+somesocket.recv(length)
						while (len(data) < length):
							data = data + somesocket.recv(length)
						if (len(data)>length):
							lastend = data[length:]
							data = data[:length]
						packet = json.loads(data)
						action = packet['action']
						if action=='heartbeat':
							response = '{\"status\":\"OK\"}'
							somesocket.sendall(len(response))
							statusresponse = somesocket.recv(1024)
							if (statusresponse=='OK'):
								somesocket.sendall(response)
						elif action=='download':
							print('downloading something')
							owner = packet['owner']
							requester = packet['requester']
							filename = packet['filename']
							result = self.currdb.get({'id':'{0}#{1}'.format(owner,filename)})
							if (result==None):
								print('db get result was null')
								jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOTOK\", \"reason\":\"Request file does not exist.\"}"
								if (requester==owner):
									self.send2(somesocket, jsonstring)
								else:
									self.send(requester, jsonstring)
							else:
								(idX, accessX, filenameX, ownerX, accesslistX, compressionX) = result
								#check if request has access
								if (accessX=='public' or requester==owner or requester in accesslistX):
									try:
										objectdata = open('{2}/{0}/{1}'.format(ownerX, filenameX,self.curd)).read()
										jsonstring = "{\"actionresponse\":\"download\", \"status\":\"OK\", \"objectdata\":\""+objectdata+"\", \"compression\":\""+compressionX+"\"}"
										if (requester==ownerX):
											self.send2(somesocket, jsonstring)
										else:
											self.send(requester, jsonstring)
									except IOError, e:
										jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOTOK\", \"reason\":\""+str(e)+"\"}"
										if (requester==ownerX):
											self.send2(somesocket, jsonstring)
										else:
											self.send(requester, jsonstring)
								else:
									print('no access.')
									jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOTOK\", \"reason\":\"Do not have access to file.\"}"
									self.send(requester, jsonstring)
						elif action=='upload':
							print('uploading something')
							duration = packet['duration']
							access = packet['access']
							accesslist = packet['accesslist']
							if (accesslist=='None'):
								accesslist = []
							if (access!='public'):
								accesslist = packet['accesslist']
							compression = packet['compression']
							filename = packet['filename']
							owner = packet['owner']
							objectdata = packet['objectdata']

							print('checking existence of folder: {}'.format(owner))
							if not os.path.exists('{0}/{1}'.format(self.curd, owner)):
								os.makedirs('{0}/{1}'.format(self.curd,owner))
								print('owner did not have any shared files. his folder has been created')
							filepath = '{2}/{0}/{1}'.format(owner, filename, self.curd)
							if not os.path.isfile(filepath):
								print('The upload does not yet exist')
								#primary key
								primkey = '{0}#{1}'.format(owner,filename)
								try:
									self.currdb.insert(('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
									_file = open(filepath, 'w')
									_file.write(objectdata)
									_file.close()
									jsonstring = jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"OK\"}"
									self.send2(somesocket, jsonstring)
								except MySQLdb.Error,e:
									print(e)
									jsonstring = jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"NOTOK\", \"reason\": \""+str(e)+"\"}"
									self.send2(somesocket, jsonstring)
							else:
								jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"NOTOK\", \"reason\": \"The file already exists.\"}"
								self.send2(somesocket, jsonstring)
						elif action == 'identify':
							accessor = json.loads(data)
							self.users[accessor['username']] = (somesocket, address)
						elif action == 'remove':
							owner = packet['owner']
							requester = packet['requester']
							filename = packet['filename']
							if (owner==requester):
								try:
									self.currdb.delete({'id':'{0}#{1}'.format(owner,filename)})
									filepath = '{2}/{0}/{1}'.format(owner, filename, self.curd)
									os.remove(filepath)
									jsonstring = jsonstring = "{\"actionresponse\":\"remove\", \"status\":\"OK\"}"
									self.send2(somesocket, jsonstring)
								except Exception,e:
									jsonstring = "{\"actionresponse\":\"remove\", \"status\":\"NOTOK\", \"reason\": \""+str(e)+"\"}"
									self.send2(somesocket, jsonstring)
							else:
								jsonstring = "{\"actionresponse\":\"remove\", \"status\":\"NOTOK\", \"reason\": \"Access denied.\"}"
								self.send2(somesocket, jsonstring)
						elif action == 'getfiles':
							requester = packet['requester']
							#compiling a json list with the files
							filelist = "\"files\" : ["
							public = self.currdb.getpublicfiles()
							lenpublic = len(public)
							accesssible = self.currdb.getsharedfiles(requester)
							lenaccesssible = len(accesssible)
							i = 0
							for row in public:
								(idX, accessX, filenameX, ownerX, accesslistX, compressionX) = row
								filelist += "{\"id\":\""+idX+"\", \"access\":\""+accessX+"\", \"filename\":\""+filenameX+"\", \"compression\":\""+compressionX+"\", \"owner\":\""+ownerX+"\"}"
								if (i != lenpublic-1):
									filelist += ','
								i += 1
							i = 0
							if (lenaccesssible==0):
								filelist += ']'
							else:
								for row in accesssible:
									(idX, accessX, filenameX, ownerX, accesslistX, compressionX) = row
									filelist += "{\"id\":\""+idX+"\", \"access\":\""+accessX+"\", \"filename\":\""+filenameX+"\", \"compression\":\""+compressionX+"\", \"owner\":\""+ownerX+"\"}"
									if (i != lenaccesssible-1):
										filelist += ','
									i += 1
								filelist += ']'
							#compiling final json response
							jsonstring = "{\"actionresponse\":\"getfiles\", "+filelist+"}"
							self.send2(somesocket, jsonstring)
						data = ''
		except Exception,e:
			print(e)
	def send(self,username, data):
		(sock, addr) = self.users[username]
		length = len(data)
		sock.sendall("{}".format(length))
		response = sock.recv(1024)
		if (response=='OK'):
			sock.sendall(data)
	def send2(self,somesocket,data):
		length = len(data)
		somesocket.sendall("{}".format(length))
		response = somesocket.recv(1024)
		if (response=='OK'):
			somesocket.sendall(data)
	def stop(self):
		print('stopping')
		self.sockt.close()
	def request_service(self):
		(host,port) = self.sockt.getsockname()
		return '{0}:{1}'.format(host,port)
	#Method for disconnecting user
	def disconnect(self, username):
		try:
			(sock, addr) = self.users[username]
			sock.close()
			del self.users[username]
		except:
			pass
