# Cahier De Contexte Academique PFE Pour La Generation Des Diagrammes

## 1. Intitule du projet

**Plateforme intelligente de detection du port des equipements de protection individuelle (EPI), de gestion des alertes et de suivi des audits HSE**

---

## 2. Contexte academique du projet

Ce projet de fin d'etudes s'inscrit dans le domaine de la securite industrielle assistee par l'intelligence artificielle.

L'objectif principal de la plateforme est de renforcer la prevention des risques sur site en automatisant la detection des non-conformites relatives au port des equipements de protection individuelle, puis en assurant leur prise en charge operationnelle a travers un systeme structure d'alertes et d'audits.

La solution proposee ne se limite pas a une detection visuelle. Elle introduit egalement une logique metier complete permettant de :

- surveiller plusieurs cameras
- analyser des images ou flux terrain
- identifier les EPI manquants
- generer des alertes metier
- suivre le traitement des incidents
- ouvrir et cloturer des audits
- produire une tracabilite exploitable sous forme de captures, statistiques et rapports

Ainsi, le projet combine vision par ordinateur, architecture web et modelisation metier autour d'un besoin concret de supervision HSE.

---

## 3. Problematique

Dans les environnements industriels, le non-respect du port des EPI constitue une source majeure de risque humain et organisationnel.

Les approches traditionnelles de controle reposent souvent sur des inspections humaines ponctuelles, avec plusieurs limites :

- couverture partielle du terrain
- manque de continuite dans la surveillance
- difficulte de centraliser les incidents
- absence de suivi structure apres detection
- faible tracabilite des actions correctives

La problematique du projet peut donc etre formulee ainsi :

**Comment concevoir une plateforme intelligente capable de detecter automatiquement les non-conformites EPI, de centraliser les incidents sous forme d'alertes et d'assurer un suivi metier complet jusqu'a la cloture d'un audit ?**

---

## 4. Objectifs du projet

### Objectif general

Concevoir une plateforme web intelligente permettant la detection automatique des non-conformites EPI et leur traitement metier a travers un workflow d'alerte et d'audit.

### Objectifs specifiques

- detecter automatiquement les EPI manquants a partir d'images ou flux video
- associer les non-conformites detectees a une camera et a un contexte terrain
- generer des alertes metier en cas de non-conformite
- gerer les statuts des alertes selon leur prise en charge
- ouvrir des audits relies aux alertes necessitant un suivi structure
- suivre l'audit jusqu'a sa cloture avec notes et captures de preuve
- offrir une visualisation synthétique via tableaux de bord et reporting
- garantir une separation des roles entre operateur, superviseur et administrateur

---

## 5. Presentation generale de la solution

La plateforme repose sur une architecture client-serveur separee en deux sous-systemes principaux.

### Frontend

Le frontend est developpe avec **React**, **TypeScript** et **Vite**.

Il fournit les interfaces suivantes :

- authentification utilisateur
- tableau de bord
- supervision des cameras
- consultation et traitement des alertes
- ouverture et suivi des audits
- gestion des regles HSE
- reporting statistique

### Backend

Le backend est developpe avec **Django** et **Django REST Framework**.

Il assure :

- l'authentification et la gestion des utilisateurs
- l'exposition des API REST
- la logique metier des alertes et des audits
- l'integration du moteur YOLO
- la generation des rapports PDF et exports CSV

### Base de donnees

Le projet utilise actuellement **SQLite** comme base locale de developpement.

### Moteur IA

Le systeme de detection utilise un modele **YOLO** afin d'identifier la presence ou l'absence des equipements de protection sur les images soumises.

---

## 6. Architecture fonctionnelle de la plateforme

Le systeme met en relation plusieurs blocs metier complementaires :

1. **Gestion des utilisateurs**
2. **Gestion des cameras**
3. **Gestion des regles HSE**
4. **Detection IA**
5. **Gestion des alertes**
6. **Gestion des audits**
7. **Reporting et export**

### 6.1 Gestion des utilisateurs

Le systeme repose sur un modele utilisateur personnalise base sur l'email.

Trois profils sont consideres :

- `Administrateur`
- `Superviseur`
- `Operateur`

Chaque role dispose d'un niveau d'acces adapte aux responsabilites metier.

### 6.2 Gestion des cameras

Chaque camera constitue une source potentielle de surveillance.

Une camera possede :

- un nom
- un emplacement
- un flux video
- un etat de disponibilite

Les cameras peuvent etre associees a des regles HSE et produire des logs de detection ainsi que des alertes.

### 6.3 Gestion des regles HSE

Les regles HSE definissent les EPI attendus selon une zone ou une camera donnee.

Elles permettent d'interpreter les detections brutes en termes de conformite ou de non-conformite metier.

### 6.4 Detection IA

Le moteur YOLO analyse les images recues, produit les detections et permet de calculer un resultat de conformite.

Chaque execution de detection genere un `DetectionLog` contenant :

- les detections brutes
- les statistiques calculees
- le temps de traitement
- l'indicateur de conformite

### 6.5 Gestion des alertes

Lorsqu'une non-conformite est confirmee, une alerte peut etre creee.

L'alerte constitue l'entite metier centrale de signalement d'incident.

Elle contient notamment :

- la camera concernee
- la date de detection
- les EPI manquants
- le niveau de criticite
- le statut de traitement
- l'image de preuve
- les notes de suivi

