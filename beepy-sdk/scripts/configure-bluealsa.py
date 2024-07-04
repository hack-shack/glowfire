#!/usr/bin/python
# Robot for bluealsa, to control common things from Python.
# (c) 2023 Asa Durkee. MIT License.

import os
import subprocess

# Failsafe settings (low quality sound)
# sudo bluealsa --profile=a2dp-source --device=hci0 --codec=SBC --sbc-quality=low

# Higher quality version
# sudo bluealsa --profile=a2dp-source --codec=aptX

#bluealsa --profile=a2dp-source --device=hci0 --codec=SBC --sbc-quality=low --initial-volume=1 &

# Reference
# https://www.sigmdel.ca/michel/ha/rpi/bluetooth_in_rpios_01_en.html


bluealsa_service_params = ['--profile=a2dp-source','--device=hci0','--codec=SBC','--sbc-quality=low']
str_params = ' '.join(bluealsa_service_params)
print(str_params)
bluealsa_service_file_contents = ("""; Unit file from bluealsa wiki by borine

[Unit]
Description=Bluealsa daemon
Documentation=https://github.com/Arkq/bluez-alsa/
After=dbus-org.bluez.service
Requires=dbus-org.bluez.service
StopWhenUnneeded=true

[Service]
Type=dbus
BusName=org.bluealsa
EnvironmentFile=-/etc/default/bluealsa
ExecStart=/usr/bin/bluealsa """ + str_params + """
Restart=on-failure
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
RemoveIPC=true
RestrictAddressFamilies=AF_UNIX AF_BLUETOOTH
; Also non-privileged can user be used
;User=bluealsa
;Group=audio
;NoNewPrivileges=true

[Install]
WantedBy=bluetooth.target
""")

file_to_write = os.path.join('/lib/systemd/system/bluealsa.service')

def write_bluealsa_service_file(file):
    if not os.path.exists(file):
        try:
            open(file, 'w').close()
        except PermissionError as error:
            exit('ERROR: ' + str(error))

    try:
        with open(file,'r+') as f:
                f.seek(0)
                f.truncate()
                for line in bluealsa_service_file_contents:
                        f.write(line)
    except PermissionError as error:
        exit('ERROR: ' + str(error))

def main():
    if not os.getuid() == 0: print('-' * 40 + \
    '\n\nINFO :\tNot running as root.\n\tMay fail to write configuration.\n\n' + '-' * 40)
    write_bluealsa_service_file(file_to_write)

    # Running bluealsa manually must be done as root.

    # run this and authenticate 4 times
    # systemctl enable bluetooth.service
    # So now this line will work:
    # systemctl status dbus-org.bluez.service
    # when systemd loads the bluealsa.service file.

    # systemctl daemon-reload
    # auth once

    # start bluealsa service:
    # sudo service bluealsa start


# Start of script
# =================
main()