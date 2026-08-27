# EPI Detection

Application de surveillance du port des équipements de protection individuelle (EPI) par intelligence artificielle. Une caméra ou une image est analysée par un modèle YOLO qui détecte les personnes et leurs EPI (casque, gilet, gants, etc.), calcule un taux de conformité, et déclenche automatiquement une alerte en cas de non-conformité. Les alertes, audits et règles HSE sont centralisés dans un tableau de bord web.

## Objectif du projet

Aider les équipes HSE (Hygiène, Sécurité, Environnement) à :

- détecter en temps réel (ou sur image) si une personne filmée par une caméra porte les EPI requis ;
- générer automatiquement des alertes lorsqu'une non-conformité est détectée ;
- historiser les détections, gérer des audits et exporter des rapports (PDF/CSV) ;
- configurer des règles HSE par caméra (quels EPI sont obligatoires, niveau de criticité) ;
- offrir un tableau de bord avec statistiques de conformité et gestion des utilisateurs par rôle (admin / superviseur / opérateur).

## Architecture

Le projet est composé de deux applications principales, plus un projet de référence :

```
epi_detection/
├── backend/            # API Django REST (auth, métier, détection YOLO, alertes, audits)
│   └── api/
│       ├── manage.py
│       ├── api/settings.py     # configuration centrale
│       ├── models/best.pt      # poids du modèle YOLO
│       └── Apps/
│           ├── Users/          # authentification JWT (cookies), rôles
│           ├── Cameras/        # gestion des caméras
│           ├── detection/      # inférence YOLO, logs, stats
│           ├── alertes/        # création/liste/traitement des alertes
│           ├── audits/         # sessions d'audit, captures, export PDF/CSV
│           └── RegleSHE/       # règles HSE par caméra
├── frontend/           # SPA React + TypeScript + Vite (tableau de bord)
│   └── src/
│       ├── App.tsx             # routes + AuthProvider
│       ├── context/AuthContext.tsx
│       ├── lib/api.ts           # client API central
│       ├── lib/epiDetectionApi.ts
│       ├── pages/                # Dashboard, Cameras, Alerts, HSERules, Reporting, Admin...
│       └── components/WebcamFeed.tsx  # flux caméra + détection live
├── Model-Deployment/   # projet Flask + YOLO indépendant, utilisé comme référence/démo
└── docker-compose.yml  # lance backend + frontend + Model-Deployment ensemble
```

### Stack technique

**Backend** (Django 4.2, `backend/api/`)
- Django REST Framework + `djangorestframework-simplejwt` (JWT en cookies HttpOnly)
- `ultralytics` (YOLO) pour la détection
- `reportlab` pour la génération de rapports PDF
- SQLite en local (`db.sqlite3`), PostgreSQL en production
- `google-generativeai` pour des analyses IA complémentaires (Gemini), limitées à 5 requêtes/jour
- `boto3` / `django-storages` pour le stockage S3 en production (optionnel, activé via `USE_S3=True`)

**Frontend** (React 18 + TypeScript, `frontend/`)
- Vite, React Router v6
- Tailwind CSS + composants Radix/shadcn-ui
- Recharts pour les graphiques

## Prérequis

- Python 3.11
- Node.js 18+ et npm
- Git

## Installation et lancement (sans Docker)

Le backend et le frontend se lancent séparément, chacun dans son propre terminal.

### 1. Backend — http://localhost:8000

```powershell
cd backend\api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
python manage.py migrate
python manage.py runserver
```

L'interface d'administration Django est disponible sur http://localhost:8000/admin.

### 2. Frontend — http://localhost:8080

```powershell
cd frontend
npm install
npm run dev
```

Créer un fichier `frontend/.env.local` avec :

```
VITE_API_BASE_URL=http://localhost:8000
```

### Récapitulatif des URLs (dev local)

| Application | URL |
|---|---|
| Frontend (tableau de bord) | http://localhost:8080 |
| Backend API (Django) | http://localhost:8000 |
| Admin Django | http://localhost:8000/admin |

## Lancement avec Docker

Un `docker-compose.yml` à la racine permet de lancer le backend, le frontend et le projet de référence `Model-Deployment` ensemble :

```powershell
docker compose up --build
```

Ports exposés par défaut :

| Service | Port |
|---|---|
| Backend | 8010 |
| Frontend | 8090 |
| Model-Deployment (référence) | 3333 |

Le backend attend un fichier d'environnement `backend/api/api/.env` (non versionné) contenant les secrets et variables de configuration (clé Django, base de données, éventuels identifiants AWS S3, clé Gemini, etc.).

## Commandes utiles

**Backend** (depuis `backend/api/`)
```powershell
python manage.py test Apps.Users.tests   # lancer une suite de tests précise
```

**Frontend** (depuis `frontend/`)
```powershell
npm run build     # build de production
npm run lint       # ESLint
npm test           # tests unitaires (Vitest)
```

## Principaux endpoints API

| Préfixe | Domaine |
|---|---|
| `/api/users/` | Authentification, gestion des utilisateurs |
| `/api/cameras/` | Gestion des caméras |
| `/api/detection/` | Détection YOLO, logs, statistiques |
| `/api/alerts/` | Alertes, traitement en masse |
| `/api/rules/hse-rules/` | Configuration des règles HSE |
| `/api/audits/` | Audits, captures, export PDF/CSV |

## Points d'attention

- L'authentification utilise des cookies JWT (HttpOnly), pas de header `Authorization` — `CORS_ALLOW_CREDENTIALS = True` est requis côté backend.
- Le statut des caméras est `active`/`inactive`/`error` côté backend ; le frontend traduit vers `online`/`offline` selon les vues.
- Les statuts d'alerte envoyés au backend doivent être sans accents : `resolu`, `en_cours`, `nouveau`.
- Le stockage S3 ne s'active que si `USE_S3=True` et que toutes les variables AWS sont renseignées ; sinon les fichiers sont stockés localement.

## Déploiement

Le projet est déployé sur AWS via un pipeline CodeBuild → CodeDeploy (voir `Deploy.md` pour les commandes de redémarrage de Gunicorn/Nginx en production).
