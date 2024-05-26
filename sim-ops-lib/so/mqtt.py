
import json
import paho.mqtt.client as mqtt

class MQTT:
    def __init__(self) -> None:
        self.client = mqtt.Client()
        self.client.connect(host='so-mqtt', port=1883)
        
    def publish(self, topic, data):
        print('publis', 'topic', topic)
        return self.client.publish(topic, json.dumps(data))
