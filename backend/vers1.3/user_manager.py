#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Connected people management
#

class user(object):
	def __init__(self, macaddress, username):
		self.macaddr = macaddress
		self.username = username
	def getusername(self):
		return self.username
	def getmacaddr(self):
		return self.macaddr

class user_manager(object):
	def __init__(self):
		self.connected = []
		self.recentlyconnected = []
	#
	# Called when user connects
	def connect(self,user):
		print('user connected')
	#
	# Called when user disconnects
	def disconnect(self,user):
		print('user disconnected')
	#
	# Retrieve number of connected users
	def numconnected(self):
		return len(self.connected)
	#
	# Retrieve connected users
	def getconnected(self):
		return self.connected
