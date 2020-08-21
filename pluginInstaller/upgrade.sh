#!/usr/bin/env bash

rm SuperCPBackup.zip
cp ~chris/SuperCPBackup.zip .
/usr/local/CyberCP/bin/python pluginInstaller.py upgrade --pluginName SuperCPBackup