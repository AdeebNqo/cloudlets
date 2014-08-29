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
		print('trying connect {}'.format(username))
