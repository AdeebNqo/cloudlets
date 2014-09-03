#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This is the class that controls all the cloudlet
# components
#
# "I am a master of logic and a powerfully convincing debater.
#  In fact, against my better judgment, I can talk myself out of doing anything."
#
# -Jarod Kintz
#
from broker import broker
import argparse
import time
import os
from asyncproc import Process
import threading
import re

t = None
connectsubcribers = []
disconnectsubcribers = []
connect = re.compile('(\d+): New client connected from (.+) as (.+).')
disconnect = re.compile('\d+: Socket read error on client .+, disconnecting.')
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
def main(brokerport):
	global t
	t = threading.Thread(target=process)
	t.daemon = True
	t.start()
	b = broker(brokerport)
	b.wait()
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Broker for listening to cloudlet connections.')
	parser.add_argument('-p','--port', type=int, nargs=1, help='Port to listen on.', required=False)
	args = vars(parser.parse_args())
	if (args['port']!=None):
		mqttport = args['port'][0]
		if (mqttport<1025):
			#
			# Defualting to using default port
			# as user attempted to use the root's
			# ports. There is no reason the program
			# should be run as root
			#
			mqttport = 1883
	else:
		mqttport = 1883 #default port
	main(mqttport)
