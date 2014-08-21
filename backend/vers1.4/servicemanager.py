#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Class handles the loading of all available
# services.
#
# "On two occasions, I have been asked [by members of Parliament],
# 'Pray, Mr. Babbage, if you put into the machine wrong figures, will the right answers come out?'
# I am not able to rightly apprehend the kind of confusion of
# ideas that could provoke such a question."
#
# -Charles Babbage

import os
import lex
class service(object):
	def __init__(self, name, cloudletv, description, authors, copyright, website):
		self.name = name
		self.cloudletv = cloudletv
		self.description = description
		self.authors = authors
		self.copyright = copyright
		self.website = website
	def add_module(self,module):
		self.module = module
class servicemanager(object):
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
		self.t_Name = r'\AName=(.)*\Z'
		self.t_CloudletV = r'\ACloudletV=(.)*\Z'
		self.t_Description = r'\ADescription=(.)*\Z'
		self.t_Authors = r'\AAuthors=(.)*\Z'
		self.t_Copyright = r'\ACopyright=(.)*\Z'
		self.t_Website = r'\AWebsite=(.)*\Z'
		self.analyzer = lex.lex(module=self)
		#loading services
		self.update()
	def update(self):
		# Method that will read in services
		# from disk. Should always called when there
		# are new services
		self.curdir = os.getcwd()
		self.servicesfolder = '{0}{1}services'.format(self.curdir, os.sep)
		self.servicefolders = [x[0] for x in os.walk(self.servicesfolder)]
		self.services = []
		if (len(self.services)>0):
			for folder in self.servicefolders:
				input_data = ''
				desc = open('{0}{1}description.txt'.format(folder,os.sep))
				for line in desc.readlines():
					input_data+=line
				analyzer.input(input_data)
				name = None
				cloudletv = None
				description = None
				authors = None
				copyright = None
				website = None
				for token in analyzer:
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
				someservice.add_module(__import__(folder, fromlist = ["*"]))
				self.services.append(someservice)
	def get_services(self):
		return self.services
	def get_service(self,servicename):
		for service in self.services:
			if (service.name==servicename):
				return service
		return None
	#
	# Echo error when parsing description file
	#
	def t_error(self,token):
		print("Illegal character '%s'" % token.value[0])
		token.lexer.skip(1)
