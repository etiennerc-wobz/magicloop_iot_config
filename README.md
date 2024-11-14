# magicloop-wifi-config

1/ linux package install 
sudo apt-get update
sudo apt-get upgrade
sudo apt install -y network-manager
sudo systemctl disable dhcpcd
sudo systemctl disable wpa_supplicant
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

2/ config files
Dans /etc/NetworkManager/NetworkManager.conf

[main]
plugins=ifupdown,keyfile
dns=dnsmasq

3/ Configurer le points l'accès 

sudo nmcli connection add type wifi ifname wlan0 con-name Hotspot autoconnect no ssid RPi_Hotspot
sudo nmcli connection modify Hotspot 802-11-wireless.mode ap ipv4.addresses 192.168.1.1/24 ipv4.method shared

4/ Paramétrer l’interface Ethernet

sudo nmcli connection modify 'Wired connection 1' ipv4.method auto

5/ Configurer NetworkManager pour le Point d’Accès Wi-Fi 

sudo nano /etc/NetworkManager/system-connections/Hotspot.nmconnection

[connection]
id=Hotspot
uuid=ee402fa0-784a-480d-8942-22bd5acc3e03
type=wifi
autoconnect=false
interface-name=wlan0

[wifi]
band=bg
channel=6
mode=ap
ssid=RPi_Hotspot

[wifi-security]
key-mgmt=wpa-psk
psk=salutetienne

[ipv4]
address1=192.168.0.1/24
method=shared

[ipv6]
addr-gen-mode=default
method=auto

[proxy]

sudo systemctl restart NetworkManager

place check_wifi_enable_ap.sh to /usr/local/bin/
place wifi_check.service to /etc/systemd/system/
place wifi_check.timer to /etc/systemd/system/


5/ Configurer Avahi

sudo apt update
sudo apt install avahi-daemon

sudo systemctl start avahi-daemon
sudo systemctl enable avahi-daemon

sudo nano /etc/hostname
    raspberry-pi-magicloop-config

sudo nano /etc/hosts
    127.0.1.1   raspberry-pi-magicloop-config

sudo reboot

ping raspberry-pi-magicloop-config.local