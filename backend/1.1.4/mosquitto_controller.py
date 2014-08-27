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

t = None
connectsubcribers = []
disconnectsubcribers = []
connect = re.compile('(\d+): New client connected from (.+) as (.+).')
disconnect = re.compile('\d+: Socket read error on client .+, disconnecting.')

def main():
	global t
	t = threading.Thread(target=process)
	t.daemon = True
	t.start()
def process():
	proc = Process('mosquitto')
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
					notify(line)
			else:
				notify(out)
def connectsubcribe(func):
	connectsubcribers.append(1)
def disconnectsubcribe(func):
	disconnectsubcribers.append(func)
def notify(val):
	if connect.match(val):
		print('connect')
		print('x'+val+'x')
		if len(connectsubcribers) >0:
			for func in connectsubcribers:
				print(func)
		else:
			print('No subscriber for incoming connections.')
	elif disconnect.match(val):
		print('disconnect')
		print('x'+val+'x')
	else:
		print(val)
if __name__=='__main__':
	main()
	t.join()
