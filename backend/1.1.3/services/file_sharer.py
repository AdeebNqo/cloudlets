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
import struct
import MySQLdb
import StringIO
import math

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
                self.db = MySQLdb.connect(host="localhost",user="root",passwd="101",db="cloudlet")
                self.cur = self.db.cursor()
                self.cur.execute('CREATE TABLE IF NOT EXISTS files(hash VARCHAR(100) PRIMARY KEY NOT NULL, owner TEXT NOT NULL, path TEXT NOT NULL, private INT NOT NULL, filesize REAL NOT NULL , allowed TEXT)')
                self.db.commit()
	def getpublicfiles(self):
	    self.cur.execute('select hash, path from files where private=0')
	    result = self.cur.fetchall()
            paths = []
            for row in result:
                    paths.append((row[0], row[1]))
            return paths
	def uploadfile(self,_hash, owner, path, private, filesize, allowed):
                print('uploading files to database')
                priv = 1 if private else 0
                try:
                        allowed = '\'{}\''.format(allowed)
                        owner = '\'{}\''.format(owner)
                        path = '\'{}\''.format(path)
                        _hash = '\'{}\''.format(_hash)
                        self.cur.execute("INSERT INTO files (hash, owner, path, private, filesize, allowed)  values({0}, {1}, {2}, {3}, {4}, {5});".format(_hash, owner, path, priv, filesize, allowed))
                        self.db.commit()
                except Exception, err:
                        print traceback.format_exc()
                        return False
                return True
	def downloadfile(self,_hash):
		self.cur.execute('select hash, owner, path, private, filesize, allowed from files where hash=\"{}\"'.format(_hash))
		result = self.cur.fetchall()
		vals = {}
                for row in result:
                        vals['hash'] = row[0]
                        vals['owner'] = row[1]
                        vals['path'] = row[2]
                        vals['private'] = row[3]
                        vals['filesize'] = row[4]
                        vals['allowed'] = row[5]
                        return vals
		return None
        def getaccessiblefiles(self, macaddress):
                files = []
                self.cur.execute('select hash, path, allowed from files where private=0')
                result = self.cur.fetchall()
                for row in result:
                        _hash = row[0]
                        path = row[1]
                        allowed = row[2]
                        if macaddress in allowed:
                                files.append((_hash,path))
                paths = self.getpublicfiles()
                finalresult = []
                if (paths != None):
                        finalresult = paths
                #print('files: {0}, finalresult: {1}'.format(files, finalresult))
                return list(set(files+finalresult))

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
        def getUTF(self, val):
                return ''.join(self.writeUTF([], val))
        def writeUTF(self, data, val):
                utf8 = val.encode('utf-8')
                length = len(utf8)
                data.append(struct.pack('!H', length))
                format = '!{}s'.format(str(length))
                data.append(struct.pack(format, utf8))
                return data
	def handleclient(self, sock, addr):
		connectstring = sock.recv(44)
                macaddress = connectstring.split()[1]
                print(connectstring)
                sock.sendall(self.getUTF('OK'))
                print('sent OK')

                #
		# first thing to do is to retrieve
		# all publicly available files and share
		# them --- broadcast them
		#
                accessiblefiles = self.db.getaccessiblefiles(macaddress)
                print('accessiblefiles: {}'.format(accessiblefiles))
                numfiles = sock.recv(1024)
                print('client wants to know num of accessible files.')
                sock.sendall(self.getUTF('{}'.format(len(accessiblefiles))))
                reply = sock.recv(1024)
                print('client says {}'.format(reply))
                if (reply.endswith('OK')):
                        print('providing accessible files')
                        for _file in accessiblefiles:
                                (_hash, path) = _file
                                print('sending {} to client.'.format((self.getUTF('file {0} {1}'.format(_hash, path)))))
                                sock.sendall(self.getUTF('file {0} {1}'.format(_hash, path)))
                                reply = sock.recv(1024) #if not 'OK', consider resending
                print("waiting for request from client...")
                #Continous handling of client
		while True:
                        try:
                                action = sock.recv(1024)
                                mybuffer = StringIO.StringIO(action)
                                mybuffer.read(2)
                                action = mybuffer.read()
                                print('client says {}'.format(action))
                                splitaction = action.split()
                                if (action.startswith('download')):
                                        print('download file')
                                        _hash = splitaction[1]
                                        fileinfo = self.db.downloadfile(_hash)
                                        print('client requesting {}'.format(fileinfo))
                                	print('now transferring file')
                                	_file = open(fileinfo['path'],'rb')
                                        fsize = fileinfo['filesize']
                                	sock.sendall(self.getUTF('download {0}'.format(fsize)))
                                	reply= sock.recv(1024)
                                        mybuffer = StringIO.StringIO(reply)
                                        mybuffer.read(2)
                                        reply = mybuffer.read()
                                        if (reply=='OK'):
                        			for i in range(int(math.floor(fsize))):
                        				sock.sendall(_file.read(1))
                        			data = sock.recv(100)
                        			print('client says {}'.format(data))
                                        	_file.close()
                                elif (action.startswith('upload')):
                                        #request transfer from client
                                        print('upload file')
                                        sock.sendall(self.getUTF('transfer'))
                                        print('sent transfer string')
                                        metadatasize = int(splitaction[1])
                                        filesize = int(splitaction[2])
                                        #reading configuration
                                        metadata = (self.readmetadata(sock,metadatasize)) #sock.recv(metadatasize)
                                        sock.sendall(self.getUTF('OK'))
                                        print('client sent metadata {}'.format(metadata))
                                        meta = json.loads(metadata)
                                        name, ext = os.path.splitext(meta['filename'])
                                        f = self.readfile(sock, filesize, ext)
                                        f.flush()
                                        _hash, path = self.fileman.place(f,meta['filename'])
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
                f = tempfile.NamedTemporaryFile(suffix=_suffix, bufsize=1024)
                while True:

                        try:
                                data = sock.recv(size)
                        except :
                                data = None
                        if not data:
                                break
                        f.write(data)
                        data = None
                return f
	def handle(self):
		#waiting for client requests
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversock.bind(('10.10.0.5', self.chosenport))
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
