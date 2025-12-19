import os
import sys
import time
import paho.mqtt.client as mqtt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

config.load()

BROKER = config.get("broker")  # IP of the broker device
PORT = config.get("port")
TOPIC = config.get("topic")
print(f"Using broker: {BROKER}, port: {PORT}, topic: {TOPIC}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    # Replace this with your actual sensor reading
    sensor_value = 42
    msg_info = client.publish(TOPIC, str(sensor_value), qos=1)
    msg_info.wait_for_publish()
    print(f"Published sensor value: {sensor_value}")
    time.sleep(1)
