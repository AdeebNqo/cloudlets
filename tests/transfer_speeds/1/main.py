import ConfigParser
from client import Client
from time import sleep
import socket
import fcntl
import struct
import threading
import datetime
import random
import os
import sys
import time
'''
Method for retrieving mac address of the interface provided.
args:
        interfacename name of the interface
'''
def getrealmac(interfacename):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s',interfacename[:15]))
        return ''.join(['%02x:'%ord(char) for char in info[18:24]])[:-1]
'''
Method for retrieving fake mac address

'''
def getfakemac():
        mac = [ 0x00, 0x24, 0x81,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")
numclients = int(config.get('DEFAULT','numclients'))
ip = config.get('DEFAULT','ip')
action = config.get('DEFAULT','action')
numtimes = int(config.get('DEFAULT','numtimes'))
port = config.get('DEFAULT', 'port')
interface = config.get('DEFAULT','interface')
macaddress = getrealmac(interface)
transferfile = config.get('DEFAULT', 'testfile')
actions = action.split(',')

def clientwork(num):
        client = Client('user{}'.format(num), getfakemac(), ip, port)
        sleep(3)
        #client.requestavailableservices()
        #client.requestconnectedusers()
        print('requesing file_sharer')
        client.requestservice('file_sharer')
        print('requested file_sharer')
        #client.requestserviceuserlist('file_sharer')
        while (client.filesharingclient == None):
                pass
        print('have access to file_sharer')
	#Perfoming the assigned actions
        f = open(transferfile, 'r')
        somfile = f.read()

        uploadrates = []
        downloadrates = []
        removerates = []
        viewrates = []
        for actionX in actions:
                print('user{1} is testing action: {0}'.format(actionX,num))
                if (actionX=='upload'):
                        for i in range(numtimes):
                                print(i)

                                start = datetime.datetime.now()
                                client.filesharingclient.upload('1h', 'public', None, '0', transferfile, somfile)
                                diff = datetime.datetime.now() - start
                                rate = (os.path.getsize(transferfile) / abs(diff.total_seconds()))
                                uploadrates.append(rate)
                                client.filesharingclient.remove(client.filesharingclient.username, transferfile)
                elif(actionX=='download'):
                        for i in range(numtimes):
                                print(i)

                                client.filesharingclient.upload('1h', 'public', None, '0', transferfile, somfile)
                                start = datetime.datetime.now()
                                recv = client.filesharingclient.download(client.filesharingclient.username, client.filesharingclient.username, transferfile)
                                diff = datetime.datetime.now() - start
                                rate = (sys.getsizeof(recv) / abs(diff.total_seconds()))
                                downloadrates.append(rate)
                                client.filesharingclient.remove(client.filesharingclient.username, transferfile)
                #
                # For the following actions, we will measure the
                # time it takes to get a response.
                #
                elif(actionX=='remove'):
                        for i in range(numtimes):
                                print(i)

                                client.filesharingclient.upload('1h', 'public', None, '0', transferfile, somfile)
                                start = datetime.datetime.now()
                                client.filesharingclient.remove(client.filesharingclient.username, transferfile)
                                diff = datetime.datetime.now() - start
                                rate = abs(diff.total_seconds())
                                removerates.append(rate)
                elif(actionX=='view'):
                        for i in range(numtimes):
                                print(i)

                                start = datetime.datetime.now()
                                response = client.filesharingclient.getaccessiblefiles()
				diff = datetime.datetime.now() - start
                                rate = abs(diff.total_seconds())
                                viewrates.append(rate)
                elif (action=='checknewfiles'):
                        for i in range(numtimes):
                                print(i)

                                print(client.filesharingclient.checknewfiles())
                                print(client.filesharingclient.upload('1h', 'public', None, '0', transferfile, somfile))
                                print(client.filesharingclient.checknewfiles())
                                print(client.filesharingclient.remove(client.filesharingclient.username, transferfile))
                                print(client.filesharingclient.checknewfiles())
                                print(client.filesharingclient.checknewfiles())
        print('name: user{}'.format(i))
        print('upload (bytes/s): {}'.format(uploadrates))
        print('download (bytes/s): {}'.format(downloadrates))
        print('remove response times (seconds): {}'.format(removerates))
        print('view response times: {}'.format(viewrates))
        print('\n')
clients = []
for i in range(numclients):
        t = threading.Thread(target=clientwork, args=(i,))
        #t.daemon = True
        t.start()
        clients.append(t)
	print('started...')
for t in clients:
        t.join()
