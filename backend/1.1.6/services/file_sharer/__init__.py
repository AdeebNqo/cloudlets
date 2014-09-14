#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# File sharing service
#
# "Any sufficiently advanced bug is indistinguishable from a feature."
# -Bruce Brown
#
import socket
import json
class file_sharer():
	def __init__(self):
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind('127.0.0.1', 0)
		self.sockt.listen(1)
		print('service created')
	def start(self):
		print('starting')
		t = threading.Thread(target=wait_connections)
		t.daemon = True
		t.start()
	def wait_connections(self):
		while True:
			conn, addr = self.sockt.accept()
			self.handle(conn, addr)
	def handle(self, somesocket, address):
		data = ''
		lastend = None
		while True:
			length = int(somesocket.recv(1024))
			somesocket.sendall('OK')
			if (lastend!=None):
				data=data+lastend
				lastend = None
			data = data+somesocket.recv(length)
			while (len(data) < length):
				data = data + somesocket.recv(length)
			if (len(data)>length):
				lastend = data[length:]
				data = data[:length]
			packet = json.loads(data)
			action = packet['action']
			if action=='heartbeat':
				response = '{\"status\":\"OK\"}'
				somesocket.sendall(len(response))
				statusresponse = somesocket.recv(1024)
				if (statusresponse=='OK'):
					somesocket.sendall(response)
			elif action=='download':
				print('downloading something')
				owner = data['owner']
				requester = data['requester']
				filename = data['filename']
			elif action=='upload':
				print('uploading something')
				duration = data['duration']
				access = data['access']
				if (access!='public'):
					accesslist = data['accesslist']
				compression = data['compression']
				filename = data['filename']
				owner = data['owner']
				objectdata = data['data']
			elif action=='transfer':
				print('transefering something to someone')
				owner = data['owner']
				receiver = data['receiver']
				oncloudlet = data['oncloudlet']
				if (oncloudlet=='0'):
					objectdata = data['data']
				filename = data['filename']
	def stop(self):
		print('stopping')
		self.sockt.close()
	def request_service(self):
		(host,port) = self.sockt.getnameinfo()
		return '{0}:{1}'.format(host,port)
