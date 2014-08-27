subscribers = []

def subscribe(subscriber):
	subscribers.append(subscriber)
def notify(action, userdetails):
	for subscriber in subscribers:
		if (action=='connect'):
			subscriber(userdetails)
		elif (action=='disconnnect'):
			prit
