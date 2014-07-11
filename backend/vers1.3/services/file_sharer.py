from super.service import service
import socket
import threading
import sqlite3 as sql
import sys
import tempfile
import shutil
import os
import datetime
import time

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
            print('db log: '.format(err))
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
		self.connectedclients = []
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
	def handleclient(self, sock, addr):
		#
		# first thing to do is to retrieve
		# all publicly available files and share
		# them --- broadcast them
		#
		sock.setblocking(1)
		while True:
		    action = sock.recv(1024)
		    print('requested action is {}'.format(action))
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

		        metadatasize = int(splitaction[1])
		        filesize = int(splitaction[2])
		        #reading configuration
		        metadata = self.readsock(sock,metadatasize,False) #sock.recv(metadatasize)
                        print('server log: received file metadata')
                        print('received {}'.format(metadata))
		        f = self.readsock(sock, filesize,True) #sock.recv(filesize)
                        shutil.copy(f, 'filename.png')
                        os.remove(f.name)
                        print('server log: received file data')
		        sock.sendall('ok')
        #private method
        def readsock(self,sock,size,isfile):
                if (not isfile):
                        read = 0
                        data = None
                        while (read<size):
                                #
                                # Controlling number of bytes read in order to only
                                # read metadata
                                tmp = size-read
                                if (tmp<1024):
                                        readsize = tmp
                                else:
                                        readsize = 1024
                                #reading data segment
                                if (data==None):
                                        data = sock.recv(readsize)
                                else:
                                        data = data+sock.recv(readsize)
                                read = sys.getsizeof(data)
                                print('current:{0} ,filesize:{1}'.format(read,size))
                        return data
                else:
                        f = tempfile.NamedTemporaryFile(suffix='.png')
                        read = 0
                        while True:
                                #
                                # Controlling number of bytes read in order to only
                                # read metadata
                                tmp = size-read
                                if (tmp<1024):
                                        readsize = tmp
                                else:
                                        readsize = 1024
                                data = sock.recv(readsize)
                                f.write(data)
                                read = read + os.path.getsize(f.name)
                                if ( not (read<size)):
                                        f.close()
                                        break
                                else:
                                        ts = time.time()
                                        print('{2} -- tmpfile: {0} , expected: {1}'.format(os.path.getsize(f.name), size, datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')))
                        return f
	def handle(self):
		#waiting for client requests
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversock.bind(('127.0.0.1', self.chosenport))
		self.serversock.listen(1)
		while True:
			conn, addr = self.serversock.accept()
			self.connectedclients.append((conn, addr))
			#Creating thread to handle client
			clienthandler = threading.Thread(target=self.handleclient, args=(conn, addr))
			clienthandler.daemon = True
			clienthandler.start()
	def start(self):
		print('file sharer started')
		self.chosenport = self.get_open_port()
		servethread = threading.Thread(target=self.handle)
		servethread.daemon = True
		servethread.start()
		return self.chosenport

	def __str__(self):
		return '{0}-{1}-{2}'.format(self.__name__, self.description, self.host)

	#
	# Not to be called outside class --- sorta
	def get_open_port(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("",0))
		s.listen(1)
		port = s.getsockname()[1]
		s.close()
		return port
