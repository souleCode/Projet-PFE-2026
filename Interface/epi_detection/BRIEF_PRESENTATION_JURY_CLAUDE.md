# Brief Pour Claude - Generation D'Une Presentation PFE Devant Jury

## 1. Role attendu de Claude

Agis comme un assistant expert en redaction academique et en structuration de presentations de soutenance de projet de fin d'etudes.

Tu dois generer une presentation claire, professionnelle, credible et defendable devant un jury universitaire pour un projet de type PFE en informatique.

Le ton doit etre :

- academique
- technique
- structuré
- sobre et professionnel
- orienté soutenance devant jury

La presentation ne doit pas ressembler a un discours marketing.

---

## 2. Sujet du PFE

**Conception et developpement d'une plateforme intelligente de detection du port des EPI, de gestion des alertes et de suivi des audits HSE**

---

## 3. Resume du projet

Le projet consiste a concevoir une plateforme web intelligente permettant de detecter automatiquement les non-conformites liees au port des equipements de protection individuelle a partir d'images ou de flux video.

La solution ne se limite pas a la detection automatique. Elle integre egalement un workflow metier complet de gestion d'incidents :

- detection IA des EPI manquants
- creation d'alertes metier
- traitement des alertes
- ouverture d'audits de suivi
- ajout de captures et de notes
- cloture du traitement avec tracabilite

Le projet combine donc :

- intelligence artificielle appliquee a la vision par ordinateur
- architecture web frontend/backend
- modelisation metier HSE
- reporting et suivi operationnel

---

## 4. Technologies utilisees

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Recharts

### Backend

- Django
- Django REST Framework
- JWT en cookies HttpOnly
- ReportLab pour les rapports PDF

### Intelligence artificielle

- YOLO pour la detection des EPI

### Base de donnees

- SQLite en environnement local actuel

---

## 5. Modules fonctionnels de la plateforme

Les modules principaux de la plateforme sont :

1. authentification et gestion des utilisateurs
2. gestion des cameras
3. gestion des regles HSE
4. detection automatique des EPI
5. gestion des alertes
6. gestion des audits
7. reporting et export

---

## 6. Workflow metier principal

Le workflow principal de la plateforme est le suivant :

1. une image est capturee depuis une camera ou un flux video
2. le backend lance le modele YOLO
3. un log de detection est enregistre
4. si une non-conformite EPI est detectee, une alerte est creee
5. l'utilisateur consulte l'alerte
6. si necessaire, il ouvre un audit de suivi
7. il ajoute des notes et des captures
8. il fait evoluer l'audit jusqu'a sa cloture
9. l'alerte associee passe a l'etat resolu

---

## 7. Entites metier importantes

Les entites metier principales du systeme sont :

- `User`
- `Camera`
- `HSERule`
- `DetectionLog`
- `Alert`
- `Audit`
- `AuditCapture`

Relations importantes :

- une camera produit des logs de detection et des alertes
- une alerte peut donner lieu a un audit
- un audit peut contenir plusieurs captures
- un utilisateur peut creer des audits et traiter des alertes

---

## 8. Avancement reel du projet

Fonctionnalites deja implementees dans la plateforme :

- authentification par utilisateur et roles
- gestion des cameras
- detection de non-conformites EPI
- creation et traitement d'alertes
- gestion des regles HSE
- reporting statistique
- ouverture d'audits depuis les alertes
- detail d'audit avec gestion de statut
- ajout de captures dans l'audit
- generation PDF et export CSV des audits
- prevention de doublons d'audits actifs pour une meme alerte

---

## 9. Valeur ajoutee du projet

La valeur ajoutee de la plateforme reside dans la combinaison de deux dimensions souvent traitees separement :

1. la detection intelligente des non-conformites EPI par IA
2. la gestion metier structuree du traitement de l'incident

Le projet ne fournit donc pas seulement une detection automatique, mais un veritable systeme decisionnel et de suivi HSE.

---

## 10. Difficultes et enjeux techniques a mentionner

La presentation doit faire apparaitre quelques enjeux techniques pertinents pour un jury, par exemple :

- integration entre moteur IA et architecture web
- transformation d'une detection technique en alerte metier exploitable
- gestion des roles et droits d'acces
- synchronisation entre alertes et audits
- prevention des doublons d'audits actifs
- generation de rapports de suivi

---

## 11. Structure attendue de la presentation

Genere une presentation de soutenance en francais avec une structure academique classique.

La presentation doit contenir environ **12 a 15 slides**.

Structure recommandee :

1. page de garde
2. contexte general et motivation
3. problematique
4. objectifs du projet
5. analyse de l'existant ou limites des approches classiques
6. solution proposee
7. architecture generale de la plateforme
8. description des modules fonctionnels
9. workflow metier principal
10. modelisation ou diagrammes importants
11. demonstration des fonctionnalites principales
12. resultats obtenus et apports du projet
13. limites actuelles
14. perspectives d'amelioration
15. conclusion

---

## 12. Ce que Claude doit produire

Je veux que tu produises les elements suivants :

1. un **plan complet de presentation slide par slide**
2. pour chaque slide :
   - le **titre**
   - l'**objectif de la slide**
   - les **points cles a afficher**
   - une **proposition de texte oral** a dire devant le jury
3. une **version concise et defendable** du discours global
4. des **suggestions de visuels** a mettre dans certaines slides

---

## 13. Contraintes importantes

- ne pas produire une presentation trop chargee
- utiliser un style adapte a un jury universitaire
- rester coherent avec un projet de PFE en informatique appliquee a la securite industrielle
- ne pas inventer de fonctionnalites qui n'existent pas
- valoriser le caractere intelligent, metier et traceable de la solution
- garder une logique de defense orale claire : probleme -> solution -> architecture -> demonstration -> bilan

---

## 14. Format de sortie attendu

Claude doit repondre avec cette structure :

### A. Plan global de la soutenance

### B. Presentation detaillee slide par slide

Pour chaque slide :

- Titre
- Objectif
- Contenu a afficher
- Texte oral suggere
- Visuel recommande

### C. Conseils de soutenance

Ajouter enfin :

- conseils pour parler devant le jury
- erreurs a eviter
- questions probables du jury avec pistes de reponse

---

## 15. Prompt final a donner a Claude

En te basant sur le contexte ci-dessous, genere une presentation de soutenance PFE complete, academique et defendable devant un jury universitaire, en francais.

Je veux :

- un plan global de 12 a 15 slides
- le detail de chaque slide
- un texte oral suggere
- des suggestions de visuels
- des conseils de soutenance
- quelques questions probables du jury avec elements de reponse

Contexte du projet :

[copier ici les sections 2 a 10 de ce document]