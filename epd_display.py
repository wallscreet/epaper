#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from epd_driver import EPD_4in26
import time

class EPDDisplay:
    def __init__(self):
        self.epd = EPD_4in26()
        self.width = 800    # adjust for your specific panel resolution
        self.height = 480

    def initialize(self):
        """Initialize and clear the screen."""
        self.epd.init()
        self.clear()

    def clear(self):
        """Clear the e-ink display to white."""
        print("Clearing screen...")
        self.epd.clear()
        print("Screen cleared.")

    def display_text(self, text, font_size=24):
        """Render and display text on the e-ink screen."""
        print(f"Displaying text: {text}")
        # Create a blank image (white background)
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_size)
        except IOError:
            font = ImageFont.load_default()

        # Word wrapping for long text
        lines = []
        words = text.split(' ')
        line = ''
        for word in words:
            if draw.textlength(line + ' ' + word, font=font) < self.width - 20:
                line += ' ' + word
            else:
                lines.append(line.strip())
                line = word
        lines.append(line.strip())

        # Draw each line
        y = 10
        for line in lines:
            draw.text((10, y), line, font=font, fill=0)
            y += font_size + 5

        # Send image buffer to the display
        self._send_image(image)

    # def _send_image(self, image):
    #     """Convert image to buffer and send to the EPD."""
    #     print("Transmitting image buffer...")
    #     image = image.convert('1')
    #     buf = list(image.tobytes())

    #     # Break into bytes (8 pixels per byte)
    #     self.epd.send_command(0x10)
    #     for b in buf:
    #         self.epd.send_data(b)

    #     # Refresh display
    #     self.epd.send_command(0x12)
    #     self.epd.wait_until_idle()
    #     print("Image displayed.")
    def _send_image(self, image):
        """
        Convert a PIL image (mode '1' or convertible) into the packed bytes expected by
        the e-paper and send it using the low-level driver.
        Assumes display resolution is 800x480 (width x height).
        """
        TARGET_WIDTH = 800
        TARGET_HEIGHT = 480

        # Ensure image is in 1-bit mode
        img = image.convert('1')

        # If image size doesn't match, resize or rotate to fit.
        if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
            # try rotating if orientation swapped
            if img.size == (TARGET_HEIGHT, TARGET_WIDTH):
                img = img.rotate(90, expand=True)
            else:
                img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))

        # Pack 8 pixels per byte, MSB first (bit7 = leftmost pixel of the group)
        width = TARGET_WIDTH
        height = TARGET_HEIGHT
        bytes_per_row = width // 8
        buf = bytearray(bytes_per_row * height)

        for y in range(height):
            for x_byte in range(bytes_per_row):
                byte = 0
                for bit in range(8):
                    x = x_byte * 8 + bit
                    pixel = img.getpixel((x, y))
                    # Pillow '1' mode: 0=black, 255=white
                    if pixel == 0:
                        # set bit: MSB first
                        byte |= (0x80 >> bit)
                buf[y * bytes_per_row + x_byte] = byte

        # Send buffer to display
        print(f"Transmitting {len(buf)} bytes to display...")
        # Many Waveshare modules expect two-stage write: command 0x10 then 0x13 with same data
        self.epd.send_command(0x10)
        # send as chunks to avoid flooding SPI
        CHUNK = 1024
        for i in range(0, len(buf), CHUNK):
            chunk = buf[i:i+CHUNK]
            self.epd.send_data(list(chunk))

        # Some controllers expect a 2nd buffer write to 0x13 for the active buffer
        self.epd.send_command(0x13)
        for i in range(0, len(buf), CHUNK):
            chunk = buf[i:i+CHUNK]
            self.epd.send_data(list(chunk))

        # Trigger refresh
        self.epd.send_command(0x12)  # DISPLAY_REFRESH
        self.epd.wait_until_idle()
        print("Image displayed.")


    def sleep(self):
        """Put display to sleep."""
        self.epd.sleep()
