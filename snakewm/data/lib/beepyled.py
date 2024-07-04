#!/usr/bin/python

"""
Copyright (c) 2023 Asa Durkee. MIT License.
Python controller for beepy RGB and keyboard LEDs.
Requires beepy-keyboard-driver by ardangelo.

Run this file as a script to run the LED fade demo.
"""
import io
import os
import time

def get_running_hardware():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as raspi_model:
            if "raspberry pi" in raspi_model.read().lower():
                system_string = raspi_model
                return "raspi"
    except Exception:
        print("ERROR: This running machine is not a raspi.")
        print("ERROR: beepyled requires raspi hardware.")
    return False

HW_RUN = get_running_hardware()

# Each LED is exposed directly on the file system (Linux 'sysfs')
# by the beepberry-keyboard-driver by ardangelo.
# Read and write to these 'files' to inspect and control LEDs.
led_power = "/sys/firmware/beepy/led"  # Controls power to all LEDs
led_red   = "/sys/firmware/beepy/led_red"
led_green = "/sys/firmware/beepy/led_green"
led_blue  = "/sys/firmware/beepy/led_blue"
keyboard_backlight = "/sys/firmware/beepy/keyboard_backlight"

# Delay between brightness changes in the LED fade demo.
breathe_delay = 0.1     # 1.000 = 1 second. 0.001 = 1ms.

__all__ = ["BeepyLed"]

class BeepyLed:
    """ Interface for the beepy RGB and keyboard LEDs.
        Constructor - creates a BeepyLed object.
        Parameters:
            led_name - name of the LED to control.
            brightness - 0 through 255.
    """
    def __init__(self, led_name = led_red):
        with open(led_name, mode='w') as led:
            led.write('1')  # brightness from 0-255

    def set_led(self, led_name, brightness):
        print("INFO : Setting " + led_name + " brightness to " + brightness)
        with open(led_name, mode='w') as led:
            led.write(str(brightness))

# Demo example. Run this file as a script to run the LED fade demo.
def main():
    with open(led_power, mode='w') as enable_power_to_leds:
        enable_power_to_leds('1')
    leds_to_illuminate = [led_red, led_green, led_blue, keyboard_backlight]
    for led in leds_to_illuminate:
        print("INFO : Fading " + led + "...")
        breathe(led)

def breathe(led_to_illuminate):
    breathe_brightness_levels = [0,10,30,60,100,120,160,200,225,255]
    for brightness in breathe_brightness_levels:
        with open(led_to_illuminate, mode='w') as set_led_brightness_to:
            set_led_brightness_to.write(str(brightness))
        time.sleep(breathe_delay)
    for brightness in reversed(breathe_brightness_levels):
        with open(led_to_illuminate, mode='w') as set_led_brightness_to:
            set_led_brightness_to.write(str(brightness))
        time.sleep(breathe_delay)

if __name__ == "__main__":
    uid = os.geteuid()
    print("INFO : Current UID is " + str(uid) + ".")
    if os.geteuid() == 0:
        print("INFO : Script is running as root. This is expected behavior.")
    if os.geteuid() != 0:
            exit("ERROR: You need to run this script with sudo, or as the root user.")
    print("INFO : Running LED demo: fading R,G,B, keyboard LEDs...")
    main()
