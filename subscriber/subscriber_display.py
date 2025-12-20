import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from subscriber.mqtt_subscriber import MQTTSubscriber  

config.load()

BROKER = config.get("broker-subscriber")
PORT = config.get("port")
TOPIC = config.get("topic")  

subscriber = MQTTSubscriber(
    broker=BROKER,
    port=PORT,
    topic=TOPIC,
)

subscriber.connect()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
