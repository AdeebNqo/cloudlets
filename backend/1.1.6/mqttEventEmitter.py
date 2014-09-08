#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file starts mosquitto and registers connect/disconnect events
# 
#
import threading
import os
import broadcaster
import re
import subprocess
import broadcaster

class mqttEventEmitter(object):
	def __init__(self, port):
		self.connect = re.compile('(\d+): New client connected from (.+) as (.+).')
		self.disconnect = re.compile('\d+: Socket read error on client .+, disconnecting.')
		self.t = threading.Thread(target=self.startmosquitto, args=(port,))
		self.t.daemon = True
		self.t.start()
	#
	# This method starts Mosquitto
	# and reads all the error messages it
	# produces.
	def startmosquitto(self, port):	
		process = subprocess.Popen('mosquitto -p {}'.format(port),shell=True,stderr=subprocess.PIPE)
		# Poll process for new output until finished
		while True:
			nextline = process.stderr.readline()
			if nextline == '' and process.poll() != None:
				break
			lines = nextline.split('\n')
			if (len(lines)>1):
				for line in lines:
					self.notify(line)
			else:
				self.notify(nextline)
					
	#
	# Method called when an
	# error message is receieved.
	#
	def notify(self,value):
		if self.connect.match(value):
			(username,macaddress) = re.search(self.connect,value).group(3).split('|')
			broadcaster.connect(username,macaddress)
			print('connect: {}'.format(username))
		elif self.disconnect.match(value):
			items = value.split()
			vals = items[len(items)-2].split('|')
			broadcaster.disconnect(vals[0],vals[1][:len(vals[1])-1])
			print('disconnect: {}'.format(vals[0]))
		else:
			print(value)
	#
	# This method should be used to block
	# the classes that created mqttEventHandler
	# to exit. Exiting should only be achieved through
	# ctrl-c
	#
	def wait(self):
		while True:
		    self.t.join(600)
		    if not self.t.isAlive():
			break
