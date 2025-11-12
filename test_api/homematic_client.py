#!/usr/bin/env python3
"""
Exemple de client Python pour l'API Homematic IP Connect

Ce script permet de :
- Se connecter au système Homematic IP via WebSocket
- Récupérer la liste des appareils (DISCOVER_REQUEST)
- Interroger et contrôler un appareil (CONTROL_REQUEST)
"""

import asyncio
import inspect
import json
import ssl
import sys
import uuid
from typing import Dict, Any, List
import websockets


class HomematicClient:
    """Client pour l'API Homematic IP Connect"""

    def __init__(self, plugin_id: str, host: str, authtoken: str):
        """
        Initialise le client Homematic

        Args:
            plugin_id: Identifiant unique du plugin (ex: com.example.plugin.python)
            host: Adresse du HCU (ex: hcu1-XXXX.local)
            authtoken: Token d'authentification
        """
        self.plugin_id = plugin_id
        self.host = host
        self.authtoken = authtoken
        self.websocket = None
        self.devices: List[Dict[str, Any]] = []

    async def connect(self):
        """Établit la connexion WebSocket avec le HCU"""
        uri = f"wss://{self.host}:9001"

        # Configuration SSL pour accepter les certificats auto-signés
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Headers d'authentification
        headers = {
            "authtoken": self.authtoken,
            "plugin-id": self.plugin_id
        }

        print(f"Connexion à {uri}...")
        connect_kwargs = {
            "ssl": ssl_context,
        }

        # websockets>=12 renamed extra_headers -> additional_headers;
        # detect the accepted parameter to stay compatible with older versions.
        connect_signature = inspect.signature(websockets.connect)
        header_arg = (
            "additional_headers"
            if "additional_headers" in connect_signature.parameters
            else "extra_headers"
        )
        connect_kwargs[header_arg] = headers

        self.websocket = await websockets.connect(
            uri,
            **connect_kwargs,
        )
        print("Connecté au WebSocket")

        # Envoyer le message PLUGIN_STATE_RESPONSE au démarrage
        await self.send_plugin_ready(str(uuid.uuid4()))

    async def send_message(self, message: Dict[str, Any]):
        """Envoie un message JSON via le WebSocket"""
        message_str = json.dumps(message, indent=2)
        await self.websocket.send(message_str)
        print(f"\n→ Message envoyé:\n{message_str}")

    async def send_plugin_ready(self, message_id: str):
        """Envoie un message PLUGIN_STATE_RESPONSE"""
        message = {
            "id": message_id,
            "pluginId": self.plugin_id,
            "type": "PLUGIN_STATE_RESPONSE",
            "body": {
                "pluginReadinessStatus": "READY"
            }
        }
        await self.send_message(message)

    async def send_discover_response(self, message_id: str):
        """
        Envoie une réponse DISCOVER avec la liste des appareils

        Pour cet exemple, on déclare des appareils fictifs.
        Dans une vraie application, vous découvririez vos appareils réels.
        """
        message = {
            "id": message_id,
            "pluginId": self.plugin_id,
            "type": "DISCOVER_RESPONSE",
            "body": {
                "success": True,
                "devices": [
                    {
                        "deviceType": "LIGHT",
                        "deviceId": "light-salon-1",
                        "firmwareVersion": "1.0.0",
                        "friendlyName": "Lumière Salon",
                        "modelType": "LED-Controller",
                        "features": [
                            {
                                "type": "switchState",
                                "on": False
                            }
                        ]
                    },
                    {
                        "deviceType": "TEMPERATURE_SENSOR",
                        "deviceId": "temp-chambre-1",
                        "firmwareVersion": "1.0.0",
                        "friendlyName": "Capteur Température Chambre",
                        "modelType": "DHT22",
                        "features": [
                            {
                                "type": "temperature",
                                "value": 21.5,
                                "unit": "CELSIUS"
                            }
                        ]
                    },
                    {
                        "deviceType": "THERMOSTAT",
                        "deviceId": "thermostat-bureau-1",
                        "firmwareVersion": "2.0.0",
                        "friendlyName": "Thermostat Bureau",
                        "modelType": "Smart-Thermo",
                        "features": [
                            {
                                "type": "targetTemperature",
                                "value": 20.0,
                                "unit": "CELSIUS"
                            },
                            {
                                "type": "currentTemperature",
                                "value": 19.5,
                                "unit": "CELSIUS"
                            }
                        ]
                    }
                ]
            }
        }

        # Sauvegarder les appareils localement
        self.devices = message["body"]["devices"]
        await self.send_message(message)

    async def send_control_response(self, message_id: str, device_id: str, success: bool = True):
        """Envoie une réponse CONTROL_RESPONSE"""
        message = {
            "id": message_id,
            "pluginId": self.plugin_id,
            "type": "CONTROL_RESPONSE",
            "body": {
                "deviceId": device_id,
                "success": success
            }
        }
        await self.send_message(message)

    async def handle_control_request(self, message: Dict[str, Any]):
        """
        Gère une requête CONTROL_REQUEST pour contrôler un appareil

        Dans cet exemple, on affiche simplement les commandes reçues.
        Dans une vraie application, vous enverriez ces commandes à vos appareils réels.
        """
        device_id = message["body"].get("deviceId")
        features = message["body"].get("features", [])

        print(f"\n🎛️  Commande de contrôle reçue pour l'appareil: {device_id}")
        for feature in features:
            feature_type = feature.get("type")
            if feature_type == "switchState":
                on_state = feature.get("on")
                print(f"   → Changer l'état: {'ON' if on_state else 'OFF'}")
            elif feature_type == "targetTemperature":
                temp = feature.get("value")
                print(f"   → Température cible: {temp}°C")
            else:
                print(f"   → Feature: {feature}")

        # Simuler le contrôle de l'appareil (ici on répond toujours succès)
        await self.send_control_response(message["id"], device_id, success=True)

    async def handle_message(self, data: str):
        """Gère les messages reçus du HCU"""
        message = json.loads(data)
        print(f"\n← Message reçu:\n{json.dumps(message, indent=2)}")

        message_type = message.get("type")
        message_id = message.get("id")

        if message_type == "PLUGIN_STATE_REQUEST":
            await self.send_plugin_ready(message_id)

        elif message_type == "DISCOVER_REQUEST":
            print("\n🔍 Requête de découverte des appareils...")
            await self.send_discover_response(message_id)

        elif message_type == "CONTROL_REQUEST":
            await self.handle_control_request(message)

    async def listen(self):
        """Écoute les messages du HCU en continu"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("\nConnexion fermée")
        except Exception as e:
            print(f"\nErreur: {e}")

    async def run(self):
        """Lance le client (connexion et écoute)"""
        await self.connect()
        await self.listen()

    def get_devices(self) -> List[Dict[str, Any]]:
        """Retourne la liste des appareils découverts"""
        return self.devices

    def get_device_by_id(self, device_id: str) -> Dict[str, Any]:
        """Retourne un appareil spécifique par son ID"""
        for device in self.devices:
            if device["deviceId"] == device_id:
                return device
        return None


async def main():
    """Fonction principale"""
    if len(sys.argv) < 4:
        print("Usage: python homematic_client.py <plugin-id> <hcu-address> <authtoken-file>")
        print("\nExemple:")
        print("  python homematic_client.py com.example.plugin.python hcu1-XXXX.local authtoken.txt")
        sys.exit(1)

    plugin_id = sys.argv[1]
    host = sys.argv[2]
    authtoken_file = sys.argv[3]

    # Lire le token d'authentification
    try:
        with open(authtoken_file, 'r') as f:
            authtoken = f.read().strip()
    except FileNotFoundError:
        print(f"Erreur: Fichier {authtoken_file} non trouvé")
        sys.exit(1)

    # Créer et lancer le client
    client = HomematicClient(plugin_id, host, authtoken)

    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n\nArrêt du client...")
    except Exception as e:
        print(f"\nErreur: {e}")


if __name__ == "__main__":
    asyncio.run(main())
