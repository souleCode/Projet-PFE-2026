# Brief Pour Generer Les Diagrammes Architecturaux

Ce document sert de contexte a donner a GPT pour generer 3 diagrammes architecturaux de la plateforme EPI Detection.

Les 3 diagrammes attendus sont :

1. un diagramme de classe
2. un diagramme de use case complet
3. un diagramme de sequence

L'objectif est de representer le fonctionnement reel du projet, en restant fidele au code actuel.

---

## 1. Contexte general de la plateforme

La plateforme EPI Detection sert a surveiller le port des EPI (equipements de protection individuelle) via analyse d'image/video.

Le systeme detecte les non-conformites, cree des alertes, puis permet d'ouvrir un audit pour suivre le traitement jusqu'a la cloture.

La plateforme est composee de :

- un frontend React + TypeScript + Vite
- un backend Django REST Framework
- une base SQLite locale actuellement
- un moteur de detection YOLO appele par le backend

Le flux metier principal est :

1. une camera ou un flux video fournit une image
2. le backend lance la detection EPI
3. un log de detection est enregistre
4. si non-conformite, une alerte est creee
5. un utilisateur consulte l'alerte
6. il peut ouvrir un audit de suivi
7. l'audit passe par les statuts `ouvert` -> `en_cours` -> `clos`
8. des captures et notes peuvent etre ajoutees a l'audit
9. la cloture de l'audit formalise le traitement de l'incident

---

## 2. Perimetre fonctionnel a representer

Les diagrammes doivent se concentrer sur le coeur metier suivant :

- gestion des utilisateurs et des roles
- gestion des cameras
- regles HSE associees aux cameras
- logs de detection
- alertes de non-conformite
- audits de suivi
- captures rattachees aux audits

Ne pas entrer dans le detail des composants UI generiques ni des bibliotheques frontend.

---

## 3. Acteurs metier

Acteurs principaux :

- `Operateur`
- `Superviseur`
- `Administrateur`
- `Systeme de detection IA`

Contraintes de role :

- `admin` : administration complete, regles HSE, suppression sensible, supervision globale
- `superviseur` : suivi operationnel, consultation, traitement, audit
- `operateur` : consultation des alertes et traitement limite selon les ecrans

---

## 4. Entites metier a utiliser dans le diagramme de classe

### User

Role : utilisateur authentifie de la plateforme.

Attributs principaux :

- `id`
- `email`
- `first_name`
- `last_name`
- `role` dans `admin | superviseur | operateur`
- `is_active`
- `is_staff`
- `created_at`
- `updated_at`

Relations :

- un `User` peut creer plusieurs `Audit`
- un `User` peut etre assigne a plusieurs `Alert`
- un `User` peut resoudre plusieurs `Alert`
- un `User` peut ajouter plusieurs `AuditCapture`

### Camera

Role : source de surveillance terrain.

Attributs principaux :

- `id`
- `name`
- `location`
- `stream_url`
- `status` dans `active | inactive | error`
- `is_active`
- `created_at`
- `updated_at`

Relations :

- une `Camera` possede plusieurs `DetectionLog`
- une `Camera` possede plusieurs `Alert`
- une `Camera` peut etre associee a plusieurs `HSERule`
- une `Camera` peut etre associee a plusieurs `Audit`

### HSERule

Role : regle metier definissant les EPI attendus sur une ou plusieurs cameras ou une zone.

Attributs principaux :

- `id`
- `name`
- `epi_type` ancien champ encore present
- `epi_criticites` liste JSON d'objets du type `{ epi, criticite }`
- `is_active`
- `description`
- `zone`

Relations :

- une `HSERule` est liee a plusieurs `Camera`

### DetectionLog

Role : trace technique de chaque appel de detection.

Attributs principaux :

- `id`
- `camera`
- `timestamp`
- `detections_json`
- `stats_json`
- `is_compliant`
- `processing_time`

Relations :

