import paho.mqtt.client as mqtt
from logger_utils import get_logger
import logging

logger = get_logger(__name__, log_file="publisher.log", level=logging.DEBUG)


class MQTTClient:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.connected = False
        self.disconnected = False

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=2)
        logger.debug(
            f"MQTTClient initialized for broker: {broker}, port: {port}, topic: {topic}"
        )

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            self.disconnected = False
            logger.info("Connected to MQTT broker")
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

    def connect(self):
        self.client.connect(self.broker, self.port, 10)
        self.client.loop_start()

    def publish(self, payload, qos=1):
        if not self.connected:
            logger.warning("Cannot publish, client not connected")
            return
        msg_info = self.client.publish(self.topic, payload, qos=qos)
        msg_info.wait_for_publish()
        logger.debug(f"Published: {payload}")
