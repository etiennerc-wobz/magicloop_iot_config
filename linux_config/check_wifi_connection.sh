#!/bin/bash
if ! iwconfig wlan0 | grep -q "ESSID:\"\""; then
    sudo systemctl start hostapd
    sudo systemctl start dnsmasq
fi