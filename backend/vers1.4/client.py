import mosquitto
import sys
import threading

i = 0
mqttclient = None
def interface():
	while True:
		choice = input('1. Get Connected User List\n2. Get list of services\n3. Use Specific Service\n')
		if (choice==1):
			mqttclient.publish('server/connectedusers',"true")
		elif (choice==2):
		    mqttclient.publish('server/servicelist',"true")
		elif (choice==3):
		    name = input('service name')
def on_publish(mosq, obj):
	print("log: Message "+str(obj)+" published.")
def on_message(obj, msg):
    if (msg.topic=='client/service'):
        print(msg.payload)
def on_subscribe(mosq, obj, qos_list):
 	print("log: Subscribed.")
def main():
    global mqttclient
    mqttclient = mosquitto.Mosquitto('client')
    mqttclient.on_publish = on_publish
    mqttclient.on_message = on_message
    mqttclient.on_subscribe = on_subscribe
    mqttclient.connect('127.0.0.1', port=9999, keepalive=60)
    mqttclient.subscribe('client/connecteduser',1)
    mqttclient.subscribe('client/service',1)
    if(i):
        t = threading.Thread(target=interface)
        t.daemon = True
        t.start()
    while True:
        mqttclient.loop()
if __name__=='__main__':
	try:
	    i = sys.argv[1]
	except:
		pass
	main()
