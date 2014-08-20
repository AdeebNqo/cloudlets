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
def main(mqttport):
	mqttserver = mosquitto.Mosquitto('cloudlet|maincontrol')
	mqttserver.on_subscribe = self.on_subscribe
	mqttserver.on_connect = self.on_connect
	mqttserver.on_message = self.on_message
	mqttserver.on_unsubscribe = self.on_unsubscribe
	mqttserver.connect('127.0.0.1', mqttport, keepalive=60)
	while self.status:
		mqttserver.loop()
def on_subscribe(self, mosq, obj, mid, qos_list):
	print('hello')
def on_unsubscribe(self, mosq, obj, mid):
	print('hi')
def on_connect(self,mosq, obj, rc):
	if (rc==0):
		#
		# If connection is successful, registering for topics
		#
		print('everything is amazing')
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
def on_message(self,mosq, obj, msg):
	print('wazini?')
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Server for listening to cloudlet connections.')
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
