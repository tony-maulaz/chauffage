# Homematic IP Playground

Ce dépôt regroupe deux usages complémentaires de l’écosystème Homematic IP :

- `test_api/` — exemples autour de la librairie eQ‑3 Homematic IP Connect (client WebSocket, messages DISCOVER/CONTROL, etc.).
- `chauffage/` — backend FastAPI basé sur `homematicip` + dashboard Vue/Vuetify pour visualiser 12 capteurs (température/humidité/batterie) avec un workflow Docker prêt pour PC ou Raspberry Pi.

La section suivante documente la spécification de la librairie Homematic IP Connect (eQ‑3). Les chapitres suivants expliquent comment lancer le backend/dashboard, construire le frontend en dev/prod et utiliser Docker.

---

## 1. Librairie Homematic IP Connect (eQ‑3)

Tout le code et les exemples d’utilisation sont disponibles dans `test_api/`. Le répertoire contient :

- `homematic_client.py` : client WebSocket minimaliste pour le HCU.
- `test_client.py` : script de test.
- `requirements.txt` : dépendances Python pour cette partie.
- `README.md` : guide détaillé (messages supportés, adaptation à vos appareils, exemples de sortie, etc.).

### Fonctionnalités couvertes

- Connexion sécurisée (WebSocket TLS) au Home Control Unit.
- Gestion des messages `PLUGIN_STATE_REQUEST`, `DISCOVER_REQUEST`, `CONTROL_REQUEST`.
- Simulation de plusieurs types d’appareils (lumière, thermostat, capteur température).
- Traces détaillées des échanges (`→`, `←`) pour faciliter le débogage.

### Prérequis rapides

1. Python 3.8+.
2. Accès au HCU en mode développeur et `authtoken`.
3. Dépendances : `pip install -r test_api/requirements.txt`.

### Démarrage express

```bash
cd test_api
python homematic_client.py <plugin-id> <hcu-address> token.txt
```

Une documentation exhaustive (structures des messages, adaptation à vos appareils, etc.) est disponible dans `test_api/README.md` et peut être consultée séparément pour garder cette racine focalisée sur la spécification eQ‑3.

### Fichiers à copier avant de lancer les services

Plusieurs fichiers sont ignorés par Git car ils contiennent des secrets. Copiez les modèles fournis, puis complétez les valeurs :

```bash
cp config.ini.example config.ini                   # utilisé par le backend FastAPI
cp token.txt.example token.txt                     # token plugin pour les clients/tests
cp test_api/token.txt.example test_api/token.txt   # équivalent pour test_api/
cp chauffage/frontend/.env.example chauffage/frontend/.env.local  # options frontend
```

`test_api/authtoken.txt.example` reste disponible pour générer un second token si besoin.

---

## 2. Dashboard « chauffage » (API FastAPI + Frontend Vue/Vuetify)

Le dossier `chauffage/` regroupe :

- `backend/` : API FastAPI qui s’appuie sur la librairie officielle `homematicip` (cloud eQ‑3) pour exposer vos capteurs (`/health`, `/sensors`, `/devices`).
- `frontend/` : application Vue 3 + Vite + Vuetify (thème sombre) affichant jusqu’à 12 cartes capteurs (température/humidité, icône batterie, horodatage).
- `main.py` : point d’entrée Uvicorn qui monte l’API et le build frontend depuis un même serveur.
- `requirements.txt` : dépendances backend.
- `spec_chauffage.md` : cahier des charges détaillé.

### 2.1 Prérequis

- Python 3.11+ (recommandé 3.12).
- Node.js ≥ 18 (pour Vite/Vuetify ; le Dockerfile utilise Node 20).
- `config.ini` généré via `hmip_generate_auth_token` contenant `AuthToken` et `AccessPoint`.
- `HMIP_CONFIG` doit pointer vers ce fichier (sinon placez‑le à la racine du dépôt).

### 2.2 Backend local (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate        # ou .venv\Scripts\activate sous Windows
pip install -r chauffage/requirements.txt

export HMIP_CONFIG=/chemin/vers/config.ini  # ou placez config.ini à la racine
uvicorn chauffage.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints principaux :
- `GET /health` — statut + ID access point.
- `GET /sensors` — liste des capteurs environnement (avec `battery_low`, `last_update`, etc.).
- `GET /devices` — inventaire complet Homematic IP.
- `/` — frontend compilé (si `frontend/dist` existe), sinon message d’instruction pour lancer le build.

### 2.3 Frontend — mode développement

```bash
cd chauffage/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 4173
```

- Configurez l’ordre et les noms des capteurs dans `src/config/sensors.js` (12 slots max).  
- L’application interroge `/sensors` toutes les 60 s (modifiable via `VITE_POLL_INTERVAL`).  
- Pour du hot-reload sans installer Node localement, utilisez `docker compose up frontend-dev` (voir § 2.5).

### 2.4 Frontend — build production

