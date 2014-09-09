#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# File sharing service
# 
# "Any sufficiently advanced bug is indistinguishable from a feature."
# -Bruce Brown
#
import json
class file_sharer():
	def __init__(self):
		print('service created')
	def start(self):
		print('starting')
	def stop(self):
		print('stopping')
	def request_service(self):
		print('requesting open ip:port')
		return '127.0.0.1:80'
