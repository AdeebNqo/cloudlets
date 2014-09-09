#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file is the test client
#
import mosquitto
import sys
import threading
import uuid
import socket

i = 0
mqttclient = None
identifier = 'client{0}|{1}'.format(str(uuid.uuid4().get_hex().upper()[0:6]),str(uuid.uuid4().get_hex().upper()[0:10]))

def interface():
	while True:
		choice = input('1. Get Connected User List\n2. Get list of services\n3. Request Service\n')
		if (choice==1):
			mqttclient.publish('server/connectedusers',"true")
		elif (choice==2):
			mqttclient.publish('server/servicelist',"true")
		elif (choice==3):
			requestservice('file_sharer')
			while True:
				schoice = input('1. Upload\n2. Fetch\n3. Remove\n4. Update\n5. Main Menu\n:>')
				if schoice==5:
					break
				elif (schoice==1):
					upload('hello','world')
def on_publish(mosq, obj):
	print("log: Message "+str(obj)+" published.")
def on_message(obj, msg):
	if (msg.topic=='client/service'):
		print(msg.payload)
	elif (msg.topic=='client/useservice/{}'.format(identifier)):
		print('trying to use service')
	elif (msg.topic=='client/connecteduser'):
		print(msg.payload)
	elif (msg.topic=='server/useservice/{0}'.format(identifier)):
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind((socket.gethostname(), 0))
		serversocket.listen(5)
		(ip,port) = serversocket.getnameinfo()
		mqttclient.publish(msg.payload,"{0}:{1}".format(ip, port))
		print('just sent address {0}:{1}'.format(ip, port))
	elif (msg.topic=='client/service_request/{0}/recvIP'.format(identifier)):
		print(msg.payload)
	else:
		print(msg.payload)
def on_subscribe(mosq, obj, qos_list):
	print("log: Subscribed.")
def main():
	global mqttclient
	mqttclient = mosquitto.Mosquitto(identifier)
	mqttclient.on_publish = on_publish
	mqttclient.on_message = on_message
	mqttclient.on_subscribe = on_subscribe
	mqttclient.connect('127.0.0.1', port=9999, keepalive=60)
	mqttclient.subscribe('client/connecteduser',1)
	mqttclient.subscribe('client/service',1)
	mqttclient.subscribe('client/service_request/{}'.format(identifier),1)
	mqttclient.subscribe('client/service_request/{0}/recvIP'.format(identifier),1)
	if(i):
		t = threading.Thread(target=interface)
		t.daemon = True
		t.start()
	while True:
		mqttclient.loop()
def requestservice(servicename):
	mqttclient.subscribe('client/useservice/{}'.format(identifier),1)
	mqttclient.publish('server/useservice','{0};{1}'.format(identifier,servicename))
if __name__=='__main__':
	try:
	    i = sys.argv[1]
	except:
		pass
	main()
