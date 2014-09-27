#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file is the test client
#
import mosquitto
import sys
import threading
import uuid
import socket
import zlib
import re
import base64

class Client(object):
	def __init__(self,username,macaddress, ip, portX):
		self.filesharingclient = None #Object that will interface with the file sharing service

		self.username = username
		self.macaddress = macaddress
		self.ip = ip
		self.port = portX
		self.identifier = '{0}|{1}'.format(username, macaddress)
		self.iprequestpattern = re.compile('client/service_request/.*/'+self.identifier+'/recvIP')
		self.mqttclient = mosquitto.Mosquitto(self.identifier)
		#self.mqttclient.on_publish = self.on_publish
		self.mqttclient.on_message = self.on_message
		#self.mqttclient.on_subscribe = self.on_subscribe
		self.mqttclient.on_connect = self.on_connect
		self.mqttclient.connect(ip, port=portX, keepalive=60)
		t = threading.Thread(target=self.loop)
		t.daemon = True
		t.start()
		#dictionary of active service interactions
		self.activeserviceclients = {}
	def loop(self):
		while True:
			self.mqttclient.loop()
	'''
	The following are actions the client can make.
	'''
	def requestservice(self,servicename):
		self.mqttclient.publish('server/useservice','{0};{1}'.format(self.identifier,servicename))
	def requestconnectedusers(self):
		self.mqttclient.publish('server/connectedusers',self.username)
	def requestavailableservices(self):
		self.mqttclient.publish('server/servicelist', self.username)
	def advertizeservices(self,services):
		self.mqttclient.publish('server/service',services)
	def requestserviceuserlist(self,servicename):
		self.mqttclient.publish('server/serviceusers','{0}|{1}'.format(servicename, self.username))
	'''
	The following are mqtt callback methods. Their names should be enough to explain
	what they do.
	'''
	def on_connect(self, mosq, obj, rc):
		if rc==0:
			self.mqttclient.subscribe('client/connecteduser/{}'.format(self.username),1)#receive connected user
			self.mqttclient.subscribe('client/service/{}'.format(self.username),1)#receive available service
			self.mqttclient.subscribe('client/serviceuserslist/{}'.format(self.username),1)#receive available service
			self.mqttclient.subscribe('client/service_request/{}'.format(self.identifier),1)#receive service requests
			self.mqttclient.subscribe('client/service_request/+/{0}/recvIP'.format(self.identifier),1)#receive ip:port for service requests made
	def on_message(self, mosq, obj, msg):
		if (msg.topic==('client/service/{}'.format(self.username))):
			#print('cloudlet service is {}'.format(msg.payload))
			debug = 0
		elif (msg.topic=='client/useservice/{}'.format(self.identifier)):
			#print('trying to use service')
			debug = 0
		elif (msg.topic=='client/connecteduser/{}'.format(self.username)):
			#print('cloudlet connected user is {}'.format(msg.payload))
			debug = 0
		elif (msg.topic=='client/serviceuserslist/{}'.format(self.username)):
			#print('file_sharer user is {}'.format(msg.payload))
			debug = 0
		elif (msg.topic=='client/service_request/{0}'.format(self.identifier)):
			#the first thing the client should do is use the payload
			# to determine whether to allow the request
			(usrname, macaddr, servicename)  = msg.payload.split('|')
			#sending response to the requesting channel
			#global servicesocket
			#(ip,port) = serversocket.getsockname()
			mqttclient.publish('server/service_request/{0}/{1}|{2}'.format(servicename, usrname, macaddr), "{0}:{1}".format('127.0.0.1', 80))
			#print('just sent address {0}:{1}'.format(ip, port))
		elif (self.iprequestpattern.match(msg.topic)):
			(servicename, address) = msg.payload.split('|')
			(host, port) = address.split(':')
			self.filesharingclient = FileSharingClient(self.username, self.ip, int(port))
			self.activeserviceclients[servicename] = (self.filesharingclient)
		else:
			print('received {0}, on channel {1}'.format(msg.payload, msg.topic))
'''
The following class should handle all interactions between
client and cloudlet with respect to the file sharing services
'''
import json
class FileSharingClient(object):
	def __init__(self,username, ip, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip,port))
		self.username = username
		self.identify()
		self.recvdata = ''
	def identify(self):
		jsonstring = "{\"action\":\"identify\", \"username\":\""+self.username+"\"}"
		self.send(jsonstring)
	def upload(self, duration, access, accesslist, compression, filename, objectdata):
		objectdata = base64.b64encode(objectdata)
		jsonstring = "{\"action\":\"upload\", \"duration\":\""+duration+"\", \"access\":\""+access+"\", \"accesslist\":"
		if accesslist==None:
			jsonstring += "\"None\""
		else:
			jsonstring += "\""+":".join(accesslist)+"\""
		jsonstring += ",\"compression\":\""+compression+"\", \"filename\":\""+filename+"\", \"owner\":\""+self.username+"\", \"objectdata\":\""+objectdata+"\"}"
		self.send(jsonstring)
		return self.recv()
	def remove(self,owner,filename):
		jsonstring = "{\"action\":\"remove\", \"owner\":\""+owner+"\", \"requester\":\""+self.username+"\", \"filename\":\""+filename+"\"}"
		self.send(jsonstring)
		return self.recv()
	def download(self, owner, requester, filename):
		jsonstring = "{\"action\":\"download\", \"owner\":\""+owner+"\", \"requester\":\""+requester+"\", \"filename\":\""+filename+"\"}"
		self.send(jsonstring)
		return self.recv()
	def heartbeat(self):
		print('heartbeat')
		jsonstring = "{\"action\":\"heartbeat\"}"
		self.send(jsonstring)
		response = self.recv()
		if (response['status']!='OK'):
			#connecting broken
			self.s.close()
	def transfer(self, owner, receiver, oncloudlet, filename, objectdata):
		objectdata = base64.b64encode(objectdata)
		jsonstring = "{\"action\":\"transfer\", \"owner\":\""+owner+"\", \"receiver\":\""+receiver+"\", \"oncloudlet\":\""+oncloudlet+"\", \"filename\":\""+filename+"\", \"objectdata\":\""+objectdata+"\"}"
		self.send(jsonstring)
		return self.recv()
	def getaccessiblefiles(self):
		jsonstring = "{\"action\":\"getfiles\", \"requester\":\""+self.username+"\"}"
		self.send(jsonstring)
		return self.recv()
	def checknewfiles(self):
		jsonstring = "{\"action\":\"checknewfiles\", \"requester\":\""+self.username+"\"}"
		self.send(jsonstring)
		return self.recv()
	def send(self, jsonstring):
		length = len(jsonstring)
		self.s.sendall("{}".format(length))
		response = self.s.recv(1024)
		if (response=='OK'):
			self.s.sendall(jsonstring)
	def recv(self):
		length = ''
		while (length=='' or length==None):
			length = self.s.recv(1024)
			pass
		length = int(length)
		self.s.sendall('OK')
		data = ''
		if self.recvdata != '':
			data += self.recvdata
		recvsize = 0
		while (recvsize < length):
			datachunk = self.s.recv(1024)
			if (datachunk != None):
				recvsize = recvsize + len(datachunk)
				data += datachunk
		return json.loads(data)
