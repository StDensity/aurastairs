import paho.mqtt.client as mqtt
from logger_utils import get_logger
import json
import logging

logger = get_logger(__name__, log_file="subscriber.log", level=logging.DEBUG)


class MQTTSubscriber:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.connected = False
        self.disconnected = False

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=2)
        logger.debug(
            f"MQTTSubscriber initialized for broker: {broker}, port: {port}, topic: {topic}"
        )

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            self.disconnected = False
            logger.info("Connected to MQTT broker")
            self.client.subscribe(self.topic)
            logger.debug(f"Subscribed to topic: {self.topic}")
        else:
            logger.error(f"Connection failed with code {rc}")

    def on_disconnect(
        self, client, userdata, disconnect_flags, reason_code, properties
    ):
        self.connected = False
        self.disconnected = True
        if reason_code != 0:
            logger.warning(f"Unexpected disconnect. Code: {reason_code}")
        else:
            logger.info("Disconnected cleanly")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode()
            data = json.loads(payload_str)
            logger.info(f"Message received: {data}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON: {msg.payload}")

    def connect(self):
        self.client.connect(self.broker, self.port, 10)
        self.client.loop_start()


if __name__ == "__main__":
    # Example usage
    BROKER = "localhost"  # or IP of broker
    PORT = 1883
    TOPIC = "aurastairs/motion"

    subscriber = MQTTSubscriber(BROKER, PORT, TOPIC)
    subscriber.connect()

    # Keep running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Subscriber stopped by user")
