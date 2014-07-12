#
# Client for testing purposes
#
import mosquitto
import threading
import socket
import os
import sys
import binascii

sock = None

def getdata(sock):
	data = None
	while True:
		data = sock.recv(1024)
		if (data!=None):
			break
	return data
def on_publish(mosq, obj, mid):
	print("Message "+str(mid)+" published.")
def on_message(mosq, obj, msg):
	filename = 'Zed.svg'
	print(msg.payload)
	vals = msg.payload.split('-')
	name, description, host, port = vals[0], vals[1], vals[2], vals[3]
	f = threading.Thread(target=file_service, args=(host,int(port)))
	f.daemon = True
	f.start()
	f.join()
	_file = open(os.getcwd()+os.sep+filename,'rb')
	metadata = '''
	  {
	        "filename":\"'''+filename+'''\",
	        "keepAlive":"2h",
	        "private":true
	  }
	'''
	msize = sys.getsizeof(metadata) #metadata size
	fsize = os.path.getsize(os.getcwd()+os.sep+filename) #file size
	sock.sendall('upload {0} {1}'.format(msize, fsize))
	response = getdata(sock)
	if (response=='transfer'):
		sock.sendall(metadata)
		data = getdata(sock)
		if (data=='ok'):
			#sock.sendall(_file.read(fsize))
			for i in range(fsize):
				sock.sendall(_file.read(1))
				print('sent {0} bytes of {1} bytes'.format(i,fsize))
			data = getdata(sock)
			print('server says {}'.format(data))

	else:
		print('upload error: response from server was {}'.format(reponse))
	_file.close()


def on_subscribe(mosq, obj, mid, qos_list):
 	print("Subscribe with mid "+str(mid)+" received.")
def file_service(host, port):
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	#sock.settimeout(45)

def main():
	mqttclient = mosquitto.Mosquitto('client')
	mqttclient.on_publish = on_publish
	mqttclient.on_message = on_message
	mqttclient.on_subscribe = on_subscribe
	mqttclient.connect('127.0.0.1', port=9999, keepalive=60)
	mqttclient.subscribe("servers/service")
	#mqttclient.publish("client/list", payload=None)
	mqttclient.subscribe("server/service",1)
	mqttclient.subscribe('server/connecteduser',1)
	mqttclient.publish("client/servicelist", "hello world", 1)
	while True:
		mqttclient.loop()
if __name__=='__main__':
	main()
