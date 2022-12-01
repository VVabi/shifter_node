import json
import paho.mqtt.client as mqtt


class BetterMqttClient():
    def __init__(self, host):
        self.client = mqtt.Client()
        self.client.on_message=self.on_message
        self.client.connect(host)
        self.client.loop_start()
        self.callbacks = {}

    def register_callback(self, topic, cb):
        if topic in self.callbacks:
            self.callbacks[topic].append(cb)
        else:
            self.callbacks[topic] = [cb]
        self.client.subscribe(topic)
    
    def on_message(self, client, userdata, message):
        topic = message.topic

        if topic in self.callbacks:
            for cb in self.callbacks[topic]:
                cb(topic, json.loads(str(message.payload.decode("utf-8"))))

    def publish(self, topic, payload):
        return self.client.publish(topic, payload)

    def publish_message(self, message):
        return self.publish(message.get_topic(), json.dumps(message.to_dict()))