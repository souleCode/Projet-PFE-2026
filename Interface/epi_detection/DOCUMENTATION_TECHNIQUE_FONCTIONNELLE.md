# Documentation Technique Et Fonctionnelle

## 1. Objet du projet

Ce projet est une plateforme de supervision HSE orientee detection des EPI a partir de flux video et d'images.

L'application permet de :

- gerer des utilisateurs avec roles
- gerer des cameras et leur statut
- lancer des detections EPI sur image
- generer automatiquement des alertes en cas de non-conformite
- suivre le traitement des alertes
- ouvrir et suivre des audits terrain
- produire des indicateurs et des rapports

Le projet est compose de deux parties :

- un backend Django REST API
- un frontend React + TypeScript + Vite


## 2. Documentation fonctionnelle

### 2.1 Acteurs et roles

Le systeme gere trois roles principaux :

- `admin` : administration complete de la plateforme
- `superviseur` : supervision operationnelle, traitement des alertes, mise a jour de certains objets
- `operateur` : consultation et usage standard de l'application

### 2.2 Droits principaux par role

| Fonctionnalite | Admin | Superviseur | Operateur |
| --- | --- | --- | --- |
| Se connecter | Oui | Oui | Oui |
| Consulter son profil | Oui | Oui | Oui |
| Changer son mot de passe | Oui | Oui | Oui |
| Creer un compte utilisateur | Oui | Non | Non |
| Voir la liste des utilisateurs | Oui | Oui | Non |
| Modifier un autre utilisateur | Oui | Non | Non |
| Gerer les cameras | Oui | Partiel | Consultation |
| Changer le statut d'une camera | Oui | Oui | Non |
| Consulter les alertes | Oui | Oui | Oui |
| Mettre a jour une alerte | Oui | Oui | Non |
| Creer ou modifier une regle HSE | Oui | Non | Non |
| Consulter les regles HSE | Oui | Oui | Oui |
| Creer un audit | Oui | Oui | Oui |
| Exporter les audits CSV | Oui | Oui | Non |

### 2.3 Parcours fonctionnel principal

#### A. Gestion des utilisateurs

Un administrateur cree les comptes utilisateurs. Chaque utilisateur possede un email unique, un nom, un prenom et un role.

#### B. Gestion des cameras

Les cameras representent les points de surveillance. Chaque camera dispose d'un nom, d'une localisation, d'un statut et eventuellement d'une URL de flux.

#### C. Detection EPI

Le module de detection analyse une image et determine si les EPI attendus sont portes ou non. Les resultats sont traces dans des logs de detection.

#### D. Generation d'alerte

Si une detection n'est pas conforme et qu'une camera est associee, une alerte peut etre creee. L'alerte contient notamment :

- la camera
- la date de detection
- les EPI manquants
- le niveau de criticite
- une image associee
- un statut de traitement

#### E. Traitement des alertes

Les alertes suivent en general ce cycle :

- `nouveau`
- `en_cours`
- `resolu`
- `ignore`

Lorsqu'une alerte est prise en charge, le systeme enregistre automatiquement un horodatage de premiere prise en compte. Lorsqu'elle est resolue, le systeme enregistre egalement l'utilisateur qui l'a resolue ainsi que la date de resolution.

#### F. Audit

Une alerte importante peut donner lieu a un audit. Un audit permet de formaliser le suivi terrain, d'ajouter des notes, de joindre des captures et de produire un rapport PDF.

Les statuts d'audit sont :

- `ouvert`
- `en_cours`
- `clos`

#### G. Reporting

Le module de reporting consolide les donnees metier :

- nombre de detections
- taux de conformite
- repartition des incidents
- statistiques d'alertes
- indicateurs MTTA et MTTR
- recurrence par camera et par zone


## 3. Documentation technique

### 3.1 Architecture generale

#### Backend

- Framework : Django + Django REST Framework
- Authentification : JWT avec cookies HttpOnly
- Base de donnees : PostgreSQL RDS dans la configuration actuelle
- Stockage media : S3 via `django-storages` quand configure
- Detection IA : modele YOLO

#### Frontend

- Framework : React 18
- Langage : TypeScript
- Build tool : Vite
- UI : Tailwind CSS + composants UI
- Routage : React Router

### 3.2 Modules backend

- `Apps.Users` : utilisateurs, authentification, roles, permissions
- `Apps.Cameras` : cameras et statut des cameras
- `Apps.detection` : detection EPI, logs, statistiques, KPIs
- `Apps.alertes` : alertes et traitement operationnel
- `Apps.audits` : audits, captures, rapports PDF, export CSV
- `Apps.RegleSHE` : regles HSE par camera/zone

### 3.3 Routes frontend principales

| Route | Description |
| --- | --- |
| `/login` | connexion utilisateur |
| `/register` | page de creation de compte cote frontend |
| `/` | dashboard principal |
| `/cameras` | gestion et consultation des cameras |
| `/alerts` | consultation et traitement des alertes |
| `/audits/:auditId` | detail d'un audit |
| `/hse-rules` | gestion des regles HSE |
| `/reporting` | reporting et KPIs |
| `/admin` | administration |

