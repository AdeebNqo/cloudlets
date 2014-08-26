ToDo:

[ ] Add File Sharing service

[ ] Create event listener to catch client (dis)connects

[ ] Create data storage and compression handlers

Plugin development
==================

The services all should be under the folder
`/services/`. When you create a new service
called 'myservice' for instance. Create a folder
under the services folder that looks like this:

	- myservice
		- `description.txt`
		- `__init__.py`

The description file is a description of your
service. It also contains your contact information.
Here's a sample a description file:

	Name=myservice
	CloudletV=1.4
	Description=A test service that prints hello.
	Authors=Andile Uyeva <uyeva@linuxanyone.com>
	Copyright=Copyright © 2007 Andile Uyeva
	Website=http://andileuyeva.com/

These fields are the only ones allowed, all others will be
ignored. Also, it is good practice to name your service folder
with the same name of the service for the users' convience.
Each service should have two methods:

	1. start(mqttbroker)
	2. stop()

The main/driver class for your service which is to be created
in the `__init__.py` file, must have the same name as the service.

Cloudlet Connect Protocol
==========================

There are four channels to consider when trying to communicate
between a client and the broker.

	1. server/connectedusers - Used by clients to request list
	of connected users
	2. server/connecteduser - Used by broker to send connected
	users one by one.
	3. client/servicelist - Used by clients to request list
	of available services
	4. server/service - Used by broker to send available services
	5. server/useservice - Used by client when they request to use a specific service. It is expected that they send their identifier and service name they want to use.


