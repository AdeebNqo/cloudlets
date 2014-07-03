#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Component that accepts and broadcasts client connections
#
import zmq
import threading

class connector(object):
	def __init__(self,host,port):
		self.host = host
		self.port = port
	def start(self):
		serveforeverthread = threading.Thread(target=self.reallystart)
		serveforeverthread.start()
	def reallystart(self):
		context = zmq.Context()
		socket = context.socket(zmq.DEALER)
		sock.bind("tcp://{0}:{1}".format(self.host,self.port))
		while True:
    			message = sock.recv()
			sock.send(message)
