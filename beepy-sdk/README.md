DESCRIPTION
===========
Installs a developer toolchain on the beepy device described here:
  * [https://beepy.sqfmi.com](https://beepy.sqfmi.com)
  * [https://github.com/beeper/beepberry](https://github.com/beeper/beepberry)
This toolchain installs DirectFB2, SDL2, and pygame.
USB audio out support using ALSA ('aplay -L', etc.)
Bluetooth audio out using bluealsa.
Software rendering only.

QUICK SETUP (skipping important details)
========================================
  * SSH to the Raspi
  * sudo apt install -y git
  * cd ~
  * git clone --depth 1 https://github.com/hack-shack/beepy-directfb2
  * cd beepy-directfb2
  * python build-sdk.py


FULL SETUP (headless over SSH)
========================================
  * Get a spare microSD card.
  * Download Raspberry Pi Imager from https://www.raspberrypi.com/software
  * Open the Raspberry Pi Imager tool.
    * The tool's main window opens to a large Raspberry Pi logo.
    * On the left, click the button: "CHOOSE DEVICE."
    * A list of devices appears. Click the icon for "Raspberry Pi Zero 2 W."
    * Returning to the main window, click the button: "CHOOSE OS." 
    * A list of Operating Systems appears. Click the second icon, a black-and white Raspberry Pi icon listed as "Raspberry Pi OS (other)"
    * A list of other Operating Systems appears. Click "Raspberry Pi OS (Legacy, 64-bit) Lite."
    * NOTE: Avoid the urge to install Raspberry Pi OS Full (not Lite). This build script will fail.
    * Returning to the main window, click "CHOOSE STORAGE" and choose your microSD card.
    * Returning to the main window, click the "NEXT" button in the lower right corner.
    * It will ask if you want to use OS customization. Click EDIT SETTINGS.
      * If asked to pre-fill a password from the system keychain, click No.
        * The GENERAL tab appears. Do the following:
          * Set hostname: recommend something like "beepy"
          * Set username and password: checked.
            * Create a username and password for yourself.
          * Configure wireless LAN
            * SSID: must be a 2.4GHz SSID as the Raspi Zero 1 and 2 do not have 5GHz radios
            * SSID password: enter it here
            * Wireless LAN country: you can type the ISO shortname instead of using the dropdown. US is US BTW
          * Set locale settings: important for your clock
            * Keyboard layout: leave at "us" to correctly map the beepy's built-in Q20 keyboard
          * Click the SERVICES tab.
             * Enable SSH: checked. Use password authentication: selected.
          * Click SAVE at the bottom of the window.
    * You will return back to the "Use OS customisation?" dialog. Now, click YES.
    * A warning dialog appears. Confirm that you want to erase the microSD card by clicking YES.
    * Your system may prompt you for your password. Enter it here.
    * When done, a prompt appears indicating Write Successful. Click Continue but do not remove the microSD.

Enable SSH
  * When the imaging is done, create a file called "ssh" on the root level of the bootfs drive that the Imager has made. This will trigger ssh to start automatically at boot.
    * On a Mac, in Terminal: touch /Volumes/bootfs/ssh
  * NOTE: If you do not create this file, SSH will not start and you will be unable to get into the Pi.

Configure USB Ethernet Gadget ("Ethernet over USB")
  * Open the Raspberry Pi OS config.txt file:
      * vi /Volumes/bootfs/config.txt
  * Add a new line at the bottom of the file:
      * dtoverlay=dwc2
This enables the Raspberry Pi to appear as a USB device. It loads DesignWare USB2 DRD Core support into the device tree.
  * Write and quit.

Enable USB Ethernet Gadget
  * vi /Volumes/bootfs/cmdline.txt
  * After rootwait, insert (on the same line):
    * modules-load=dwc2,g_ether
  * Write and quit.

  * Eject microSD card and install into the Raspberry Pi.
  * Connect a microUSB data cable to the Pi's "center" port, the USB-Data port.

  * Start a continuous ping to the device. Ping its .local address. Continue trying to ping, until it responds via mDNS. The Pi Zero 2 may take 2-4 minutes to boot the first time. The Pi Zero, 6-10 minutes.
  * Monitor for the Ethernet Gadget to come up.
    * On Mac:   > System Settings > Network > watch for "RNDIS/Ethernet Gadget" to become active.
    * It is normal for the Gadget to have a link-local IP (169.254.x.x).

  * SSH to the Raspi
  * sudo apt install -y git
  * cd ~
  * git clone --depth 1 https://github.com/hack-shack/beepy-sdk
  * cd beepy-sdk
  * python build-sdk.py

Don't run install-sharp-driver.py. The build-sdk script will obtain its dependencies, then do this for you.

RUNNING DIRECTFB EXAMPLES
===========================================================
Currently, you must run examples as root.

  * cd ~/beepy-sdk
  * sudo su
  * export DFBARGS="system=fbdev,fbdev=/dev/fb1,graphics-vt"
    ** Here are other options you can add to DFBARGS (comma separated):
    ** Run the app with --dfb:help to find all options and pass DFBARGS directly at runtime.
    ** no-cursor : Hide mouse pointer
    ** dma : Enable DMA (default off)
    ** graphics-vt : Prevent console messages from appearing onscreen.
    ** memcpy=generic64 : Skip memcpy probing, saving startup time.
    ** Reference: https://linux.die.net/man/5/directfbrc
(On 32-bit Raspi OS)
  * LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf/;export LD_LIBRARY_PATH
(On 64-bit Raspi OS)
  * LD_LIBRARY_PATH=/usr/local/lib/aarch64-linux-gnu/;export LD_LIBRARY_PATH

Now you can run examples. Quit them with ctrl-C. Remember, you will need to first set the 2 environmental variables above in your session before running them.

Display an image (replace the USERNAME with your actual Pi home username)
  * /usr/local/bin/df_image_sample -no-logo -dfb:no-cursor,system=fbdev,fbdev=/dev/fb1 data/raven.png
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
