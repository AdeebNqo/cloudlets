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

print('creating clients...')
for i in range(numclients):
        client = Client('client{}'.format(i), macaddress, ip, port)
        sleep(2)
        print('requesting available services...')
        print(client.requestavailableservices())
print('done.')
while True:
        pass
