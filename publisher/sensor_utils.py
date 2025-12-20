import random
import time

def get_motion_sensor():
    """
    Mock function to simulate a motion sensor.
    Returns:
        1 if motion detected
        0 if no motion
    """
    # Simulate random motion detection
    return random.choice([0, 1])

def is_valid_sensor_data(data):
    """
    Validate the sensor data.
    Args:
        data: The sensor data to validate.
    Returns:
        True if data is valid, False otherwise.
    """
    return data in [0, 1]

def pre_process_sensor_data(data):
    """
    Pre-process the sensor data before publishing.
    Args:
        data: The raw sensor data.
    Returns:
        Processed sensor data.
    """
    # Example pre-processing: just return the data as is for now
    return data