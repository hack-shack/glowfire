#!/usr/bin/python
# Robot for bluetoothctl, for common Bluetooth tasks (reconnect, pair, etc.)
# Interacts with bluetoothctl using subprocess(); uses regex to parse its output.
# (c) 2023 Asa Durkee. MIT License.

# Note! bluealsa must be running for this to connect to the headphones.

import re
import subprocess

# Utility functions
# -----------------
def scan(seconds = 20, cleaner_scan=True):
    # cleaner_scan meaning:
    # hide entries where the device name is also its MAC, or if it is a CHG event. Useful for pairing.
    print('DEBUG: Scanning for Bluetooth devices for ' + str(seconds) + ' seconds.')
    result = subprocess.run(['bluetoothctl','--timeout',str(seconds),'scan','on'],capture_output=True)
    devices = str(result.stdout)
    regex_split = re.compile(r'\\n')
    filtered = re.split(regex_split, devices)
    print('DEBUG: Number of Bluetooth events found : ' + str(len(filtered))) # not strictly accurate, what with the leading 'b'
    re_state_type_mac_name = re.compile(r'(?:.+\[0;9[0-9].+?)((?:[A-Z]{3})).+? ([a-zA-Z]+?) ((?:[a-fA-F0-9]:?){12}) (.+)')

    all_items = []

    for line in filtered:
        state_type_mac_name = re.search(re_state_type_mac_name,line)
        if state_type_mac_name:
            state = state_type_mac_name.group(1)
            devtype  = state_type_mac_name.group(2)
            mac   = state_type_mac_name.group(3)
            devname  = state_type_mac_name.group(4)
            all_items.append({'state':state,'devtype':devtype,'macid':mac,'devname':devname})

    if cleaner_scan == True:
        no_macnames = []
        for item in all_items:
            if item['devtype'] == 'Controller':
                continue
            elif item['state'] == 'DEL':  # or 'CHG':
                continue
            elif item['devname'].startswith('ManufacturerData'):
                continue
            elif item['devname'].startswith('RSSI:'):
                continue
            elif item['devname'].startswith('TxPower:'):
                continue
            matchable = re.sub('-', ':', item['devname'])
            if matchable == item['macid']:
                continue
            if matchable != item['macid']:
                no_macnames.append(item)
        print(no_macnames)
        return(no_macnames)
    return(all_items)
    
def pair(macid = 0):
    print('DEBUG: Attempting to pair with ' + macid)
    if macid == 0:
        exit('ERROR: Must provide a MAC address to the pair function.')
    if macid != 0:
        # TODO: Sanitize input. Must be 12 bytes, hex, etc. Check if on trusted list before reconnecting.
        #scan_result = subprocess.run(['bluetoothctl','scan','off'], capture_output = True)
        #print(scan_result)
        pair_timeout = 5
        try:
            result = subprocess.run(['bluetoothctl','--timeout',str(pair_timeout),'pair',str(macid)], capture_output = True, timeout=pair_timeout)
        except:
            print('DEBUG: Timeout expired.')
            exit
        print(result)
        result = subprocess.run(['bluetoothctl','--timeout','1','trust',macid], capture_output = True)
        print(result)
        result = subprocess.run(['bluetoothctl','--timeout','1','connect',macid], capture_output = True)
        print(result)

def reconnect(macid):
    if macid == 0:
        exit('ERROR: Must provide a MAC ID to the reconnect function.')
    bt_device = get_conn_state(macid)
    if macid != 0:
        # TODO: Sanitize input. Must be 12 bytes, hex, etc. Check if on trusted list before reconnecting.
        if(bt_device['connected'] == False):
            print('DEBUG: ' + bt_device['macid'] + ' not connected.')
            print('DEBUG: Reconnecting.')
            result = subprocess.run(['bluetoothctl','--timeout','1','connect',macid])
            print(result.stdout)
        if(bt_device['connected'] == True):
            print('DEBUG: ' + bt_device['macid'] + ' - ' + bt_device['name'] + ' is already connected.')
    if(bt_device['connected'] == False):
        print('DEBUG: ' + bt_device['macid'] + ' not connected.')
        print('DEBUG: Reconnecting.')
        result

