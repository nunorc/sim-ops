
import os, json
import paho.mqtt.client as mqtt

SO_MQTT = os.getenv('SO_MQTT', 'so-mqtt')
if not SO_MQTT:
    SO_MQTT = 'so-mqtt'

class MQTT:
    def __init__(self, host=SO_MQTT, port=1883) -> None:
        self.client = mqtt.Client()
        self.client.connect(host=host, port=port)
        
    def publish(self, topic, data):
        return self.client.publish(topic, json.dumps(data))
