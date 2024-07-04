"""
Install bluez-alsa: Bluetooth Audio ALSA Backend
MIT License.

bluez-alsa connects the ALSA sound system to Bluetooth devices.
It enables you to create one or more virtal audio devices,
typically specified in /etc/asound.conf, for ALSA to source from / 
sink into ("play" or "send" audio, respectively).
On the other side, bluez-alsa takes these audio streams, then
re-encodes them using a predefined codec, and streams to (or from)
the Bluetooth device using the bluez library.

No apt or pip packages for bluez-alsa, so we will build from source.
References:
https://github.com/arkq/bluez-alsa/wiki/Installation-from-source
https://introt.github.io/docs/raspberrypi/bluealsa.html
https://github.com/arkq/bluez-alsa/wiki/Using-BlueALSA-as-default-ALSA-PCM
https://manpages.debian.org/unstable/bluez-alsa-utils/bluealsa.8.en.html
https://forum.armbian.com/topic/6480-bluealsa-bluetooth-audio-using-alsa-not-pulseaudio/
https://wiki.archlinux.org/title/Advanced_Linux_Sound_Architecture/Configuration_examples
https://askubuntu.com/questions/891623/how-to-list-access-all-the-available-audio-input-and-output-ports-channels-of-a
https://github.com/Arkq/bluez-alsa/issues/32
https://stackoverflow.com/questions/17811620/choppy-sound-on-alsa-after-30-min?rq=4

"""
# COMPLETED
Build prerequisite: fdk-aac
#git clone fdk-aac
$ sudo make install
Libraries install to /usr/local/lib

# COMPLETED
Build prerequisite: lc3plus
git clone https://github.com/arkq/LC3plus
$ cd LC3plus/src/floating_point
Build the shared library:
$ make libLC3plus.so
# ('make help' to get compile options)
Manually install the binary, headers, and shared library:
$ sudo mkdir /usr/local/include/LC3plus
$ sudo cp LC3plus /usr/local/bin/
$ sudo cp *.h /usr/local/include/LC3plus/
$ sudo cp libLC3plus.so /usr/local/lib/


### Install required dependencies
### -----------------------------
$ sudo apt install -y bluez-source bluez-tools libbluetooth-dev libdbus-1-dev libreadline-dev
$ sudo apt install -y libglib2.0-dev python3-docutils libbsd0 libbsd-dev libsbc-dev libsbc1

### Install optional dependencies
### -----------------------------
$ sudo apt install -y bluez pipewire
Install dependencies for LDAC configure option: --enable-ldac
$ sudo apt install -y libldacbt-abr-dev libldacbt-enc-dev
Install dependencies for aptX "openaptx" (--with-libopenaptx):
$ sudo apt install -y libopenaptx-dev libopenaptx0
Install MP3 support dependencies (--enable-mp3lame):
$ sudo apt install -y libmp3lame-dev libmp3lame0
Install MPEG decoding support dependencies (--enable-mpg123)
$ sudo apt install -y libmpg123-0 libmpg123-dev mpg123
Install aptX support (for --enable-aptx and/or --enable-aptx-hd)
# NOTE: This may need to be manually installed.
Install spandsp (--enable-msbc):
$ sudo apt install -y libspandsp-dev libspandsp2



### Download and configure ALSA
### ---------------------------
$ git clone https://github.com/Arkq/bluez-alsa
$ cd bluez-alsa
$ autoreconf --install
Run autoreconf to generate a .configure file. This will take a minute or two.
$ autoreconf --install
Print configure flags:
$ ./configure --help
Continue the build.
$ mkdir build && cd build
$ ../configure    <-- you will actually do the below:
Configure with these options (change the alsaplugindir to 32-bit version if on 32-bit OS)
AAC not working currently, so omitting.
CFLAGS="-I/usr/local/include/LC3plus" LDFLAGS="-L/usr/local/lib/" ../configure --enable-manpages  --enable-ldac \
--enable-mp3lame --enable-mpg123 \
--with-libopenaptx --enable-aptx --enable-aptx-hd \
--enable-msbc --enable-rfcomm --enable-hcitop \
--with-alsaplugindir=/usr/lib/aarch64-linux-gnu/alsa-lib/

old settings
$ CFLAGS="-I/usr/local/include/LC3plus" LDFLAGS="-L/usr/local/lib/" ../configure --enable-manpages --enable-aac --enable-lc3plus --enable-ldac \
--enable-mp3lame --enable-mpg123 \
--with-libopenaptx --enable-aptx --enable-aptx-hd \
--enable-msbc --enable-rfcomm --enable-hcitop \
--with-alsaplugindir=/usr/lib/aarch64-linux-gnu/alsa-lib/
Build:
$ make
Install:
$ sudo make install
$ ./libtool --finish /usr/lib/aarch64-linux-gnu/alsa-lib/


Configure /etc/asound.conf



### Test 1/3: Verify the bluealsa daemon is running
### -----------------------------------------------
$ sudo bluealsa --profile=a2dp-source --device=hci0 --codec=SBC --sbc-quality=low

The above settings avoid MOST stuttering.
Stutters a lot with sbc-quality=xq+, xq, and high; and a little with sbc-quality=medium.
Hardly stutters with --codec=SBC and --sbc-quality=low.

(Higher quality version:)
 sudo bluealsa --profile=a2dp-source --codec=aptX

Leave this running.
Create a new terminal. Name it 'bluetoothctl'.