def bt_devices():
    result = subprocess.run(['bluetoothctl','--timeout','1','devices'],capture_output=True,encoding='UTF-8')
    device = result.stdout.split()
    if len(device) == 0:
        print('No device found. Pair, trust, and connect, manually, first.')
        exit('ERROR: No device found.')
    elif len(device) == 17:
        return device[1] # MAC address field as string, colons and all
    else:
        exit('ERROR: bt_devices(): MAC address must be in the format XX:XX:XX:XX:XX:XX')
    print(device)
    

def get_conn_state(macid):
    def str_to_bool_yesno(str):
            if str == 'yes':
                return True
            if str == 'no':
                return False
            else:
                exit("ERROR: str_to_bool_yesno input must be either str 'yes' or str 'no'.")
                
    if macid == 0:
        print('DEBUG: No MAC address provided to get_conn_state().')
        macid = bt_devices()
    result = subprocess.run(['bluetoothctl','--timeout','1','info',macid],capture_output=True,encoding='UTF-8')
    filtered = result.stdout.splitlines()
    regex_macid     = "^Device ([A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2})"
    regex_name      = "Name: (.+)$"
    regex_alias     = "Alias: (.+)$"
    regex_paired    = "Paired: (.+)$"
    regex_trusted   = "Trusted: (.+)$"
    regex_connected = "Connected: (.+)$"
    
    for line in filtered:
        mac_address = re.search(regex_macid, line)
        if mac_address:
            macid = mac_address.group(1)

        bt_dev_name = re.search(regex_name, line)
        if bt_dev_name:
            name = bt_dev_name.group(1)

        bt_dev_alias = re.search(regex_alias, line)
        if bt_dev_alias:
            alias = bt_dev_alias.group(1)

        bt_state_paired = re.search(regex_paired, line)
        if bt_state_paired:
            paired = str_to_bool_yesno(bt_state_paired.group(1))

        bt_state_trusted = re.search(regex_trusted, line)
        if bt_state_trusted:
            trusted = str_to_bool_yesno(bt_state_trusted.group(1))

        bt_state_connected = re.search(regex_connected, line)
        if bt_state_connected:
            connected = str_to_bool_yesno(bt_state_connected.group(1))
    results = [{'macid':macid,'name':name,'alias':alias,'paired':paired,'trusted':trusted,'connected':connected}]
    return(results[0])

def choose_macid(bt_scan_results):
    macid = ''
    while macid == '':
        if bt_scan_results == 0:
            print('INFO: No Bluetooth items detected in the last scan.')
        print('INFO : Bluetooth scan results')
        print('-'*40)
        for index, item in enumerate(bt_scan_results):
            print('Device Number: ' + str(index) + ' - MAC: ' + item['macid'] + ' - Name: ' + item['devname'])
        print('-'*40)
        device_number = input('Enter the Device Number to pair, r to rescan, q to quit: ')
        if device_number == 'r':
            bt_scan_results = scan()
            continue
        if device_number == 'q':
            break
        try:
            device_number = int(device_number)
            if (0 <= device_number <= 99):
                if device_number < (len(bt_scan_results)):
                    print("Selected device number: " + str(device_number))
                    macid = bt_scan_results[device_number] #[device_number['macid']]
                    print(macid['macid'])
                    return(macid['macid'])
        except:
            print('DEBUG: problem casting device_number to int.')
    return(item['macid'])


# Tests
# -----------------
# ensure alsa config is OK
def verify_alsa_config():
    pass


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
    found_devices = scan()
    macid_to_use = choose_macid(found_devices)
    
    # Step 3: pair, trust, and connect
    pair(macid_to_use)

    # Step 4: reconnect

# Script start
# -----------------
main()