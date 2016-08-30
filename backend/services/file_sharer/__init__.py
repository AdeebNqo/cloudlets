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
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import broadcaster
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

'''
Class responsible for deleting files after delay
'''
class delayremover(object):
	def __init__(self, db, DIR):
		self.delays = []
		self.db = db
		self.DIR = DIR
		self.users = {}
		broadcaster.disconnectsubscribe(self.ondisconnect)
	def remove(self, owner, filename, time):
		t = threading.Thread(target=self.reallyremove, args=(owner, filename, time,))
		t.daemon = True
		t.start()
	def reallyremove(self,owner,filename,timeX):
		time.sleep(timeX)
		self.db.delete('{0}#{1}'.format(owner, filename))
		os.remove('{0}/{1}/{2}'.format(self.DIR, owner, filename))
	def removeonleave(self,name,filedetails):
		if name in self.users:
			self.users[name].append(filedetails)
		else:
			self.users[name] = [filedetails]
	def ondisconnect(self,name,mac):
		if name in self.users:
			filedetailsX = self.users[name]
			for filedetails in filedetailsX:
				(owner,filename) = filedetails
				self.db.delete('{0}#{1}'.format(owner, filename))
				os.remove('{0}/{1}/{2}'.format(self.DIR, owner, filename))

class file_sharer():
	def __init__(self):
		#Creating and connecting to the database the file metadata will be stored in.
		self.currdb = db('berkeleydb')
		self.currdb.set_credentials('localhost', 'root', 101, 'cloudletX', 'files')
		self.currdb.connect()
		#Starting server socket to enable clients to connect to file sharing service
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind(('10.10.0.51', 0))
		self.sockt.listen(1)
		(host,port) = self.sockt.getsockname()
		self.host = host
		self.port = port
		self.users = {}
		self.curd = os.path.dirname(__file__)
		#creating way of enabling temporal data
		self.delayremoverX = delayremover(self.currdb, self.curd)
		#Removing data from last session
		try:
			#cleaning database
			self.currdb.cleandata()
			#cleaning folders
			dirs = [name for name in os.listdir(self.curd)]
			for DIR in dirs:
				if (os.path.isdir('{0}/{1}'.format(self.curd,DIR))):
					shutil.rmtree('{0}/{1}'.format(self.curd,DIR))
			broadcaster.disconnectsubscribe(self.reallydisconnect)
		except Exception,e:
			traceback.print_exc()
	def start(self):
		t = threading.Thread(target=self.wait_connections)
		t.daemon = True
		t.start()
	def wait_connections(self):
		while True:
			conn, addr = self.sockt.accept()
			t = threading.Thread(target=self.handle, args=(conn,addr,))
			t.daemon = True
			t.start()
	def handle(self, somesocket, address):
		try:
			cacheusername = None
			cachefilelist = None
			data = ''
			lastend = None
			#Handling requests from client
			while True:
				length = somesocket.recv(1024)
				#First if statement will be met
				#when the client disconnects
				if (sys.getsizeof(length)==0):
					try:
						length = None
						#self.disconnect(cacheusername)
					except:
						pass
					break
				#Second if statement will be met when there is data
				#recieved from client
				elif (length!='' or length!=None):
					dosomething = False
					try:
						#reading size of packet to be sent by client
						length = int(length)
						dosomething = True
					except:
						pass
					#If the client will send an actual packet
					if (dosomething):
						#Tell client to send the packet
						somesocket.sendall('OK')
						#Recieving the data being sent by the client.
						if (lastend!=None):
							data=data+lastend
							lastend = None
						try:
							data = data+somesocket.recv(length)
						except:
							pass
						while (len(data) < length):
							data = data + somesocket.recv(length)
						if (len(data)>length):
							lastend = data[length:]
							data = data[:length]
						#parsing the data which was sent
						#by the client as it's a json string
						packet = json.loads(data)
						#viewing what the client wants to do
						action = packet['action']
						if action=='heartbeat':
							response = '{\"status\":\"OK\"}'
							somesocket.sendall(len(response))
							statusresponse = somesocket.recv(2)
							if (statusresponse=='OK'):
								somesocket.sendall(response)
						elif action=='download':
							print('downloading something')
							owner = packet['owner']
							requester = packet['requester']
							filename = packet['filename']
							result = self.currdb.get({'id':'{0}#{1}'.format(owner,filename)})
							if (result==None):
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
										print('downloading successful')
									except IOError, e:
										jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOTOK\", \"reason\":\""+self.cleansend(str(e))+"\"}"
										if (requester==ownerX):
											self.send2(somesocket, jsonstring)
										else:
											self.send(requester, jsonstring)
										print('downloading failed')
										try:
											self.currdb.connect()
										except:
											pass
								else:
									jsonstring = "{\"actionresponse\":\"download\", \"status\":\"NOTOK\", \"reason\":\"Do not have access to file.\"}"
									self.send(requester, jsonstring)
									print('downloading failed')
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
							if not os.path.exists('{0}/{1}'.format(self.curd, owner)):
								os.makedirs('{0}/{1}'.format(self.curd,owner))
							filepath = '{2}/{0}/{1}'.format(owner, filename, self.curd)
							if not os.path.isfile(filepath):
								#primary key
								primkey = '{0}#{1}'.format(owner,filename)
								try:
									self.currdb.insert(('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
									_file = open(filepath, 'w')
									_file.write(objectdata)
									_file.close()
									jsonstring = jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"OK\"}"
									self.send2(somesocket, jsonstring)
									print('uploading successful')
									#scheduling a delete after some the specified time, if neccessary
									if (duration!=None or duration!=""):
										if (duration=='Onleave'):
											self.delayremoverX.removeonleave(cacheusername,(owner,filename))
										else:
											chars = list(duration)
											durationX = ''.join(chars[:len(chars)-1])
											self.delayremoverX.remove(owner,filename,float(durationX))
								except MySQLdb.Error,e:
									jsonstring = jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"NOTOK\", \"reason\": \""+self.cleansend(str(e))+"\"}"
									self.send2(somesocket, jsonstring)
									print('uploading failed')
									try:
										self.currdb.connect()
									except:
										pass
							else:
								jsonstring = "{\"actionresponse\":\"upload\", \"status\":\"NOTOK\", \"reason\": \"The file already exists.\"}"
								self.send2(somesocket, jsonstring)
								print('uploading failed')
						elif action == 'identify':
							accessor = json.loads(data)
							cacheusername = accessor['username']
							self.users[accessor['username']] = (somesocket, address)
						elif action == 'remove':
							print('removing something')
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
									print('removing successful')
								except Exception,e:
									jsonstring = "{\"actionresponse\":\"remove\", \"status\":\"NOTOK\", \"reason\": \""+self.cleansend(str(e))+"\"}"
									self.send2(somesocket, jsonstring)
									print('removing failed')
									try:
										self.currdb.connect()
									except:
										pass
							else:
								jsonstring = "{\"actionresponse\":\"remove\", \"status\":\"NOTOK\", \"reason\": \"Access denied.\"}"
								self.send2(somesocket, jsonstring)
								print('removing failed')
						elif action == 'getfiles':
							print('getting files')
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
							print('getting files done')
						elif (action == 'update'):
							#
							# Retrieving metadata
							#
							print('updating file')
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

							primkey = '{0}#{1}'.format(owner,filename)
							#checking if file exists
							result = self.currdb.get(primkey)
							if (result!=None):
								try:
									self.currdb.insert(('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
									if ('objectdata' in packet):
										filepath = '{2}/{0}/{1}'.format(owner, filename, self.curd)
										if os.path.isfile(filepath):
											os.remove(filepath)
										_file = open(filepath, 'w')
										_file.write(packet['objectdata'])
										_file.close()
										jsonstring = jsonstring = "{\"actionresponse\":\"update\", \"status\":\"OK\"}"
										self.send2(somesocket, jsonstring)
										print('uploading successful')
									else:
										jsonstring = jsonstring = "{\"actionresponse\":\"update\", \"status\":\"OK\"}"
										self.send2(somesocket, jsonstring)
										print('uploading successful')
								except Exception,e:
									jsonstring = jsonstring = "{\"actionresponse\":\"update\", \"status\":\"NOTOK\", \"reason\": \""+self.cleansend(str(e))+"\"}"
									self.send2(somesocket, jsonstring)
									print('uploading failed')
									try:
										self.currdb.connect()
									except:
										pass
							else:
								jsonstring = "{\"actionresponse\":\"update\", \"status\":\"NOTOK\", \"reason\": \"No such file.\"}"
								self.send2(somesocket, jsonstring)
								print('updating failed')

						elif action == 'checknewfiles':
							print('checking for new files')
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
							if (jsonstring==cachefilelist):
								jsonstringX = "{\"actionresponse\":\"checknewfiles\", \"status\":\"nonewfiles\"}"
								self.send2(somesocket, jsonstringX)
								print('no new files')
							else:
								jsonstringX = "{\"actionresponse\":\"checknewfiles\", \"status\":\"newfiles\"}"
								cachefilelist = jsonstring
								self.send2(somesocket, jsonstringX)
								print('found new files')
						data = ''
		except Exception,e:
			pass
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
		#print('stopping')
		self.sockt.close()
	def request_service(self):
		(host,port) = self.sockt.getsockname()
		return '{0}:{1}'.format(host,port)
	def reallydisconnect(self,name,mac):
		self.disconnect(name)
	#Method for disconnecting user
	def disconnect(self, username):
		try:
			(sock, addr) = self.users[username]
			sock.close()
			del self.users[username]
		except:
			pass
	def cleansend(self,someval):
		someval = someval.replace('\"',"")
		someval = someval.replace('\'',"")
		return someval
