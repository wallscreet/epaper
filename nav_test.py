import RPi.GPIO as GPIO

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for navigation switches
UP_PIN = 26
DOWN_PIN = 19
LEFT_PIN = 13
RIGHT_PIN = 6
MID_PIN = 5
SET_PIN = 12

# List of all switch pins
SWITCH_PINS = [UP_PIN, DOWN_PIN, LEFT_PIN, RIGHT_PIN, MID_PIN, SET_PIN]

# Setup each pin with internal pull-up resistor
for pin in SWITCH_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Example callback function for button press
def button_pressed(channel):
    print(f"Button on GPIO {channel} pressed!")

# Add event detection for each pin (detects low signal when pressed)
for pin in SWITCH_PINS:
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

try:
    print("Monitoring navigation switches. Press Ctrl+C to exit.")
    while True:
        pass  # Keep script running to detect events
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings