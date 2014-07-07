#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Server for interfacing with clients
#
import argparse
from connector import connector
def main(mqttport):
	print('connecting to port {}'.format(mqttport))
	#
	# The connector works with any host, however
	# since we only have one host --- the server
	# creates the default host. This is to make
	# the connector non-rigid
	#
	con = connector('127.0.0.1',port)
	con.start()

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Server for listening to cloudlet connections.')
	parser.add_argument('-p','--port', type=int, nargs=1, help='Port to listen on.', required=False)
	args = vars(parser.parse_args())
	if (args['port']!=None):
		mqttport = args['port'][0]
		if (mqttport<1025):
			#
			# Defualting to using default port
			# as user attempted to use the root's
			# ports. There is no reason is program
			# should be run as root
			#
			mqttport = 9999
	else:
		mqttport = 9999 #default port
	main(mqttport)
