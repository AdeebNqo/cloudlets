#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This class handles communication between the services
# and the broker
#
# "If builders built buildings the way programmers wrote programs, then
#  the first woodpecker that came along wound destroy civilization."
# -Gerald Weinberg
import servicemanager
import sys
class handler(object):
	def __init__(self,mqttserver, runtimemodule):
		print('creating handler...')
		mosquitto_controller = runtimemodule
		print(dir(mosquitto_controller))
		self.serviceman = servicemanager.servicemanager()
		self.mqttserver = mqttserver #Mqtt Broker connection
		self.load_services()
		self.connectedusers = {} #users connected to cloudlet
		self.runningservices = []
		#starting all registered services
		for service in self.serviceman.get_services():
			servicename = service.name.split('=')[1]
			for attr in dir(service.module):
				if (attr==servicename):
					serviceobj = getattr(service.module, attr)()
					serviceobj.start(mqttserver)
					self.runningservices.append(serviceobj)
		print(dir(mosquitto_controller))
		mosquitto_controller.connectsubcribe(self.userdisconnecting)
		print('handler created!')
		print(mosquitto_controller.connectsubcribers)
	def connect_user(self,details):
		self.connectedusers[details] = set()
	def disconnect_user(self,details):
		del self.connectedusers[details]
	def use_service(self,details,servicename):
		self.connectedusers[details].add(self.serviceman.get_service(servicename))
	def load_services(self):
		for service in self.serviceman.get_services():
			self.mqttserver.subscribe(service.name,1)
	def get_servicedetails(self):
		rlist = []
		for service in self.serviceman.get_services():
			rlist.append(service.__str__())
		return rlist
	def get_connectedusers(self):
		return self.connectedusers.keys()
	def userdisconnecting(self,userdetails):
		print('helo connect user')
	def userconnecting(self,userdetails):
		print('world')