Les statuts d'alerte sont :

- `nouveau`
- `en_cours`
- `resolu`
- `ignore`

### 6.6 Gestion des audits

L'audit sert a formaliser le suivi d'une alerte quand un simple traitement instantane n'est pas suffisant.

Il permet de :

- structurer l'investigation
- ajouter des notes de suivi
- attacher des captures de preuve
- suivre l'evolution du traitement
- produire un rapport exportable

Les statuts d'audit sont :

- `ouvert`
- `en_cours`
- `clos`

Une regle metier importante est appliquee :

**une meme alerte ne doit pas posseder plusieurs audits actifs simultanement**

### 6.7 Reporting et export

Le systeme fournit des indicateurs statistiques permettant d'analyser :

- la conformite globale
- les incidents par type
- les incidents par camera
- les alertes critiques
- les audits ouverts
- certains KPI de pilotage comme le MTTA et le MTTR

Des exports CSV et PDF sont egalement disponibles.

---

## 7. Entites metier a modeliser dans le diagramme de classe

Le diagramme de classe doit se concentrer sur les entites suivantes.

### User

Attributs essentiels :

- id
- email
- first_name
- last_name
- role
- is_active
- is_staff
- created_at
- updated_at

### Camera

Attributs essentiels :

- id
- name
- location
- stream_url
- status
- is_active

### HSERule

Attributs essentiels :

- id
- name
- epi_type
- epi_criticites
- is_active
- description
- zone

### DetectionLog

Attributs essentiels :

- id
- camera
- timestamp
- detections_json
- stats_json
- is_compliant
- processing_time

### Alert

Attributs essentiels :

- id
- camera
- timestamp
- epi_missing
- criticity
- status
- image
- detection_log
- assigned_to
- resolved_by
- resolved_at
- notes

### Audit

Attributs essentiels :

- id
- title
- camera
- alert
- created_by
- status
- notes
- created_at
- updated_at

### AuditCapture

Attributs essentiels :

- id
- audit
- image
- description
- taken_at
- taken_by

---

## 8. Relations a representer dans le diagramme de classe

Les relations suivantes doivent apparaitre clairement :

- un `User` peut creer plusieurs `Audit`
- un `User` peut etre assigne a plusieurs `Alert`
- un `User` peut resoudre plusieurs `Alert`
- un `User` peut ajouter plusieurs `AuditCapture`
- une `Camera` peut posseder plusieurs `DetectionLog`
- une `Camera` peut posseder plusieurs `Alert`
- une `Camera` peut etre associee a plusieurs `Audit`
- une `Camera` peut etre associee a plusieurs `HSERule`
- un `DetectionLog` peut donner lieu a une `Alert`
- une `Alert` peut etre liee a plusieurs `Audit` dans le temps
- un `Audit` peut contenir plusieurs `AuditCapture`

Il est recommande d'afficher les cardinalites.

---

## 9. Use case complet a representer

Le use case principal a modeliser est :

**Traiter une non-conformite EPI depuis la detection jusqu'a la cloture d'un audit**

### Acteurs du use case

- Systeme de detection IA
- Operateur
- Superviseur
- Administrateur

### Description du scenario principal

1. le systeme recoit une image issue d'une camera
2. le moteur YOLO analyse l'image
3. le backend enregistre un log de detection
4. si une non-conformite est constatee, une alerte est creee
5. l'utilisateur consulte les alertes generees
6. si l'incident necessite un suivi, il ouvre un audit
7. l'audit est cree et lie a l'alerte
8. l'utilisateur met a jour les notes et ajoute des captures
9. l'audit evolue jusqu'au statut `clos`
10. l'alerte associee est consideree comme `resolu`

### Extensions possibles

- ignorer l'alerte en cas de faux positif
- interdire la creation d'un audit si un audit actif existe deja
- exporter un rapport PDF de l'audit cloture

---

## 10. Sequence principale a representer

Le diagramme de sequence doit montrer les interactions suivantes :

1. capture d'image
2. appel API de detection
3. execution YOLO
4. enregistrement du `DetectionLog`
5. creation conditionnelle de l'`Alert`
6. consultation de l'alerte par l'utilisateur
7. creation de l'`Audit`
8. verification anti-doublon d'audit actif
9. ajout d'une `AuditCapture`
10. cloture de l'`Audit`
11. synchronisation de l'`Alert` vers `resolu`

Participants recommandes :

- Camera
- Frontend React
- API Django
- Service YOLO
- Base de donnees
- Utilisateur

---

## 11. Consignes a donner a l'outil de generation de diagrammes

En te basant sur ce contexte, genere les diagrammes suivants avec un niveau de formalisation academique adapte a un rapport de PFE :

1. un diagramme de classe UML
2. un diagramme de use case UML
3. un diagramme de sequence UML

Contraintes :

- rester fidele au fonctionnement reel du systeme
- privilegier les entites metier et non les details techniques secondaires
- afficher les cardinalites dans le diagramme de classe
- faire apparaitre clairement les acteurs dans le use case
- montrer les appels systeme et les changements d'etat dans le diagramme de sequence
- si possible, fournir une version Mermaid ou PlantUML

---

## 12. Sortie attendue

La reponse ideale doit contenir :

1. un titre pour chaque diagramme
2. une courte justification academique de ce que represente chaque diagramme
3. le code Mermaid ou PlantUML correspondant
4. une breve explication de lecture pour chaque diagramme