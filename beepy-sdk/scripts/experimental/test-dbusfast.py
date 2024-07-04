#!/usr/bin/python
# (c) 2022 Bluetooth Devices Authors.
# (c) 2023 Asa Durkee.
# MIT License.

# Requires: sudo pip install dbus_fast

# Scans for devices using D-Bus to communicate with BlueZ.
# References:
# https://www.raspberrypi-bluetooth.com/bluez-5_5-and-dbus.html
#
# A pythonic way to understand dbus namespace:
# https://pydbus.readthedocs.io/en/latest/dbusaddressing.html

from dbus_fast.aio import MessageBus
import asyncio

async def main():
    bus = await MessageBus().connect()
    # the introspection xml would normally be included in your project, but
    # this is convenient for development
    introspection = await bus.introspect('org.bluez', '/org/bluez')

    obj = bus.get_proxy_object('org.bluez', '/org/bluez', introspection)
    #player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    device1 = obj.get_interface('org.bluez.Device1')
    properties = obj.get_interface('org.freedesktop.DBus.Properties')

    # call methods on the interface (this causes the media player to play)
    #await player.call_play()
    await device1.get_proxy_object('Address')

    #volume = await player.get_volume()
    #print(f'current volume: {volume}, setting to 0.5')

    #await player.set_volume(0.5)

    # listen to signals
    def on_properties_changed(interface_name, changed_properties, invalidated_properties):
        for changed, variant in changed_properties.items():
            print(f'property changed: {changed} - {variant.value}')

    properties.on_properties_changed(on_properties_changed)

    await asyncio.Event().wait()

asyncio.run(main())