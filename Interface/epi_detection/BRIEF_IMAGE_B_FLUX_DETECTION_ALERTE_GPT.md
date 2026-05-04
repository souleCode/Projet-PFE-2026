# Brief GPT - Figure B - Flux detection vers alerte

## Objectif

Ce fichier sert a generer avec GPT une image technique pour la page de conception architecturelle du projet EPI Guard.

Image a produire :

- Figure B - Flux detection vers alerte

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
- couche contextuelle : Gemini Vision avec file d'attente admin et reprise apres cooldown
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

Pour cette image :

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


## Nom recommande du fichier

`figure-b-flux-detection-alerte.png`


## Prompt a utiliser dans GPT

```text
Genere une image technique professionnelle en francais, style schema d'architecture logicielle et diagramme de sequence simplifie, avec fond clair, palette sobre blanc/gris clair et accents orange ambre.

Titre du schema : "Figure B - Flux detection vers alerte"

Objectif : illustrer clairement le flux fonctionnel et technique du projet EPI Guard depuis l'analyse d'une image jusqu'a la creation d'une alerte, puis l'ouverture potentielle d'un audit.

Le schema doit refleter l'architecture actuelle, incluant le suivi de personne et la couche d'analyse contextuelle Gemini.

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


## Variante si GPT demande un style plus precis

Tu peux ajouter cette phrase a la fin du prompt :

```text
Style visuel attendu : diagramme informatique premium, propre, moderne, institutionnel, avec mise en page claire, alignements rigoureux, icones minimalistes et lisibilite optimale pour documentation technique et soutenance academique.
```


## Consigne apres generation

Une fois l'image generee, l'enregistrer idealement sous :

- `frontend/public/figure-b-flux-detection-alerte.png`

Puis l'inserer dans la page frontend de conception architecturelle a la place de la zone reservee pour la figure B.
