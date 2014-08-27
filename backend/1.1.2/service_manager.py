#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Class to manage registered services
#
import json
import types
import os
from pprint import pprint
class service_manager(object):
	def __init__(self):
		self.loadconfig()
	def loadconfig(self):
		with open('services.json') as jsondata:
			services = json.load(jsondata)
		self.servicenames = services['services']
	def loadmodules(self):
		self.modules = {}
		lst = os.listdir("./services")
		for direc in lst:
			try:
				if (direc.endswith('.py') or direc.endswith('.py')):
					direc = os.path.splitext(direc)[0]
				self.modules[direc] = __import__("services." + direc, fromlist = ["*"])
			except ImportError as err:
				pass
	def loadservices(self):
		self.services = []
			for service in self.servicenames:
				for attr in dir(self.modules[service]):
					if attr==service:
						serviceobj = getattr(self.modules[service], attr)()
						self.services.append(serviceobj)
	def getservices(self):
		if (len(self.modules)>0):
			self.loadservices()
			return self.services
		else:
			return None
