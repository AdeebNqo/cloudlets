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
import userMan
import serviceMan
import time

class commHandler(object):
	def __init__(self,mqttport):
		self.mqttserver = None
		self.usermanager = None
		self.servicemanager = None
		#
		# Setting up all the neccessary callback methods
		# for mosquitto communication. mqqtconnection.loop()
		# is called using a thread.
		#
		self.mqttserver = mosquitto.Mosquitto('cloudlet|maincontrol')
		self.mqttserver.on_subscribe = self.on_subscribe
		self.mqttserver.on_connect = self.on_connect
		self.mqttserver.on_message = self.on_message
		self.mqttserver.on_unsubscribe = self.on_unsubscribe
		self.mqttserver.connect('127.0.0.1', mqttport, keepalive=60)
		self.t = threading.Thread(target=self.loop)
		self.t.daemon = True
		self.t.start()

		self.requestlist = set()
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
	to explain what each method does.
	'''
	def on_subscribe(self, mosq, obj, mid, qos_list):
		print('broker subscribed to channel.')
	def on_unsubscribe(self,mosq, obj):
		print('broker: unsubscribe')
	def on_message(self,mosq, obj, msg):
		if (msg.topic=='server/connectedusers'):
			#broadcast available users
			for user in self.usermanager.get_connected():
				self.mqttserver.publish('client/connecteduser/{}'.format(msg.payload),'|'.join(user),1)
			print('received msg. topic is server/connectedusers')
		elif (msg.topic=='server/servicelist'):
			#broadcast available services
			for servicedetail in self.servicemanager.get_servicelist():
				self.mqttserver.publish('client/service/{}'.format(msg.payload),servicedetail.__str__(),1)
			print('received msg. topic is server/servicelist')
		elif (msg.topic=='server/logout'):
			(name, mac) = msg.payload.split('|')
			broadcaster.disconnect(name,mac)
		elif (msg.topic=='server/serviceusers'):
			#channel used by client when requesting to know users of a specific service
			try:
				(servicename, requester) = msg.payload.split('|')
				serviceusers = self.usermanager.who_uses(servicename)
				for user in serviceusers:
					self.mqttserver.publish('client/serviceuserslist/{}'.format(requester), user)
			except:
				pass
		elif (msg.topic=='server/useservice'):
			items = msg.payload.split(';')
			(username,macaddress) = items[0].split('|')
			servicename = items[1]
			#
			# Begin by seeing if client is not already using service
			# and if that service exists
			#
			if (self.usermanager.service_request((username,macaddress), servicename)=='OK'):
				response = self.servicemanager.request_service((username,macaddress), servicename).split()
				print('service request: service manager says {}'.format(response))
				if (response[0]=='OK'):
					ipport = response[1]
					print('client has successfully requested service and should get it.')
					if ('|' in ipport):
						#creating channel with the identifier of the mobile that is requesting service.
						self.mqttserver.subscribe('server/service_request/{2}/{0}|{1}'.format(username,macaddress, servicename),1)
						#adding that channel to watchlist to that it can be removed once device responds
						self.requestlist.add('server/service_request/{2}/{0}|{1}'.format(username,macaddress,servicename))
						#sending the username and macaddress of guy requesting service to the mobile device with service.
						#this is crucial as this means that the mobile has the chance to look at the identifier and determine whether
						#or not to reject the connection
						self.mqttserver.publish('client/service_request/{}'.format(ipport),'{0}|{1}|{2}'.format(username,macaddress,servicename))
					elif (ipport != 'Service not available'):
						print('requested service is available')
						self.mqttserver.publish('client/service_request/{2}/{0}|{1}/recvIP'.format(username,macaddress, servicename), '{0}|{1}'.format(servicename, ipport))
				else:
					self.mqttserver.publish('client/useservice/{}'.format(items[0]),'NE')
			else:
				self.mqttserver.publish('client/useservice/{}'.format(items[0]),'NE')
		elif (msg.topic=='server/service'):
			self.servicemanager.add_service(msg.payload)
		else:
			print('last else, the msg topic is {}'.format(msg.topic))
			if (msg.topic in self.requestlist):
				(serverstring, serverequeststring, servicename, usernameandmacaddress) = msg.topic.split('/')
				(username, macaddress) = usernameandmacaddress.split('|')
				print('sent ip to {0}|{1}'.format(username, macaddress))
				self.mqttserver.publish('client/service_request/{2}/{0}|{1}/recvIP'.format(username, macaddress, servicename), "{0}|{1}".format(servicename, msg.payload))
				self.requestlist.remove(msg.topic)
	'''
	Called once, only when the communication
	handler is connecting to mosquitto.
	'''
	def on_connect(self,mosq, obj, rc):
		if (rc==0):
			#
			# If connection is successful, registering for topics
			#
			self.mqttserver.subscribe('server/connectedusers',1)
			self.mqttserver.subscribe('server/servicelist',1)
			self.mqttserver.subscribe('server/useservice',1)
			self.mqttserver.subscribe('server/service',1)
			self.mqttserver.subscribe('server/serviceusers',1)
			self.mqttserver.subscribe('server/logout',1)
			# Creating the user manager if the communication is functioning
			self.usermanager = userMan.userMan()
			# Creating the service manager and loading services
			self.servicemanager = serviceMan.serviceMan()
			self.servicemanager.loadlocal_services()

			#
			# Subscribing to mosquitto event broadcaster to receive
			# connect and disconnect signals.
			#
			broadcaster.connectsubscribers.append(self.on_userconnect)
			broadcaster.disconnectsubscribers.append(self.on_userdisconnect)
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
	The following methods are for maintaining the
	connect and disconnect events sent by the broadcaster.

	Arguments:
	username: Username of the connecting/disconnecting party.
	macaddress: Macaddress of the connecting/disconnecting party.
	'''
	def on_userconnect(self,username,macaddress):
		macaddress = macaddress.split()[0]
		response = self.usermanager.connect(username, macaddress)
		time.sleep(2)
		self.mqttserver.publish('server/login/{}'.format(username),response)
	def on_userdisconnect(self,username,macaddress):
		#
		# Notifying services used by client to remove it
		#
		usedservices = self.usermanager.get_servicesofclient((username,macaddress))
		for service in usedservices:
			self.servicemanager.disconnectfromservice(service,username)
		#
		#disconnecting user from user manager and removing all
		#their advertized services
		#
		self.usermanager.disconnect(username, macaddress)
		self.servicemanager.remove_allservices('{0}|{1}'.format(username, macaddress))

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
