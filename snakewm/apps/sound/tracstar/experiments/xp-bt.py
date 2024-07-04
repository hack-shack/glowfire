#!/usr/bin/python
"""
Reference: https://github.com/pybluez/pybluez
"""

# TODO: dependency: 'sudo apt install -y python3-bluez'

import bluetooth
from bluetooth.ble import DiscoveryService

def ble_discover():
    svc = DiscoveryService()
    devices = svc.discover(2)
    if len(devices.items()) < 1:
        print("No BLE devices found.")
    if len(devices.items()) > 0:
        print("Found {} BLE devices.".format(len(devices.items())))
    for address,name in devices.items():
        print("name : {}, address: {}".format(name,address))

def main():
    ble_discover()

if __name__=="__main__":
    main()