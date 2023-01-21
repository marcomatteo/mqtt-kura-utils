# mqtt-kura-utils
This repository have some basic utility scripts for testing MQTT messages between Kura and Kapua.

The connection to the broker is not with TLS, it may will be added in feature developments.
The MQTT credentials are usually stored locally in a _config.ini_ file. 

The file structure is like the following:

```
[MQTTSection]
mqtt.url=url
mqtt.clientid=clientid
mqtt.user=user
mqtt.password=password
mqtt.topic=topic
```
