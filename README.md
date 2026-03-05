# Homematic IP Playground
La section suivante documente la spécification de la librairie Homematic IP Connect (eQ‑3). Les chapitres suivants expliquent comment lancer le backend/dashboard, construire le frontend en dev/prod et utiliser Docker.
---

## Dashboard « chauffage » (API FastAPI + Frontend Vue/Vuetify)

Le dossier `chauffage/` regroupe :

- `backend/` : API FastAPI qui s’appuie sur la librairie officielle `homematicip` (cloud eQ‑3) pour exposer vos capteurs (`/health`, `/sensors`, `/devices`).
- `frontend/` : application Vue 3 + Vite + Vuetify (thème sombre) affichant jusqu’à 12 cartes capteurs (température/humidité, icône batterie, horodatage).
- `main.py` : point d’entrée Uvicorn qui monte l’API et le build frontend depuis un même serveur.
- `requirements.txt` : dépendances backend.

### 1 Prérequis

- Python 3.11+ (recommandé 3.12).
- Node.js ≥ 18 (pour Vite/Vuetify ; le Dockerfile utilise Node 20).
- `config.ini` généré via `hmip_generate_auth_token` contenant `AuthToken` et `AccessPoint`.
- `HMIP_CONFIG` doit pointer vers ce fichier (sinon placez‑le à la racine du dépôt).

### 2 Backend Endpoints (FastAPI)

Endpoints principaux :
- `GET /health` — statut + ID access point.
- `GET /sensors` — liste des capteurs environnement (avec `battery_low`, `last_update`, etc.).
- `GET /devices` — inventaire complet Homematic IP.
- `/` — frontend compilé (si `frontend/dist` existe), sinon message d’instruction pour lancer le build.

### 3 Docker & Docker Compose

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

### 4 Arborescence utile

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
└── requirements.txt
```

---

## 5 Déploiement sur Raspberry Pi

Guide pas à pas pour installer et lancer l'application sur un Raspberry Pi (testé sur Raspberry Pi OS 64-bit).

### Option A — Docker (recommandé)

C'est la méthode la plus simple : pas besoin d'installer Python ou Node sur la machine.

**1. Installer Docker**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Se déconnecter / reconnecter pour que le groupe prenne effet
```

**2. Cloner le dépôt**
```bash
git clone <URL_DU_REPO> chauffage
cd chauffage
```

**3. Générer le token d'authentification Homematic IP**

Depuis une machine disposant d'un accès Python :
```bash
pip install homematicip
hmip_generate_auth_token
```
Copiez le fichier `config.ini` généré à la racine du dépôt sur le Raspberry Pi.

**4. Lancer l'application**
```bash
docker compose up --build -d chauffage
```

L'application est accessible sur `http://<IP_DU_RASPBERRY>:8000`.

**5. Relancer automatiquement au démarrage**

Le service redémarre tout seul grâce au `restart: unless-stopped` déjà configuré dans `docker-compose.yml`. Rien de plus à faire.

**6. Voir les logs / arrêter**
```bash
docker compose logs -f chauffage   # suivre les logs en direct
docker compose stop                # arrêter
docker compose up -d               # relancer (sans rebuild)
```

---

## 6 Résumé des commandes fréquentes

| Action | Commande |
| --- | --- |
| Docker (prod) | `docker compose up --build chauffage` |
| Docker (front dev) | `docker compose up frontend-dev` |
| Lanceur rapide (docker prod) | `make start` |
| Build frontend via Docker | `make build` |
| Frontend dev container | `make frontend-dev` |
| Stopper les conteneurs | `make stop` |

---

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

`.env.local` : `VITE_THEME_MODE=auto`.

Toutes les variables frontend peuvent être définies dans `chauffage/frontend/.env.local` (copiez `.env.example` comme base).
