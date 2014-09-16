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

class Client(object):
	def __init__(self,username,macaddress, ip, portX):
		self.username = username
		self.macaddress = macaddress
		self.ip = ip
		self.port = portX
		self.identifier = '{0}|{1}'.format(username, macaddress)
		print(self.identifier)
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
	def requestservice(servicename):
		self.mqttclient.publish('server/useservice','{0};{1}'.format(self.identifier,servicename))
	def requestconnectedusers(self):
		self.mqttclient.publish('server/connectedusers',"true")
	def requestavailableservices(self):
		self.mqttclient.publish('server/servicelist',"true")
	def advertizeservices(self,services):
		self.mqttclient.publish('server/service',services)
	'''
	The following are mqtt callback methods. Their names should be enough to explain
	what they do.
	'''
	def on_connect(self, mosq, obj, rc):
		if rc==0:
			print('connected!')
			self.mqttclient.subscribe('client/connecteduser',1)#receive connected user
			self.mqttclient.subscribe('client/service',1)#receive available service
			self.mqttclient.subscribe('client/service_request/{}'.format(self.identifier),1)#receive service requests
			self.mqttclient.subscribe('client/service_request/+/{0}/recvIP'.format(self.identifier),1)#receive ip:port for service requests made
	def on_message(self, mosq, obj, msg):
		print(msg.topic)
		if (msg.topic=='client/service'):
			print(msg.payload)
		elif (msg.topic=='client/useservice/{}'.format(self.identifier)):
			print('trying to use service')
		elif (msg.topic=='client/connecteduser'):
			print(msg.payload)
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
			print('receieved address {0}:{1}'.format(host,port))
			self.filesharingclient = FileSharingClient(self.username, host, int(port))
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
		self.s.connect((host,port))
		self.username = username
		self.identify()
		self.recvdata = ''
	def identify(self):
		jsonstring = "{\"action\":\"identify\", \"username\":\""+self.username+"\"}"
		self.send(jsonstring)
	def upload(self, duration, access, accesslist=[None], compression, filename, owner, objectdata):
		print('upload')
		jsonstring = "{\"duration\":\"{0}\", \"access\":\"{1}\", \"accesslist\":{2}, \"compression\":\"{3}\", \"filename\":\"{4}\", \"owner\":\"{5}\", \"objectdata\":\"{6}\"".format(duration, access, accesslist, compression, filename, owner, objectdata)
		self.send(jsonstring)
	def remove(self,owner,filename):
		jsonstring = "{\"action\":\"remove\", \"owner\":\"{0}\", \"filename\":\"{1}\"}".format(owner, filename)
		self.send(jsonstring)
	def download(self, owner, requester, filename):
		jsonstring = "{\"owner\":\"{0}\", \"requester\":\"{1}\", \"filename\":\"{2}\"}".format(owner, requester, filename)
		self.send(jsonstring)
	def heartbeat(self):
		print('heartbeat')
		jsonstring = "{\"action\":\"heartbeat\"}"
		self.send(jsonstring)
		response = self.recv()
		if (response['status']!='OK'):
			#connecting broken
			self.s.close()
	def transfer(self, owner, receiver, oncloudlet, filename, objectdata):
		print('transfer')
		jsonstring = "{\"action\":\"transfer\", \"owner\":\"{0}\", \"receiver\":\"{1}\", \"oncloudlet\":\"{2}\", \"filename\":\"{3}\", \"objectdata\":\"{4}\"}".format(owner, receiver, oncloudlet, filename, objectdata)
		self.send(jsonstring)
	def send(self, jsonstring):
		length = len(jsonstring)
		self.s.sendall(length)
		response = self.s.recv(1024)
		if (response=='OK'):
			self.s.sendall(jsonstring)
	def recv(self):
		length = int(self.s.recv(1024))
		data = None
		if self.recvdata != '':
			data += self.recvdata
		while (len(data) < length):
			data += self.s.recv(1024)
		self.recvdata = data[length:]
		data = data[:length]
		return json.loads(data)
