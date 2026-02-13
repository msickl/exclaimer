#!/usr/bin/env python3

import subprocess

print("Create a symbolic link and configure the systemd service")
subprocess.run('ln -s /opt/exclaimer/etc/exclaimer.service /etc/systemd/system/', shell=True)

subprocess.run('systemctl enable exclaimer.service', shell=True)
subprocess.run('systemctl daemon-reload', shell=True)
subprocess.run('systemctl start exclaimer.service', shell=True)