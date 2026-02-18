# 🔧 Guide d'Utilisation - Détection d'EPI avec Deep Learning

## 📋 Table des Matières
1. [Prérequis](#prérequis)
2. [Configuration Roboflow](#configuration-roboflow)
3. [Utilisation dans Google Colab](#utilisation-dans-google-colab)
4. [Paramètres Personnalisables](#paramètres-personnalisables)
5. [Interprétation des Résultats](#interprétation-des-résultats)
6. [Dépannage](#dépannage)

---

## 🎯 Prérequis

### 1. Compte Roboflow
- Créez un compte gratuit sur [Roboflow.com](https://roboflow.com)
- Uploadez vos données (dossiers Train, Test, Val)
- Labelisez vos images si ce n'est pas déjà fait
- Générez une version du dataset au format YOLOv8

### 2. Google Colab
- Ouvrez [Google Colab](https://colab.research.google.com)
- Activez le GPU : `Runtime > Change runtime type > GPU > T4`
- Pour de meilleures performances, utilisez Colab Pro (GPU A100)

---

## 🔐 Configuration Roboflow

### Étape 1 : Obtenir votre API Key
1. Connectez-vous à Roboflow
2. Cliquez sur votre profil (en haut à droite)
3. Allez dans `Settings` → `Roboflow API`
4. Copiez votre API Key privée

### Étape 2 : Identifier votre Workspace et Project
1. Dans Roboflow, ouvrez votre projet
2. L'URL ressemble à : `https://app.roboflow.com/WORKSPACE_NAME/PROJECT_NAME/VERSION`
3. Notez :
   - `WORKSPACE_NAME` : le nom de votre workspace
   - `PROJECT_NAME` : le nom de votre projet
   - `VERSION` : le numéro de version (généralement 1)

### Étape 3 : Mettre à jour le code

Dans le script, modifiez ces lignes (Section 2) :

```python
class Config:
    # Remplacez avec VOS informations
    ROBOFLOW_API_KEY = "votre_clé_api_ici"
    WORKSPACE_NAME = "votre_workspace"
    PROJECT_NAME = "votre_projet"
    VERSION_NUMBER = 1
```

**Exemple réel :**
```python
ROBOFLOW_API_KEY = "xYz123AbC456..."
WORKSPACE_NAME = "industrial-safety"
PROJECT_NAME = "ppe-detection"
VERSION_NUMBER = 1
```

---

## 🚀 Utilisation dans Google Colab

### Méthode 1 : Copier-Coller Direct

1. Ouvrez un nouveau notebook Google Colab
2. Copiez l'intégralité du code fourni
3. Collez-le dans une cellule
4. **Modifiez les paramètres Roboflow** (voir ci-dessus)
5. Exécutez la cellule : `Shift + Enter`

### Méthode 2 : Upload du Fichier

1. Uploadez le fichier `.py` dans Colab
2. Créez une nouvelle cellule et exécutez :

```python
# Charger et exécuter le script
%run ppe_detection_training.py
```

### Méthode 3 : Depuis GitHub (Recommandé)

1. Uploadez le script sur votre GitHub
2. Dans Colab, clonez et exécutez :

```python
!git clone https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
%cd VOTRE_REPO
!python ppe_detection_training.py
```

---

## ⚙️ Paramètres Personnalisables

### 1. Paramètres d'Entraînement

Modifiez dans la classe `Config` :

```python
class Config:
    # Nombre d'époques (plus = meilleur mais plus long)
    EPOCHS = 100  # Augmentez à 150-200 pour de meilleurs résultats
    
    # Taille du batch (dépend de votre GPU)
    BATCH_SIZE = 16  # T4: 8-16, A100: 32-64, V100: 24-32
    
    # Taille des images
    IMG_SIZE = 640  # Options: 320, 416, 512, 640, 1280
    
    # Early stopping patience
    PATIENCE = 20  # Arrête si pas d'amélioration après 20 epochs
```

### 2. Choix des Modèles

Modifiez `Config.MODELS` pour entraîner seulement certains modèles :

```python
# Exemple : Entraîner seulement YOLOv8 et YOLOv11
MODELS = {
    'YOLOv8n': 'yolov8n.pt',
    'YOLOv11n': 'yolo11n.pt',
}

# Variantes disponibles par taille :
# n (nano) : le plus rapide, moins précis
# s (small) : bon équilibre
# m (medium) : meilleure précision
# l (large) : très précis mais lent
# x (xlarge) : maximum de précision

# Exemples :
'YOLOv8m': 'yolov8m.pt',  # YOLOv8 medium
'YOLOv11l': 'yolo11l.pt',  # YOLOv11 large
```

### 3. Augmentation de Données

Dans `training_args` de la fonction `train_model()` :

```python
# Augmentation HSV (couleurs)
'hsv_h': 0.015,  # Variation de teinte
'hsv_s': 0.7,    # Variation de saturation
'hsv_v': 0.4,    # Variation de luminosité

# Transformations géométriques
'degrees': 10.0,      # Rotation (degrés)
'translate': 0.1,     # Translation
'scale': 0.5,         # Zoom
'fliplr': 0.5,        # Flip horizontal (50%)

# Augmentation avancée
'mosaic': 1.0,        # Mosaïque de 4 images
'mixup': 0.0,         # Mixup (désactivé par défaut)
'copy_paste': 0.0,    # Copy-paste augmentation
```

---

## 📊 Interprétation des Résultats

### Métriques Principales

**1. mAP50-95 (Mean Average Precision)**
- Métrique la plus importante
- Mesure la précision à différents seuils (IoU de 0.5 à 0.95)
- **Bon :** > 0.70
- **Excellent :** > 0.85

**2. mAP50**
- Précision avec seuil IoU de 0.5
- Plus facile à atteindre que mAP50-95
- **Bon :** > 0.80
- **Excellent :** > 0.90

**3. Precision**
- Parmi les détections positives, combien sont correctes ?
- Important si vous voulez éviter les fausses alarmes
- **Bon :** > 0.75

**4. Recall**
- Parmi tous les objets réels, combien sont détectés ?
- Important si vous ne voulez rien manquer
- **Bon :** > 0.70

**5. F1-Score**
- Moyenne harmonique de Precision et Recall
- Meilleur indicateur global
- **Bon :** > 0.75

### Fichiers Générés

Après l'exécution, vous trouverez :

```
/content/results/
├── benchmark_results.csv         # Résultats en tableau
├── benchmark_results.json        # Résultats en JSON
├── benchmark_visualization.png   # Graphiques comparatifs
├── radar_chart.png               # Comparaison radar
└── [MODEL_NAME]/
    ├── weights/
    │   ├── best.pt               # Meilleur modèle
    │   └── last.pt               # Dernier checkpoint
    ├── results.png               # Courbes d'entraînement
    ├── confusion_matrix.png      # Matrice de confusion
    ├── F1_curve.png             # Courbe F1
    ├── PR_curve.png             # Courbe Precision-Recall
    └── val_batch0_pred.jpg      # Prédictions sur validation

/content/models/
└── [MODEL_NAME]_best.pt          # Modèles sauvegardés
```

---

## 🎯 Utiliser le Meilleur Modèle

Une fois l'entraînement terminé :

```python
from ultralytics import YOLO

# Charger le meilleur modèle (remplacez par le nom réel)
model = YOLO('/content/models/YOLOv11s_best.pt')

# Faire des prédictions
results = model.predict(
    source='path/to/image.jpg',
    conf=0.25,        # Seuil de confiance
    iou=0.45,         # Seuil IoU pour NMS
    save=True,        # Sauvegarder les images annotées
    save_txt=True,    # Sauvegarder les labels
)

# Afficher les résultats
for result in results:
    result.show()
```

---

## 🔧 Dépannage

### Problème 1 : Erreur CUDA Out of Memory

**Symptômes :** `RuntimeError: CUDA out of memory`

**Solutions :**
```python
# Réduire la taille du batch
Config.BATCH_SIZE = 8  # ou même 4

# Réduire la taille des images
Config.IMG_SIZE = 416  # au lieu de 640

# Libérer la mémoire entre les entraînements
torch.cuda.empty_cache()
```

### Problème 2 : Roboflow API Error

**Symptômes :** `Error downloading dataset`

**Solutions :**
1. Vérifiez que votre API key est correcte
2. Vérifiez les noms workspace/project (sensible à la casse)
3. Assurez-vous que la version existe
4. Vérifiez votre connexion internet

### Problème 3 : Résultats Médiocres (mAP < 0.50)

**Causes possibles :**
- Dataset trop petit (< 500 images)
- Labels de mauvaise qualité
- Classes déséquilibrées
- Images de mauvaise qualité

**Solutions :**
```python
# 1. Augmenter les epochs
Config.EPOCHS = 200

# 2. Augmenter l'augmentation de données
'hsv_h': 0.03,
'degrees': 20.0,
'mosaic': 1.0,

# 3. Utiliser un modèle plus grand
MODELS = {'YOLOv11m': 'yolo11m.pt'}  # au lieu de 'n' ou 's'

# 4. Réduire le learning rate
'lr0': 0.0005,  # au lieu de 0.001
```

### Problème 4 : Entraînement Trop Long

**Symptômes :** Un modèle prend > 2 heures

**Solutions :**
```python
# Utiliser un modèle plus petit
MODELS = {'YOLOv8n': 'yolov8n.pt'}  # nano = plus rapide

# Réduire les epochs
Config.EPOCHS = 50

# Augmenter le batch size (si possible)
Config.BATCH_SIZE = 32
```

---

## 📈 Conseils pour Améliorer les Résultats

### 1. Qualité des Données

✅ **À FAIRE :**
- Labels précis et cohérents
- Variété dans les conditions (éclairage, angles, distances)
- Au moins 1000+ images par classe
- Distribution équilibrée des classes

❌ **À ÉVITER :**
- Labels approximatifs
- Images floues ou de mauvaise qualité
- Toutes les images dans les mêmes conditions
- Classes très déséquilibrées (10 images vs 1000)

### 2. Stratégie d'Entraînement

**Premier entraînement (exploration rapide) :**
```python
Config.EPOCHS = 50
Config.BATCH_SIZE = 16
MODELS = {'YOLOv8n': 'yolov8n.pt'}  # Modèle rapide
```

**Entraînement final (meilleure performance) :**
```python
Config.EPOCHS = 200
Config.BATCH_SIZE = 32  # si GPU le permet
MODELS = {'YOLOv11m': 'yolo11m.pt'}  # Modèle plus gros
```

### 3. Fine-tuning

Si un modèle donne de bons résultats, vous pouvez le réentraîner :

```python
# Partir du modèle déjà entraîné
model = YOLO('/content/models/YOLOv11s_best.pt')

# Réentraîner avec moins d'epochs et learning rate plus faible
model.train(
    data='data.yaml',
    epochs=50,
    lr0=0.0001,  # Learning rate plus faible
    # ... autres paramètres
)
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez la section **Dépannage** ci-dessus
2. Consultez la documentation Ultralytics : https://docs.ultralytics.com
3. Forum Roboflow : https://forum.roboflow.com
4. GitHub Issues Ultralytics : https://github.com/ultralytics/ultralytics/issues

---

## 🎉 Bonne Chance avec Votre Projet !

N'oubliez pas :
- 🚀 Commencez avec des entraînements courts pour valider
- 📊 Analysez les courbes d'entraînement
- 🔄 Itérez sur vos données si les résultats ne sont pas satisfaisants
- 💾 Sauvegardez régulièrement vos meilleurs modèles

**Le succès en Computer Vision = 80% qualité des données + 20% choix du modèle !**
