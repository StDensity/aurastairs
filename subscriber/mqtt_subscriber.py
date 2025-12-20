import json
import paho.mqtt.client as mqtt
from logger_utils import get_logger, clear_log
import logging

clear_log("subscriber.log")

logger = get_logger(__name__, log_file="subscriber.log", level=logging.DEBUG)


class MQTTSubscriber:
    def __init__(self, broker, port, topic, on_message_callback):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_message_callback = on_message_callback

        self.connected = False

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(1, 2)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            logger.info("Subscriber connected")
            client.subscribe(self.topic)
        else:
            logger.error(f"Connect failed: {rc}")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self.connected = False
        logger.warning(f"Disconnected: {reason_code}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
            logger.debug(f"Received: {data}")
            self.on_message_callback(data)
        except Exception as e:
            logger.error(f"Bad message: {e}")

    def connect(self):
        self.client.connect(self.broker, self.port, 10)
        self.client.loop_start()
