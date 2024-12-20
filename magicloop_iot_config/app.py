from flask import Flask, render_template, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/wifi-config')
def wifi_config():
    return render_template('wifi_config.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/current_ips', methods=['GET'])
def current_ips():
    """Retourne les adresses IP actuelles."""
    return jsonify({
        "ethernet_ip": get_ip_address("eth0"),
        "wifi_ip": get_ip_address("wlan0"),
        "wifi_ssid": get_wifi_ssid()
    })

@app.route('/scan_networks', methods=['GET'])
def scan_networks():
    print("scan_networks")
    """Retourne les réseaux Wi-Fi disponibles sans doublons."""
    return jsonify(scan_wifi())

@app.route('/connect_wifi', methods=['POST'])
def connect_wifi():
    data = request.get_json()
    ssid = data['ssid']
    password = data.get('password', '')
    previous_ssid = get_wifi_ssid()
    # Créer une nouvelle connexion
    try : 
        connect_command = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
        subprocess.check_call(connect_command)
        return jsonify({"success": True, "message": f"Connecté à {ssid}"})
    except subprocess.CalledProcessError:
        if previous_ssid:
            try:
                reconnect_command = ["nmcli", "dev", "wifi", "connect", previous_ssid]
                subprocess.check_call(reconnect_command)
                return jsonify({
                    "success": False,
                    "message": f"Échec de connexion à {ssid}. Reconnecté à {previous_ssid}."
                })
            except subprocess.CalledProcessError:
                # Impossible de reconnecter au réseau précédent
                ap_command = ["nmcli", "connection", "up", "Hotspot"]
                subprocess.check_call(ap_command)
                return jsonify({
                    "success": False,
                    "message": "Échec de connexion et impossible de revenir au réseau précédent. Activation du Hotspot"
                }), 500
        else:
            # Aucune connexion précédente trouvée
            subprocess.check_call(ap_command)
            return jsonify({
                "success": False,
                "message": "Échec de connexion et aucun réseau précédent. Activation du Hotspot"
            }), 500


@app.route('/forget_network', methods=['POST'])
def forget_network():
    data = request.get_json()
    if data is None:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400
    ssid = data.get('ssid')
    if not ssid:
        return jsonify({"success": False, "message": "SSID non spécifié"}), 400

    try:
        # Commande pour oublier le réseau
        subprocess.check_call(["nmcli", "con", "delete", ssid])
        return jsonify({"success": True, "message": f"Réseau '{ssid}' oublié avec succès"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": "Erreur lors de la suppression du réseau"}), 500

@app.route('/toggle_hotspot', methods=['POST'])
def toggle_hotspot():
    data = request.get_json()  # Utilisez request.get_json() au lieu de request.json directement
    if data is None:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    enable = data.get('enable')  # Maintenant, 'data' est utilisé en toute sécurité
    print(f"toggle_hotspot return {enable}")
    try:
        if enable:
            # Activer le hotspot
            subprocess.run(["nmcli", "connection", "up", "Hotspot"], check=True)
            hotspot_active = True
        else:
            # Désactiver le hotspot
            subprocess.run(["nmcli", "connection", "down", "Hotspot"], check=True)
            hotspot_active = False
        return jsonify({"success": True, "hotspot_active": hotspot_active})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": "Erreur lors de la gestion du hotspot"}), 500

@app.route('/hotspot_status', methods=['GET'])
def hotspot_status():
    # Vérifie si le hotspot est actif
    result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,NAME", "connection", "show"], capture_output=True, text=True)
    is_hotspot_active = "yes:Hotspot" in result.stdout
    return jsonify({"hotspot_active": is_hotspot_active})

@app.route('/service_status', methods=['GET'])
def service_status():
    """Retourne l'état des services magic_bin et magic_carpet."""
    services = ["magic_bin", "magic_carpet"]
    status = {}
    
    for service in services:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
            )
            # Analyse le statut (actif ou inactif)
            status[service] = result.stdout.strip()
        except Exception as e:
            status[service] = f"Erreur: {str(e)}"
    
    return jsonify(status)

def get_ip_address(interface):
    """Récupère l'adresse IP actuelle pour une interface donnée."""
    result = subprocess.run(['nmcli', '-g', 'IP4.ADDRESS', 'device', 'show', interface], capture_output=True, text=True)
    return result.stdout.strip()

def get_wifi_ssid():
    """Récupère le SSID actuel du réseau Wi-Fi."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            active, ssid = line.split(":")
            if active == "oui":
                return ssid
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du SSID: {e}")
        return None

def scan_wifi():
    """Scanne les réseaux Wi-Fi disponibles."""
    print("scan_wifi")
    result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY', 'dev', 'wifi'], capture_output=True, text=True)
    networks = {}
    for line in result.stdout.strip().split("\n"):
        print(f'scan_wifi line {line}')
        if line:
            ssid, security = line.split(":")
            if ssid not in networks:
                networks[ssid] = {"ssid": ssid, "security": security}
    return list(networks.values())

def disconnect_wifi():
    subprocess.run(['nmcli', 'radio', 'wifi', 'off'], check=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
