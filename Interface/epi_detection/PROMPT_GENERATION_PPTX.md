# Prompt — Génération d'une Présentation PPTX de Soutenance PFE

## Rôle attendu

Tu es un expert en développement Python et en design de présentations académiques professionnelles.
Tu dois générer un **script Python complet et exécutable** utilisant la bibliothèque `python-pptx` pour créer une présentation de soutenance PFE de **15 slides** (présentation solo, 15 minutes).

Le script doit produire un fichier `soutenance_EPI_Detection.pptx` de haute qualité, prêt à être ouvert dans PowerPoint ou LibreOffice Impress.

---

## Contexte du projet à présenter

**Titre du projet :**
> Conception et développement d'une plateforme intelligente de détection du port des EPI, de gestion des alertes et de suivi des audits HSE

**Ce que le projet fait :**
La plateforme détecte automatiquement les non-conformités liées aux équipements de protection individuelle (casque, gilet, gants, lunettes) à partir d'images ou flux vidéo, via un modèle IA YOLOv8. Elle génère ensuite un workflow métier HSE complet : création d'alertes, traitement, ouverture d'audits avec captures de preuves, et génération de rapports PDF.

**Stack technique :**
- **Frontend** : React 18 + TypeScript + Vite + Tailwind CSS + Recharts
- **Backend** : Django 4.2 + Django REST Framework + JWT HttpOnly cookies
- **IA** : YOLOv8 via bibliothèque `ultralytics`
- **Base de données** : PostgreSQL (prod) / SQLite (local)
- **Déploiement** : AWS EC2 (backend via CodeBuild/CodeDeploy) + Cloudflare (frontend CDN)
- **Stockage** : AWS S3 pour les images d'alertes
- **PDF** : ReportLab pour les rapports d'audit

**Modules fonctionnels :**
1. Authentification par rôles (Admin / Superviseur / Opérateur) — JWT en cookies HttpOnly
2. Gestion des caméras (nom, localisation, statut actif/inactif/erreur)
3. Règles HSE — définition des EPI attendus par caméra/zone avec niveaux de criticité
4. Détection IA — analyse image via YOLO → log de détection → conformité calculée
5. Gestion des alertes — création automatique, cycle de vie (nouveau → en cours → résolu/ignoré)
6. Gestion des audits — suivi structuré, captures de preuves, rapport PDF, export CSV
7. Reporting & KPIs — taux de conformité, MTTA (temps moyen avant prise en charge), MTTR

**Workflow métier central :**
```
Capture image → POST /api/detection/detect/ → YOLO → DetectionLog
→ [si non-conforme] → Alerte créée automatiquement
→ Utilisateur consulte → Ouvre Audit → Ajoute captures/notes
→ Audit clôturé → Alerte → Résolu → Export PDF
```

**Valeur ajoutée du projet :**
Contrairement aux systèmes qui ne font que détecter, cette plateforme transforme une détection brute IA en incident métier tracé et géré jusqu'à sa résolution, avec traçabilité complète.

**Problématique :**
> Comment concevoir une plateforme intelligente capable de détecter automatiquement les non-conformités EPI, de centraliser les incidents sous forme d'alertes et d'assurer un suivi métier complet jusqu'à la clôture d'un audit ?

**Informations à remplacer dans le script (placeholders) :**
- `[VOTRE_NOM]` → ton nom complet
- `[NOM_ECOLE]` → nom de l'école / université
- `[ENCADRANT]` → nom de l'encadrant académique
- `[ANNEE_UNIVERSITAIRE]` → ex. 2025–2026
- `[FILIERE]` → ex. "Génie Logiciel" / "Informatique"

---

## Système de design

### Palette de couleurs

```python
# Couleurs principales (format RGB pour python-pptx)
NAVY       = (15, 23, 42)      # #0F172A — fond titres / header bar
NAVY_CARD  = (30, 41, 59)      # #1E293B — cartes sur fond sombre
ORANGE     = (249, 115, 22)    # #F97316 — accent HSE principal
BLUE_ELEC  = (59, 130, 246)    # #3B82F6 — accent secondaire
WHITE      = (255, 255, 255)   # #FFFFFF
LIGHT_BG   = (248, 250, 252)   # #F8FAFC — fond des slides contenu
TEXT_DARK  = (15, 23, 42)      # #0F172A — texte principal sur fond clair
TEXT_MUTED = (100, 116, 139)   # #64748B — texte secondaire
GREEN_OK   = (16, 185, 129)    # #10B981 — indicateur positif
RED_KO     = (239, 68, 68)     # #EF4444 — indicateur négatif
BORDER     = (226, 232, 240)   # #E2E8F0 — bordures légères
```

