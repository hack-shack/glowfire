# ALSA audio on beepy
# -------------------

List devices on system:
```
$ cat /proc/asound/modules
```

It will return something like:
```
 0 snd_usb_audio
 1 vc4
```
Attached SYBA USB dongle appears as device 0.
VC4 is the Pi's VideoCore4 device (HDMI output).

Play sample track to the USB dongle:
```
$ sudo aplay --device=hw:0 Holst_The_Planets_Jupiter.wav 
```
