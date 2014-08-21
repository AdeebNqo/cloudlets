import mosquitto
def on_publish(mosq, obj, mid):
	print("Message "+str(mid)+" published.")
def on_message(mosq, obj, msg):
	print(msg)
def on_subscribe(mosq, obj, mid, qos_list):
 	print("Subscribe with mid "+str(mid)+" received.")
def main():
	mqttclient = mosquitto.Mosquitto('client')
	mqttclient.on_publish = on_publish
	mqttclient.on_message = on_message
	mqttclient.on_subscribe = on_subscribe
	mqttclient.connect('127.0.0.1', port=9999, keepalive=60)
	while True:
		mqttclient.loop()
if __name__=='__main__':
	main()
