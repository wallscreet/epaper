import RPi.GPIO as GPIO
import time

# Import with error handling
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Run with 'sudo python3 nav_test.py'")
    exit(1)

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Suppress warnings
GPIO.cleanup()  # Reset GPIO states at start

# Define GPIO pins for navigation switches
UP_PIN = 26
DOWN_PIN = 19
LEFT_PIN = 13
RIGHT_PIN = 6
MID_PIN = 5
SET_PIN = 12

# List of all switch pins with labels for clarity
SWITCH_PINS = [
    (UP_PIN, "UP"),
    (DOWN_PIN, "DOWN"),
    (LEFT_PIN, "LEFT"),
    (RIGHT_PIN, "RIGHT"),
    (MID_PIN, "MID"),
    (SET_PIN, "SET")
]

# Setup each pin with internal pull-up resistor
for pin, _ in SWITCH_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Monitoring navigation switches (polling). Press Ctrl+C to exit.")
    while True:
        for pin, label in SWITCH_PINS:
            if GPIO.input(pin) == GPIO.LOW:  # Button pressed (low due to pull-up)
                print(f"{label} button on GPIO {pin} pressed!")
        time.sleep(0.01)  # 10ms delay to reduce CPU usage (per docs)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings