#
# Client for testing purposes
#
import mosquitto

def on_publish(mosq, obj, mid):
	print("Message "+str(mid)+" published.")
def on_message(mosq, obj, msg):
	print(msg)
def main():
	mqttclient = mosquitto.Mosquitto('client')
	mqttclient.connect('127.0.0.1', port=9999, keepalive=60)
	mqttclient.on_publish = on_publish
	mqttclient.on_message = on_message
	mqttclient.subscribe("server/service")
	#mqttclient.publish("client/list", payload=None)
	mqttclient.publish("client/list", "hello world", 1)
	while True:
		mqttclient.loop()
if __name__=='__main__':
	main()
