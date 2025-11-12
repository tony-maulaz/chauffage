#!/usr/bin/env python3
"""
Script de test interactif pour l'API Homematic IP Connect

Ce script permet de tester facilement les fonctionnalités :
- Connexion au système
- Récupération de la liste des appareils
- Interrogation d'un appareil spécifique
"""

import asyncio
import json
import sys
from homematic_client import HomematicClient


async def test_connection_and_discovery():
    """Teste la connexion et la découverte des appareils"""

    if len(sys.argv) < 4:
        print("Usage: python test_client.py <plugin-id> <hcu-address> <authtoken-file>")
        print("\nExemple:")
        print("  python test_client.py com.example.test hcu1-XXXX.local authtoken.txt")
        sys.exit(1)

    plugin_id = sys.argv[1]
    host = sys.argv[2]
    authtoken_file = sys.argv[3]

    # Lire le token
    try:
        with open(authtoken_file, 'r') as f:
            authtoken = f.read().strip()
    except FileNotFoundError:
        print(f"Erreur: Fichier {authtoken_file} non trouvé")
        sys.exit(1)

    print("=" * 70)
    print("TEST CLIENT HOMEMATIC IP CONNECT API")
    print("=" * 70)
    print()

    # Créer le client
    client = HomematicClient(plugin_id, host, authtoken)

    # Tâche pour écouter les messages
    async def listen_task():
        try:
            await client.listen()
        except Exception as e:
            print(f"Erreur d'écoute: {e}")

    # Tâche principale de test
    async def test_task():
        await asyncio.sleep(2)  # Attendre un peu après la connexion

        print("\n" + "=" * 70)
        print("TEST 1: RÉCUPÉRATION DE LA LISTE DES APPAREILS")
        print("=" * 70)
        print("\nEn attente de la réponse DISCOVER du HCU...")
        print("(Le HCU devrait envoyer une requête DISCOVER_REQUEST)")

        # Attendre que les appareils soient découverts
        for i in range(10):
            await asyncio.sleep(1)
            if client.get_devices():
                break

        devices = client.get_devices()

        if devices:
            print(f"\n✓ {len(devices)} appareil(s) découvert(s):\n")
            for i, device in enumerate(devices, 1):
                print(f"{i}. {device['friendlyName']}")
                print(f"   - ID: {device['deviceId']}")
                print(f"   - Type: {device['deviceType']}")
                print(f"   - Modèle: {device['modelType']}")
                print(f"   - Firmware: {device['firmwareVersion']}")
                print(f"   - Features: {len(device['features'])} feature(s)")
                for feature in device['features']:
                    print(f"      • {feature['type']}: {json.dumps(feature, ensure_ascii=False)}")
                print()

            print("\n" + "=" * 70)
            print("TEST 2: INTERROGATION D'UN APPAREIL SPÉCIFIQUE")
            print("=" * 70)

            # Tester l'interrogation du premier appareil
            test_device_id = devices[0]['deviceId']
            device = client.get_device_by_id(test_device_id)

            if device:
                print(f"\n✓ Appareil trouvé: {device['friendlyName']}")
                print(f"\nDétails complets:")
                print(json.dumps(device, indent=2, ensure_ascii=False))
            else:
                print(f"\n✗ Appareil {test_device_id} non trouvé")

            print("\n" + "=" * 70)
            print("TEST 3: INTERROGATION PAR ID")
            print("=" * 70)

            # Tester différentes interrogations
            test_ids = [dev['deviceId'] for dev in devices]

            for device_id in test_ids:
                device = client.get_device_by_id(device_id)
                if device:
                    print(f"\n✓ {device_id}: {device['friendlyName']}")
                    features_summary = ", ".join([f['type'] for f in device['features']])
                    print(f"  Features: {features_summary}")

        else:
            print("\n✗ Aucun appareil découvert")
            print("Le HCU n'a pas envoyé de requête DISCOVER_REQUEST")

        print("\n" + "=" * 70)
        print("TESTS TERMINÉS")
        print("=" * 70)
        print("\nLe client continue d'écouter les messages du HCU...")
        print("Appuyez sur Ctrl+C pour quitter.\n")

    try:
        # Connecter
        await client.connect()

        # Lancer les deux tâches en parallèle
        await asyncio.gather(
            listen_task(),
            test_task()
        )

    except KeyboardInterrupt:
        print("\n\nArrêt du client...")
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection_and_discovery())
