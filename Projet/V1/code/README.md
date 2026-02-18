# 🦺 Détection d'EPI - Pipeline d'Entraînement Multi-Modèles

> **Système automatisé pour entraîner et comparer plusieurs modèles de détection d'objets pour la sécurité industrielle (EPI - Équipements de Protection Individuelle)**

---

## 🎯 Objectif du Projet

Ce projet permet d'entraîner automatiquement **4 modèles SOTA** (State-Of-The-Art) pour la détection d'EPI :
- **YOLOv8** (nano et small)
- **YOLOv11** (nano et small)  
- **RTDETRv2** (large)

Puis génère un **benchmark complet** avec visualisations pour identifier le meilleur modèle pour votre cas d'usage.

---

## ⚡ Démarrage Rapide (5 minutes)

### 1️⃣ Copier le code dans Google Colab

```python
# 1. Ouvrez https://colab.research.google.com
# 2. Créez un nouveau notebook
# 3. Collez le code de ppe_detection_training.py
```

### 2️⃣ Configurer Roboflow

Modifiez ces 4 lignes dans le code :

```python
class Config:
    ROBOFLOW_API_KEY = "VOTRE_CLE_API"      # ← Votre clé API Roboflow
    WORKSPACE_NAME = "VOTRE_WORKSPACE"      # ← Nom de votre workspace
    PROJECT_NAME = "VOTRE_PROJECT"          # ← Nom de votre projet
    VERSION_NUMBER = 1                      # ← Version du dataset
```

**Où trouver ces informations ?**
- **API Key** : Roboflow → Settings → Roboflow API
- **Workspace/Project** : Visible dans l'URL de votre projet
  - URL : `https://app.roboflow.com/mon-workspace/mon-projet/1`
  - Workspace : `mon-workspace`
  - Project : `mon-projet`
  - Version : `1`

### 3️⃣ Activer le GPU et lancer

```python
# Dans Colab :
# Runtime → Change runtime type → T4 GPU → Save

# Puis exécutez toutes les cellules :
# Runtime → Run all
```

### 4️⃣ Récupérer les résultats

Après l'entraînement (1-3 heures selon GPU), vous aurez :

```
📊 Fichiers générés :
├── benchmark_results.csv            # Tableau comparatif
├── benchmark_visualization.png      # Graphiques
├── radar_chart.png                  # Comparaison radar
└── models/
    ├── YOLOv8n_best.pt             # Modèles entraînés
    ├── YOLOv11s_best.pt
    └── ...
```

---

## 📊 Exemple de Résultats

Après l'entraînement, le système affiche automatiquement :

```
🏆 MEILLEUR MODÈLE: YOLOv11s
   ├─ mAP50-95: 0.8234
   ├─ mAP50: 0.9156
   ├─ Precision: 0.8871
   ├─ Recall: 0.8456
   ├─ F1-Score: 0.8659
   └─ Temps d'entraînement: 45.32 min
```

Et génère des visualisations comparatives :

