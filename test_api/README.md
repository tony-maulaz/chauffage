# Exemple Python pour l'API Homematic IP Connect

Ce répertoire contient un exemple d'implémentation Python pour l'API Homematic IP Connect. L'exemple démontre comment établir une connexion WebSocket avec le Homematic IP Home Control Unit (HCU) et interagir avec lui.

## Fonctionnalités

- Connexion WebSocket sécurisée au HCU
- Réponse aux requêtes d'état du plugin (`PLUGIN_STATE_REQUEST`)
- Découverte des appareils (`DISCOVER_REQUEST`)
- Contrôle des appareils (`CONTROL_REQUEST`)
- Gestion des différents types d'appareils (lumières, capteurs de température, thermostats)

## Prérequis

- **Python 3.7+** : Assurez-vous d'avoir Python 3.7 ou supérieur installé
- **Homematic IP HCU** : Accès à un Homematic IP Home Control Unit avec le mode développeur activé
- **Token d'autorisation** : Obtenez le token d'autorisation pour votre plugin depuis le HCU

## Installation

1. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

### 1. Préparer le token d'autorisation

Obtenez le token d'autorisation pour votre identifiant de plugin et sauvegardez-le dans un fichier (par exemple `authtoken.txt`) :

```bash
echo "votre-token-ici" > authtoken.txt
```

### 2. Lancer le client

Utilisez la commande suivante pour lancer le client :

```bash
python homematic_client.py <plugin-id> <hcu-address> <authtoken-file>
python3 homematic_client.py ch.test.plugin.python hcu1-8284.local token.txt
python3 homematic_client.py ch.test.plugin.python 192.168.0.163 token.txt
```

Remplacez les paramètres par :
- `<plugin-id>` : Identifiant unique de votre plugin (ex: `com.example.plugin.python`)
- `<hcu-address>` : Adresse de votre HCU (ex: `hcu1-XXXX.local`)
- `<authtoken-file>` : Chemin vers le fichier contenant le token (ex: `authtoken.txt`)

**Exemple** :
```bash
python homematic_client.py com.example.plugin.python hcu1-5678.local authtoken.txt
```

## Structure du code

### Classe `HomematicClient`

La classe principale qui gère la connexion et la communication avec le HCU :

- `connect()` : Établit la connexion WebSocket
- `send_plugin_ready()` : Indique que le plugin est prêt
- `send_discover_response()` : Répond avec la liste des appareils disponibles
- `handle_control_request()` : Gère les commandes de contrôle des appareils
- `listen()` : Écoute les messages du HCU en continu

### Exemple d'appareils

Le script déclare 3 appareils fictifs pour la démonstration :

1. **Lumière Salon** (`light-salon-1`)
   - Type : LIGHT
   - Feature : switchState (on/off)

2. **Capteur Température Chambre** (`temp-chambre-1`)
   - Type : TEMPERATURE_SENSOR
   - Feature : temperature (lecture de température)

3. **Thermostat Bureau** (`thermostat-bureau-1`)
   - Type : THERMOSTAT
   - Features : targetTemperature, currentTemperature

## Adaptation à vos appareils

Pour adapter ce code à vos propres appareils :

1. **Modifiez `send_discover_response()`** pour déclarer vos appareils réels
2. **Implémentez `handle_control_request()`** pour communiquer avec vos appareils physiques
3. Ajoutez la logique nécessaire pour lire l'état de vos appareils

## Types de messages

### PLUGIN_STATE_REQUEST/RESPONSE
Indique l'état de disponibilité du plugin au HCU.

### DISCOVER_REQUEST/RESPONSE
Permet au HCU de découvrir les appareils disponibles via le plugin.

### CONTROL_REQUEST/RESPONSE
Permet au HCU d'envoyer des commandes aux appareils (allumer/éteindre, changer température, etc.).

## Débogage

Le script affiche tous les messages échangés avec le HCU :
- `→` Message envoyé
- `←` Message reçu
- `🔍` Requête de découverte
- `🎛️` Commande de contrôle

## Exemple de sortie

```
Connexion à wss://hcu1-5678.local:9001...
Connecté au WebSocket

→ Message envoyé:
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "pluginId": "com.example.plugin.python",
  "type": "PLUGIN_STATE_RESPONSE",
  "body": {
    "pluginReadinessStatus": "READY"
  }
}

← Message reçu:
{
  "id": "abc123",
  "type": "DISCOVER_REQUEST"
}

🔍 Requête de découverte des appareils...
```

## Documentation complète

Pour plus d'informations sur l'API Homematic IP Connect, consultez la documentation complète dans `connect-api-documentation-1.0.1.html` à la racine du dépôt.

## License

Cet exemple est sous licence [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0.txt).

## Mainteneur

Exemple développé pour l'API Homematic IP Connect.\
Homematic IP est une marque de **eQ-3 AG**.
