import ConfigParser

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
interface = config.get('DEFAULT','interface')
macaddress = getmac(interface)
