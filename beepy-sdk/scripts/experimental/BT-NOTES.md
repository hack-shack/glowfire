# To use Bluetooth headphones

Configure ALSA with the bluealsa sound bridge:
$ sudo ./scripts/configure-alsa.py

Start bluealsa with failsafe settings:
$ sudo bluealsa --profile=a2dp-source --device=hci0 --codec=SBC --sbc-quality=low
Leave it running in a terminal window.

Pair the headphones:
bluetoothctl
> scan on
# wait for the headphones to appear, then copy their MAC address
> scan off
> pair (mac address)
> trust (mac address)
> connect (mac address)
If bluealsa is running correctly, the headphones should successfully connect.
The headphones need bluealsa to be running in order to finish the 'connect' command.

# List all bluealsa PCM devices
sudo bluealsa-aplay -l

# Ensure the MAC address for your device is in /etc/asound.conf
open /etc/asound.conf
There should be an entry for pcm.bt-headphones.
The device MAC may be xx:xx:xx:xx:xx:xx.
Replace it with the MAC address of your device and save.






# Launch bluealsa with this hands-free profile
# (only mono/8khz but you get mic if it has one)
sudo bluealsa --profile=hfp-ag --device=hci0 --codec=mSBC --sbc-quality=low --profile=a2dp-source --profile=a2dp-sink

# Test recording from mic
arecord -D bluealsa [flags] [filename]

# References
https://www.alsa-project.org/wiki/Asoundrc

Gist with info on D-Bus control:
https://ukbaz.github.io/howto/python_gio_1.html

# Examples
```bash

$ busctl tree org.bluez

$ busctl introspect org.bluez /org/bluez

$ busctl introspect org.bluez /org/bluez/hci0
```

