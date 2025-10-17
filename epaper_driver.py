import spidev
import RPi.GPIO as GPIO
import time

# Pin definitions
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24
PWR_PIN = 18
MOSI_PIN = 10
SCLK_PIN = 11

class EPaper:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([RST_PIN, DC_PIN, CS_PIN, PWR_PIN], GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def spi_writebyte(self, data):
        self.spi.writebytes([data])

    def reset(self):
        self.digital_write(RST_PIN, 0)
        time.sleep(0.2)
        self.digital_write(RST_PIN, 1)
        time.sleep(0.2)

    def send_command(self, command):
        self.digital_write(DC_PIN, 0)
        self.digital_write(CS_PIN, 0)
        self.spi_writebyte(command)
        self.digital_write(CS_PIN, 1)

    def send_data(self, data):
        self.digital_write(DC_PIN, 1)
        self.digital_write(CS_PIN, 0)
        self.spi_writebyte(data)
        self.digital_write(CS_PIN, 1)

    def wait_busy(self):
        while self.digital_read(BUSY_PIN) == 1:
            time.sleep(0.01)

    def init(self):
        self.digital_write(PWR_PIN, 1)
        self.reset()
        self.send_command(0x12)  # Soft reset
        self.wait_busy()
        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x01)
        self.send_data(0x00)
        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)
        self.send_command(0x44)  # X address start/end
        self.send_data(0x00)
        self.send_data(0x31)
        self.send_command(0x45)  # Y address start/end
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_command(0x4E)  # X address counter
        self.send_data(0x00)
        self.send_command(0x4F)  # Y address counter
        self.send_data(0xF9)
        self.send_command(0x3C)  # Border waveform
        self.send_data(0x05)
        self.send_command(0x21)  # Display update control
        self.send_data(0x00)
        self.send_data(0x80)
        self.send_command(0x18)  # Temperature sensor
        self.send_data(0x80)
        self.wait_busy()

    def display(self, image):
        self.send_command(0x24)  # Write RAM
        for i in image:
            self.send_data(i)
        self.send_command(0x20)  # Display update
        self.wait_busy()

    def clear(self):
        self.send_command(0x24)  # Write RAM
        for i in range(0, 5000):
            self.send_data(0xFF)
        self.send_command(0x20)  # Display update
        self.wait_busy()

    def sleep(self):
        self.send_command(0x10)  # Deep sleep
        self.send_data(0x01)
        self.digital_write(PWR_PIN, 0)

if __name__ == "__main__":
    epd = EPaper()
    epd.init()
    epd.clear()
    epd.sleep()
    GPIO.cleanup()
