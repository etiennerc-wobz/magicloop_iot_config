import os
import yaml
import threading
import paho.mqtt.client as mqtt
import json
import queue

class MagicCarpet:

    class GeneralState:
        def __init__(self,id = '',name = '',wifi = '',tpe_linked = ''):
            self.id = id
            self.name = name
            self.wifi = wifi
            self.tpe_linked = tpe_linked
        
        def update_general_state(self,id = '',name = '',wifi = '',tpe_linked = ''):
            self.id = id
            self.name = name
            self.wifi = wifi
            self.tpe_linked = tpe_linked
        
        def return_general_state(self):
            return {
                'id': self.id,
                'name': self.name,
                'wifi': self.wifi,
                'tpe_linked': self.tpe_linked
            }
        
        def update_tpe_linked(self,tpe):
            self.tpe_linked = tpe

        def return_tpe_linked(self):
            return {'id' : self.tpe_linked }


    def __init__(self,rpi_name,username,password):
        module_dir = os.path.dirname(__file__)
        with open(os.path.join(module_dir,'../config/server_config.yaml')) as yaml_file:
            try :
                config = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                print(exc)
        self.broker_address = config['broker_address']
        self.port = config['port']
        self.username = username
        self.password = password
        self.rpi_name = rpi_name

        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)

        self.connected = threading.Event()
        # Assignation des callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.general_state = self.GeneralState()

    def connect(self):
        """Connexion au courtier MQTT."""
        print(f"Connexion à {self.broker_host}:{self.broker_port}")
        self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """Callback pour la connexion au broker."""
        if rc == 0:
            print(f"Connecté au broker avec le code de retour {rc}")
            self.client.subscribe(self.sub_topic)
            self.connected.set()
        else : 
            print(f"Échec de la connexion, code de retour: {rc}")

    def on_message(self, client, userdata, message):
        """Callback pour les messages reçus."""
        try:
            payload = json.loads(message.payload.decode('utf-8'))
            topic = message.topic
            data = {
                'topic' : topic,
                'payload' : payload
            }
            print(f"Message reçu sur {topic}: {payload}")
            if topic.endswith('/state'):
                self.decode_state(payload)
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")

    def publish_data(self,topic, payload):
        """Publie des données sur un sujet MQTT"""
        try:
            if not self.connected.is_set():
                print("Non connecté au broker MQTT. Tentative de publication échouée.")
                return

            self.client.publish(topic, json.dumps(payload))
            print(f"Données publiées sur {topic}: {payload}")
        except Exception as e:
            print(f"Erreur lors de la publication des données: {e}")

    def decode_state(self,payload):
        state = payload.get('state_type')
        data = payload.get('data')
        if state == 'general' :
            self.update_general_state(data)
        if state == 'tpe_linked':
            self.update_tpe_linked(data)
        if state == 'current_item_list_read':
            self.update_current_item_read(data)
        elif state == 'current_mode':
            self.update_current_mode(data)
        elif state == 'new_association':
            self.update_current_item_read(data)
        elif state == 'new_desassociation':
            self.update_current_item_read(data)

    def update_general_state(self,data):
        self.general_state.update_general_state(data['id'], data['name'],data['wifi'],data['tpe_linked'])

    def update_tpe_linked(self,data):
        self.general_state.update_tpe_linked(data['tpe_linked'])

    def update_current_item_read(self,data):

