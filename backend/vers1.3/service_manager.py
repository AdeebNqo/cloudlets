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
		self.modules = {}
		self.services = []
		self.runningservices = [] #services which are running, with their ports

	#
	# Loads configuration file.
	# Notifies program of available
	# services
	#
	def loadconfig(self):
		with open('services.json') as jsondata:
			services = json.load(jsondata)
		self.servicenames = services['services']
	#
	# Loads modules of services advertized
	# in configuration file
	#	
	def loadmodules(self):
		self.modules = {}
		lst = os.listdir("./services")
		for direc in lst:
			try:
				# Remove extention from filename
				if (direc.endswith('.py') or direc.endswith('.py')):
					direc = os.path.splitext(direc)[0]
				#loading module
				self.modules[direc] = __import__("services." + direc, fromlist = ["*"])
			except ImportError as err:
				pass
	#
	# Creating objects of each service.
	# Each service is to implement the service
	# abstract class
	#
	def loadservices(self):
		self.services = []
		for service in self.servicenames:
			for attr in dir(self.modules[service]):
				if attr==service:
					serviceobj = getattr(self.modules[service], attr)()
					self.services.append(serviceobj)
	#
	# Retrieve objects of all advertized
	# services
	#	
	def getservices(self):
		#
		# If there are no stored advertized services
		# load configuration file. If there are still none
		# return nothing
		#
		if (len(self.servicenames)==0):
			self.loadconfig()
			if (len(self.servicenames)==0):
				return None
		#
		# If there are no stored loaded modules, load
		# them. In the case where none exist, return
		# nothing
		#	
		if (len(self.modules)==0):
			self.loadmodules()
			if (len(self.modules)==0):
				return None
		#
		# If there are no stored service objects, load
		# them. If there are none after loading, return
		# nothing
		#
		if (len(self.services)==0):
			self.loadservices()
			if (len(self.services)==0):
				return None
		#
		# In the case where services exist,
		# return them
		#
		return self.services
