# Brief GPT - Images Architecture Technique

## Objectif

Ce fichier sert a generer avec GPT deux images techniques pour la page de conception architecturelle du projet EPI Guard.

Les deux images a produire sont :

- Figure B - Flux detection vers alerte
- Figure C - Deploiement et exploitation

Le style attendu doit etre :

- technique
- propre
- professionnel
- lisible dans un memoire, une soutenance ou une documentation d'architecture
- fond clair de preference
- palette sobre avec accents orange/ambre compatibles avec l'identite visuelle du projet
- texte en francais

Le rendu ne doit pas etre artistique. Il doit ressembler a un schema d'architecture ou a un diagramme systeme clair, structure et exploitable.


## Contexte projet

Le projet EPI Guard est une plateforme de supervision HSE pour la detection des EPI.

Architecture technique du systeme :

- frontend : React + TypeScript + Vite
- backend : Django REST Framework
- authentification : JWT via cookies HttpOnly
- moteur de detection : module detection + modele YOLO
- couche contextuelle : Gemini Vision avec file admin, quota et retry estime
- donnees : SQLite en local ou PostgreSQL en environnement distant
- stockage media : local ou AWS S3
- domaines backend : Users, Cameras, detection, alertes, audits, RegleSHE

Workflow metier principal :

1. une image ou un flux est analyse
2. la detection EPI produit un log
3. la non-conformite persistante est suivie par personne via bounding boxes et matching IoU
4. si non-conformite, une alerte est creee
5. si la non-conformite persiste, une analyse Gemini est mise en file
6. l'alerte peut etre prise en charge puis resolue
7. un audit peut etre ouvert avec captures et rapport PDF
8. les KPIs et reportings sont consolides dans le systeme


## Consignes globales de generation

Pour chaque image :

- produire une image nette, horizontale, en haute resolution
- prevoir un rendu compatible page web et rapport PDF
- utiliser des blocs, fleches, icones et etiquettes lisibles
- eviter les textes trop petits
- eviter les effets 3D inutiles
- conserver un style d'architecture logicielle moderne et sobre
- utiliser des titres courts et clairs

Format recommande :

- ratio 16:9 ou paysage large
- PNG haute qualite


## Prompt GPT - Figure B

### Nom recommande du fichier

`figure-b-flux-detection-alerte.png`

### Prompt a utiliser dans GPT

```text
Genere une image technique professionnelle en francais, style schema d'architecture logicielle et diagramme de sequence simplifie, avec fond clair, palette sobre blanc/gris clair et accents orange ambre.

Titre du schema : "Figure B - Flux detection vers alerte"

Objectif : illustrer clairement le flux fonctionnel et technique du projet EPI Guard depuis l'analyse d'une image jusqu'a la creation d'une alerte, puis l'ouverture potentielle d'un audit.

Le schema doit refleter l'etat actuel du projet, incluant le suivi de personne et la couche Gemini Vision.

Le schema doit montrer ces composants sous forme de blocs ou colonnes clairement separes :

1. Utilisateur / Operateur
2. Frontend React + TypeScript
3. API Django REST
4. Module Detection + YOLO
5. Suivi de persistance par personne
6. File d'analyse Gemini Vision
7. Base de donnees
8. Module Alertes
9. Module Audits

Le schema doit montrer les etapes suivantes avec fleches ordonnees et etiquettes courtes :

- soumission image ou requete de detection
- appel API POST /api/detection/detect/
- analyse par le module detection et le modele YOLO
- production des detections et des stats
- enregistrement d'un DetectionLog
- regroupement des non-conformites par personne detectee
- suivi temporel de la meme personne via bounding boxes / IoU
- verification de conformite EPI
- si non conforme : creation d'une alerte
- si la non-conformite persiste : creation d'une entree GeminiContextAnalysis en file d'attente
- traitement manuel admin via POST /api/detection/gemini-analyses/process-next/
- si quota Gemini temporairement depasse : conservation en file avec prochain essai estime
- enregistrement de l'image et des metadonnees d'alerte
- consultation de l'alerte par les equipes HSE
- decision d'ouvrir un audit
- creation d'un audit lie a l'alerte

Ajouter visuellement les conditions metier suivantes :

- branche "conforme" : simple journalisation
- branche "non conforme" : creation d'alerte
- branche "non-conformite persistante" : file Gemini Vision
- branche "quota temporaire Gemini" : retry / cooldown puis nouvel essai

Le schema doit aussi faire apparaitre les objets metier suivants de maniere lisible :

- DetectionLog
- NonComplianceState
- GeminiContextAnalysis
- Alert
- Audit

Contraintes graphiques :

- rendu propre, professionnel, tres lisible
- pas de style cartoon
- icones fines et modernes si necessaire
- fleches bien visibles
- hierarchie visuelle nette
- texte en francais uniquement

Ajouter un sous-titre discret en bas :
"Flux technique de traitement d'une detection EPI, du suivi par personne jusqu'a l'alerte, la file Gemini et l'audit."
```


