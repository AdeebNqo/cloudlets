from super.service import service
import socket
import threading
import sqlite3 as sql

class File(object):
    def __init__(self, _hash, owner, path, privacystate, filesize, accessusers):
        self._hash = _hash
        self.owner = owner
        self.path = path
        self.private = privacystate
        self.filesize = filesize
        self.allowed = accessusers
        
class database(object):
    def __init__(self):
        try:
            self.conn = sql.connect('filestore.db')
            self.cursor  = self.conn.cursor()
            self.cursor.execute('SELECT name FROM sqlite_temp_master WHERE type=\'table\';')
            data = self.cursor.fetchall()
            if (len(data)==0):
                #if there are no tables
                self.cursor.execute('create tables files(hash TEXT PRIMARY KEY NOT NULL, owner TEXT NOT NULL, path TEXT NOT NULL, private INT NOT NULL, filesize REAL NOT NULL , allowed TEXT)')
                data = self.cursor.fetchall()
                print('db log: {}'.format(data))
        except sql.Error as err:
            print(err)
    def getpublicfiles(self):
        self.cursor.execute('select * from files where private=?',0)
        result = self.cursor.fetchall()
        return result
    def uploadfile(self,_file):
        return True
    def downloadfile(self,_hash):
        self.cursor.execute('select * from files where hash=?',_hash)
        result = self.cursor.fetchone()
        print('result is {}'.format(result))
        return result
        
class file_sharer(service):
	def __init__(self):
		self.chosenport = -1 #port that will by the service
		self.connectedclient = []
		self.db = database()
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
	def heartbeatclient(self,sock,addr):
	        print('heart beating client')
	def handleclient(self, sock, addr):
	        while True:
	            action = sock.recv(1024)
	            splitaction = action.split()
	            if (action.startswith('download')):
	                print('download file')
	                _hash = splitaction[1]
	                fileinfo = self.db.downloadfile(_hash)
	                #
	                # 1. calculate filesize
	                # 2. send 'download-request filesize'
	                # 3. wait for 'ok'
	                # 4. transfer file
	                #
	            elif (action.startswith('upload')):
	                print('upload file')
	                #request transfer from client
	                sock.sendall('transfer')
	                
	                metadatasize = float(splitaction[1])
	                filesize = float(splitaction[2])
	                #reading configuration
	                metadata = sock.recv(metadatasize)
	                file = sock.recv(filesize)
	                print('received {}'.format(metadata))
	def handle(self):
		while True:
			print('handling')
			#waiting for client requests
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('127.0.0.1', self.chosenport))
			s.listen(1)
			conn, addr = s.accept()
			self.connectedclien.append((conn, addr))
			#Creating thread to handle client
			clienthandler = threading.Thread(target=self.handleclient, args=(conn, addr))
			clienthandler.daemon = true
			clienthandler.start()
			#starting heart beat thread for client
			heartbeathandler = threading.Thread(self.heartbeatclient, args=(conn,addr))
			heartbeathandler.daemon = true
			heartbeathandler.start()
			
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