- un `DetectionLog` appartient optionnellement a une `Camera`
- un `DetectionLog` peut etre lie a une seule `Alert`

### Alert

Role : incident metier cree suite a une non-conformite detectee.

Attributs principaux :

- `id`
- `camera`
- `timestamp`
- `epi_missing` liste JSON
- `criticity` dans `faible | moyenne | elevee`
- `status` dans `nouveau | en_cours | resolu | ignore`
- `image`
- `detection_log`
- `assigned_to`
- `first_acknowledged_at`
- `resolved_by`
- `resolved_at`
- `notes`

Relations :

- une `Alert` appartient a une `Camera`
- une `Alert` peut provenir d'un `DetectionLog`
- une `Alert` peut etre assignee a un `User`
- une `Alert` peut etre resolue par un `User`
- une `Alert` peut etre liee a plusieurs `Audit` dans le temps
- une `Alert` ne doit pas avoir plusieurs audits actifs simultanes

### Audit

Role : dossier de suivi et de traitement d'une alerte ou d'un incident.

Attributs principaux :

- `id`
- `title`
- `camera`
- `alert`
- `created_by`
- `status` dans `ouvert | en_cours | clos`
- `notes`
- `created_at`
- `updated_at`

Relations :

- un `Audit` peut etre lie a une `Camera`
- un `Audit` peut etre lie a une `Alert`
- un `Audit` est cree par un `User`
- un `Audit` possede plusieurs `AuditCapture`

Regle metier importante :

- pour une meme `Alert`, un seul `Audit` actif est autorise a la fois (`ouvert` ou `en_cours`)

### AuditCapture

Role : preuve ou capture rattachee a un audit.

Attributs principaux :

- `id`
- `audit`
- `image`
- `description`
- `taken_at`
- `taken_by`

Relations :

- une `AuditCapture` appartient a un seul `Audit`
- une `AuditCapture` est ajoutee par un `User`

---

## 5. Relations metier a faire apparaitre dans le diagramme de classe

Relations recommandees avec cardinalites :

- `User 1 -> 0..* Audit` via `created_by`
- `User 1 -> 0..* Alert` via `assigned_to`
- `User 1 -> 0..* Alert` via `resolved_by`
- `User 1 -> 0..* AuditCapture` via `taken_by`
- `Camera 1 -> 0..* DetectionLog`
- `Camera 1 -> 0..* Alert`
- `Camera 1 -> 0..* Audit`
- `Camera 0..* <-> 0..* HSERule`
- `DetectionLog 1 -> 0..1 Alert`
- `Alert 1 -> 0..* Audit`
- `Audit 1 -> 0..* AuditCapture`

Le diagramme de classe doit privilegier le metier plutot que les serializers, views ou composants frontend.

---

## 6. Use case complet a representer

Le use case complet a choisir est :

`Traiter une non-conformite EPI depuis la detection jusqu'a la cloture d'audit`

### Acteurs impliques

- Systeme de detection IA
- Operateur
- Superviseur
- Administrateur

### Objectif du use case

Permettre de detecter une non-conformite EPI, creer une alerte, ouvrir un audit de suivi, ajouter des preuves, puis cloturer formellement le traitement.

### Etapes metier du use case

1. le systeme recoit une image depuis une camera
2. le systeme analyse l'image avec YOLO
3. le systeme enregistre un `DetectionLog`
4. si non-conformite, le systeme cree une `Alert`
5. l'utilisateur consulte la liste des alertes
6. l'utilisateur ouvre le detail ou le traitement de l'alerte
7. l'utilisateur ouvre un `Audit` lie a l'alerte
8. l'audit est cree avec le statut `ouvert`
9. l'alerte passe en `en_cours`
10. l'utilisateur renseigne les notes d'audit
11. l'utilisateur ajoute une ou plusieurs `AuditCapture`
12. l'utilisateur fait evoluer l'audit vers `en_cours`
13. quand le traitement est termine, l'utilisateur cloture l'audit
14. la cloture synchronise l'alerte vers `resolu`
15. un rapport PDF ou un export CSV peut etre genere

