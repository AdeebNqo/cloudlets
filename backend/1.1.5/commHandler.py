#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file controls the communications of the
# cloudlet
#
import mosquitto
import argparse
import threading
import broadcaster

class commHandler(object):
	def __init__(self,mqttport):
		self.mqttserver = None
		#
		#Setting up all the neccessary callback methods
		#for mosquitto communication. mqqtconnection.loop()
		#is called using a thread.
		
		self.mqttserver = mosquitto.Mosquitto('cloudlet|maincontrol')
		self.mqttserver.on_subscribe = self.on_subscribe
		self.mqttserver.on_connect = self.on_connect
		self.mqttserver.on_message = self.on_message
		self.mqttserver.on_unsubscribe = self.on_unsubscribe
		self.mqttserver.connect('127.0.0.1', mqttport, keepalive=60)
		self.t = threading.Thread(target=self.loop)
		self.t.daemon = True
		self.t.start()

		print('broker started!')
	def loop(self):
		while 1:
			self.mqttserver.loop()
	def wait(self):
		while True:
		    self.t.join(600)
		    if not self.t.isAlive():
			break
	'''
	The following methods are callback methods
	for mqtt. The method names should be enough
	to explain what each one does.
	'''
	def on_subscribe(self,mosq, obj, qos_list):
		print('broker subscribed to channel.')
	def on_unsubscribe(self,mosq, obj):
		print('hi')
	def on_message(self,obj, msg):
	    if (msg.topic=='server/connectedusers'):
		#broadcast available users
		#for user in conhandler.get_connectedusers():
		#    self.mqttserver.publish('client/connecteduser',user,1)
		print('received msg. topic is server/connectedusers')
	    elif (msg.topic=='server/servicelist'):
		#broadcast available services
		#for servicedetail in conhandler.get_servicedetails():
		#    self.mqttserver.publish('client/service',servicedetail,1)
		print('received msg. topic is server/servicelist')
	    elif (msg.topic=='server/useservice'):
		items = msg.payload.split(';')
		#self.conhandler.use_service(items[0], items[1])
		print('received msg. topic is server/useservice')
	    else:
		print(msg.topic)
	def on_connect(self,mosq, rc):
		if (rc==0):
			print('broker successfuly connected!')
			#
			# If connection is successful, registering for topics
			#
			self.mqttserver.subscribe('server/connectedusers',1)
			self.mqttserver.subscribe('server/servicelist',1)
			self.mqttserver.subscribe('server/useservice',1)

			#subscribing
			broadcaster.connectsubscribers.append(self.on_userconnect)
			broadcaster.disconnectsubscribers.append(self.on_userdisconnect)
			print(broadcaster.connectsubscribers)
		elif (rc==1):
			raise Exception('Mosquitto error: Unacceptable protocol version')
		elif (rc==2):
			raise Exception('Mosquitto error: Identifier rejected')
		elif (rc==3):
			raise Exception('Mosquitto error: Server unavailable')
		elif (rc==4):
			raise Exception('Mosquitto error: Bad user name or password')
		elif (rc==5):
			raise Exception('Mosquitto error: Not authorised')
	'''
	The following methods are for maintaing the
	connect and disconnect events sent by the broadcaster.
	'''
	def on_userconnect(self,username,macaddress):
		print('{} just connected!'.format(username))
	def on_userdisconnect(self,username,macaddress):
		print('{} just disconnected!'.format(username))
	
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Broker for listening to cloudlet connections.')
	parser.add_argument('-p','--port', type=int, nargs=1, help='Port to listen on.', required=False)
	args = vars(parser.parse_args())
	if (args['port']!=None):
		mqttport = args['port'][0]
		if (mqttport<1025):
			#
			# Defualting to using default port
			# as user attempted to use the root's
			# ports. There is no reason the program
			# should be run as root
			#
			mqttport = 1883
	else:
		mqttport = 1883 #default port
	b = commHandler(mqttport)
	b.wait()
