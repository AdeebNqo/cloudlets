#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file starts mosquitto and registers connect/disconnect events
# 
#
from asyncproc2 import Process
import threading
import os
class mqttEventEmitter(object):
	def __init__(self, port):
		self.t = threading.Thread(target=self.startmosquitto, args=(port,))
		self.t.daemon = True
		self.t.start()
	#
	# This method starts Mosquitto
	# and reads all the error messages it
	# produces.
	def startmosquitto(self, port):
		proc = Process('mosquitto','-p','{}'.format(port))
		while True:
			# check to see if process has ended
			poll = proc.wait(os.WNOHANG)
			if poll != None:
				break
			# print any new output
			out = proc.readerr()
			if out != "":
				lines = out.split('\n')
				if (len(lines)>1):
					for line in lines:
						self.notify(line)
				else:
					self.notify(out)
	#
	# Method called when an
	# error message is receieved.
	#
	def notify(self,value):
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
