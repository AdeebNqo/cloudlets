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
import fcntl
import struct

class Client(object):
	def __init__(self,username,macaddress, ip, portX):
		self.username = username
		self.macaddress = macaddress
		self.ip = ip
		self.port = portX
		self.identifier = '{0}|{1}'.format(username, macaddress)
		self.mqttclient = mosquitto.Mosquitto(self.identifier)
		#self.mqttclient.on_publish = self.on_publish
		self.mqttclient.on_message = self.on_message
		#self.mqttclient.on_subscribe = self.on_subscribe
		self.mqttclient.on_connect = self.on_connect
		self.mqttclient.connect(ip, port=portX, keepalive=60)
		t = threading.Thread(target=self.loop)
		t.daemon = True
		t.start()
	def loop(self):
		while True:
			mqttclient.loop()
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
			self.mqttclient.subscribe('client/service_request/{}'.format(identifier),1)#receive service requests
			self.mqttclient.subscribe('client/service_request/+/{0}/recvIP'.format(identifier),1)#receive ip:port for service requests made
	def on_message(self, mosq, obj, msg):
		print(msg.topic)
		global iprequestpattern
		if (msg.topic=='client/service'):
			print(msg.payload)
		elif (msg.topic=='client/useservice/{}'.format(identifier)):
			print('trying to use service')
		elif (msg.topic=='client/connecteduser'):
			print(msg.payload)
		elif (msg.topic=='client/service_request/{0}'.format(identifier)):
			#the first thing the client should do is use the payload
			# to determine whether to allow the request
			(usrname, macaddr, servicename)  = msg.payload.split('|')
			#sending response to the requesting channel
			global servicesocket
			(ip,port) = serversocket.getsockname()
			mqttclient.publish('server/service_request/{0}/{1}|{2}'.format(servicename, usrname, macaddr), "{0}:{1}".format(ip, port))
			print('just sent address {0}:{1}'.format(ip, port))
		elif (iprequestpattern.match(msg.topic)):
			(servicename, address) = msg.payload.split('|')
			(host, port) = address.split(':')
			print('receieved address {0}:{1}'.format(host,port))
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host,int(port)))
			s.sendall('500')
		else:
			print('received {0}, on channel {1}'.format(msg.payload, msg.topic))
