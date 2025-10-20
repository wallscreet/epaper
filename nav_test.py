import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()  # Reset GPIO states

UP_PIN = 26
DOWN_PIN = 19
LEFT_PIN = 13
RIGHT_PIN = 6
MID_PIN = 5
SET_PIN = 12

SWITCH_PINS = [UP_PIN, DOWN_PIN, LEFT_PIN, RIGHT_PIN, MID_PIN, SET_PIN]

for pin in SWITCH_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_pressed(channel):
    print(f"Button on GPIO {channel} pressed!")

for pin in SWITCH_PINS:
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_pressed, bouncetime=200)

try:
    print("Monitoring navigation switches. Press Ctrl+C to exit.")
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()