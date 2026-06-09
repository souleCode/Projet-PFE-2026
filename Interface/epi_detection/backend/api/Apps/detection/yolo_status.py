"""
Logique de détection EPI avec état : porté (vert), présent (jaune), manquant (rouge)
"""
from django.conf import settings
from ultralytics import YOLO
import threading
import numpy as np

_model = None
_lock  = threading.Lock()


def get_model() -> YOLO:
    """Charge le modèle YOLO (singleton thread-safe). Préfère ONNX si disponible (moins de RAM)."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                onnx_path = settings.YOLO_ONNX_PATH
                pt_path   = settings.YOLO_MODEL_PATH
                if onnx_path.exists():
                    model_path = onnx_path
                    print(f"[YOLO] ONNX trouvé — chargement depuis {model_path}")
                else:
                    model_path = pt_path
                    print(f"[YOLO] ONNX absent — fallback sur {model_path}")
                _model = YOLO(str(model_path))
                print(f"[YOLO] Modèle chargé. Classes : {_model.names}")
                # Warm-up : compile le graph ONNX/PyTorch pour que la première
                # vraie requête ne soit pas lente.
                dummy = np.zeros((640, 640, 3), dtype=np.uint8)
                _model(dummy, verbose=False)
                print("[YOLO] Warm-up terminé.")
    return _model


# ===================== Couleurs par état ======================================
COLORS = {
    "worn":    "#22c55e",  # vert  - EPI porté
    "present": "#eab308",  # jaune - EPI présent mais non porté
    "missing": "#ef4444",  # rouge - EPI manquant
    "person":  "#3b82f6",  # bleu  - personne
}

EPI_CLASSES = ["hardhat", "vest", "glass","mask", "safety_boots", "ear_protection"]


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


def is_epi_worn(person_bbox, epi_bbox, iou_threshold=0.03):
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
    # track(persist=True) maintient les IDs entre frames successives
    results = model.track(image, persist=True, verbose=False)

    persons = []
    epis    = {}  

    # ============================ Séparer détections person vs EPI ==========================
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in model.names:
                continue

            class_name = model.names[cls_id]
            conf       = round(float(box.conf[0]), 4)
            bbox       = list(map(int, box.xyxy[0]))
            track_id   = int(box.id[0]) if box.id is not None else None

            if class_name == "person":
                persons.append({"bbox": bbox, "conf": conf, "track_id": track_id})
            elif class_name in EPI_CLASSES:
                if class_name not in epis:
                    epis[class_name] = []
                epis[class_name].append({"bbox": bbox, "conf": conf})

    #=================== Associer chaque EPI à une personne (ou pas) ============================
    detections = []
    workers    = []  # liste structurée par travailleur pour le frontend
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
                    "status":     "worn",  #  porté
                })
            else:
                free_epis[epi_class].append(epi)
                detections.append({
                    "class":      epi_class,
                    "confidence": epi["conf"],
                    "bbox":       epi["bbox"],
                    "color":      COLORS["present"],
                    "status":     "present",  # présent mais non porté
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
        person_has_mask = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("mask", [])
        )
        person_has_glass = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("glass", [])
        )
        person_has_boots = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("safety_boots", [])
        )
        person_has_ear = any(
            is_epi_worn(person["bbox"], epi["bbox"]) for epi in epis.get("ear_protection", [])
        )

        # Couleur : rouge si un EPI manque, sinon bleu
        is_compliant = person_has_hardhat and person_has_vest and person_has_mask and person_has_glass and person_has_boots and person_has_ear
        person_color = COLORS["person"] if is_compliant else COLORS["missing"]

        detections.append({
            "class":      "person",
            "confidence": person["conf"],
            "bbox":       person["bbox"],
            "color":      person_color,
            "status":     "compliant" if is_compliant else "missing_epi",
        })

        # Ajout d'une entrée pour chaque EPI manquant
        if not is_compliant:
            missing_epis = []
            if not person_has_hardhat:
                missing_epis.append("hardhat")
            if not person_has_vest:
                missing_epis.append("vest")
            if not person_has_mask:
                missing_epis.append("mask")
            if not person_has_glass:
                missing_epis.append("glass")
            if not person_has_boots:
                missing_epis.append("safety_boots")
            if not person_has_ear:
                missing_epis.append("ear_protection")
            for epi in missing_epis:
                detections.append({
                    "class": epi,
                    "confidence": None,
                    "bbox": person["bbox"],
                    "color": COLORS["missing"],
                    "status": "missing_epi",
                })

        # ── Entrée structurée par travailleur ──────────────────────────────────
        epi_status_map = {
            "hardhat":        "worn" if person_has_hardhat else "missing",
            "vest":           "worn" if person_has_vest    else "missing",
            "mask":           "worn" if person_has_mask    else "missing",
            "glass":          "worn" if person_has_glass   else "missing",
            "safety_boots":   "worn" if person_has_boots   else "missing",
            "ear_protection": "worn" if person_has_ear     else "missing",
        }
        workers.append({
            "worker_id":    person["track_id"] if person["track_id"] is not None else len(workers) + 1,
            "bbox":         person["bbox"],
            "confidence":   round(person["conf"], 2),
            "is_compliant": is_compliant,
            "epis":         epi_status_map,
            "missing_count": sum(1 for s in epi_status_map.values() if s == "missing"),
        })

    #========================== Stats globales =====================================

    # Index inversé : workers déjà ajoutés dans la boucle persons ci-dessous
    # (voir remplissage de `workers` dans la boucle)

    stats = {
        "total":         len(detections),
        "person":        len(persons),
        "hardhat_worn":  len(worn_epis["hardhat"]),
        "vest_worn":     len(worn_epis["vest"]),
        "glass_worn":    len(worn_epis["glass"]),
        "mask_worn":     len(worn_epis["mask"]),
        "boots_worn":    len(worn_epis["safety_boots"]),
        "ear_worn":      len(worn_epis["ear_protection"]),

        "hardhat_free":  len(free_epis["hardhat"]),
        "vest_free":     len(free_epis["vest"]),
        "glass_free":    len(free_epis["glass"]),
        "mask_free":     len(free_epis["mask"]),
        "boots_free":    len(free_epis["safety_boots"]),
        "ear_free":      len(free_epis["ear_protection"]),
    }

    # Conformité : tous les EPI obligatoires portés ?
    missing_epi = []
    if stats["hardhat_worn"] == 0:
        missing_epi.append("hardhat")
    if stats["vest_worn"] == 0:
        missing_epi.append("vest")
    if stats["mask_worn"] == 0:
        missing_epi.append("mask")
    if stats["glass_worn"] == 0:
        missing_epi.append("glass")
    if stats["boots_worn"] == 0:
        missing_epi.append("safety_boots")
    if stats["ear_worn"] == 0:
        missing_epi.append("ear_protection")
    stats["compliance"]             = len(missing_epi) == 0
    stats["missing_epi"]            = missing_epi
    stats["processingTime"]         = round(
        results[0].speed.get("inference", 0) / 1000, 4
    ) if results else 0.0
    stats["workers"]                = workers
    stats["total_workers"]          = len(workers)
    stats["non_compliant_workers"]  = sum(1 for w in workers if not w["is_compliant"])

    return detections, stats