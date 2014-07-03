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
		self.status = True
	def start(self):
		serveforeverthread = threading.Thread(target=self.reallystart)
		serveforeverthread.daemon = True
		serveforeverthread.start()
	def stop(self):
		self.status = False
	def reallystart(self):
		context = zmq.Context()
		socket = context.socket(zmq.DEALER)
		socket.bind("tcp://{0}:{1}".format(self.host,self.port))
		while self.status:
    			message = socket.recv()
			socket.send(message)
