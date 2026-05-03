# Contexte du projet EPI Detection

## Objectif fonctionnel

Cette application sert a surveiller le port des EPI (equipements de protection individuelle) via detection video/image, puis a centraliser les non-conformites sous forme d'alertes, d'audits et de regles HSE.

Le projet est compose de deux blocs principaux :

- un backend Django REST qui gere l'authentification, les entites metier, la detection YOLO, les alertes et les exports
- un frontend React/Vite qui fournit le tableau de bord, la vue temps reel, la gestion des regles HSE, des alertes et de l'administration

## Vue d'ensemble de l'architecture

### Backend

Le backend se trouve dans `backend/api/` et est un projet Django 4.2 expose en API REST.

Technos principales :

- Django
- Django REST Framework
- `djangorestframework-simplejwt`
- `django-cors-headers`
- `ultralytics` pour YOLO
- `reportlab` pour les rapports PDF
- SQLite comme base locale actuelle (`backend/api/db.sqlite3`)

Point d'entree :

- `backend/api/manage.py`
- configuration centrale : `backend/api/api/settings.py`
- routage principal : `backend/api/api/urls.py`

### Frontend

Le frontend se trouve dans `frontend/` et est une SPA React + TypeScript construite avec Vite.

Technos principales :

- React 18
- TypeScript
- React Router
- TanStack Query (installe mais peu exploite pour l'instant)
- Tailwind CSS
- composants Radix / shadcn/ui
- Recharts pour les graphiques

Point d'entree :

- `frontend/src/main.tsx`
- routage applicatif : `frontend/src/App.tsx`

## Backend : structure metier

Le backend est organise par apps Django dans `backend/api/Apps/`.

### 1. Users

Responsabilites :

- utilisateur personnalise base sur l'email
- authentification par JWT stocke en cookies HttpOnly
- roles `admin`, `superviseur`, `operateur`

Fichiers importants :

- `backend/api/Apps/Users/models.py`
- `backend/api/Apps/Users/views.py`
- `backend/api/Apps/Users/Authentication.py`
- `backend/api/Apps/Users/permissions.py`
- `backend/api/Apps/Users/urls.py`

Endpoints principaux :

- `POST /api/users/login/`
- `POST /api/users/logout/`
- `POST /api/users/register/`
- `GET /api/users/`
- `GET/PATCH /api/users/me/`
- `POST /api/users/change-password/`
- `GET/PATCH/DELETE /api/users/<id>/`

Note importante : le backend configure une vue custom `RefreshTokenView` dans `views.py`, mais `urls.py` branche actuellement `TokenRefreshView` de SimpleJWT.

### 2. Cameras

Responsabilites :

- gestion des cameras
- statut de fonctionnement
- rattachement indirect aux regles HSE et aux logs de detection

Modele principal :

- `name`
- `location`
- `stream_url`
- `status` dans `active`, `inactive`, `error`
- `is_active`

Endpoints principaux :

- `GET/POST /api/cameras/`
- `GET/PATCH/DELETE /api/cameras/<id>/`
- `PATCH /api/cameras/<id>/status/`
- `GET /api/cameras/active/`

### 3. detection

Responsabilites :

- recevoir une image ou frame envoyee par le frontend
- lancer YOLO
- calculer les statistiques de conformite
- enregistrer un `DetectionLog`
- creer une alerte automatiquement si necessaire

Fichiers importants :

- `backend/api/Apps/detection/views.py`
- `backend/api/Apps/detection/yolo_status.py`
- `backend/api/Apps/detection/yolo_fusion.py`
- `backend/api/Apps/detection/yolo.py`
- modele : `backend/api/Apps/detection/models.py`

Endpoints principaux :

- `POST /api/detection/detect/`
- `GET /api/detection/logs/`
- `GET /api/detection/logs/<id>/`
- `GET /api/detection/stats/`

Flux metier principal :

1. le frontend capture une image depuis webcam ou video
2. il envoie le fichier a `POST /api/detection/detect/`
3. le backend lance `run_detection_with_status(image)`
4. un `DetectionLog` est sauvegarde
5. si la detection n'est pas conforme et qu'une camera est fournie, le backend verifie les EPI attendus via les regles HSE actives de la camera
6. une alerte peut etre creee via `Apps.alertes.utils.create_alert_if_needed`

### 4. alertes

Responsabilites :

- enregistrer les non-conformites detectees
- exposer la liste/pagination/filtres
- permettre la mise a jour de statut, l'assignation et la resolution

Modele principal :

- camera
- timestamp
- `epi_missing`
- `criticity`
- `status`
- image de preuve
- lien optionnel vers `DetectionLog`
- utilisateurs assignes / resolutifs

Endpoints principaux :

- `GET /api/alerts/`
- `GET /api/alerts/stats/`
- `PATCH /api/alerts/bulk/`
- `GET /api/alerts/<id>/`
- `PATCH /api/alerts/<id>/update/`

### 5. RegleSHE

Responsabilites :

- definir les EPI attendus par zone ou camera
- associer plusieurs cameras a une regle HSE
- stocker les criticites dans un JSON `epi_criticites`

Modele principal : `HSERule`

Champs utiles :

- `name`
- `epi_type` (ancien champ, encore present)
- `epi_criticites` (nouveau champ principal)
- `is_active`
- `description`
- `cameras`
- `zone`

Endpoints principaux :

- `GET/POST /api/rules/hse-rules/`
- `GET/PATCH/DELETE /api/rules/hse-rules/<id>/`

### 6. audits

Responsabilites :

- suivi d'audits lies ou non a une alerte
- captures d'ecran associees
- export CSV
- generation PDF

Endpoints principaux :

- `GET/POST /api/audits/`
- `GET /api/audits/export/`
- `GET/PATCH/DELETE /api/audits/<id>/`
- `GET /api/audits/<id>/report/`
- `GET/POST /api/audits/<audit_id>/captures/`
- `DELETE /api/audits/<audit_id>/captures/<id>/`

## Backend : configuration importante

### Authentification

Le backend impose l'authentification par defaut sur DRF via `CookieJWTAuthentication`.

Concretement :

- les cookies `access_token` et `refresh_token` sont poses en HttpOnly
- le frontend doit envoyer `credentials: "include"`
- le frontend ne manipule pas directement le token dans le stockage local

### CORS / CSRF

Dans `settings.py`, les origines actuellement prevues sont surtout locales :

- `http://localhost:8080`
- `http://localhost:3000`
- `http://localhost:5173` pour CSRF

Le frontend actuel Vite doit donc generalement tourner sur `5173`, sauf reconfiguration.

### Modele YOLO

Le modele attendu est :

- `backend/models/best.pt`

Chemin configure dans `settings.py` via `YOLO_MODEL_PATH`.

## Frontend : structure applicative

### Routage

Le routage principal est gere dans `frontend/src/App.tsx`.

Routes publiques :

- `/login`
- `/register`

Routes protegees :

- `/` -> Dashboard
- `/cameras`
- `/alerts`
- `/hse-rules`
- `/reporting`
- `/admin`

La protection se fait via `AuthProvider` + `ProtectedRoute`.

### Authentification frontend

Fichiers utiles :

- `frontend/src/context/AuthContext.tsx`
- `frontend/src/lib/api.ts`

Fonctionnement :

1. au chargement, le frontend appelle `authApi.me()`
2. si l'utilisateur est reconnu par cookie, il reste connecte
3. `login()` appelle `POST /api/users/login/`, puis recharge `me`
4. `logout()` appelle `POST /api/users/logout/`

### Ecrans principaux

#### Dashboard

Fichier : `frontend/src/pages/Dashboard.tsx`

Ce qui est deja branche :

- `GET /api/detection/stats/`
- `GET /api/alerts/`
- `GET /api/cameras/active/`

Le dashboard affiche :

- compteurs globaux de detection
- incidents de la semaine
- repartition par type d'incident
- cameras actives
- profil utilisateur courant

#### Cameras

Fichier : `frontend/src/pages/Cameras.tsx`

Role :

- afficher la liste des cameras
- utiliser la webcam locale ou une video uploadee
- envoyer des frames au backend pour detection EPI
- afficher le statut des EPI attendus pour la camera selectionnee

Composants / services lies :

- `frontend/src/components/WebcamFeed.tsx`
- `frontend/src/components/EPIStatusPanel.tsx`
- `frontend/src/components/BuzzerAlert.tsx`
- `frontend/src/lib/epiDetectionApi.ts`

Flux principal :

1. chargement des cameras via `GET /api/cameras/`
2. selection d'une camera
3. recuperation des EPI attendus depuis `camera.hse_rules[0].epi_criticites`
4. capture periodique d'une frame cote navigateur
5. envoi au backend via `POST /api/detection/detect/`
6. mise a jour visuelle des EPI detectes/manquants

#### Alerts

Fichier : `frontend/src/pages/Alerts.tsx`

Ce qui est deja branche :

- chargement pagine via `GET /api/alerts/?page=...&page_size=...`

Limite actuelle :

- le changement de statut est seulement simule localement dans le composant, il n'appelle pas encore `PATCH /api/alerts/<id>/update/`

#### HSERules

Fichier : `frontend/src/pages/HSERules.tsx`

Ce qui est deja branche :

- `GET /api/rules/hse-rules/`
- `POST /api/rules/hse-rules/`
- `PATCH /api/rules/hse-rules/<id>/`
- `GET /api/cameras/`

Role :

- gerer les regles HSE
- associer des EPI et criticites
- rattacher des cameras a une regle

#### Admin

Fichier : `frontend/src/pages/Admin.tsx`

Ce qui est deja branche :

- `GET /api/users/`
- `POST /api/users/register/`

Role :

- panneau reserve aux administrateurs
- visualisation des utilisateurs
- creation d'utilisateurs
- parties Edge/Cloud encore largement statiques

#### Reporting

Fichier : `frontend/src/pages/Reporting.tsx`

Etat actuel :

- l'ecran est essentiellement statique / mocke
- le bouton PDF ouvre `/api/reports/pdf`, mais l'API backend expose en realite les rapports PDF d'audit sur `/api/audits/<id>/report/`

## Zones de couplage importantes backend <-> frontend

### 1. URL d'API

Le frontend utilise deux variables selon les fichiers :

- `VITE_API_URL`
- `VITE_API_BASE_URL`

Elles ne sont pas harmonisees. Par defaut, plusieurs composants retombent sur `http://localhost:8000`.

### 2. Cookies d'authentification

Toutes les requetes authentifiees doivent passer avec `credentials: "include"`. C'est deja le cas dans la plupart des appels manuels `fetch`.

### 3. Donnees camera / statut

Le backend utilise les statuts :

- `active`
- `inactive`
- `error`

Certaines vues frontend utilisent encore des valeurs ou conventions differentes comme `online`, `offline` ou `cam.active`.

### 4. Statut des alertes

Le backend attend notamment :

- `nouveau`
- `en_cours`
- `resolu`
- `ignore`

Dans le frontend, certaines valeurs affichent encore `résolu` avec accent. Cela peut provoquer des incoherences de mapping si le code commence a appeler l'API de mise a jour.

## Points de vigilance observes

Ces points ne bloquent pas la comprehension du projet, mais ils sont utiles pour la suite :

1. le frontend est partiellement branche au backend, avec encore des ecrans ou sous-parties mockes
2. la page Alerts ne persiste pas encore les changements de statut
3. la page Reporting ne correspond pas encore aux endpoints d'audit reels
4. les conventions de nommage API (`VITE_API_URL` vs `VITE_API_BASE_URL`) sont incoherentes
5. certaines conventions de statut divergent entre frontend et backend (`active`/`inactive` vs `online`/`offline`)
6. `RegleSHE/models.py` conserve un ancien champ `epi_type` et un nouveau champ `epi_criticites`, ce qui indique une transition de modele encore en cours

## Commandes utiles pour relancer le projet

### Backend

Depuis `backend/` :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd api
python manage.py runserver
```

URL par defaut :

- `http://localhost:8000/`

### Frontend

Depuis `frontend/` :

```powershell
npm install
npm run dev
```

URL Vite habituelle :

- `http://localhost:5173/`

## Fichiers prioritaires pour une prochaine reprise

Si l'objectif est de continuer le projet rapidement, il faut relire en priorite :

### Backend

- `backend/api/api/settings.py`
- `backend/api/api/urls.py`
- `backend/api/Apps/detection/views.py`
- `backend/api/Apps/alertes/views.py`
- `backend/api/Apps/RegleSHE/views.py`
- `backend/api/Apps/Users/views.py`

### Frontend

- `frontend/src/App.tsx`
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/epiDetectionApi.ts`
- `frontend/src/pages/Cameras.tsx`
- `frontend/src/components/WebcamFeed.tsx`
- `frontend/src/pages/Dashboard.tsx`

## Resume rapide

Le coeur du projet est deja pose :

- auth securisee par cookies JWT
- gestion des utilisateurs, cameras, regles HSE, alertes, audits
- detection EPI par YOLO avec journalisation
- interface React pour l'exploitation metier

Le travail restant semble surtout porter sur l'alignement fin backend/frontend, la suppression des mocks restants, et la stabilisation des conventions d'API et de statuts.
