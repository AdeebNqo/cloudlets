#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Connector for interfacing with client requests
#
import threading
import mosquitto

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
		while self.status:
			mqttserver.loop()
