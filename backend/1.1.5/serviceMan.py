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
				someservice = service(name, cloudletv, description, authors, copyright, website)
				someservice.add_module(imp.load_source(name.split('=')[1], '{0}/__init__.py'.format(folder)))
				self.services.append(someservice)
	def service_request(self,userdetails,servicename):
		for service in self.services:
			print(service.name)
			if (service.name=='Name={}'.format(servicename)):
				return 'OK'
		return 'NE'
	def get_services(self):
		return self.services
	#
	# Echo error when parsing description file
	#
	def t_error(self,token):
		#print("Illegal character {}".format(token.value[0]))
		token.lexer.skip(1)
