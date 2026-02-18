"""
Logique de détection EPI avec état : porté (vert), présent (jaune), manquant (rouge)
"""
from django.conf import settings
from ultralytics import YOLO
import threading

_model = None
_lock  = threading.Lock()


def get_model() -> YOLO:
    """Charge le modèle YOLO (singleton thread-safe)"""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                model_path = settings.YOLO_MODEL_PATH
                print(f"[YOLO] Chargement du modèle depuis {model_path}...")
                _model = YOLO(str(model_path))
                print(f"[YOLO] Modèle chargé. Classes : {_model.names}")
    return _model


# ===================== Couleurs par état ======================================
COLORS = {
    "worn":    "#22c55e",  # vert  - EPI porté
    "present": "#eab308",  # jaune - EPI présent mais non porté
    "missing": "#ef4444",  # rouge - EPI manquant
    "person":  "#3b82f6",  # bleu  - personne
}

EPI_CLASSES = ["hardhat", "vest", "glass"]


def iou(box1, box2):
    """Calcule l'IoU (Intersection over Union) entre deux bounding boxes."""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area  = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area  = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


def is_epi_worn(person_bbox, epi_bbox, iou_threshold=0.1):
    """
    Vérifie si un EPI est porté par une personne.
    Un EPI est considéré "porté" si son IoU avec la personne > seuil.
    Seuil bas (0.1) car casque/gilet = petite zone vs personne entière.
    """
    return iou(person_bbox, epi_bbox) > iou_threshold


def run_detection_with_status(image):
    """
    Lance YOLO et détermine l'état de chaque EPI : porté / présent / manquant.
    
    Retourne (detections, stats) où :
    - detections = liste de {class, confidence, bbox, color, status}
    - stats = {total, person, hardhat_worn, vest_worn, ..., compliance, missing_epi}
    """
    model   = get_model()
    results = model(image)

    persons = []
    epis    = {}  # {epi_class: [(bbox, conf), ...]}

    # ============================ Séparer détections person vs EPI ==========================
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in model.names:
                continue

            class_name = model.names[cls_id]
            conf       = round(float(box.conf[0]), 4)
            bbox       = list(map(int, box.xyxy[0]))

            if class_name == "person":
                persons.append({"bbox": bbox, "conf": conf})
            elif class_name in EPI_CLASSES:
                if class_name not in epis:
                    epis[class_name] = []
                epis[class_name].append({"bbox": bbox, "conf": conf})

    #=================== Associer chaque EPI à une personne (ou pas) ============================
    detections = []
    worn_epis  = {epi: [] for epi in EPI_CLASSES}  # EPI portés par personne
    free_epis  = {epi: [] for epi in EPI_CLASSES}  # EPI présents mais non portés

    for epi_class, epi_list in epis.items():
        for epi in epi_list:
            is_worn = False
            for person in persons:
                if is_epi_worn(person["bbox"], epi["bbox"]):
                    is_worn = True
                    break

            if is_worn:
                worn_epis[epi_class].append(epi)
                detections.append({
                    "class":      epi_class,
                    "confidence": epi["conf"],
                    "bbox":       epi["bbox"],
                    "color":      COLORS["worn"],
                    "status":     "worn",  # 🟢 porté
                })
            else:
                free_epis[epi_class].append(epi)
                detections.append({
                    "class":      epi_class,
                    "confidence": epi["conf"],
                    "bbox":       epi["bbox"],
                    "color":      COLORS["present"],
                    "status":     "present",  # 🟡 présent mais non porté
                })

    # ======================Ajouter les personnes (rouge si EPI manquant) ======================
    for person in persons:
        # Vérifier si cette personne porte les EPI obligatoires
        person_has_hardhat = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("hardhat", [])
        )
        person_has_vest = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("vest", [])
        )

        # Couleur : rouge si un EPI manque, sinon bleu
        is_compliant = person_has_hardhat and person_has_vest
        person_color = COLORS["person"] if is_compliant else COLORS["missing"]

        detections.append({
            "class":      "person",
            "confidence": person["conf"],
            "bbox":       person["bbox"],
            "color":      person_color,
            "status":     "compliant" if is_compliant else "missing_epi",
        })

    #========================== Stats globales =====================================
    stats = {
        "total":         len(detections),
        "person":        len(persons),
        "hardhat_worn":  len(worn_epis["hardhat"]),
        "vest_worn":     len(worn_epis["vest"]),
        "glass_worn":    len(worn_epis["glass"]),
        "hardhat_free":  len(free_epis["hardhat"]),
        "vest_free":     len(free_epis["vest"]),
        "glass_free":    len(free_epis["glass"]),
    }

    # Conformité : tous les EPI obligatoires portés ?
    missing_epi = []
    if stats["hardhat_worn"] == 0:
        missing_epi.append("hardhat")
    if stats["vest_worn"] == 0:
        missing_epi.append("vest")

    stats["compliance"]     = len(missing_epi) == 0
    stats["missing_epi"]    = missing_epi
    stats["processingTime"] = round(
        results[0].speed.get("inference", 0) / 1000, 4
    ) if results else 0.0

    return detections, stats