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
action = config.get('DEFAULT','action')
numtimes = int(config.get('DEFAULT','numtimes'))
port = config.get('DEFAULT', 'port')
interface = config.get('DEFAULT','interface')
macaddress = getmac(interface)
transferfile = config.get('DEFAULT', 'testfile')
actions = action.split(',')

def clientwork():
        client = Client('client{}'.format(i), macaddress, ip, port)
        sleep(2)
        client.requestavailableservices()
        client.requestconnectedusers()
        client.requestserviceuserlist('file_sharer')
        client.requestservice('file_sharer')
        print('waiting for authentication...')
        while (client.filesharingclient == None):
                pass
        clients.append(client)
        #Perfoming the assigned actions
        somfile = open(transferfile, 'r').read()
        for actionX in actions:
            if (actionX=='upload'):
                for i in range(numtimes):
                    print(clients[0].filesharingclient.upload('1h', 'public', None, '0', transferfile, somfile))
            elif(actionX=='download'):
                for i in range(numtimes):
                    print(clients[0].filesharingclient.download(clients[0].filesharingclient.username, clients[0].filesharingclient.username, transferfile))
            elif(actionX=='remove'):
                for i in range(numtimes):
                    print(clients[0].filesharingclient.remove(clients[0].filesharingclient.username+'x', transferfile))
            elif(actionX=='view'):
                for i in range(numtimes):
                    print(clients[0].filesharingclient.getaccessiblefiles())
print('creating clients...')
clients = []
for i in range(numclients):
        t = threading.Thread(target=clientwork)
while True:
        pass