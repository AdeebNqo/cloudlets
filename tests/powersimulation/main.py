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
import datetime
import math
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
filenames = transferfile.split(',')
actions = action.split(',')
print('actions {}'.format(actions))
simulationtimeout = int(config.get('DEFAULT', 'simulationtimeout'))
actiontimeout = int(config.get('DEFAULT', 'actiontimeout'))

def clientwork(num):
        client = Client('user{}'.format(num), getfakemac(), ip, port)
        sleep(3)
        #client.requestavailableservices()
        #client.requestconnectedusers()
        client.requestservice('file_sharer')
        #client.requestserviceuserlist('file_sharer')
        while (client.filesharingclient == None):
                pass
	#Perfoming the assigned actions
        f1 = open(filenames[0], 'r')
        somfile1 = f1.read()
        f2 = open(filenames[1], 'r')
        somfile2 = f2.read()
        fileobjects = [f1, f2]

        start = datetime.datetime.now()
        timespent = 0
        while True:
                new_time = datetime.datetime.now()
                diff = (new_time-start).total_seconds()
                timespent += diff
                timespent = int(math.floor(timespent))
                if (timespent>simulationtimeout):
                        print('user{0} stopping since it spent {1} seconds.'.format(num,timespent))
                        break
                else:
                        actionX = random.choice(actions)
                        if (actionX=='upload'):
                                fileobj = random.choice(fileobjects)
                                if (fileobj==f1):
                                        somfile = somfile1
                                        transferfileX = filenames[0]
                                else:
                                        somfile = somfile2
                                        transferfileX = filenames[0]
                                client.filesharingclient.upload('1h', 'public', None, '0', transferfileX, somfile)
                        elif(actionX=='download'):
                                recv = client.filesharingclient.download(client.filesharingclient.username, client.filesharingclient.username, random.choice(filenames))
                        elif(actionX=='remove'):
                                print(client.filesharingclient.remove(client.filesharingclient.username, random.choice(filenames)))
                        elif(actionX=='view'):
                                response = client.filesharingclient.getaccessiblefiles()
                        elif (actionX=='checknewfiles'):
                                print(client.filesharingclient.checknewfiles())
                        elif (actionX=='requestavailableservices'):
                                client.requestavailableservices()
                        elif (actionX=='requestconnectedusers'):
                                client.requestconnectedusers()
                        elif (actionX=='requestusersoffilesharer'):
                                client.requestserviceuserlist('file_sharer')
                        #wait until making another action
                        time.sleep(actiontimeout)
clients = []
for i in range(numclients):
        t = threading.Thread(target=clientwork, args=(i,))
        #t.daemon = True
        t.start()
        clients.append(t)
for t in clients:
        t.join()
print('Finished!')
