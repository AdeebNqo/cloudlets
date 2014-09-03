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
	def start(self, mqttserver):
		print('starting')
	def stop(self):
		print('stopping')
	def upload(self,payload):
		metdata = json.load(payload)
		#check file duplicates
		#if ok - create thread that will wait for client to send file
		#send response
		return 'upload called'
	def remove(self,payload):
		return 'remove called'
	def fetch(self,payload):
		return 'fetch called'
	def update(self,payload):
		return 'update called'
