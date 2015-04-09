import service as serv
import json
import lex
import os
import imp
import traceback
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
		self.services = set()
		#
		# Fields that will keep reference to the
		# services
		#
		self.curdir = os.path.dirname(__file__)
		print(self.curdir)
		self.servicesfolder = '{0}{1}services'.format(self.curdir, os.sep)
		self.servicefolders = [x[0] for x in os.walk(self.servicesfolder)]

	def add_service(self, source):
		data = json.loads(source)
		username = data['username']
		macaddress = data['macaddress']
		for service in data['services']:
			self.analyzer.input(service)
			name,cloudletv,description,authors,copyright,website = (None,)*6
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
			someservice = serv.service(name, cloudletv, description, authors, copyright, website)
			someservice.set_owner(username, macaddress)
			self.services.add(someservice)
	def remove_service(self, identifier, servicename):
		(username, macaddress, servicename) = identifier.split('|')
		for service in self.services:
			if (service.macaddress==macaddress and service.username==username and service.name=='Name={}'.format(servicename)):
				self.services.remove(service)
	def remove_allservices(self,identifier):
		(username, macaddress) = identifier.split('|')
		for service in self.services:
			if (service.macaddress==macaddress and service.username==username):
				self.services.remove(service)
	def loadlocal_services(self):
		if (len(self.servicefolders)>1):
			for folder in self.servicefolders[1:]:
				try:
					input_data = ''
					desc = open('{0}{1}description.txt'.format(folder,os.sep))
					for line in desc.readlines():
						input_data+=line
						self.analyzer.input(input_data)
						name,cloudletv,description,authors,copyright,website = (None,)*6
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
					someservice = serv.service(name, cloudletv, description, authors, copyright, website)
					someservice.add_module(imp.load_source(name.split('=')[1], '{0}/__init__.py'.format(folder)))
					someservice.macaddress = 'local'
					someservice.username = 'local'
					self.services.add(someservice)
				except Exception,e:
					pass
					#traceback.print_exc()
	def request_service(self, userdetails, servicename):
		for service in self.services:
			if (service.simplename==servicename and service.isallowed(userdetails[0], userdetails[1])):
				response = 'OK '+service.ipport()
				return response
		return 'NE'
	def get_servicelist(self):
		return self.services
	#
	# Method for removing person from services
	#
	def disconnectfromservice(self, servicename, username):
		try:
			for service in self.services:
				if (service.name == 'Name={}'.format(servicename)):
					service.disconnect(username)
					break
		except:
			pass
	'''
	Skiping errors when parsing service description file

	'''
	def t_error(self,token):
		token.lexer.skip(1)
