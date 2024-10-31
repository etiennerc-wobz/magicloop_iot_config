from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__)

# Scan des réseaux Wi-Fi
def scan_wifi_networks():
    networks = []
    try:
        output = subprocess.check_output(['sudo', 'iwlist', 'wlan0', 'scan']).decode('utf-8')
        for line in output.split("\n"):
            if "ESSID" in line:
                ssid = line.strip().split(":")[1].replace('"', '')
                networks.append(ssid)
    except subprocess.CalledProcessError:
        print("Erreur de scan des réseaux Wi-Fi.")
    return list(set(networks))

# Route de la page d'accueil
@app.route('/')
def index():
    networks = scan_wifi_networks()  # Liste des réseaux Wi-Fi disponibles
    return render_template('index.html', networks=networks)

# Route pour la connexion au Wi-Fi
@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form['ssid']
    password = request.form['password']
    # Mise à jour du fichier wpa_supplicant pour se connecter
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as wpa_file:
        wpa_file.write(f'\nnetwork={{\n  ssid="{ssid}"\n  psk="{password}"\n}}')
    # Recharger la configuration Wi-Fi
    subprocess.call(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)