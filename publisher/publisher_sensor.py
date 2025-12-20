import time, sys, os, json, logging
from mqtt_client import MQTTClient
from sensor_utils import (
    get_motion_sensor,
    is_valid_sensor_data,
    pre_process_sensor_data,
)
from logger_utils import get_logger, clear_log

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

clear_log("publisher.log")
logger = get_logger(__name__, log_file="publisher.log", level=logging.DEBUG)

config.load()
logger.debug("Configuration loaded")


def handle_config_update(config_data):
    """Handle incoming configuration updates."""
    try:
        # Update config file
        with open(config.CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        logger.info(f"Config file updated: {config_data}")

        # Reload config in memory
        config.load()
        logger.info("Config reloaded")
    except Exception as e:
        logger.error(f"Failed to update config: {e}")


mqtt_client = MQTTClient(
    broker=config.get("broker-publisher"),
    port=config.get("port"),
    topic=config.get("topic"),
    config_topic=config.get("config_topic"),
    on_config_update=handle_config_update,
)
mqtt_client.connect()

PUBLISH_INTERVAL = config.get("publish_interval_s", 3)
WARMUP_IGNORE = config.get("warmup_ignore_s", 60)

logger.info(f"Publish interval: {PUBLISH_INTERVAL}s")
logger.info(f"Warmup ignore: {WARMUP_IGNORE}s")


seq_counter = 0
boot_time = time.time()
last_publish_time = 0

while True:
    now = time.time()

    if now - boot_time < WARMUP_IGNORE:
        time.sleep(0.1)
        continue

    sensor_value = get_motion_sensor()
    is_sensor_valid = is_valid_sensor_data(sensor_value)

    if is_sensor_valid:
        sensor_value = pre_process_sensor_data(sensor_value)

    # --- Publish pacing ---
    if now - last_publish_time >= PUBLISH_INTERVAL:
        data = {
            "sensor_value": sensor_value,
            "is_sensor_valid": is_sensor_valid,
            "timestamp": now,
            "seq": seq_counter,
        }

        payload = json.dumps(data)
        mqtt_client.publish(payload)

        # logger.debug(f"Published: {data}")

        seq_counter += 1
        last_publish_time = now

    # Prevent CPU burn
    time.sleep(0.05)
