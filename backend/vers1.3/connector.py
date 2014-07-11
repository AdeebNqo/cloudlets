#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Connector for interfacing with client requests
#
import threading
import mosquitto
import time
from service_manager import service_manager
from user_manager import user_manager,user

class connector(object):
	def __init__(self,mqtthost,mqttport):
		self.mqtthost = mqtthost
		self.mqttport = mqttport
		self.status = True
		self.serviceman = service_manager()
		self.peopleman = user_manager()
	def start(self):
		self.status = True
		serveforeverthread = threading.Thread(target=self.reallystart)
		serveforeverthread.daemon = True
		serveforeverthread.start()
	def stop(self):
		self.status = False
	def reallystart(self):
		mqttserver = mosquitto.Mosquitto('server')
		mqttserver.on_subscribe = self.on_subscribe
		mqttserver.on_connect = self.on_connect
		mqttserver.on_message = self.on_message
		mqttserver.on_unsubscribe = self.on_unsubscribe
		mqttserver.connect('127.0.0.1', port=self.mqttport, keepalive=60)
		while self.status:
			mqttserver.loop()
			#time.sleep(300)
	#
	#
	def on_subscribe(self, mosq, obj, mid, qos_list):
		print("Subscribe with mid "+str(mid)+" received.")
	def on_unsubscribe(self, mosq, obj, mid):
		print("Unsubscribe with mid "+str(mid)+" received.")	
	#
	# Connection callback
	# Used for registering to certain
	# topics -- avoiding massive traffic from
	# clients
	#
	def on_connect(self,mosq, obj, rc):
		print('connected!')
		if (rc==0):
			#
			# If connection is successful, register for topicse
			mosq.subscribe("client/connect",1)
			mosq.subscribe('client/disconnect',1)
			mosq.subscribe('client/list', 1)
			mosq.subscribe('client/servicelist',1)
			print('subscribed.')
		elif (rc==1):
			raise Exception('Mosquitto error: Unacceptable protocol version')
		elif (rc==2):
			raise Exception('Mosquitto error: Identifier rejected')
		elif (rc==3):
			raise Exception('Mosquitto error: Server unavailable')
		elif (rc==4):
			raise Exception('Mosquitto error: Bad user name or password')
		elif (rc==5):
			raise Exception('Mosquitto error: Not authorised')
	#
	# Handling incoming messages on subscribed topics
	#
	def on_message(self,mosq, obj, msg):
		print("receiving {0} on topic {1}.".format(msg.payload, msg.topic))
		if (msg.topic=='client/connect'):
			vals = msg.payload.split()
			person = user(vals[0],vals[1])
			self.peopleman.connect(person)
			print('client connected')
		elif (msg.topic=='client/disconnect'):
			print('client disconnected')
			vals = msg.payload.split()
			person = user(vals[0],vals[1])
			self.peopleman.disconnect(person)
		elif (msg.topic=='client/list'):
			print('client list requested')
			connected = self.peopleman.getconnected()
			for person in connected:
				mosq.publish('server/connecteduser',person.getusername())
		elif (msg.topic=='client/servicelist'):
			print('service list requested')
			services = self.serviceman.getservices()
			for service in services:
				#print('publishing service \'{0}\''.format(str(service)))
				mosq.publish('server/service', '{0}-{1}'.format(str(service),service.start()))
				self.serviceman.runningservices.append((service,service.port))