### Test 2/3: Verify you can connect to the Bluetooth headset or speaker
### --------------------------------------------------------------------
$ sudo bluetoothctl
[bluetooth]# scan on
Find the MAC for your device and copy it. Then pair with it as follows.
Substitute your MAC for the one used below.
[bluetooth]# pair 1a:2b:3c:4d:5e:6f
[bluetooth]# scan off
[bluetooth]# trust 1a:2b:3c:4d:5e:6f
[bluetooth]# connect 1a:2b:3c:4d:5e:6f
At this point, the Bluetooth speaker may emit its 'connected!' noise, if it has one.
[BT SPEAKER]# set alias "Bluetooth Speaker"
[BT SPEAKER]# devices
[BT SPEAKER]# info 1a:2b:3c:4d:5e:6f
Look for "Connected: yes". If not:
[BT SPEAKER]# connect 1a:2b:3c:4d:5e:6f

Leave this running.
Create a new terminal.


### Test 3/3: Verify you can create arbitrary audio sinks in bluealsa
### -----------------------------------------------------------------
Show dbus devices:
# busctl
org.bluealsa should be in there.

List all soundcards and digital audio devices:
$ aplay -l

List all defined PCMs:
$ aplay -L

List all sound modules:
$ cat /proc/asound/modules

You'll have noticed by now that BlueALSA doesn't show up as a card, only a PCM.

We have to reference it directly.
$ aplay -D bluealsa music/test.mp3
Don't wear the Bluetooth headphones. It will be loud static. You'll see it's trying to play raw.
Export a WAV file from Audacity and try it again.

Play back a WAV:
$ aplay -D bluealsa music/test.wav
It should sound normal (though possibly choppy).
Try it with more options:
$ aplay -D bluealsa -c 2 --buffer-time=500000 --buffer-size=500000 --mmap --interactive -v --dump-hw-params music/test.wav


List bluetooth devices for playback:
$ bluealsa-aplay -L


Specify SDL2 audio driver:
https://wiki.libsdl.org/SDL2/FAQUsingSDL

https://www.libsdl.org/release/SDL-1.2.15/docs/html/sdlenvvars.html

SDL_AUDIODRIVER='alsa';export SDL_AUDIODRIVER
AUDIODEV (the audio device to use, if SDL_PATH_DSP isn't set)




# Bluetooth support in Python
https://github.com/elsampsa/btdemo



# Install Bluetooth support in Python
# -----------------------------------
This lacks the ability to pair, reconnect, etc. We need almost like a bluetoothctl wrapper.
Install bluedot and its dependencies:
pip install bluedot dbus-python

## Test rfcomm
python
>>> import bluedot.btcomm
>>> a = bluedot.btcomm.BluetoothAdapter()
>>> print(a.paired_devices)
You should receive a list of paired devices.




# Bluetooth support in Python, other notes
# ---------------------------
https://stackoverflow.com/questions/58819546/using-bluetooth-with-python-and-dbus
* pybluez doesn't work (hand-installed) and package won't install, doesn't use dbus, etc.
* consider rfcomm:
https://www.stuffaboutcode.com/2017/07/python-bluetooth-rfcomm-client-server.html
* bluedot rfcomm: https://github.com/martinohanlon/BlueDot/blob/master/docs/btcommapi.rst









# Experiment: Build SDL_sound for testing
# ---------------------------------------
Handles playback of many formats - including MOD, etc.
https://icculus.org/SDL_sound/
Git: https://github.com/icculus/SDL_sound
$ git clone https://github.com/icculus/SDL_sound
$ cd SDL_sound
$ mkdir build
$ cd build
$ cmake ..
$ make
$ sudo make install
Installs a binary at /usr/local/bin/playsound






List all formats:
sudo apt install -y mpd
mpd --version

TODO:
  * Play using low volume.
  * Pause/Next/Prev button support.


/etc/asound.conf:

### Utility: Verify you can delete a Bluetooth device
### -------------------------------------------------
$ bluetoothctl
[bt-speaker]# devices
<find the MAC of the device you want to delete>
[bt-speaker]# remove C8:7B:23:0C:66:96



Install Python bindings
python3-bluez
pybluez


-------------------------


reconnect bluetooth on a raspi
https://gist.github.com/simlei/226fdfec2063dd3bdae47b2c6ae6aca1


bluetoothctl automation
automates the reconnection process
https://gist.github.com/RamonGilabert/046727b302b4d9fb0055




# Scanning for headphones which have been put into PAIR mode

bluetoothctl 

[bluetooth]# scan on
< all sorts o' BT devices will appear >
Devices will continue to stream in.
Event types on the left are CHG, DEL, NEW
To stop devices streaming in:
[bluetoothctl]# scan off
turn scan back on
put bt headset into pairing mode
watch for its name
copy its MAC address
pair <paste MAC address here>
Should pair almost immediately, and you'll get attributes back.
Your prompt will now be the paired device name.
scan off
[Canned Air]# info
<Its MAC address>, Name, Class, Icon, Paired:<bool>,
Trusted:<bool=no>,Blocked:<bool=no>,Connected:<bool=yes>,
LegacyPairing:<bool=no>

Lost connection?
# connect <its MAC address>
# devices <- list paired devices

----------------------
[NEW] Primary Service (Handle 0xb0e4)
	/org/bluez/hci0/dev_C8_7B_23_0C_66_96/service0005
	0000febe-0000-1000-8000-00805f9b34fb
	Bose Corporation

bluetoothctl
trust C8:7B:23:0C:66:96
connect C8:7B:23:0C:66:96
devices
quit
$ MAC=C8:7B:23:0C:66:96




sudo vi /etc/asound.conf
You'll see the pcm.!default device, hw, card 1, etc. Below that:
defaults.bluealsa {
    interface "hci0"
    device "C8:7B:23:0C:66:96"
    profile "a2dp"
}

$ hcitool name C8:7B:23:0C:66:96


Look at bluealsa:
$ bluealsa --help