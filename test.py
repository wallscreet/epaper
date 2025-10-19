#!/usr/bin/python

import sys
import os
import logging
from driver import EPD, epdconfig
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd4in26 Demo")
    epd = EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype('Font.ttc', 24)
    font18 = ImageFont.truetype('Font.ttc', 18)
    font35 = ImageFont.truetype('Font.ttc', 35)
    font55 = ImageFont.truetype('Font.ttc', 55)

    # Loading the logo
    logging.info("Loading and converting logo...")
    logo = Image.open('logo.png')  # Your logo file
    logo = logo.convert('L')  # Convert to grayscale
    logo = logo.convert('1')  # Convert to 1-bit monochrome (black/white)
    max_size = (200, 200) # Resize logo
    logo.thumbnail(max_size, Image.Resampling.LANCZOS)  # Resize while preserving aspect ratio

    logo_width, logo_height = logo.size
    logo_x = (epd.height - logo_width) // 2  # Center horizontally
    logo_y = 100  # Center vertically

    # Drawing on the Vertical image
    logging.info("Drawing on the Vertical image...")
    Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    # draw.text((2, 0), 'Hello, world!', font = font35, fill = 0)
    text = 'Hello, world!'
    bbox = draw.textbbox((0, 0), text, font=font55)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (epd.height - text_width) // 2
    y = (epd.width - text_height) // 2
    draw.text((x, y), text, font=font55, fill=0)

    # draw.text((2, 30), 'www.coreaderai.com', font = font35, fill = 0)
    text2 = 'www.coreaderai.com'
    bbox2 = draw.textbbox((0, 0), text2, font=font35)
    text2_width = bbox2[2] - bbox2[0]
    text2_height = bbox2[3] - bbox2[1]
    x2 = (epd.height - text2_width) // 2  # Left margin
    y2 = y + text_height + 20  # Below first text
    draw.text((x2, y2), text2, font=font35, fill=0)

    Limage.paste(logo, (logo_x, logo_y))

    epd.display(epd.getbuffer(Limage))
    time.sleep(10)

    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epdconfig.module_exit(cleanup=True)
    exit()