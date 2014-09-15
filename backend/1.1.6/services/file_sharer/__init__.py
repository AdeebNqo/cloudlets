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
from db import db
import os
class file_sharer():
	def __init__(self):
		self.currdb = db('mysql')
		self.currdb.setcredentials('localhost', 'root', 101, 'cloudletX', 'files')
		self.currdb.connect()
		self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockt.bind('127.0.0.1', 0)
		self.sockt.listen(1)
		self.users = {}
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
				files = self.currdb.get({'id':'{0}:{1}'.format(owner,filename)})
				print(files)
				#now need to check if requester has access
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

				if not os.path.exists(owner):
					os.makedirs(owner)
				filepath = '{0}/{1}'.format(owner, filename)
				if not os.path.isfile(filepath):
					_file = open(filepath, 'w')
					_file.write(objectdata)
					_file.close()
					#primary key
					primkey = '{0}:{1}'.format(owner,filename)
					self.currdb.insert(('id', 'access', 'filename', 'owner', 'accesslist'), (primkey, access, filename, owner, accesslist.join(':')))
			elif action=='transfer':
				print('transefering something to someone')
				owner = data['owner']
				receiver = data['receiver']
				oncloudlet = data['oncloudlet']
				if (oncloudlet=='0'):
					objectdata = data['data']
				filename = data['filename']

				(recv_socket, recv_address) = self.connections[receiver]
				filepath = '{0}/{1}'.format(owner,filename)
				if oncloudlet==1:
					with open(filepath) as _file:
						objectdata = _file.read()
				jsonstring = '{\"action\":\"recv\", \"owner\":\"{0}\", \"filename\":\"{1}\", \"objectdata\":\"{2}\"}'.format(owner, filename, objectdata)
				recv_socket.sendal(len(jsonstring))
				if (recv_socket.recv(1024)=='OK'):
					recv_socket.sendall(jsonstring)
			elif action == 'identify':
				self.connections[data['username']] = (somesocket, address)

	def stop(self):
		print('stopping')
		self.sockt.close()
	def request_service(self):
		(host,port) = self.sockt.getnameinfo()
		return '{0}:{1}'.format(host,port)
