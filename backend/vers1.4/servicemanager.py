#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Class handles the loading of all available
# services.
#
# “On two occasions, I have been asked [by members of Parliament],
# 'Pray, Mr. Babbage, if you put into the machine wrong figures, will the right answers come out?'
# I am not able to rightly apprehend the kind of confusion of
# ideas that could provoke such a question.” 
#
# -Charles Babbage

import os
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
		self.update()
	def update(self):
		# Method that will read in services
		# from disk. Should always called when there
		# are new services
		self.curdir = os.getcwd()
		self.servicesfolder = '{0}{1}services'.format(self.curdir, os.sep)
		self.servicefolders = [x[0] for x in os.walk(self.servicesfolder)]
		self.services = []
		for folder in self.servicefolders:
			desc = open('{0}{1}description.txt'.format(folder,os.sep)
			someservice = new service() ##parse description docs and parse it here
			someservice.add_module(__import__(folder, fromlist = ["*"]))
			self.services.append(someservice)
	def get_services(self):
		return self.services
