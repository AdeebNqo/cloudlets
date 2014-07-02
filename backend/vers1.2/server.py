#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Server class for listening for interfacing with users
#
import sys
import argparse
import SocketServer

class client_handler(SocketServer.BaseRequestHandler):
	def handle(self):
		print('hello')
def main(host,port):
	server = SocketServer.TCPServer((host, port), client_handler)
	print('waiting for clients...')
	server.serve_forever()
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
		host = 'localhost'
	main(host,port)
