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
import select

class mqttEventEmitter(object):
	def __init__(self, port):
		print('event handler started...fuck dat b!')
		self.connect = re.compile('(\d+): New client connected from (.+) as (.+).')
		self.disconnect = re.compile('.*, disconnecting.')
		self.t = threading.Thread(target=self.startmosquitto, args=(port,))
		self.t.daemon = True
		self.t.start()
	#
	# This method starts Mosquitto
	# and reads all the error messages it
	# produces.
	def startmosquitto(self, port):	
		process = subprocess.Popen('mosquitto -p {}'.format(port), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)		
		# Poll process for new output until finished
		while True:
			#the items to be read by process
			reads = [process.stderr.fileno()]
			returned = select.select(reads, [], [])
			for readydata in returned[0]:
				#if (readydata == process.stdout.fileno()):
				#	self.processline(process.stdout.readline())
				if (readydata == process.stderr.fileno()):
					self.processline(process.stderr.readline())
	#	
	# Method for processing line comming out of mosquitto
	#
	def processline(self,line):
		if (len(line)>0):
			lines = line.split('\n')
			if (len(lines)>1):
				for line in lines:
					self.notify(line)
			else:
				self.notify(line)
					
	#
	# Method called when an
	# error message is receieved.
	#
	def notify(self,value):
		if self.connect.match(value):
			print('detected connection')
			(username,macaddress) = re.search(self.connect,value).group(3).split('|')
			macaddress = macaddress.split()[0]
			print('connected person has details (username,macaddress): ({0}, {1})'.format(username,macaddress))
			broadcaster.connect(username,macaddress)
		elif self.disconnect.match(value):
			print('detected disconnection')
			items = value.split()
			vals = items[len(items)-2].split('|')
			print('disconnected person has details (username,macaddress): ({0}, {1})'.format(vals[0], vals[1][:len(vals[1])-1]))
			broadcaster.disconnect(vals[0],vals[1][:len(vals[1])-1])
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
