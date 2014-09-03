#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file loads the cloudlet services. Also is
# in charge of handling service requests
# 
#
from service import service
import lex
import imp
import os
class serviceMan(object):
	def __init__(self):
		#regular expressions for the tokens
		self.tokens = [
			'Name',
			'CloudletV',
			'Description',
			'Authors',
			'Copyright',
			'Website'
			]
		self.t_Name = r'Name=.*'
		self.t_CloudletV = r'CloudletV=.*'
		self.t_Description = r'Description=.*'
		self.t_Authors = r'Authors=.*'
		self.t_Copyright = r'Copyright=.*'
		self.t_Website = r'Website=.*'
		self.analyzer = lex.lex(module=self)
		#
		# Fields that will keep reference to the
		# services
		#
		self.curdir = os.getcwd()
		self.servicesfolder = '{0}{1}services'.format(self.curdir, os.sep)
		self.servicefolders = [x[0] for x in os.walk(self.servicesfolder)]
		self.services = []
		self.serviceobjs = []
	'''
	Loading services from memory.
	The "service" objects will be stored in "self.services"

	The service will not be loaded if the cloudlet version and
	it's name is not provided. In the future, no service will
	be loaded unless it has all the fields in the description file.
	'''
	def load(self):
		if (len(self.servicefolders)>1):
			del self.services[:]
			for folder in self.servicefolders[1:]:
				input_data = ''
				desc = open('{0}{1}description.txt'.format(folder,os.sep))
				for line in desc.readlines():
					input_data+=line
					self.analyzer.input(input_data)
					name = None
					cloudletv = None
					description = None
					authors = None
					copyright = None
					website = None
					for token in self.analyzer:
						if (token.type=='Name'):
							name = token.value
						elif (token.type=='CloudletV'):
							cloudletv = token.value
						elif (token.type=='Description'):
							description = token.value
						elif (token.type=='Authors'):
							authors = token.value
						elif (token.type=='Copyright'):
							copyright = token.value
						elif (token.type=='Website'):
							website = token.value
				if (name!=None and cloudletv!=None):
					someservice = service(name, cloudletv, description, authors, copyright, website)
					someservice.add_module(imp.load_source(name.split('=')[1], '{0}/__init__.py'.format(folder)))
					self.services.append(someservice)
	'''
	Loads the actual service objects into a list
	'''
	def load_serviceobj(self):
		del self.serviceobjs[:]
		for service in self.services:
			name = service.name.split('=')[1]
			serviceobj = getattr(service.module, name)()
			self.serviceobjs.append(serviceobj)
	'''
	Checking the existence of a service. This is used
	when a client requests a service.
	'''
	def service_request(self,userdetails,servicename):
		for service in self.services:
			print(service.name)
			if (service.name=='Name={}'.format(servicename)):
				return 'OK'
		return 'NE'
	'''
	Retrieving the list of loaded services
	'''	
	def get_services(self):
		return self.services
	'''
	Retrieve service by name from loaded services.
	
	Arguments:
	servicename: The name of the service to be retrieved
	'''
	def get_service(self,servicename):
		for service in self.services:
			if (service.name==servicename):
				return service
		return None
	'''
	Retrieve service object by name from loaded services objects.
	
	Arguments:
	servicename: The name of the service object to be retrieved
	'''
	def get_serviceobj(self,servicename):
		for service in self.serviceobjs:
			if (service.__class__.__name__==servicename):
				return service
		return None
	'''
	Transfering service requests between communication handler
	and the services.

	Arguments:
	channel: The channel that received the data
	payload: The data being sent by the client
	'''
	def transfer_request(self,channel,payload):
		vals = channel.split('/')
		requested_service = self.get_serviceobj(vals[1])
		requested_function = getattr(requested_service, vals[3])
		return requested_function(payload)
	'''
	Skiping errors when parsing service description file
	
	'''
	def t_error(self,token):
		#print("Illegal character {}".format(token.value[0]))
		token.lexer.skip(1)