## Prompt GPT - Figure C

### Nom recommande du fichier

`figure-c-deploiement-exploitation.png`

### Prompt a utiliser dans GPT

```text
Genere une image technique professionnelle en francais, style diagramme d'infrastructure et de deploiement logiciel, avec fond clair, palette sobre blanc/gris clair et accents orange ambre.

Titre du schema : "Figure C - Deploiement et exploitation"

Objectif : illustrer l'architecture de deploiement et les points d'exploitation technique du projet EPI Guard, en montrant a la fois le mode local/developpement et les services distants optionnels AWS.

Le schema doit refleter la version actuelle, y compris la dependance externe Gemini API et la supervision admin des analyses contextuelles.

Le schema doit presenter une vue d'infrastructure claire avec zones distinctes.

Zones a representer :

1. Poste client / navigateur utilisateur
2. Frontend React + Vite
3. Backend Django REST API
4. Base locale SQLite ou base distante PostgreSQL
5. Stockage media local ou AWS S3
6. Module detection / YOLO
7. Service Gemini API externe
8. Administration et supervision technique

Le schema doit montrer les flux et relations suivants :

- le navigateur consomme le frontend
- le frontend appelle l'API backend
- le backend utilise les cookies JWT pour l'authentification
- le backend lit et ecrit dans la base de donnees
- le backend stocke les images dans le media local ou S3
- le backend invoque le module detection / YOLO
- le backend envoie certaines analyses persistantes a Gemini API
- les administrateurs techniques interviennent sur configuration, base, stockage, comptes, file Gemini et maintenance

Le schema doit clairement faire apparaitre deux modes de fonctionnement :

- Mode local : SQLite + media local + developpement local
- Mode distant/cloud : PostgreSQL + AWS S3 + configuration par variables d'environnement

Le schema doit aussi montrer que Gemini est une dependance API externe avec quota et retry temporaire, sans etre hebergee dans l'application.

Ajouter une zone ou bandeau "Exploitation technique" avec les points suivants sous forme de petits blocs :

- administration des comptes et roles
- supervision des cameras
- maintenance corrective
- evolution applicative
- verification des migrations
- configuration DB et S3
- supervision du quota Gemini
- verification des retries et cooldowns Gemini

Le rendu doit ressembler a un vrai schema de deploiement de systeme informatique :

- blocs d'infrastructure
- fleches de communication
- etiquettes techniques courtes
- style institutionnel, clair, sobre, academique

Le texte doit etre entierement en francais.

Ajouter un sous-titre discret en bas :
"Vue de deploiement et d'exploitation technique du systeme EPI Guard avec YOLO, Gemini API et modes local ou distant."
```


## Variante si GPT demande un style plus precis

Tu peux ajouter cette phrase a la fin de chaque prompt :

```text
Style visuel attendu : diagramme informatique premium, propre, moderne, institutionnel, avec mise en page claire, alignements rigoureux, icones minimalistes et lisibilite optimale pour documentation technique et soutenance academique.
```


## Consigne apres generation

Une fois les images generees, les enregistrer idealement sous :

- `frontend/public/figure-b-flux-detection-alerte.png`
- `frontend/public/figure-c-deploiement-exploitation.png`

Puis les inserer dans la page frontend de conception architecturelle a la place des zones reservees pour les figures B et C.