# apps/detection/yolo_fusion.py

"""
Pipeline complet EPI Detection avec Pose Estimation
Main Processing (YOLO) + Extra Processing (Pose) + Fusion (IoU)
"""

from django.conf import settings
import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pathlib import Path
import threading
# Singletons pour les modèles (thread-safe)
_yolo_model = None
_pose_detector = None
_lock = threading.Lock()

# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

COLORS = {
    "worn":    "#22c55e",  # vert
    "present": "#eab308",  # jaune
    "missing": "#ef4444",  # rouge
    "person":  "#3b82f6",  # bleu
}

EPI_CLASSES = ["hardhat", "vest", "glass", "mask", "safety_boots", "ear_protection"]

IOU_THRESHOLDS = {
    'hardhat': 0.15,
    'vest': 0.3,
    'boots': 0.2,
    'glass': 0.15,
    'mask': 0.15,
    'ear_protection': 0.15,
}

# ══════════════════════════════════════════════════════════════════════
# CHARGEMENT DES MODÈLES
# ══════════════════════════════════════════════════════════════════════

def get_yolo_model():
    """Charge le modèle YOLO (singleton thread-safe)"""
    global _yolo_model
    if _yolo_model is None:
        with _lock:
            if _yolo_model is None:
                model_path = settings.YOLO_MODEL_PATH
                print(f"[YOLO] Chargement du modèle depuis {model_path}...")
                _yolo_model = YOLO(str(model_path))
                print(f"[YOLO] Modèle chargé. Classes : {_yolo_model.names}")
    return _yolo_model


def get_pose_detector():
    """Charge MediaPipe Pose (singleton thread-safe)"""
    global _pose_detector
    if _pose_detector is None:
        with _lock:
            if _pose_detector is None:
                model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
                model_path = Path(settings.BASE_DIR) / "models" / "pose_landmarker_lite.task"
                model_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not model_path.exists():
                    print(f"[POSE] Téléchargement du modèle MediaPipe...")
                    import urllib.request
                    urllib.request.urlretrieve(model_url, str(model_path))
                
                print(f"[POSE] Chargement du modèle depuis {model_path}...")
                base_options = python.BaseOptions(model_asset_path=str(model_path))
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.IMAGE,
                    num_poses=1,
                    min_pose_detection_confidence=0.5
                )
                _pose_detector = vision.PoseLandmarker.create_from_options(options)
                print(f"[POSE] Modèle chargé.")
    return _pose_detector




# ──────────────────────────────────────────────────────────────
# 1. MAIN PROCESSING: Détection EPI avec YOLO
# ──────────────────────────────────────────────────────────────

class MainProcessing:
    """Détection EPI + Personnes avec YOLO"""
    def __init__(self, yolo_epi_model_path):
        print("🔧 Chargement YOLO EPI Model...")
        self.model = YOLO(yolo_epi_model_path)
        print("   ✅ YOLO EPI chargé")
        
        # Mapping des classes (adapter selon votre modèle)
        self.class_names = {
            0: 'glass',
            1: 'hardhat',
            2: 'mask',
            3: 'person',
            4: 'safety_boots',
            5: 'vest'
        }
    
    def detect(self, image):
        """
        Détecte tous les objets (EPI + personnes)
        
        Returns:
            dict: {
                'persons': [bbox, conf, ...],
                'hardhat': [bbox, conf, ...],
                'vest': [...],
                'boots': [...],
                'glass': [...]
            }
        """
        results = self.model(image, verbose=False)
        
        detections = {
            'persons': [],
            'hardhat': [],
            'vest': [],
            'boots': [],
            'glass': []
        }
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                class_name = self.class_names.get(cls_id, 'unknown')
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                bbox_data = {
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                    'class_id': cls_id
                }
                
                if class_name == 'person':
                    detections['persons'].append(bbox_data)
                elif class_name == 'hardhat':
                    detections['hardhat'].append(bbox_data)
                elif class_name == 'vest':
                    detections['vest'].append(bbox_data)
                elif class_name == 'safety_boots':
                    detections['boots'].append(bbox_data)
                elif class_name == 'glass':
                    detections['glass'].append(bbox_data)
        
        return detections


