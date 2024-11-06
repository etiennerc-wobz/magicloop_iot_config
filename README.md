# magicloop-wifi-config

1/ linux package install 
sudo apt update
sudo apt install hostapd dnsmasq

2/ config files
Add hostapd.conf to /etc/hostapd/hostapd.conf
Add dnsmasq.conf to /etc/dnsmasq.conf
Add dhcpcd.conf to /etc/dhcpcd.conf
place check_wifi_connection.sh to /etc/network/interfaces or /etc/rc.local

