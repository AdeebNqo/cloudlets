#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file keeps track of who is connected to cloudlet
#
# "If builders built buildings the way programmers wrote programs, then
#  the first woodpecker that came along wound destroy civilization."
# -Gerald Weinberg
#
class userMan(object):
	def __init__(self):
		self.connectedusers = {} #users connected to cloudlet
	def connect(self,username,macaddress):
		if len(self.connectedusers)==0:
			self.connectedusers[(username,macaddress)] = set()
			return 'OK'
		else:
			for (usr,mac) in self.connectedusers.iterkeys():
				if username==usr:
					return 'UDUP'
				elif macaddress==mac:
					return 'MDUP'
			self.connectedusers[(username,macaddress)] = set()
			return 'OK'
	def disconnect(self,username,macaddress):
		del self.connectedusers[(username,macaddress)]
	#
	# This method should be called by the communication
	# handler when a client requests a service
	#
	def service_request(self,userdetails,servicename):
		try:
			if servicename in self.connectedusers[userdetails]:
				return 'NOTOK'
			else:
				self.connectedusers[userdetails].add(servicename)
				return 'OK'
		except KeyError:
			return 'OK'
	#
	# Method for getting all connected users
	#
	def get_connected(self):
		return self.connectedusers.keys()
	#
	# Method to retrieve all services used by a client
	# returns set of services
	#
	def get_servicesofclient(self,nameandmacaddr):
		return self.connectedusers[nameandmacaddr]
