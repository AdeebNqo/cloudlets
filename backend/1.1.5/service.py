#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file represents a service
#
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
