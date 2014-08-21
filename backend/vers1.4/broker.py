#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This is the broker class. It handles connections
# between the clients and the services
#
# "Get your facts first, then you can distort them as you please."
#  -Mark Twain
#

import mosquitto
import argparse
import handler

mqttserver = None
conhandler = None

def on_subscribe(mosq, obj, mid, qos_list):
	print('hello')
def on_unsubscribe(mosq, obj, mid):
	print('hi')
def on_message(mosq, obj, msg):
	if (msg.topic=='client/connect'):
			print(msg.payload)
def on_connect(mosq, rc):
	if (rc==0):
		#
		# If connection is successful, registering for topics
		#
		print('everything is amazing')
		global conhandler
		conhandler = handler.handler(mqttserver)
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
def main(mqttport):
	global mqttserver
	mqttserver = mosquitto.Mosquitto('cloudlet|maincontrol')
	mqttserver.on_subscribe = on_subscribe
	mqttserver.on_connect = on_connect
	mqttserver.on_message = on_message
	mqttserver.on_unsubscribe = on_unsubscribe
	mqttserver.connect('127.0.0.1', mqttport, keepalive=60)
	while 1:
		mqttserver.loop()
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
			mqttport = 9999
	else:
		mqttport = 9999 #default port
	main(mqttport)
