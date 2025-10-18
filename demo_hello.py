#!/usr/bin/env python3
from epd_display import EPDDisplay
import time

if __name__ == '__main__':
    display = EPDDisplay()
    display.initialize()

    # Show text
    display.display_text("Hello, World! Raspberry Pi Zero + Waveshare 4.26 ePaper")
    time.sleep(10)

    # Clear screen again
    display.clear()
    display.sleep()