![Example Benchmark](https://via.placeholder.com/800x400/3498db/ffffff?text=Benchmark+Visualization)

---

## 🎛️ Personnalisation Rapide

### Modifier le nombre d'époques

```python
class Config:
    EPOCHS = 150  # Par défaut: 100 (plus = meilleur mais plus long)
```

### Choisir quels modèles entraîner

```python
# Entraîner seulement YOLOv11 (le plus performant)
MODELS = {
    'YOLOv11n': 'yolo11n.pt',
    'YOLOv11s': 'yolo11s.pt',
}

# Ou un seul modèle pour tester rapidement
MODELS = {
    'YOLOv8n': 'yolov8n.pt',  # Le plus rapide
}
```

### Adapter à la mémoire GPU

```python
class Config:
    # GPU T4 (Colab gratuit) :
    BATCH_SIZE = 8
    IMG_SIZE = 640
    
    # GPU A100 (Colab Pro) :
    BATCH_SIZE = 32
    IMG_SIZE = 640
    
    # GPU V100 :
    BATCH_SIZE = 24
    IMG_SIZE = 640
```

---

## 📋 Prérequis

### Données
- ✅ Dataset labelisé sur Roboflow
- ✅ Divisé en Train/Test/Val
- ✅ Format YOLOv8
- ⚠️ Minimum recommandé : 500-1000 images

### Environnement
- ✅ Google Colab (gratuit ou Pro)
- ✅ GPU activé (T4, V100, ou A100)
- ✅ Connexion internet

---

## 🏗️ Structure du Code

```python
# Section 1 : Installation et imports
# Section 2 : Configuration (MODIFIER ICI)
# Section 3 : Téléchargement des données Roboflow
# Section 4 : Fonction d'entraînement optimisée
# Section 5 : Boucle d'entraînement multi-modèles
# Section 6 : Génération du benchmark et visualisations
# Section 7 : Exécution principale
```

---

## 🎓 Classes d'EPI Supportées

Le système détecte automatiquement vos classes depuis Roboflow.

**Exemples typiques d'EPI :**
- 🪖 Casques de sécurité (Helmet)
- 🦺 Gilets haute visibilité (Vest)
- 👷 Personnes (Person)
- 👟 Chaussures de sécurité (Safety Shoes)
- 🥽 Lunettes de protection (Goggles)
- 🧤 Gants (Gloves)
- 😷 Masques (Mask)

---

## 📈 Métriques Expliquées

| Métrique | Description | Bon Score |
|----------|-------------|-----------|
| **mAP50-95** | Précision moyenne (IoU 0.5-0.95) | > 0.70 |
| **mAP50** | Précision moyenne (IoU 0.5) | > 0.80 |
| **Precision** | Détections correctes / Total détections | > 0.75 |
| **Recall** | Objets détectés / Total objets | > 0.70 |
| **F1-Score** | Moyenne harmonique P/R | > 0.75 |

---

## 🚀 Utilisation du Modèle Entraîné

Une fois le meilleur modèle identifié :

```python
from ultralytics import YOLO

# Charger le modèle
model = YOLO('/content/models/YOLOv11s_best.pt')

# Prédiction sur une image
results = model.predict(
    source='path/to/image.jpg',
    conf=0.25,      # Seuil de confiance
    save=True       # Sauvegarder l'image annotée
)

# Prédiction sur une vidéo
results = model.predict(
    source='path/to/video.mp4',
    conf=0.25,
    save=True,
    stream=True     # Stream pour vidéos longues
)

# Prédiction en temps réel (webcam)
results = model.predict(
    source=0,       # 0 = webcam par défaut
    conf=0.25,
    show=True       # Afficher en temps réel
)
```

---

## 🔧 Optimisations Incluses

Le code inclut déjà les meilleures pratiques :

✅ **Data Augmentation** : HSV, rotation, flip, mosaic  
✅ **Early Stopping** : Arrêt automatique si pas d'amélioration  
✅ **Mixed Precision Training** : Entraînement plus rapide (AMP)  
✅ **AdamW Optimizer** : Meilleur que SGD pour la plupart des cas  
✅ **Cosine Learning Rate** : Diminution progressive du learning rate  
✅ **Warmup** : Démarrage progressif pour stabiliser  

---

## 📊 Exemple de Temps d'Entraînement

Basé sur un dataset de 1000 images, 100 epochs :

| Modèle | GPU T4 | GPU V100 | GPU A100 |
|--------|--------|----------|----------|
| YOLOv8n | ~35 min | ~18 min | ~12 min |
| YOLOv8s | ~50 min | ~25 min | ~16 min |
| YOLOv11n | ~40 min | ~20 min | ~13 min |
| YOLOv11s | ~55 min | ~28 min | ~18 min |
| RTDETRv2-l | ~90 min | ~45 min | ~30 min |

**Total pour 5 modèles : ~4h (T4), ~2h (V100), ~1h30 (A100)**

---

## 🆘 Problèmes Courants

### ❌ "CUDA Out of Memory"
```python
# Solution : Réduire batch size
Config.BATCH_SIZE = 8  # ou même 4
```

### ❌ "Roboflow API Error"
```python
# Vérifiez :
# 1. API Key correcte
# 2. Workspace/Project names (case-sensitive)
# 3. Version existe bien
# 4. Connexion internet
```

### ❌ "Low mAP scores (< 0.50)"
```python
# Causes possibles :
# - Dataset trop petit (< 500 images)
# - Labels de mauvaise qualité
# - Classes déséquilibrées
# - Besoin de plus d'epochs (150-200)
```

➡️ **Consultez le GUIDE_UTILISATION.md pour plus de détails**

---

## 📚 Ressources

- 📖 [Documentation Ultralytics](https://docs.ultralytics.com)
- 📖 [Documentation Roboflow](https://docs.roboflow.com)
- 🎓 [Tutoriel YOLOv8](https://github.com/ultralytics/ultralytics)
- 🎓 [Computer Vision Basics](https://roboflow.com/learn)

---

## 📝 Licence

Ce projet utilise :
- **Ultralytics YOLOv8/v11** : AGPL-3.0
- **RTDETRv2** : Apache-2.0

---

## 🤝 Contribution

Améliorations suggérées bienvenues :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout de...'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 📧 Contact

Pour questions ou support :
- 📧 Email : [votre-email@exemple.com]
- 💼 LinkedIn : [Votre profil]
- 🐙 GitHub : [Votre username]

---

## 🎉 Remerciements

- **Ultralytics** pour YOLO
- **Roboflow** pour la gestion des datasets
- **Google Colab** pour le GPU gratuit

---

**🦺 Bonne détection d'EPI ! Restez en sécurité ! 🦺**