Note importante : la page frontend `/register` existe, mais l'API de creation de compte est actuellement reservee a l'administrateur.


## 4. Authentification et comptes

### 4.1 Mode d'authentification

Le backend utilise une authentification JWT avec cookies HttpOnly :

- cookie access : `access_token`
- cookie refresh : `refresh_token`

Caracteristiques principales :

- le frontend envoie les requetes avec `credentials: include`
- le cookie access sert aux appels proteges
- le cookie refresh permet de renouveler la session
- les cookies sont configures en `HttpOnly`

### 4.2 Connexion

Endpoint : `POST /api/users/login/`

Exemple de body :

```json
{
  "email": "admin@example.com",
  "password": "motdepasse"
}
```

Reponse attendue :

- pose les cookies d'authentification
- retourne les informations du compte connecte

### 4.3 Deconnexion

Endpoint : `POST /api/users/logout/`

Effets :

- suppression des cookies JWT
- blacklisting du refresh token quand il est disponible

### 4.4 Recuperer le profil courant

Endpoint : `GET /api/users/me/`

Permet au frontend de connaitre l'utilisateur connecte.

### 4.5 Changer son mot de passe

Endpoint : `POST /api/users/change-password/`

Exemple de body :

```json
{
  "old_password": "ancien-mot-de-passe",
  "new_password": "nouveau-mot-de-passe"
}
```

### 4.6 Creer un compte utilisateur

Endpoint : `POST /api/users/register/`

Restriction : `admin` uniquement.

Exemple de body :

```json
{
  "email": "operateur@example.com",
  "first_name": "Ali",
  "last_name": "Khaldi",
  "role": "operateur",
  "password": "Password123",
  "password2": "Password123"
}
```

Si aucun administrateur n'existe encore, il faut creer le premier compte via Django :

```powershell
python manage.py createsuperuser
```


## 5. Catalogue des API

Base URL backend : `http://localhost:8000/`

Les routes exposees sont groupees sous `/api/`.

### 5.1 Utilisateurs

Base : `/api/users/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| POST | `/api/users/login/` | connexion | public |
| POST | `/api/users/logout/` | deconnexion | authentifie |
| POST | `/api/users/token/refresh/` | renouvellement du token | public/selon mecanisme JWT |
| POST | `/api/users/register/` | creation d'un compte | admin |
| GET | `/api/users/` | liste des utilisateurs | admin, superviseur |
| GET | `/api/users/me/` | profil courant | authentifie |
| PATCH | `/api/users/me/` | mise a jour de son profil | authentifie |
| POST | `/api/users/change-password/` | changement mot de passe | authentifie |
| GET | `/api/users/{id}/` | detail utilisateur | proprietaire ou admin |
| PATCH | `/api/users/{id}/` | mise a jour utilisateur | proprietaire ou admin |
| DELETE | `/api/users/{id}/` | suppression utilisateur | admin uniquement en pratique |

### 5.2 Cameras

Base : `/api/cameras/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| GET | `/api/cameras/` | liste des cameras | authentifie |
| POST | `/api/cameras/` | creation d'une camera | admin |
| GET | `/api/cameras/active/` | liste des cameras actives | authentifie |
| GET | `/api/cameras/{id}/` | detail d'une camera | authentifie |
| PATCH | `/api/cameras/{id}/` | modifier une camera | admin, superviseur |
| DELETE | `/api/cameras/{id}/` | supprimer une camera | admin |
| PATCH | `/api/cameras/{id}/status/` | changer le statut | admin, superviseur |

Statuts camera :

- `active`
- `inactive`
- `error`

### 5.3 Detection

Base : `/api/detection/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| POST | `/api/detection/detect/` | lancer une detection sur image | authentifie |
| GET | `/api/detection/logs/` | liste des logs de detection | authentifie |
| GET | `/api/detection/logs/{id}/` | detail d'un log | authentifie |
| GET | `/api/detection/stats/` | statistiques globales de detection | authentifie |
| GET | `/api/detection/business-kpis/` | KPIs metier avances | authentifie |

Exemple de donnees envoyees a `detect/` :

- `file` : image a analyser
- `camera_id` : identifiant optionnel d'une camera

### 5.4 Alertes

Base : `/api/alerts/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| GET | `/api/alerts/` | liste des alertes | authentifie |
| GET | `/api/alerts/stats/` | statistiques d'alertes | authentifie |
| PATCH | `/api/alerts/bulk/` | mise a jour en masse | admin, superviseur |
| GET | `/api/alerts/{id}/` | detail d'une alerte | authentifie |
| PATCH | `/api/alerts/{id}/update/` | changer statut, assignation, notes | admin, superviseur |

Filtres supportes sur la liste :

- `status`
- `criticity`
- `camera_id`
- `search`

Statuts d'alerte :

- `nouveau`
- `en_cours`
- `resolu`
- `ignore`

Criticites :

