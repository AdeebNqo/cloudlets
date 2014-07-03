#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Server for interfacing with clients
#
import argparse
import zmq
from connector import connector
import time
def main(host,port):
	print('hello {0}:{1}'.format(host,port))
	con = connector(host,port)
	con.start()
	while True:
		time.sleep(100)

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Server for listening to cloudlet connections.')
	parser.add_argument('-p','--port', type=int, nargs=1, help='Port to listen on.', required=False)
	parser.add_argument('-ho','--host', nargs=1, help='Host to run server on.', required=False)
	args = vars(parser.parse_args())
	if (args['port']!=None):
		port = args['port'][0]
	else:
		port = 9999
	if (args['host']!=None):
		host = args['host'][0]
	else:
		host = '127.0.0.1'
	main(host,port)