### Variantes / extensions utiles

- si l'alerte est un faux positif, elle peut etre ignoree sans audit
- si un audit actif existe deja pour la meme alerte, un nouveau ne doit pas etre cree
- un audit peut etre consulte depuis la page Alertes ou Reporting

---

## 7. Diagramme de sequence a representer

Le diagramme de sequence doit representer le meme scenario complet :

`Detection d'une non-conformite -> creation d'alerte -> ouverture d'audit -> ajout de capture -> cloture`

### Participants recommandes

- `Camera / Flux video`
- `Frontend React`
- `API Django`
- `Service Detection / YOLO`
- `Base de donnees`
- `Utilisateur metier`

### Sequence attendue

1. `Camera / Flux video` envoie une image au `Frontend React`
2. `Frontend React` appelle `POST /api/detection/detect/`
3. `API Django` appelle le service YOLO
4. YOLO retourne les detections et la conformite
5. `API Django` enregistre `DetectionLog`
6. si non-conformite, `API Django` cree `Alert`
7. `Frontend React` charge la liste des alertes
8. `Utilisateur metier` choisit `Ouvrir audit`
9. `Frontend React` appelle `POST /api/audits/`
10. `API Django` verifie qu'il n'existe pas deja d'audit actif pour la meme alerte
11. `API Django` cree `Audit`
12. `Frontend React` redirige vers le detail de l'audit
13. `Utilisateur metier` ajoute une capture
14. `Frontend React` appelle `POST /api/audits/{audit_id}/captures/`
15. `API Django` cree `AuditCapture`
16. `Utilisateur metier` change le statut de l'audit vers `en_cours`
17. `Frontend React` appelle `PATCH /api/audits/{id}/`
18. `Utilisateur metier` cloture l'audit
19. `Frontend React` appelle `PATCH /api/audits/{id}/` avec `status=clos`
20. `Frontend React` ou le backend synchronise l'alerte associee vers `resolu`
21. `Utilisateur metier` peut demander le PDF via `GET /api/audits/{id}/report/`

### Point important

Le diagramme de sequence doit bien montrer :

- l'appel de detection
- la creation conditionnelle d'alerte
- la verification anti-doublon d'audit actif
- l'ajout de capture
- la synchronisation audit/alerte a la cloture

---

## 8. Prompt final a donner a GPT

Tu peux donner ce texte a GPT :

### Prompt

En te basant sur le contexte ci-dessous, genere 3 diagrammes UML ou Mermaid coherents et realistes pour la plateforme EPI Detection :

1. un diagramme de classe centré sur les entites metier
2. un diagramme de use case complet pour le traitement d'une non-conformite EPI jusqu'a la cloture d'audit
3. un diagramme de sequence representant le meme scenario de bout en bout

Contraintes :

- rester fidele au metier et aux relations reelles du projet
- utiliser des noms explicites en francais si utile
- ne pas inventer des classes inutiles
- montrer les cardinalites dans le diagramme de classe
- montrer les acteurs dans le use case
- montrer les appels API et les changements d'etat dans le diagramme de sequence
- si possible, fournir la sortie en Mermaid

Contexte metier :

[copier ici les sections 1 a 7 de ce document]

---

## 9. Recommandation de sortie attendue de GPT

Demander a GPT de repondre avec cette structure :

1. `Diagramme de classe`
2. `Code Mermaid du diagramme de classe`
3. `Diagramme de use case`
4. `Code Mermaid du diagramme de use case`
5. `Diagramme de sequence`
6. `Code Mermaid du diagramme de sequence`

---

## 10. Remarque importante

Dans l'etat actuel du projet, la synchronisation de cloture entre `Audit` et `Alert` est portee par le frontend lors du passage de l'audit a `clos`.

Pour les diagrammes, il est acceptable de la representer comme une regle du systeme applicatif global, sans surcharger le schema avec des details d'implementation UI.