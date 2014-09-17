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
		self.blocklist = set()
		self.simplename = self.name.split('=')[1]
	def set_owner(self, username, macaddress):
		self.username = username
		self.macaddress = macaddress
	def block(self,username,macaddress):
		self.blocklist.add((username,macaddress))
	def block(self,username,macaddress):
		self.blocklist.remove((username,macaddress))
	def isallowed(self,username,macaddress):
		return (not ((username,macaddress) in self.blocklist))
	def add_module(self,module):
		self.obj = getattr(module, self.simplename)()
		self.obj.start()
	def ipport(self):
		#check if service on mobile
		if (not 'obj' in self.__dict__.keys()):
			print('did not find obj')
			return '{0}|{1}'.format(self.username, self.macaddress)
		else:
			if (self.obj!=None):
				return self.obj.request_service()
			elif (self.username!='local' and self.macaddress!='local'):
				return '{0}|{1}'.format(self.username, self.macaddress)
			else:
				return 'Service not available'
	def __str__(self):
		return '{0};{1};{2};{3};{4};{5}'.format(self.name,self.cloudletv,self.description,self.authors,self.copyright,self.website)
