import os
import sys
import time
import paho.mqtt.client as mqtt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

config.load()

BROKER = config.get("broker-subscriber")
PORT = config.get("port")
TOPIC = config.get("topic")  # must match publisher
print(f"Using broker: {BROKER}, port: {PORT}, topic: {TOPIC}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received on {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()