### Typographie

- **Titre principal** : Calibri Bold, 36–44pt, blanc (sur fond sombre) ou NAVY (sur fond clair)
- **Titre de slide** : Calibri Bold, 28–32pt
- **Sous-titre / label** : Calibri Bold, 14–16pt, ORANGE
- **Corps de texte** : Calibri, 16–18pt, TEXT_DARK ou WHITE
- **Caption / note** : Calibri, 11–12pt, TEXT_MUTED
- **Numéro de slide** : Calibri, 10pt, TEXT_MUTED, centré en bas

### Règles de mise en page

- Format des slides : 33.87 cm × 19.05 cm (16:9 — standard PowerPoint widescreen)
- **Aucun bloc de texte plein** — uniquement listes à puces courtes (max 6 bullets) ou schémas
- Chaque bullet : 3 à 7 mots maximum, pas de phrases complètes
- **Utiliser des formes rectangulaires arrondies** (corner_radius = 100000 EMU) pour les cartes/boîtes d'information
- **Lignes de séparation** : fine barre orange ou bleue (hauteur 0.05 cm) sous les titres

### Types de layouts utilisés

| Slide | Type de layout |
|---|---|
| Titre + fin | Fond navy complet, titre centré, large |
| Plan | Fond clair, 2 colonnes de numéros |
| Contenu standard | Header barre navy en haut, fond clair, bullets |
| Schéma / workflow | Formes et flèches python-pptx, pas d'image |
| Statistiques | Cartes colorées avec chiffres clés, fond clair |
| Architecture | Blocs texte colorés reliés par des lignes |

---

## Structure exacte des 15 slides

### Slide 1 — Titre
**Layout** : Fond NAVY complet
**Contenu :**
- Barre orange horizontale en haut (pleine largeur, 1 cm de hauteur)
- Logo ou icône HSE optionnel (carré orange 2×2 cm, lettres "EPI" en blanc)
- Titre principal (centré, ligne 1) : `Plateforme Intelligente de Détection EPI`
- Titre principal (centré, ligne 2) : `Gestion des Alertes & Audits HSE`
- Séparateur orange horizontal (20 cm centré, 3pt)
- Sous-titre ligne 1 : `Projet de Fin d'Études — [FILIERE]`
- Sous-titre ligne 2 : `[VOTRE_NOM]`
- Sous-titre ligne 3 : `[NOM_ECOLE] | [ANNEE_UNIVERSITAIRE]`
- En bas à droite : `Encadrant : [ENCADRANT]`
- Barre orange en bas (pleine largeur, 0.5 cm)

### Slide 2 — Introduction : Contexte & Motivation
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Contexte & Motivation`
**Contenu — 2 colonnes :**
- **Colonne gauche** (titre en ORANGE : "Problème identifié") :
  - Inspections EPI = ponctuelles & humaines
  - Couverture terrain incomplète
  - Zéro tracabilité des incidents
  - Aucun suivi structuré post-détection
  - Risque humain sous-estimé
- **Colonne droite** (boîte NAVY arrondie, texte blanc, chiffre mis en avant) :
  - Grand chiffre mis en avant : `85 000` avec légende "accidents du travail/an en France liés aux EPI"
  - Deuxième stat : `60%` avec légende "auraient pu être évités avec un contrôle continu"
  - Source discrète en bas

> Note : Si tu n'as pas de chiffres réels, marque `[CHIFFRE_À_COMPLÉTER]` comme placeholder.

### Slide 3 — Plan de Présentation
**Layout** : Fond NAVY complet
**Titre** : `Plan de Présentation` (blanc)
**Contenu — 2 colonnes, 4 items par colonne, chaque item = boîte arrondie NAVY_CARD avec numéro orange + texte blanc :**
- `01` Problématique & Objectifs
- `02` Solution & Architecture
- `03` Modules Fonctionnels
- `04` Moteur IA — Détection YOLO
- `05` Workflow Métier
- `06` Déploiement Cloud
- `07` Résultats & Démo
- `08` Bilan & Perspectives

### Slide 4 — Problématique & Cahier des Charges
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Problématique & Objectifs`
**Contenu :**
- **Zone centrale** (grande boîte arrondie, bordure ORANGE, fond blanc) :
  - Texte en italique NAVY : *"Comment détecter automatiquement les non-conformités EPI, centraliser les incidents et assurer un suivi métier jusqu'à la clôture d'un audit ?"*
