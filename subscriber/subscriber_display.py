import os
import sys
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from mqtt_subscriber import MQTTSubscriber
from ui import SubscriberUI

config.load()

BROKER = config.get("broker-subscriber")
PORT = config.get("port")
TOPIC = config.get("topic")

root = tk.Tk()

subscriber = MQTTSubscriber(
    broker=BROKER,
    port=PORT,
    topic=TOPIC,
    on_message_callback=None,
)

ui = SubscriberUI(root, publish_config_callback=subscriber.publish_config)
subscriber.on_message_callback = ui.update_from_data

subscriber.connect()

root.mainloop()
