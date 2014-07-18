from super.service import service
import socket
import threading
import sys
import tempfile
import shutil
import os
import json
from array import array
import binascii
from file_manager import file_manager
import traceback

from bsddb3 import db

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
                        print('creating db')
                        filename = 'filestore'
                        self.dbtable = db.DB()
                        self.dbtable.open(filename, None, db.DB_HASH, db.DB_THREAD | db.DB_DIRTY_READ | db.DB_CREATE)
                        print('db created!')
                        #self.cursor  = self.conn.cursor()
                        #tables = []
                        #filesexist = False
                        #cursor = self.cursor.execute('SELECT name FROM sqlite_temp_master WHERE type=\'table\';')
                        #if (cursor.rowcount <= 0 ):
                        #        self.conn.execute('CREATE TABLE files(hash TEXT PRIMARY KEY NOT NULL, owner TEXT NOT NULL, path TEXT NOT NULL, private INT NOT NULL, filesize REAL NOT NULL , allowed TEXT);')
                        #        self.conn.commit()
                except db.DBNoSuchFileError as err:
                        mydb = db.DB()
                        mydb.open(filename, None, db.DB_HASH, db.DB_CREATE)
                        mydb.close()
                        self.__init__(self)
                        print traceback.format_exc()
                        print('db log: '.format(err))
	def getpublicfiles(self):
	    #self.cursor.execute('select path from files where private=?',(0,))
	    #result = self.cursor.fetchall()
            #paths = []
            #for row in result:
                    #paths.append(row[0])
	    #return paths
            return True
	def uploadfile(self,_hash, owner, path, private, filesize, allowed):
                print('uploading files to database')
                #priv = 1 if private else 0
                #try:
        #                allowed = '\'{}\''.format(allowed)
        #                owner = '\'{}\''.format(owner)
        #                path = '\'{}\''.format(path)
        #                _hash = '\'{}\''.format(_hash)
        #                print("INSERT INTO files (hash, owner, path, private, filesize, allowed)  values({0}, {1}, {2}, {3}, {4}, {5});".format(_hash, owner, path, priv, filesize, allowed))
        #                self.conn.execute("INSERT INTO files (hash, owner, path, private, filesize, allowed)  values({0}, {1}, {2}, {3}, {4}, {5});".format(_hash, owner, path, priv, filesize, allowed))
        #        except Exception, err:
        #                print traceback.format_exc()
        #                return False
                return True
	def downloadfile(self,_hash):
		#self.cursor.execute('select hash, owner, path, private, filesize, allowed from files where hash=?',(_hash,))
		#result = self.cursor.fetchall()
		#vals = {}
                #for row in result:
                #        vals['hash'] = row[0]
                #        vals['owner'] = row[1]
                #        vals['path'] = row[2]
                #        vals['private'] = row[3]
                #        vals['filesize'] = row[4]
                #        vals['allowed'] = row[5]
                #        return vals
		return None
        def getaccessiblefiles(self, macaddress):
                #files = []
                #block = self.cursor.execute('select path, allowed from files where private=?',(0,))
                #for row in block:
                #        path = row[0]
                #        allowed = row[0]
                #        if allowed.contains(macaddress):
                #                files.append(path)
                #paths = self.getpublicfiles()
                #return list(set(files+paths))
                return 'True'

class file_sharer(service):
	def __init__(self):
		self.chosenport = -1 #port that will by the service
		self.connectedclients = []
		self.db = database()
                self.fileman = file_manager('data/')
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
		connectstring = sock.recv(44)
                macaddress = connectstring.split()[1]
                print(connectstring)
                sock.sendall('OK')

                #
		# first thing to do is to retrieve
		# all publicly available files and share
		# them --- broadcast them
		#
                accessiblefiles = self.db.getaccessiblefiles(macaddress)
                numfiles = sock.recv(1024)
                sock.sendall('{}'.format(len(accessiblefiles)))
                for _file in accessiblefiles:
                        print(_file)

                #Continous handling of client
		while True:
                        try:
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
                                        print('sent transfer string')
                                        metadatasize = int(splitaction[1])
                                        filesize = int(splitaction[2])
                                        #reading configuration
                                        metadata = (self.readmetadata(sock,metadatasize)) #sock.recv(metadatasize)
                                        sock.sendall('ok')
                                        meta = json.loads(metadata)
                                        name, ext = os.path.splitext(meta['filename'])
                                        f = self.readfile(sock, filesize, ext)
                                        f.flush()
                                        _hash, path = self.fileman.place(f)
                                        shutil.copy(f.name , '{2}{0}{1}'.format(name, ext, path))
                                        f.close()
                                        result = self.db.uploadfile(_hash, 'user1', '{2}{0}{1}'.format(name, ext, path[:len(path)-1]), meta['private'], filesize, '') #(self,_hash, owner, path, private, filesize, allowed)
                                        print('db says: {}'.format(result))
                                        sock.sendall('ok')
                                        sock.settimeout(60)
                                        print('server log: received file data')
                        except Exception as err:
                                print traceback.format_exc()
                                pass

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
                sock.settimeout(5)
                f = tempfile.NamedTemporaryFile(suffix=_suffix)
                while True:
                        try:
                                data = sock.recv(size)
                        except :
                                pass
                        if not data:
                                break
                        f.write(data)
                        data = None
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
