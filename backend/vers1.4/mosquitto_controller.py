#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This is the class that starts mosquitto. it exists
# so that we can be able to capture client (dis)connections.
#
# "I did not attend his funeral, but I sent a nice letter saying
#  I approved of it."
#  -Mark Twain
#
import os
from asyncproc import Process
import threading
import re
class ConnectionBroadcaster(object):
	def __init__(self):
		self.connect = re.compile('\d+: New client connected from .+ as .+.')
		self.disconnect = re.compile('\d+: Socket read error on client .+, disconnecting.')
		self.t = threading.Thread(target=self.process)
		self.t.daemon = True
		self.t.start()
		self.subscribers = []
	def process(self):
		proc = Process('mosquitto')
		while True:
			# check to see if process has ended
			poll = proc.wait(os.WNOHANG)
			if poll != None:
				break
			# print any new output
			out = proc.readerr()
			if out != "":
				if self.connect.match(out):
					print('connect')
					for subscriber in self.subscribers:
						subscriber.userconnecting()
				elif self.disconnect.match(out):
					print('disconnect')
					items = out.split()
					print(items)
					for subscriber in self.subscribers:
						subscriber.userdisconnect()
				else:
					print(out)
	def wait(self):
		self.t.join()
if __name__=='__main__':
	broad = ConnectionBroadcaster()
	broad.wait()
