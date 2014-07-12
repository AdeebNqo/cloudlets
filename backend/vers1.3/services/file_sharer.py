from super.service import service
import socket
import threading
import sqlite3 as sql
import sys
import tempfile
import shutil
import os
import json
from array import array
import binascii

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
		        #request transfer from client
		        print('upload file')
		        sock.sendall('transfer')

		        metadatasize = int(splitaction[1])
		        filesize = int(splitaction[2])
		        #reading configuration
		        metadata = (self.readmetadata(sock,metadatasize)) #sock.recv(metadatasize)
                        sock.sendall('ok')
                        #print('server log: received file metadata')
                        print('received {}'.format(metadata))
                        #print('expected {0} bytes, received {1} bytes'.format(metadatasize, sys.getsizeof(metadata)))
                        meta = json.loads(metadata)
                        name, ext = os.path.splitext(meta['filename'])
                        (f,remainder) = self.readfile(sock, filesize, ext)
                        f.flush()
                        while True:
                                pass
                        #shutil.copy(f.name , 'filename{}'.format(ext))
                        #f.close()
                        #print('server log: received file data')
                        #print('filename size {0}'.format(os.path.getsize('filename.png')))
		        #sock.sendall('ok')
        #private method
        def readmetadata(self,sock,size):
                #
                # Returns `data`, the metadata.
                # Returns `rem`, sometimes it reads the first
                # part of the file data
                #
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
                                print('reading {}'.format(readsize))
                                data = sock.recv(readsize)
                        else:
                                data = data+sock.recv(readsize)
                        read = read+readsize
                return data
        #private method
        def readfile(self, sock, size, _suffix):
                sock.settimeout(10)
                f = tempfile.NamedTemporaryFile(suffix=_suffix)
                while True:
                        try:
                                data = sock.recv(size)
                        except :
                                pass
                        if not data:
                                break
                        print('x{0}x'.format(data))
                        f.write(data)
                        data = None
                return (f, size - os.path.getsize(f.name))
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
