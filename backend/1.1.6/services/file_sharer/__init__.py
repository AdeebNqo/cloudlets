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
		return cur.fetchone()
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


class file_sharer():
	def __init__(self):
		self.currdb = db('mysql')
		self.currdb.set_credentials('localhost', 'root', 101, 'cloudletX', 'files')
		self.currdb.connect()
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind(('10.0.0.51', 0))
		self.sockt.listen(1)
		self.users = {}
		print('service created')
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
		data = ''
		lastend = None
		while True:
			length = somesocket.recv(1024)
			if (length!=''):
				length = int(length)
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
					(idX, accessX, filenameX, ownerX, accesslistX) = self.currdb.get({'id':'{0}:{1}'.format(owner,filename)})
					#check if request has access
					if (accessX=='public' or requester==owner or requester in accesslistX):
						jsonstring = "{\"actionresponse\":\"download\", \"OK\"}"
						self.send(requester, jsonstring)
					else:
						jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOACCESS\"}"
						self.send(requester, jsonstring)
				elif action=='upload':
					print('uploading something')
					duration = packet['duration']
					access = packet['access']
					if (access!='public'):
						accesslist = packet['accesslist']
					compression = packet['compression']
					filename = packet['filename']
					owner = packet['owner']
					objectdata = packet['data']

					if not os.path.exists(owner):
						os.makedirs(owner)
					filepath = '{0}/{1}'.format(owner, filename)
					if not os.path.isfile(filepath):
						_file = open(filepath, 'w')
						_file.write(objectdata)
						_file.close()
						#primary key
						primkey = '{0}:{1}'.format(owner,filename)
						self.currdb.insert(('id', 'access', 'filename', 'owner', 'accesslist'), (primkey, access, filename, owner, accesslist.join(':')))
				elif action=='transfer':
					print('transefering something to someone')
					owner = data['owner']
					receiver = data['receiver']
					oncloudlet = data['oncloudlet']
					if (oncloudlet=='0'):
						objectdata = packet['data']
					filename = data['filename']

					(recv_socket, recv_address) = self.connections[receiver]
					filepath = '{0}/{1}'.format(owner,filename)
					if oncloudlet==1:
						with open(filepath) as _file:
							objectdata = _file.read()
					jsonstring = '{\"action\":\"recv\", \"owner\":\"{0}\", \"filename\":\"{1}\", \"objectdata\":\"{2}\"}'.format(owner, filename, objectdata)
					recv_socket.sendal(len(jsonstring))
					if (recv_socket.recv(1024)=='OK'):
						recv_socket.sendall(jsonstring)
				elif action == 'identify':
					accessor = json.loads(data)
					self.users[accessor['username']] = (somesocket, address)
				data = ''

	def send(self,username, data):
		(sock, addr) = self.users[username]
		length = len(data)
		sock.sendall("{}".format(length))
		response = sock.recv(1024)
		if (response=='OK'):
			sock.sendall(data)
	def stop(self):
		print('stopping')
		self.sockt.close()
	def request_service(self):
		(host,port) = self.sockt.getsocketname()
		return '{0}:{1}'.format(host,port)
