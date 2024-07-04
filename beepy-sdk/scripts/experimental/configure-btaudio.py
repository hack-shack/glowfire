#!/usr/bin/python

# Requires: sudo apt install -y python3-bluez

import bluetooth

macid = ''

def scan():
    while macid == '':
        found_devices = bluetooth.discover_devices(lookup_names=True)
        if found_devices == []:
            print('No found devices.')
            continue
        if found_devices != []:
            print('Found devices. Enter a device number to add it: ')
            for index, info in enumerate(found_devices):
                print('Device Number: ' + str(index) + ' - Info: ' + str(info))
            choice = input('Enter the device number to pair: ')
            try:
                choice = int(choice)
                print(choice)
                device = found_devices[index]
                print(device[0]) # MAC address
            except:
                exit('ERROR: Device number did not cast to int.')

# end state : bluetooth headphones should be connected

# Main
# -----------------
def main():
    # Step 1: is there a paired headphone already? skip to reconnect if yes.
    """
    macid = bt_devices()
    print(macid)
    if macid == 0:
        print('No device connected.')
    """

    # Step 2: if no paired headphones, scan for bluetooth devices, ask which one to use.
    scan()
    
    # Step 3: pair, trust, and connect
    

    # Step 4: reconnect

main()