```bash
cd chauffage/frontend
npm install          # première fois
npm run build        # génère frontend/dist
```

Le répertoire `dist/` est automatiquement pris en charge par `chauffage/main.py` (via `StaticFiles`).  
Chaque nouveau build doit être copié (ou laissé) dans `chauffage/frontend/dist` avant de redémarrer l’API.

### 2.5 Docker & Docker Compose

Le dépôt inclut un workflow multi-stage complet :

1. **Image unique** (backend + frontend build) :
   ```bash
   docker compose up --build chauffage
   ```
   - Montez votre `config.ini` via le volume déclaré dans `docker-compose.yml` (`./config.ini:/data/config.ini:ro`).
   - L’API écoute sur `http://localhost:8000`; le frontend est servi sur la même URL.

2. **Dev frontend en conteneur** :
   ```bash
   docker compose up frontend-dev
   ```
   - Monte `./chauffage/frontend` dans `/workspace/frontend`.
   - Lance `npm run dev` sur le port `4173` avec hot-reload, Node 20 déjà installé.

3. **Image autonome** :
   ```bash
   docker build -t chauffage-app .
   docker run -p 8000:8000 -e HMIP_CONFIG=/data/config.ini \
      -v $(pwd)/config.ini:/data/config.ini:ro chauffage-app
   ```

### 2.6 Arborescence utile

```
chauffage/
├── backend/
│   └── api.py         # FastAPI (routes /sensors, /devices, helpers)
├── frontend/
│   ├── src/
│   │   ├── components/SensorCard.vue
│   │   ├── views/Dashboard.vue
│   │   ├── config/sensors.js
│   │   └── services/api.js
│   └── dist/          # créé après npm run build
├── main.py            # entrypoint uvicorn + montage frontend
├── requirements.txt
└── spec_chauffage.md  # cahier des charges complet
```

---

## 3. Résumé des commandes fréquentes

| Action | Commande |
| --- | --- |
| Installer les deps backend | `pip install -r chauffage/requirements.txt` |
| Lancer FastAPI (dev) | `uvicorn chauffage.main:app --reload` |
| Dev frontend local | `npm run dev -- --host 0.0.0.0 --port 4173` |
| Build frontend prod | `npm run build` |
| Docker (prod) | `docker compose up --build chauffage` |
| Docker (front dev) | `docker compose up frontend-dev` |
| Lanceur rapide (docker prod) | `make dev` |
| Build frontend via Docker | `make build` |
| Frontend dev container | `make frontend-dev` |
| Stopper les conteneurs | `make stop` |

---

## 4. Ressources additionnelles

- `test_api/README.md` — documentation complète de la librairie Homematic IP Connect (eQ‑3).  
- `spec_chauffage.md` — spécification fonctionnelle du dashboard (UI, refresh, layout, etc.).  
- `Dockerfile` & `docker-compose.yml` — référence pour vos déploiements (PC ou Raspberry Pi).

N’hésitez pas à adapter ces scripts (Makefile, CI/CD, etc.) selon votre environnement. Le README reste votre point d’entrée pour utiliser facilement la librairie eQ‑3 et le tableau de bord chauffage.
> Astuce : utilisez le `Makefile` pour simplifier ces commandes (`make dev`, `make build`, `make frontend-dev`, `make stop`).

### Mode debug frontend

Pour visualiser des données fictives (y compris des capteurs en `battery_low`) sans dépendre de l’API, définissez la variable d’environnement Vite :

```bash
cd chauffage/frontend
VITE_DEBUG_MODE=true npm run dev
```

ou créez un fichier `.env.local` avec `VITE_DEBUG_MODE=true`. Dans ce mode, le dashboard affiche des valeurs simulées (`src/config/debug.js`).

### Connexion backend quand le front tourne en dev

Quand vous lancez `make frontend-dev` (Vite), indiquez où joindre l’API :

```bash
cd chauffage/frontend
echo "VITE_API_BASE_URL=http://localhost:8000" >> .env.local
```

Le backend accepte par défaut les origines `http://localhost:4173` et `http://127.0.0.1:4173`. Pour en ajouter d’autres (tablettes, proxy, etc.), exportez `ALLOWED_CORS_ORIGINS` avant de lancer `make dev` :

```bash
ALLOWED_CORS_ORIGINS="http://localhost:4173,http://my-tablet.local:4173" make dev
```

### Choix du thème (clair/sombre/auto)

Le frontend accepte la variable `VITE_THEME_MODE` (`light`, `dark` ou `auto`).

- `light` : thème clair permanent.
- `dark` : thème sombre permanent.
- `auto` : thème clair entre 07:00 et 19:00, sombre le reste du temps (l’évaluation est refaite toutes les minutes).

Exemple :

```bash
VITE_THEME_MODE=auto npm run dev
```

ou dans `.env.local` : `VITE_THEME_MODE=auto`.

Toutes les variables frontend peuvent être définies dans `chauffage/frontend/.env.local` (copiez `.env.example` comme base).
