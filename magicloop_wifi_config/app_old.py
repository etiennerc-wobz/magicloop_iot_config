from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    connected_ssid = get_connected_ssid()
    ip_address = get_ip_address()
    ethernet_ip = get_ethernet_ip()
    networks = scan_wifi_networks()
    return render_template('index.html', connected_ssid=connected_ssid, ip_address=ip_address, ethernet_ip=ethernet_ip, networks=networks)

def get_connected_ssid():
    result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    for line in lines:
        if line.startswith("yes:"):
            return line.split(":")[1]
    return "Not connected"

def get_ip_address():
    result = subprocess.run(['nmcli', '-g', 'IP4.ADDRESS', 'device', 'show', 'wlan0'], capture_output=True, text=True)
    return result.stdout.strip()

def get_ethernet_ip():
    result = subprocess.run(['nmcli', '-g', 'IP4.ADDRESS', 'device', 'show', 'eth0'], capture_output=True, text=True)
    return result.stdout.strip()

def scan_wifi_networks():
    result = subprocess.run(['nmcli', '-f', 'ssid,security', 'device', 'wifi', 'list'], capture_output=True, text=True)
    networks = []
    for line in result.stdout.strip().splitlines():
        ssid, security = line.split()[:2]
        networks.append({'ssid': ssid, 'security': security})
    return networks

@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form.get('ssid')
    password = request.form.get('password', '')
    try:
        if password:
            subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)
        else:
            subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], check=True)
        return jsonify(success=True, message="Connected")
    except subprocess.CalledProcessError:
        return jsonify(success=False, message="Failed to connect")

@app.route('/activate_ap', methods=['POST'])
def activate_ap():
    disconnect_wifi()
    subprocess.run(['nmcli', 'connection', 'up', 'Hotspot'], check=True)
    return jsonify(success=True, message="Access Point activated")

@app.route('/deactivate_ap', methods=['POST'])
def deactivate_ap():
    subprocess.run(['nmcli', 'connection', 'down', 'Hotspot'], check=True)
    auto_connect_wifi()
    return jsonify(success=True, message="Access Point deactivated")

def disconnect_wifi():
    subprocess.run(['nmcli', 'radio', 'wifi', 'off'], check=True)

def auto_connect_wifi():
    subprocess.run(['nmcli', 'radio', 'wifi', 'on'], check=True)

@app.route('/toggle_wifi', methods=['POST'])
def toggle_wifi():
    # Obtenir l'état actuel de l'interface Wi-Fi
    result = subprocess.run(['nmcli', '-t', '-f', 'GENERAL.STATE', 'device', 'show', 'wlan0'], capture_output=True, text=True)
    wifi_state = result.stdout.strip()

    try:
        # Activer ou désactiver selon l'état actuel
        if "100 (connected)" in wifi_state or "30 (disconnected)" in wifi_state:
            subprocess.run(['nmcli', 'radio', 'wifi', 'off'], check=True)
            message = "Wi-Fi désactivé"
        else:
            subprocess.run(['nmcli', 'radio', 'wifi', 'on'], check=True)
            message = "Wi-Fi activé"
        
        return jsonify(success=True, message=message)
    except subprocess.CalledProcessError:
        return jsonify(success=False, message="Erreur lors de la commutation Wi-Fi.")

# Route pour récupérer la liste des réseaux connus
@app.route('/get_known_networks', methods=['GET'])
def get_known_networks():
    result = subprocess.run(['nmcli', '-t', '-f', 'NAME', 'connection', 'show'], capture_output=True, text=True)
    known_networks = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return jsonify(known_networks=known_networks)

# Route pour se déconnecter du réseau Wi-Fi actuel
@app.route('/disconnect_wifi', methods=['POST'])
def disconnect_wifi():
    try:
        subprocess.run(['nmcli', 'device', 'disconnect', 'wlan0'], check=True)
        message = "Déconnecté du réseau Wi-Fi actuel."
        return jsonify(success=True, message=message)
    except subprocess.CalledProcessError:
        return jsonify(success=False, message="Erreur lors de la déconnexion.")

# Route pour oublier un réseau Wi-Fi connu
@app.route('/forget_network', methods=['POST'])
def forget_network():
    ssid = request.json.get('ssid')
    try:
        subprocess.run(['nmcli', 'connection', 'delete', ssid], check=True)
        message = f"Réseau {ssid} oublié."
        return jsonify(success=True, message=message)
    except subprocess.CalledProcessError:
        return jsonify(success=False, message=f"Erreur lors de la suppression du réseau {ssid}.")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)