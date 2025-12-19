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

# Example usage
if __name__ == "__main__":
    while True:
        motion = get_motion_sensor()
        print(f"Motion detected: {motion}")
        time.sleep(1)  # simulate 1-second polling
