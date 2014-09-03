#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file controls the cloudlet
# 
#
from mqttEventEmitter import mqttEventEmitter
from commHandler import commHandler
import argparse
import time

def main(port):
	print('Cloudlet started.')
	eventEmitter = mqttEventEmitter(port)
	time.sleep(2)
	commhandler = commHandler(port)
	eventEmitter.wait()
	commhandler.wait()
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Cloudlet controller. Controlls communications, management and connections to the cloudlet .')
	parser.add_argument('-p','--port', type=int, nargs=1, help='Port to be allocated to cloudlet.', required=False)
	args = vars(parser.parse_args())
	if (args['port']!=None):
		mqttport = args['port'][0]
		if (mqttport<1025):
			#
			# Defualting to using default port
			# as user attempted to use the roots
			# ports. There is no reason the program
			# should be run as root.
			#
			mqttport = 1883
	else:
		mqttport = 1883 #default port
	main(mqttport)
