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
class handler(object):
	def __init__(self,mqttserver):
		self.serviceman = servicemanager.servicemanager()
		self.mqttserver = mqttserver
		self.load_services()
		self.connectedusers = {} #users connected to cloudlet
		#starting all registered services
		for service in self.serviceman.get_services():
			service.start()
	def connect_user(self,details):
		self.connectedusers[details] = set()
	def disconnect_user(self,details):
		del self.connectedusers[details]
	def use_service(self,details,servicename):
		self.connectedusers[details].add(self.serviceman.get_service(servicename))
	def load_services(self):
		for service in self.serviceman.get_services():
			self.mqttserver.subscribe(service.name,1)
