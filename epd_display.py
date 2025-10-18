#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from epd_driver import EPD_4in26
import time

class EPDDisplay:
    def __init__(self):
        self.epd = EPD_4in26()
        self.width = 400    # adjust for your specific panel resolution
        self.height = 300

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

    def _send_image(self, image):
        """Convert image to buffer and send to the EPD."""
        print("Transmitting image buffer...")
        image = image.convert('1')
        buf = list(image.tobytes())

        # Break into bytes (8 pixels per byte)
        self.epd.send_command(0x10)
        for b in buf:
            self.epd.send_data(b)

        # Refresh display
        self.epd.send_command(0x12)
        self.epd.wait_until_idle()
        print("Image displayed.")

    def sleep(self):
        """Put display to sleep."""
        self.epd.sleep()
