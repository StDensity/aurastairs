import time, sys, os, json
from mqtt_client import MQTTClient
from sensor_utils import (
    get_motion_sensor,
    is_valid_sensor_data,
    pre_process_sensor_data,
)
from logger_utils import get_logger, clear_log
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import config

clear_log("publisher.log")

logger = get_logger(__name__, log_file="publisher.log", level=logging.DEBUG)

config.load()
logger.debug("Configuration loaded")

mqtt_client = MQTTClient(
    broker=config.get("broker-publisher"),
    port=config.get("port"),
    topic=config.get("topic"),
)

mqtt_client.connect()


while True:
    sensor_value = get_motion_sensor()
    is_sensor_valid = is_valid_sensor_data(sensor_value)
    if not is_sensor_valid:
        logger.warning(f"Invalid sensor data: {sensor_value}")
        is_sensor_valid = False
    else: 
        is_sensor_valid = True
        sensor_value = pre_process_sensor_data(sensor_value)
    logger.debug(f"Preprocessed sensor value: {sensor_value}")
    data = {
        "sensor_value": sensor_value,
        "is_sensor_valid": is_sensor_valid,
    }
    payload = json.dumps(data)
    mqtt_client.publish(payload)
    time.sleep(3)
