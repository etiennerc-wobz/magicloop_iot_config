#!/bin/bash

# Vérifie si une connexion est établie
if ! iwgetid -r wlan0; then
    # Si aucune connexion, démarre le point d'accès
    /usr/local/bin/start_ap.sh
else
    # Sinon, arrêtez le point d'accès si nécessaire
    sudo systemctl stop dnsmasq
    sudo systemctl stop hostapd
fi