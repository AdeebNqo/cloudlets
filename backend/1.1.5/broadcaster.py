#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This file broadcast connect and disconnet signals
# to subscribers.
#
connectsubscribers = []
disconnectsubscribers = []

def connect(username,macaddress):
	global connectsubscribers
	if len(connectsubscribers)>0:
		for func in connectsubscribers:
			func(username,macaddress)
def disconnect(username,macaddress):
	global disconnectsubscribers
	if len(disconnectsubscribers)>0:
		for func in disconnectsubscribers:
			func(username,macaddress)
def connectsubscribe(somefunc):
	global connectsubscribers
	connectsubscribers.append(somefunc)
def disconnectsubscribe(somefunc):
	global disconnectsubscribers
	disconnectsubscribers.append(somefunc)
