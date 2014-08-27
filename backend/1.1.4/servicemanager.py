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
import sys
import imp

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
	def __str__(self):
		return '{0};{1};{2};{3};{4};{5}'.format(self.name,self.cloudletv,self.description,self.authors,self.copyright,self.website)
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
		self.t_Name = r'Name=.*'
		self.t_CloudletV = r'CloudletV=.*'
		self.t_Description = r'Description=.*'
		self.t_Authors = r'Authors=.*'
		self.t_Copyright = r'Copyright=.*'
		self.t_Website = r'Website=.*'
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
		if (len(self.servicefolders)>1):
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
		print("Illegal character {}".format(token.value[0]))
		token.lexer.skip(1)
