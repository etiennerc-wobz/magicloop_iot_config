#!/bin/bash

# Nom de la connexion pour le point d'accès
AP_CONNECTION="Hotspot"
WIFI_INTERFACE="wlan0"

# Récupère la connexion actuelle pour wlan0
active_connection=$(nmcli -t -f DEVICE,CONNECTION dev | grep "$WIFI_INTERFACE" | cut -d: -f2)

# Vérifie si le hotspot est déjà activé
if [[ "$active_connection" == "$AP_CONNECTION" ]]; then
    echo "Le point d'accès est déjà actif."
    exit 0
fi

# Vérifie si un autre réseau Wi-Fi est connecté et opérationnel
if [[ -n "$active_connection" && "$active_connection" != "$AP_CONNECTION" ]]; then
    echo "Connecté à un réseau Wi-Fi ($active_connection)"
    exit 0
fi

# Si aucune connexion n'est active, activer le point d'accès
echo "Aucune connexion Wi-Fi active. Activation du point d'accès."
nmcli connection up "$AP_CONNECTION"