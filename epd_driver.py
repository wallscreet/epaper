#!/usr/bin/env python3
import RPi.GPIO as GPIO
import spidev
import time

# Pin configuration
RST_PIN  = 17
DC_PIN   = 25
CS_PIN   = 8
BUSY_PIN = 24
PWR_PIN  = 18

# SPI setup
SPI_BUS = 0
SPI_DEVICE = 0

class EPD_4in26:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)
        GPIO.setup(PWR_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = 2000000  # 2 MHz is safe
        self.spi.mode = 0b00

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def send_command(self, command):
        self.digital_write(DC_PIN, GPIO.LOW)
        self.digital_write(CS_PIN, GPIO.LOW)
        self.spi.writebytes([command])
        self.digital_write(CS_PIN, GPIO.HIGH)

    def send_data(self, data):
        self.digital_write(DC_PIN, GPIO.HIGH)
        self.digital_write(CS_PIN, GPIO.LOW)
        if isinstance(data, int):
            data = [data]
        self.spi.writebytes(data)
        self.digital_write(CS_PIN, GPIO.HIGH)

    def wait_until_idle(self):
        print("Waiting for display...")
        while GPIO.input(BUSY_PIN) == 0:
            self.delay_ms(100)
        print("Display ready.")

    def reset(self):
        self.digital_write(RST_PIN, GPIO.HIGH)
        self.delay_ms(200)
        self.digital_write(RST_PIN, GPIO.LOW)
        self.delay_ms(2)
        self.digital_write(RST_PIN, GPIO.HIGH)
        self.delay_ms(200)

    def power_on(self):
        self.digital_write(PWR_PIN, GPIO.HIGH)
        self.delay_ms(100)
        print("Power on complete.")

    def power_off(self):
        self.digital_write(PWR_PIN, GPIO.LOW)
        print("Power off.")

    # def init(self):
    #     print("Initializing EPD...")
    #     self.power_on()
    #     self.reset()
    #     # Example initialization commands (may vary by controller)
    #     self.send_command(0x01)  # POWER_SETTING
    #     self.send_data([0x03, 0x00, 0x2B, 0x2B, 0x13])

    #     self.send_command(0x06)  # BOOSTER_SOFT_START
    #     self.send_data([0x17, 0x17, 0x17])

    #     self.send_command(0x04)  # POWER_ON
    #     self.wait_until_idle()

    #     self.send_command(0x00)  # PANEL_SETTING
    #     self.send_data(0x3F)

    #     self.send_command(0x30)  # PLL_CONTROL
    #     self.send_data(0x3C)

    #     print("EPD init done.")
    def init(self):
        print("Initializing EPD...")
        try:
            self.power_on()
        except Exception:
            print("Skipping power pin activation (not used)")
        self.reset()

        # Some 4.26 controllers need an initial dummy command:
        self.send_command(0x00)
        self.send_data(0x0F)

        # Power settings
        self.send_command(0x01)
        self.send_data([0x03, 0x00, 0x2B, 0x2B, 0x09])

        self.send_command(0x06)
        self.send_data([0x17, 0x17, 0x17])

        self.send_command(0x04)
        print("Sent POWER_ON")
        self.delay_ms(200)
        #self.wait_until_idle()

        self.send_command(0x00)
        self.send_data(0x3F)

        self.send_command(0x30)
        self.send_data(0x3C)
        print("EPD init done.")

    def clear(self):
        # Example clear sequence (white)
        print("Clearing display...")
        self.send_command(0x10)
        for _ in range(800 * 480 // 8):  # Adjust resolution if needed
            self.send_data(0xFF)
        self.send_command(0x13)
        for _ in range(800 * 480 // 8):
            self.send_data(0xFF)
        self.send_command(0x12)  # DISPLAY_REFRESH
        self.wait_until_idle()
        print("Clear complete.")

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.wait_until_idle()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)
        self.power_off()

if __name__ == '__main__':
    epd = EPD_4in26()
    epd.init()
    epd.clear()
    epd.sleep()
    GPIO.cleanup()
