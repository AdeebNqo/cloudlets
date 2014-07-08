from super.service import service
import time

class file_sharer(service):
	def __init__(self):
		self.host = '127.0.0.1'
		self.minport = 8080
		self.maxport = 9090
		self.description = 'File sharing between devices'
	def getportrange(self):
		return range(self.minport, self.maxport)
	def gethost(self):
		return self.host
	def getdescription(self):
		return self.description
	def handle(self):
		while True:
			print('handling')
			time.sleep(300)