- **Titre section** en ORANGE : "Objectifs"
- **Liste d'objectifs en 2 colonnes**, chaque item avec carré orange comme puce :
  - Détection automatique EPI par IA
  - Génération d'alertes métier
  - Workflow alerte → audit → résolution
  - Traçabilité complète des incidents
  - Gestion des rôles et accès
  - KPIs & reporting opérationnel

### Slide 5 — Architecture Générale
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Architecture de la Solution`
**Contenu — Diagramme en 3 couches avec formes python-pptx :**

Créer un schéma en couches horizontales avec des rectangles arrondis :

```
┌─────────────────────────────────────────────────────────────┐
│  COUCHE FRONTEND  (fond bleu clair #EFF6FF)                 │
│  React · TypeScript · Vite · Tailwind · Recharts            │
└───────────────────────────┬─────────────────────────────────┘
                   API REST (HTTPS + JWT Cookies)
                   flèche double bidirectionnelle orange
┌───────────────────────────┴─────────────────────────────────┐
│  COUCHE BACKEND  (fond NAVY_CARD)                           │
│  Django 4.2 · DRF · YOLOv8 · ReportLab · JWT               │
└────────┬──────────────────────────────┬──────────────────────┘
         │                              │
┌────────┴───────────┐    ┌─────────────┴───────────────────┐
│  BASE DE DONNÉES   │    │  STOCKAGE & DÉPLOIEMENT         │
│  PostgreSQL RDS    │    │  AWS S3 · EC2 · Cloudflare CDN  │
└────────────────────┘    └─────────────────────────────────┘
```

- Chaque couche = rectangle arrondi avec couleur de fond distincte, titre en gras
- Flèches créées avec `add_connector` ou des formes rectangulaires fines
- Légende en bas : 3 petits badges colorés (Frontend / Backend / Cloud)

### Slide 6 — Module IA — Détection YOLO
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Moteur IA — Détection YOLOv8`
**Contenu — Pipeline horizontal + liste à droite :**

**Gauche (60%) — Pipeline en formes :**
```
[Image Entrée] ──▶ [YOLOv8 best.pt] ──▶ [Résultat] ──▶ [DetectionLog]
                                              │
                                    [Conforme ✓] ou [Non-conforme ✗]
```
- Chaque étape = rectangle arrondi NAVY_CARD (fond sombre, texte blanc)
- Flèches ORANGE entre les étapes
- Badge vert "✓ Conforme" et rouge "✗ Non-conforme" en formes colorées

**Droite (40%) — Carte NAVY_CARD arrondie :**
- Titre : `EPI détectés` (ORANGE)
- Liste avec puces colorées :
  - 🟠 Casque de chantier
  - 🟠 Gilet de sécurité
  - 🟠 Gants de protection
  - 🟠 Lunettes de sécurité
- Précision modèle : `[XX%]` (placeholder)
- Modèle : `best.pt` — entraîné sur dataset custom

### Slide 7 — Règles HSE & Conformité
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Règles HSE — Conformité par Zone`
**Contenu — 2 colonnes :**
- **Gauche** : Schéma de la liaison Caméra → Règle HSE → EPI attendus
  - Boîte "Caméra Zone A" → flèche → Boîte "Règle HSE" → flèche → liste EPI (casque critique, gilet critique, gants moyen)
  - Indication de criticité avec couleurs : rouge (critique), orange (moyen), jaune (faible)
- **Droite** : 3 badges/cartes pour les 3 rôles utilisateurs
  - ORANGE : Admin — gestion complète
  - BLUE_ELEC : Superviseur — traitement alertes
  - Gris : Opérateur — consultation

### Slide 8 — Workflow Métier Central
**Layout** : Fond NAVY complet (slide de rupture visuelle)
**Titre** : `Workflow Métier` (blanc, centré en haut)
**Contenu — Diagramme de flux horizontal en 6 étapes :**

```
[Capture Image] ──▶ [Détection YOLO] ──▶ [Alerte Créée] ──▶ [Audit Ouvert] ──▶ [Captures/Notes] ──▶ [Clôture & PDF]
```

- Chaque étape = hexagone ou cercle avec numéro (1 à 6) en ORANGE, texte blanc dessous
- Fond sombre (NAVY), flèches blanches/orange
- Sous chaque étape : sous-titre court en TEXT_MUTED clair
  - POST /detect/ | YOLOv8 | Auto-générée | Audit lié | Preuves | Rapport PDF
- En bas : 2 badges résultat final : `✓ Incident résolu` (vert) et `📄 Rapport PDF exporté` (bleu)

### Slide 9 — Modules Fonctionnels
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Modules Fonctionnels`
**Contenu — Grille 3×2 de cartes arrondies (style dashboard) :**

Créer 6 cartes rectangulaires arrondies (fond blanc, bordure legère BORDER, ombre légère simulée) :

| Carte | Icône (forme géométrique colorée) | Titre | Sous-titre |
|---|---|---|---|
| 1 | Carré ORANGE | Détection IA | YOLOv8 · Temps réel |
| 2 | Carré BLUE_ELEC | Alertes | Cycle de vie complet |
| 3 | Carré GREEN_OK | Audits | Captures & Rapports PDF |
| 4 | Carré NAVY | Caméras | Multi-zones · Statut live |
| 5 | Carré (violet #8B5CF6) | Règles HSE | EPI par zone/criticité |
| 6 | Carré RED_KO | Reporting | KPIs · MTTA · MTTR |

Chaque carte : 6 cm × 3.5 cm, titre en gras NAVY, sous-titre en TEXT_MUTED

### Slide 10 — Cycle de Vie d'une Alerte
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Cycle de Vie d'une Alerte`
**Contenu — Diagramme d'états en formes :**

**Partie gauche (60%) — Diagramme d'états :**
```
        [NOUVEAU]
           │  orange
           ▼
       [EN COURS] ──────▶ [IGNORÉ]
           │  bleu                (gris)
           ▼
       [RÉSOLU]
        (vert)
```
- Chaque état = rectangle arrondi coloré (ORANGE / BLUE_ELEC / GREEN_OK / Gris)
- Flèches avec libellés courts : "Prise en charge" / "Résolu" / "Faux positif"

**Partie droite (40%) — Carte NAVY_CARD :**
- Titre ORANGE : "Données tracées"
- Bullets blancs :
  - `first_acknowledged_at` — 1ère prise en charge
  - `resolved_by` — Utilisateur résolvant
  - `resolved_at` — Date de résolution
  - `epi_missing` — EPI manquants listés
  - `criticity` — faible / moyenne / élevée

### Slide 11 — Déploiement Cloud
**Layout** : Fond NAVY complet (slide de rupture)
**Titre** : `Infrastructure de Déploiement` (blanc)
**Contenu — Schéma en 2 flux parallèles :**

**Flux 1 (gauche) — Frontend :**
```
[Code React] ──▶ [Build Vite] ──▶ [Cloudflare CDN] ──▶ [Utilisateur]
                                        HTTPS + WAF
```
Blocs : fond BLUE_ELEC sombre, texte blanc, flèches blanches

**Flux 2 (droite) — Backend :**
```
[Git Push] ──▶ [CodeBuild] ──▶ [CodeDeploy] ──▶ [EC2 Django]
                  Build             Artefact        Gunicorn + Nginx
```
Blocs : fond ORANGE sombre, texte blanc, flèches blanches

**Bas — 3 badges AWS :**
- AWS S3 (images alertes) | PostgreSQL RDS | CloudWatch (logs)

### Slide 12 — Démonstration & Résultats
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Fonctionnalités Clés — Aperçu`
**Contenu — 2 colonnes :**

**Colonne gauche (titre ORANGE : "Implémenté")** — liste avec coche verte :
- ✓ Auth JWT sécurisée (rôles 3 niveaux)
- ✓ Détection EPI temps réel (webcam)
- ✓ Alertes automatiques + cycle de vie
- ✓ Règles HSE par caméra
- ✓ Audits avec captures de preuve
- ✓ Export PDF et CSV
- ✓ Dashboard KPIs
- ✓ Déploiement AWS + Cloudflare

**Colonne droite — Encadré NAVY_CARD (chiffres clés) :**
- Grand titre ORANGE : "Ce qui a été livré"
- `7` modules fonctionnels
- `25+` endpoints API REST
- `3` rôles avec permissions granulaires
- `1` modèle YOLO personnalisé
- `2` exports (PDF ReportLab + CSV)

### Slide 13 — Métriques & KPIs
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Indicateurs & KPIs`
**Contenu — 2 lignes de 3 cartes métriques chacune :**

Créer 6 cartes "métrique" (style stats card) avec : grande valeur en ORANGE ou BLUE_ELEC, label dessous en TEXT_MUTED

| Rang | Valeur | Label |
|---|---|---|
| 1 | MTTA | Temps moyen avant prise en charge |
| 2 | MTTR | Temps moyen avant résolution |
| 3 | Taux de conformité | Par caméra et par zone |
| 4 | Récurrence par zone | Zones à risque identifiées |
| 5 | 3 niveaux | Criticité : faible / moyenne / élevée |
| 6 | Audit PDF | Rapport généré en 1 clic |

Remplacer par `[VALEUR_MESURÉE]` pour que tu puisses remplir avec tes vraies mesures.

### Slide 14 — Bilan & Perspectives
**Layout** : Header NAVY, fond LIGHT_BG
**Titre** : `Bilan & Perspectives`
**Contenu — 2 colonnes égales :**

**Colonne gauche (titre BLUE_ELEC : "Limites actuelles")** :
- Reporting partiellement statique
- Pas de flux vidéo temps réel natif
- Modèle YOLO nécessite plus de données
- Interface alertes sans notifications push

**Colonne droite (titre ORANGE : "Perspectives")** :
- Flux RTSP / HLS en streaming
- Application mobile pour techniciens terrain
- Analyse Gemini AI pour insights avancés
- Intégration système de badges/accès
- Entraînement continu du modèle (MLOps)
- Notifications Slack/email en temps réel

### Slide 15 — Conclusion & Fin
**Layout** : Fond NAVY complet (identique slide 1)
**Contenu :**
- Barre ORANGE en haut (pleine largeur, 1 cm)
- Titre centré blanc : `Merci pour votre attention`
- Séparateur orange
- 3 points de synthèse en blanc (bullets larges) :
  - Plateforme IA + workflow métier HSE complet
  - Architecture cloud moderne et scalable
  - Solution défendable et extensible
- Encadré arrondi NAVY_CARD centré, texte ORANGE : `Questions ?`
- En bas : `[VOTRE_NOM] — [NOM_ECOLE] — [ANNEE_UNIVERSITAIRE]`
- Barre ORANGE en bas (pleine largeur, 0.5 cm)

---

## Exigences techniques du script Python

### Structure du script

```python
# Le script doit être organisé ainsi :
# 1. Imports et constantes de couleur/design
# 2. Fonctions utilitaires réutilisables
# 3. Fonctions de création pour chaque slide (une fonction par slide)
# 4. Fonction main() qui instancie la présentation, appelle les slides dans l'ordre, et sauvegarde
```

### Fonctions utilitaires à créer obligatoirement

```python
def add_slide_header(slide, prs, title, show_number=True, slide_num=None):
    """Ajoute la barre header NAVY en haut avec le titre et optionnellement le numéro de slide."""

def add_rounded_box(slide, left, top, width, height, bg_color, text="", text_color=WHITE, font_size=14, bold=False, corner_radius=150000):
    """Ajoute un rectangle arrondi coloré avec texte optionnel."""

def add_bullet_list(slide, left, top, width, height, items, color=TEXT_DARK, font_size=16, bullet_color=ORANGE):
    """Ajoute une liste à puces avec couleur de puce personnalisée."""

def add_section_label(slide, left, top, text, color=ORANGE, font_size=14):
    """Ajoute un petit label de section en couleur (titre de zone)."""

def add_horizontal_line(slide, left, top, width, color=ORANGE, thickness=50000):
    """Ajoute une ligne horizontale fine colorée."""

def set_slide_background(slide, prs, color):
    """Définit la couleur de fond d'un slide entier."""
```

### Contraintes obligatoires

1. **Toutes les dimensions** doivent être calculées avec `Inches()` ou `Cm()` ou `Pt()` de `pptx.util` — pas de valeurs en EMU codées en dur
2. **Chaque slide** doit avoir un numéro de page discret en bas à droite (10pt, TEXT_MUTED), sauf slide 1 et 15
3. **Les formes** utilisées pour les schémas doivent être créées avec `slide.shapes.add_shape()` — pas d'images PNG insérées
4. **Les flèches** entre blocs doivent être créées avec `MSO_SHAPE_TYPE` ou des formes `MSO_SHAPE.RIGHT_ARROW`
5. **Le script** doit être exécutable directement avec : `python generate_pptx.py`
6. **Le fichier de sortie** doit s'appeler `soutenance_EPI_Detection.pptx` et être sauvegardé dans le répertoire courant
7. **Pas d'images externes** — tout le visuel est créé avec des formes python-pptx
8. **Commentaires** dans le code : une ligne de commentaire pour chaque section de slide pour la lisibilité

### Imports requis

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
import copy
```

---

## Conseils de présentation à inclure en commentaire dans le script

À la fin du script, inclure un bloc commenté `# === NOTES DE SOUTENANCE ===` avec :

```
# TIMING SUGGÉRÉ (15 minutes solo) :
# Slide 1  (Titre)         : 0:30 — Accueil, présentation rapide
# Slide 2  (Contexte)      : 1:00 — Chiffres-clés, problème réel
# Slide 3  (Plan)          : 0:30 — Annoncer le plan
# Slide 4  (Problématique) : 1:00 — Poser la question de recherche
# Slide 5  (Architecture)  : 1:30 — Vue macro frontend/backend/cloud
# Slide 6  (YOLO)          : 1:30 — Montrer le pipeline IA
# Slide 7  (HSE)           : 1:00 — Expliquer règles et conformité
# Slide 8  (Workflow)      : 1:30 — Le cœur métier du projet
# Slide 9  (Modules)       : 1:00 — Tour rapide des fonctionnalités
# Slide 10 (Alertes)       : 1:00 — Cycle de vie et tracabilité
# Slide 11 (Déploiement)   : 0:30 — Cloud, montrer la maturité du projet
# Slide 12 (Résultats)     : 1:30 — Ce qui a été réellement livré
# Slide 13 (KPIs)          : 1:00 — Métriques métier
# Slide 14 (Bilan)         : 1:00 — Honnêteté sur limites + ambition perspectives
# Slide 15 (Fin)           : 0:30 — Conclusion et ouverture aux questions
# TOTAL : ~15 minutes
#
# QUESTIONS PROBABLES DU JURY :
# 1. "Quelle est la précision réelle de votre modèle YOLO ?"
#    → Citez le taux sur le dataset de validation. Si non mesuré : "C'est un axe d'amélioration identifié."
# 2. "Pourquoi Django plutôt que FastAPI pour une app IA ?"
#    → Richesse de l'écosystème Django (admin, ORM, permissions), YOLO est appelé en sync, performances suffisantes.
# 3. "Comment gérez-vous les faux positifs ?"
#    → Statut "ignoré" dans les alertes, feedback possible pour réentraînement du modèle.
# 4. "La solution est-elle déployée en production ?"
#    → Backend sur AWS EC2, frontend sur Cloudflare. URL de démo disponible si demandée.
# 5. "Qu'est-ce qui vous a posé le plus de difficultés ?"
#    → Synchronisation du cycle de vie alerte↔audit, gestion des doublons d'audits actifs.
```

---

## Format de sortie attendu

Génère **uniquement** le script Python complet, bien indenté, commenté, exécutable sans modification (hormis les placeholders `[VOTRE_NOM]` etc.). 

Le script doit faire entre 400 et 700 lignes de code Python propre. Ne génère pas d'explication avant ou après le code — **uniquement le script Python**.
