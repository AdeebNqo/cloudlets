Cloudlets
=========

##Client Development: Protocol

####Connecting

0. Client: Connect to WiFi with the ssid `CloudletX`, retrieve mac address.
1. Client: Connect to mosquitto using the name `<username>|<macaddress>`
2. Client: Subscribe to mqtt channel `server/login`
3. Client: Connecting status will be received on that channel. The possible
responses are `OK`, `UDUP` and `MDUP`.

	- `OK` : Connecting is successful.
	- `UDUP` : The username is a duplicate.
	- `MDUP` : The Mac address is a duplicate.

(Note, the cloudlet will wait for 2 seconds before sending response to `server/login`.
This should be enough time to subscribe to the channnel after connecting on the client side.)
4. Client: Connect to channels `client/connecteduser` and `client/service`


####Requesting service

Before a client can use a service, they have to request it. This process is a way of setting up the
neccessary channels for communication.

0. Client: Register for receiving service request responses on `client/useservice/<username>|<macaddress>`
1. Client: Publish the following:`<username>|<macaddress>;<servicename>` on channel `server/useservice`.
2. Client: Get response on `client/useservice/<username>|<macaddress>`, there possible responses are `OK` and `NE`.

	- `OK` : Request approved, you can start using the service.
	- `NE` : Request not approved, the service does not exist.

3. Client: If client recieves `OK`, it is important to register to a couple of channels.
	-`client/<servicename>/<username>|<macaddress>/fetch`
	-`client/<servicename>/<username>|<macaddress>/update`
	-`client/<servicename>/<username>|<macaddress>/upload`
	-`client/<servicename>/<username>|<macaddress>/remove`
These channels will used to receieve responses from the cloudlet. However, in order to send to the server for
the actions one should use the following channels:
	-`server/<servicename>/<username>|<macaddress>/fetch`
	-`server/<servicename>/<username>|<macaddress>/update`
	-`server/<servicename>/<username>|<macaddress>/upload`
	-`server/<servicename>/<username>|<macaddress>/remove`

### General Notes

The identifier for the file is the name. This is enough because each person will have their own "bubble" of storage.

1. upload : Send metadata to the channel, the response the client will get should determine what to do. The possible
responses are `FDUP`, that is filename duplicate, or `OK <ip>:<port>`. In the case where one receives the ok signal,
open a socket to the provided ip and port and transfer the file.

2. fetch: Send the metadata containing the filename of the file you want to fetch, and the address (ip:port) to use
if you can access the requested file. The file will be sent only if the reponse `OK` is sent back on the channel
`client/<servicename>/<username>|<macaddress>/fetch`

3. update: Send the metadata containing the filename of the file and the updated metadata for the file. Only two 
responses are to be expected: `OK`, `FAIL`.

4. remove: Send the metadata containing the filename of the file. Only two 
responses are to be expected: `OK`, `FAIL`.