# ──────────────────────────────────────────────────────────────
# 2. EXTRA PROCESSING: Segmentation du corps + Pose
# ──────────────────────────────────────────────────────────────

class ExtraProcessing:
    """Body/Head/Feet detection + Pose Estimation"""
    
    def __init__(self, pose_model_path=None):
        print("🔧 Chargement Pose Estimator...")
        
        # MediaPipe Pose
        if pose_model_path is None:
            model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
            pose_model_path = "/persistent/soulecode/pose_landmarker_lite.task"
            from pathlib import Path
            import os
            os.makedirs(os.path.dirname(pose_model_path), exist_ok=True)
            if not Path(pose_model_path).exists():
                import urllib.request
                urllib.request.urlretrieve(model_url, pose_model_path)
        
        base_options = python.BaseOptions(model_asset_path=pose_model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5
        )
        
        self.pose_detector = vision.PoseLandmarker.create_from_options(options)
        print("   ✅ Pose Estimator chargé")
    
# Remplacez la fonction extract_body_parts dans ExtraProcessing

    def extract_body_parts(self, image, person_bbox):
        """Extrait head, body, feet avec HEAD bbox optimisé"""
        x1, y1, x2, y2 = person_bbox
        person_crop = image[y1:y2, x1:x2]
        
        if person_crop.size == 0:
            return None
        
        person_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=person_rgb)
        
        try:
            results = self.pose_detector.detect(mp_image)
        except Exception as e:
            print(f"⚠️  Erreur pose detection: {e}")
            return None
        
        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return None
        
        h_crop, w_crop = person_crop.shape[:2]
        landmarks = results.pose_landmarks[0]
        
        # Extraire keypoints
        keypoints = {
            'nose': (int(landmarks[0].x * w_crop), int(landmarks[0].y * h_crop)),
            'left_eye': (int(landmarks[2].x * w_crop), int(landmarks[2].y * h_crop)),
            'right_eye': (int(landmarks[5].x * w_crop), int(landmarks[5].y * h_crop)),
            'left_shoulder': (int(landmarks[11].x * w_crop), int(landmarks[11].y * h_crop)),
            'right_shoulder': (int(landmarks[12].x * w_crop), int(landmarks[12].y * h_crop)),
            'left_hip': (int(landmarks[23].x * w_crop), int(landmarks[23].y * h_crop)),
            'right_hip': (int(landmarks[24].x * w_crop), int(landmarks[24].y * h_crop)),
            'left_ankle': (int(landmarks[27].x * w_crop), int(landmarks[27].y * h_crop)),
            'right_ankle': (int(landmarks[28].x * w_crop), int(landmarks[28].y * h_crop)),
        }
        
        # ═══════════════════════════════════════════════════════════
        # HEAD BBOX OPTIMISÉ (basé sur distance yeux)
        # ═══════════════════════════════════════════════════════════
        left_eye_x = keypoints['left_eye'][0]
        right_eye_x = keypoints['right_eye'][0]
        nose_x = keypoints['nose'][0]
        nose_y = keypoints['nose'][1]
        shoulder_y = min(keypoints['left_shoulder'][1], keypoints['right_shoulder'][1])
        
        eye_distance = abs(right_eye_x - left_eye_x)
        head_width = int(eye_distance * 3)  # Largeur tête
        head_top = max(0, nose_y - int(eye_distance * 1.5))  # Hauteur au-dessus du nez
        
        head_bbox_local = (
            max(0, nose_x - head_width // 2),
            head_top,
            min(w_crop, nose_x + head_width // 2),
            shoulder_y - 150  # Laisser un peu d'espace avant les épaules
        )
        
        # ═══════════════════════════════════════════════════════════
        # BODY BBOX (inchangé)
        # ═══════════════════════════════════════════════════════════
        hip_y = max(keypoints['left_hip'][1], keypoints['right_hip'][1])
        body_bbox_local = (0, shoulder_y, w_crop, hip_y)
        
        # ═══════════════════════════════════════════════════════════
        # FEET BBOX (inchangé)
        # ═══════════════════════════════════════════════════════════
        ankle_y = min(keypoints['left_ankle'][1], keypoints['right_ankle'][1])
        feet_bbox_local = (0, ankle_y, w_crop, h_crop)
        
        # Convertir en coordonnées globales
        def to_global(bbox_local):
            lx1, ly1, lx2, ly2 = bbox_local
            return (x1 + lx1, y1 + ly1, x1 + lx2, y1 + ly2)
        
        return {
            'head_bbox': to_global(head_bbox_local),
            'body_bbox': to_global(body_bbox_local),
            'feet_bbox': to_global(feet_bbox_local),
            'keypoints': {k: (x1 + v[0], y1 + v[1]) for k, v in keypoints.items()}
        }


# ──────────────────────────────────────────────────────────────
# 3. FUSION: Calcul IoU et matching EPI ↔ Corps
# ──────────────────────────────────────────────────────────────

class FusionModule:
    """Fusionne Main + Extra processing"""
    
    @staticmethod
    def calculate_iou(bbox1, bbox2):
        """Calcule IoU entre deux bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    @staticmethod
    def match_epi_to_person(epi_detections, person_body_parts):
        """
        Détermine si EPI est porté ou non via IoU
        
        Args:
            epi_detections: Liste de détections EPI (hardhat, vest, boots)
            person_body_parts: Dict avec head_bbox, body_bbox, feet_bbox
        
        Returns:
            dict: {
                'hardhat': 'WORN' | 'PRESENT' | 'MISSING',
                'vest': 'WORN' | 'PRESENT' | 'MISSING',
                'boots': 'WORN' | 'PRESENT' | 'MISSING',
                'glass': 'WORN' | 'PRESENT' | 'MISSING'
            }
        """
        status = {
            'hardhat': 'MISSING',
            'vest': 'MISSING',
            'boots': 'MISSING',
            'glass': 'MISSING'
        }
        
        if not person_body_parts:
            return status
        
        head_bbox = person_body_parts['head_bbox']
        body_bbox = person_body_parts['body_bbox']
        feet_bbox = person_body_parts['feet_bbox']
        
        # Seuils IoU (ajustables)
        THRESHOLDS = {
            'hardhat': 0.05,
            'vest': 0.4,
            'boots': 0.3,
            'glass': 0.25
        }
        
        # HARDHAT vs HEAD
        for hardhat in epi_detections.get('hardhat', []):
            iou = FusionModule.calculate_iou(hardhat['bbox'], head_bbox)
            if iou > THRESHOLDS['hardhat']:
                status['hardhat'] = 'WORN'
                break
        else:
            if len(epi_detections.get('hardhat', [])) > 0:
                status['hardhat'] = 'PRESENT'  # Détecté mais pas porté
        
        # VEST vs BODY
        for vest in epi_detections.get('vest', []):
            iou = FusionModule.calculate_iou(vest['bbox'], body_bbox)
            if iou > THRESHOLDS['vest']:
                status['vest'] = 'WORN'
                break
        else:
            if len(epi_detections.get('vest', [])) > 0:
                status['vest'] = 'PRESENT'
        
        # BOOTS vs FEET
        for boots in epi_detections.get('boots', []):
            iou = FusionModule.calculate_iou(boots['bbox'], feet_bbox)
            if iou > THRESHOLDS['boots']:
                status['boots'] = 'WORN'
                break
        else:
            if len(epi_detections.get('boots', [])) > 0:
                status['boots'] = 'PRESENT'
        
        # GLASS vs HEAD
        for glass in epi_detections.get('glass', []):
            iou = FusionModule.calculate_iou(glass['bbox'], head_bbox)
            if iou > THRESHOLDS['glass']:
                status['glass'] = 'WORN'
                break
        else:
            if len(epi_detections.get('glass', [])) > 0:
                status['glass'] = 'PRESENT'
        
        return status


# ──────────────────────────────────────────────────────────────
# 4. PIPELINE COMPLET
# ──────────────────────────────────────────────────────────────

class CompletePipeline:
    """Pipeline complet: Main + Extra + Fusion"""
    
    def __init__(self, yolo_epi_model_path):
        self.main_processing = MainProcessing(yolo_epi_model_path)
        self.extra_processing = ExtraProcessing()
        self.fusion = FusionModule()
    
    def process_image(self, image):
        """
        Traite une image complète
        
        Returns:
            list: [
                {
                    'person_bbox': (x1, y1, x2, y2),
                    'body_parts': {...},
                    'epi_status': {
                        'hardhat': 'WORN' | 'PRESENT' | 'MISSING',
                        'vest': ...,
                        'boots': ...,
                        'glass': ...
                    },
                    'is_compliant': bool
                },
                ...
            ]
        """
        # 1. Main Processing: Détecter tous les objets
        detections = self.main_processing.detect(image)
        
        results = []
        
        # 2. Pour chaque personne
        for person in detections['persons']:
            person_bbox = person['bbox']
            
            # 3. Extra Processing: Segmenter le corps
            body_parts = self.extra_processing.extract_body_parts(image, person_bbox)
            
            # 4. Fusion: Matcher EPI avec parties du corps
            epi_status = self.fusion.match_epi_to_person(detections, body_parts)
            
            # 5. Vérifier conformité (tous les EPI obligatoires portés)
            is_compliant = (
                epi_status['hardhat'] == 'WORN' and
                epi_status['vest'] == 'WORN'
                # boots et glass optionnels selon votre règle
            )
            
            results.append({
                'person_bbox': person_bbox,
                'person_confidence': person['confidence'],
                'body_parts': body_parts,
                'epi_status': epi_status,
                'is_compliant': is_compliant
            })
        
        return results,detections  # Retourner aussi les détections brutes pour debug
    
    def draw_results(self, image, results):
        """Dessine les résultats sur l'image"""
        for person_result in results:
            bbox = person_result['person_bbox']
            status = person_result['epi_status']
            is_compliant = person_result['is_compliant']
            body_parts = person_result['body_parts']
            
            x1, y1, x2, y2 = bbox
            
            # Couleur selon conformité
            color = (0, 255, 0) if is_compliant else (0, 0, 255)
            
            # Rectangle personne
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
            
            # Texte status
            y_offset = y1 - 10
            for epi_name, epi_status in status.items():
                if epi_status == 'WORN':
                    text = f"{epi_name}: ✓ PORTÉ"
                    text_color = (0, 255, 0)
                elif epi_status == 'PRESENT':
                    text = f"{epi_name}: ⚠ PRÉSENT"
                    text_color = (0, 165, 255)
                else:
                    text = f"{epi_name}: ✗ MANQUANT"
                    text_color = (0, 0, 255)
                
                cv2.putText(image, text, (x1, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
                y_offset -= 20
            
            # Dessiner body parts (debug)
            if body_parts:
                # Head bbox (bleu)
                hx1, hy1, hx2, hy2 = body_parts['head_bbox']
                cv2.rectangle(image, (hx1, hy1), (hx2, hy2), (255, 0, 0), 1)
                
                # Body bbox (vert)
                bx1, by1, bx2, by2 = body_parts['body_bbox']
                cv2.rectangle(image, (bx1, by1), (bx2, by2), (0, 255, 0), 1)
                
                # Feet bbox (orange)
                fx1, fy1, fx2, fy2 = body_parts['feet_bbox']
                cv2.rectangle(image, (fx1, fy1), (fx2, fy2), (0, 165, 255), 1)
        
        return image



# ══════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE POUR DJANGO
# ══════════════════════════════════════════════════════════════════════

def run_detection_with_fusion(image):
    """
    Point d'entrée principal pour Django
    
    Args:
        image: numpy array (H, W, 3) BGR
    
    Returns:
        (detections, stats) tuple
    """
    # Initialiser le pipeline
    yolo_model_path = settings.YOLO_MODEL_PATH
    pipeline = CompletePipeline(str(yolo_model_path))
    
    # Process
    results, yolo_detections = pipeline.process_image(image)
    
    # ═══════════════════════════════════════════════════════════
    # FORMATER LES DÉTECTIONS POUR LE FRONTEND
    # ═══════════════════════════════════════════════════════════
    detections = []
    all_persons_status = []
    
    for person_result in results:
        person_bbox = person_result['person_bbox']
        epi_status = person_result['epi_status']
        is_compliant = person_result['is_compliant']
        
        # Ajouter la personne
        detections.append({
            "class": "person",
            "confidence": person_result['person_confidence'],
            "bbox": list(person_bbox),
            "color": COLORS["person"] if is_compliant else COLORS["missing"],
            "status": "compliant" if is_compliant else "missing_epi",
        })
        
        # Ajouter les EPI détectés
        for epi_class in EPI_CLASSES:
            epi_det_status = epi_status.get(epi_class, 'MISSING')
            
            if epi_det_status == 'WORN':
                # Trouver le bbox de cet EPI dans les détections YOLO
                for epi_det in yolo_detections.get(epi_class, []):
                    detections.append({
                        "class": epi_class,
                        "confidence": epi_det['confidence'],
                        "bbox": list(epi_det['bbox']),
                        "color": COLORS["worn"],
                        "status": "worn",
                    })
                    break  # Un seul par personne
            
            elif epi_det_status == 'PRESENT':
                for epi_det in yolo_detections.get(epi_class, []):
                    detections.append({
                        "class": epi_class,
                        "confidence": epi_det['confidence'],
                        "bbox": list(epi_det['bbox']),
                        "color": COLORS["present"],
                        "status": "present",
                    })
                    break
            
            elif epi_det_status == 'MISSING' and person_result.get('body_parts'):
                # EPI manquant : dessiner bbox rouge sur la zone concernée
                body_parts = person_result['body_parts']
                missing_bbox = {
                    'hardhat': body_parts.get('head_bbox'),
                    'vest': body_parts.get('body_bbox'),
                    'glass': body_parts.get('head_bbox'),
                    'mask': body_parts.get('head_bbox'),
                    'safety_boots': body_parts.get('feet_bbox'),
                    'ear_protection': body_parts.get('head_bbox'),
                }.get(epi_class)
                
                if missing_bbox:
                    detections.append({
                        "class": f"{epi_class}_missing",
                        "confidence": None,
                        "bbox": list(missing_bbox),
                        "color": COLORS["missing"],
                        "status": "missing",
                    })
        
        all_persons_status.append({
            'compliant': is_compliant,
            'epi_status': epi_status
        })
    
    # ═══════════════════════════════════════════════════════════
    # STATS GLOBALES
    # ═══════════════════════════════════════════════════════════
    stats = {
        "total": len(detections),
        "person": len(results),
        "compliant_persons": sum(1 for p in all_persons_status if p['compliant']),
        "non_compliant_persons": sum(1 for p in all_persons_status if not p['compliant']),
    }
    
    # Stats par EPI
    for epi_class in EPI_CLASSES:
        worn_count = sum(1 for p in all_persons_status if p['epi_status'].get(epi_class) == 'WORN')
        present_count = sum(1 for p in all_persons_status if p['epi_status'].get(epi_class) == 'PRESENT')
        missing_count = sum(1 for p in all_persons_status if p['epi_status'].get(epi_class) == 'MISSING')
        
        stats[f"{epi_class}_worn"] = worn_count
        stats[f"{epi_class}_present"] = present_count
        stats[f"{epi_class}_missing"] = missing_count
    
    # Conformité
    missing_epi = []
    for epi_class in ['hardhat', 'vest']:  # EPI obligatoires
        if stats.get(f"{epi_class}_worn", 0) < stats['person']:
            missing_epi.append(epi_class)
    
    stats['compliance'] = len(missing_epi) == 0
    stats['missing_epi'] = missing_epi
    stats['processingTime'] = 0.0
    
    return detections, stats