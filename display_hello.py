from epaper_driver import EPaper
from PIL import Image, ImageDraw, ImageFont
import time

def display_hello_world():
    epd = EPaper()
    epd.init()

    # Create image buffer (400x300 for 4.26inch e-Paper)
    image = Image.new('1', (400, 300), 255)  # 255: white
    draw = ImageDraw.Draw(image)

    # Load default font
    font = ImageFont.load_default()

    # Draw text
    draw.text((100, 120), "Hello, World!", font=font, fill=0)

    # Convert image to array
    image_data = list(image.getdata())
    epd.display(image_data)

    # Sleep after 5 seconds
    time.sleep(5)
    epd.sleep()

if __name__ == "__main__":
    display_hello_world()