- `faible`
- `moyenne`
- `elevee`

### 5.5 Audits

Base : `/api/audits/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| GET | `/api/audits/` | liste des audits | authentifie |
| POST | `/api/audits/` | creation d'un audit | authentifie |
| GET | `/api/audits/export/` | export CSV | admin, superviseur |
| GET | `/api/audits/{id}/` | detail audit | authentifie |
| PATCH | `/api/audits/{id}/` | modifier titre, statut, notes | authentifie |
| DELETE | `/api/audits/{id}/` | suppression audit | admin, superviseur |
| GET | `/api/audits/{id}/report/` | rapport PDF | authentifie |
| GET | `/api/audits/{audit_id}/captures/` | liste des captures | authentifie |
| POST | `/api/audits/{audit_id}/captures/` | ajouter une capture image | authentifie |
| DELETE | `/api/audits/{audit_id}/captures/{id}/` | suppression capture | admin, superviseur |

Filtres supportes sur la liste :

- `status`
- `camera_id`
- `alert_id`

Statuts d'audit :

- `ouvert`
- `en_cours`
- `clos`

### 5.6 Regles HSE

Base : `/api/rules/hse-rules/`

| Methode | Endpoint | Description | Acces |
| --- | --- | --- | --- |
| GET | `/api/rules/hse-rules/` | liste des regles HSE | authentifie |
| POST | `/api/rules/hse-rules/` | creation d'une regle HSE | admin |
| GET | `/api/rules/hse-rules/{id}/` | detail d'une regle | authentifie |
| PATCH | `/api/rules/hse-rules/{id}/` | modification d'une regle | admin |
| DELETE | `/api/rules/hse-rules/{id}/` | suppression d'une regle | admin |


## 6. Principales entites de donnees

### 6.1 Utilisateur

Champs importants :

- `email`
- `first_name`
- `last_name`
- `role`
- `is_active`
- `created_at`

### 6.2 Camera

Champs importants :

- `name`
- `location`
- `stream_url`
- `status`
- `is_active`

### 6.3 Log de detection

Champs importants :

- `camera`
- `timestamp`
- `detections_json`
- `stats_json`
- `is_compliant`
- `processing_time`

### 6.4 Alerte

Champs importants :

- `camera`
- `timestamp`
- `epi_missing`
- `criticity`
- `status`
- `image`
- `assigned_to`
- `first_acknowledged_at`
- `resolved_by`
- `resolved_at`
- `notes`

### 6.5 Audit

Champs importants :

- `title`
- `camera`
- `alert`
- `created_by`
- `status`
- `notes`
- `created_at`

### 6.6 Capture d'audit

Champs importants :

- `audit`
- `image`
- `description`
- `taken_at`
- `taken_by`

### 6.7 Regle HSE

Champs importants :

- `name`
- `epi_type`
- `epi_criticites`
- `is_active`
- `description`
- `cameras`
- `zone`


## 7. Processus metier de reference

### 7.1 Detection vers alerte

1. un utilisateur soumet une image a analyser
2. le backend execute la detection YOLO
3. un log de detection est enregistre
4. si la detection est non conforme et reliee a une camera, une alerte peut etre creee

### 7.2 Alerte vers audit

1. une alerte est consultee dans l'ecran alertes
2. l'equipe HSE decide d'ouvrir un audit
3. un audit est cree avec un lien vers l'alerte et la camera
4. des captures et des notes sont ajoutees au fil du traitement
5. un rapport PDF peut etre exporte

### 7.3 Indicateurs metier

Le projet calcule plusieurs indicateurs utiles :

- volumetrie d'incidents
- taux de conformite
- MTTA : temps moyen avant premiere prise en charge
- MTTR : temps moyen avant resolution
- recurrence par camera
- recurrence par zone


## 8. Creation d'un nouvel environnement

### 8.1 Backend

Depuis le dossier `backend/` ou selon votre structure de virtualenv :

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 8.2 Frontend

Depuis le dossier `frontend/` :

```powershell
npm install
npm run dev
```


## 9. Variables de configuration importantes

Variables backend frequentes :

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`
- `AWS_QUERYSTRING_AUTH`

Base de donnees : il est recommande de passer egalement les informations PostgreSQL par variables d'environnement.


## 10. Points d'attention

- la page frontend d'inscription existe, mais l'API de creation d'utilisateur est reservee a l'administrateur
- le backend repose sur des cookies JWT, il faut donc conserver `credentials: include` cote frontend
- si S3 est prive, les URLs media doivent etre signees
- les roles doivent etre controles cote backend, pas seulement cote frontend


## 11. Fichiers de reference du projet

Documents deja disponibles dans le projet :

- `CONTEXTE_PROJET.md`
- `WORKFLOW_AUDITS.md`
- `BRIEF_DIAGRAMMES_PFE.md`
- `BRIEF_DIAGRAMMES_GPT.md`
- `BRIEF_PRESENTATION_JURY_CLAUDE.md`

Ce document sert de reference centrale pour la documentation technique et fonctionnelle quotidienne.