#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Connector for interfacing with client requests
#
import threading
import mosquitto
import time

class connector(object):
	def __init__(self,mqtthost,mqttport):
		self.mqtthost = mqtthost
		self.mqttport = mqttport
		self.status = True
	def start(self):
		self.status = True
		serveforeverthread = threading.Thread(target=self.reallystart)
		serveforeverthread.daemon = True
		serveforeverthread.start()
	def stop(self):
		self.status = False
	def reallystart(self):
		mqttserver = mosquitto.Mosquitto('server')
		mqttserver.connect('127.0.0.1', port=self.mqttport, keepalive=60)
		mqttserver.on_connect = self.on_connect
		mqttserver.on_message = self.on_message
		while self.status:
			mqttserver.loop()
			time.sleep(300)
	#
	# Connection callback
	# Used for registering to certain
	# topics -- avoiding massive traffic from
	# clients
	#
	def on_connect(self,mosq, obj, rc):
		if (rc==0):
			#
			# If connection is successful, register for topics
			print('success')
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
