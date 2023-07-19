DESCRIPTION
===========
Installs a DirectFB toolchain for the beepy open hardware platform described here:
  * https://beepy.sqmfi.com
  * https://github.com/beeper/beepberry

QUICK SETUP (skipping important details)
========================================
  * SSH to the Raspi
  * sudo apt install -y git
  * cd ~
  * git clone --depth 1 https://github.com/hack-shack/beepy-directfb2
  * cd beepy-directfb2
  * ./build-sdk.py


FULL SETUP (headless over SSH)
========================================
  * Get a spare microSD card.
  * Download Raspberry Pi Imager from https://www.raspberrypi.com/software
  * Open the the Raspberry Pi Imager tool.
    * The tool's main window opens to a large Raspberry Pi logo.
    * On the left, click the button: "Operating System > Choose OS".
    * A list of Operating Systems appears. Click the second icon, a black-and white Raspberry Pi icon listed as "Raspberry Pi OS (other)"
    * A list of other Operating Systems appears. Click "Raspberry Pi OS Lite (32-bit)."
    * NOTE: Fight the urge to install 64-bit. This SDK assumes the "default" 32-bit Raspbian Lite distro.
    * NOTE: Also fight the urge to install Raspberry Pi Full (not Lite). This build script will fail.
    * You'll be returned to the tool's main window. Click "Select Storage" and choose your microSD card.
    * In the tool's main window, click the gear icon in the lower right.
      * If asked to pre-fill a password from the system keychain, click No.
        * Advanced Options appears. Do the following:
          * Set hostname: recommend something like "beepy"
          * Enable SSH: checked. Use password authentication: selected.
          * Set username and password: checked.
            * Create a username and password for yourself.
        * Configure wireless LAN
          * SSID: must be a 2.4GHz SSID as the Raspi Zero 1 and 2 do not have 5GHz radios
          * SSID password: enter it here
          * Wireless LAN country: you can type the ISO shortname instead of using the dropdown. US is US BTW
        * Set locale settings: important for your clock
        * Keyboard layout: leave at "us" to correctly map the beepy's built-in Q20 keyboard
      * Configure Persistent Settings at bottom
        * Make sure "eject media when finished" is UNCHECKED
      * Click "SAVE"
      * Back in the tool's main window, click the "WRITE" button.
  * When the imaging is done, create a file called "ssh" on the root level of the bootfs drive that the Imager has made. This will trigger ssh to start automatically at boot.
    * On a Mac, in Terminal: touch /Volumes/bootfs/ssh
  * NOTE: If you do not create this file, SSH will not start and you will be unable to get into the Pi.
  * Eject and remove the microSD card from your computer.
  * Insert the microSD card into the Pi, plug USB-C into the beepy, and slide its power switch on (to the right).
  * Start a continuous ping to the device. Recommend you have a DHCP reservation for its MAC address so it's a consistent IP every time.
  * Be patient. Time after firstboot before it responds to pings: Raspi Zero 2 with Class 10 microSD: ~3 minutes. Raspi Zero 1 with slow microSD: ~6-10 minutes.

  * SSH to the Raspi
  * sudo apt install -y git
  * cd ~
  * git clone --depth 1 https://github.com/hack-shack/beepy-directfb2
  * cd beepy-directfb2
  * ./build-sdk.py

Don't run install-sharp-driver.py. The build-sdk script will obtain its dependencies, then do this for you.

RUNNING EXAMPLES
===========================================================
Currently, you must run examples as root.

  * cd ~/beepy-directfb2
  * sudo su
  * export DFBARGS="system=fbdev,fbdev=/dev/fb1"
  * LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf/;export LD_LIBRARY_PATH

Now you can run examples. Quit them with ctrl-C. Remember, you will need to first set the 2 environmental variables above in your session before running them.

Display an image (replace the USERNAME with your actual Pi home username)
  * /usr/local/bin/df_image_sample data/raven.png
  * Public domain image from "The swallow and the raven," Elmer Boyd Smith, c. 1910, https://lccn.loc.gov/2010718076

Displays a progress bar, then quits:
  * /usr/local/bin/lite_progressbar

Shows a quick animation, then quits after a few seconds:
  * /usr/local/bin/df_pss

Displays keyboard and mouse input. Good for testing the beepy hardware.
  * /usr/local/bin/df_input

A starfield controlled by the mouse. Good way to test if your touchpad is working.
  * /usr/local/bin/df_spacedream

Shows a chessboard texture. It can be moved around by clicking and dragging on the touchpad.
  * /usr/local/bin/df_texture

Displays a GUI for RGB slider adjustment. Does not affect beepy RGB LED.
  * /usr/local/bin/lite_slider

Image viewer (must specify an image file - note you must replace the home directory name)
  * /usr/local/bin/df_image_sample /home/<your username>/beepy-directfb2/data/raven.png
  * Public domain image from "The swallow and the raven," Elmer Boyd Smith, c. 1910, https://lccn.loc.gov/2010718076

Video player (must specify a video file)
  * /usr/local/bin/df_video_sample
