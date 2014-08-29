Cloudlets
=========

##Client Development: Protocol

####Connecting

0. Client: Connect to WiFi with the ssid `CloudletX`, retrieve mac address.
1. Client: Connect to mosquitto using the name `<username>|<macaddress>`
2. Client: Subscribe to mqtt channel `server/login`
3. Client: Connecting status will be received on that channel. The possible
responses are `OK`, `UDUP` and `MDUP`.

	`OK` - Connecting is successful.
	`UDUP` - The username is a duplicate.
	`MDUP` - The Mac address is a duplicate.

(Note, the cloudlet will wait for 2 seconds before sending response to `server/login`.
This should be enough time to subscribe to the channnel after connecting on the client side.)
