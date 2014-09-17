import ConfigParser
from client import Client
from time import sleep
import socket
import fcntl
import struct
'''
Method for retrieving mac address of the interface provided.
args:
        interfacename name of the interface
'''
def getmac(interfacename):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s',interfacename[:15]))
        return ''.join(['%02x:'%ord(char) for char in info[18:24]])[:-1]

#opening config file
config = ConfigParser.ConfigParser()
config.read("config.ini")
numclients = int(config.get('DEFAULT','numclients'))
ip = config.get('DEFAULT','ip')
port = config.get('DEFAULT', 'port')
interface = config.get('DEFAULT','interface')
macaddress = getmac(interface)
transferfile = config.get('DEFAULT', 'testfile')

print('creating clients...')
clients = []
for i in range(numclients):
        client = Client('client{}'.format(i), macaddress, ip, port)
        sleep(2)
        print('perfoming actions...')
        client.requestavailableservices()
        client.requestconnectedusers()
        print('requesting file sharing service...')
        client.requestservice('file_sharer')
        print('waiting for authentication...')
        while (client.filesharingclient == None):
                pass
        clients.append(client)

print('done.')
somfile = open(transferfile, 'r').read()
print('client 1 uploading file...')
print(clients[0].filesharingclient.upload('1h', 'public', None, '0', transferfile, clients[0].filesharingclient.username, somfile))
print(clients[0].filesharingclient.download(clients[0].filesharingclient.username, clients[0].filesharingclient.username, transferfile))
print('Done!')
while True:
        pass
