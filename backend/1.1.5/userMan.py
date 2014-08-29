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
				if username=='usr':
					return 'UDUP'
				elif macaddress==mac:
					return 'MDUP'
			self.connectedusers[(username,macaddress)] = set()
			return 'OK'
	def disconnect(self,username,macaddress):
		del self.connectedusers[(username,macaddress)]
