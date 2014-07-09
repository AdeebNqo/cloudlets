from super.service import service
import socket
import threading

class file_sharer(service):
	def __init__(self):
		self.chosenport = -1 #port that will by the service
	@property
	def description(self):
		return 'File sharing between devices'
	@property
	def host(self):
		return '127.0.0.1'
	@property
	def __name__(self):
		return 'file sharer'
	@property
	def port(self):
		return self.chosenport
	def gethost(self):
		return self.host
	def getdescription(self):
		return self.description
	def handle(self):
		while True:
			print('handling')
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('127.0.0.1', self.chosenport))
			s.listen(1)
			conn, addr = s.accept()
			print(addr+' connected')
	def start(self):
		print('file sharer started')
		self.chosenport = self.get_open_port()
		servethread = threading.Thread(target=self.handle)
		servethread.daemon = True
		servethread.start()
		return self.chosenport
			
	def __str__(self):
		return '{0} {1} {2}'.format(self.__name__, self.description, self.host)

	#
	# Not to be called outside class --- sorta
	def get_open_port(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("",0))
		s.listen(1)
		port = s.getsockname()[1]
		s.close()
		return port
