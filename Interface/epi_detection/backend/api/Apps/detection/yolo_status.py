"""
Logique de détection EPI avec état : porté (vert), présent (jaune), manquant (rouge)
"""
from django.conf import settings
from ultralytics import YOLO
import threading
import numpy as np

_model = None
_lock  = threading.Lock()

# Mapping tracker_id YOLO → Worker ID séquentiel (1, 2, 3...)
_tracker_to_worker: dict = {}
_next_worker_id: int = 0


def _get_worker_id(tracker_id) -> int:
    global _next_worker_id
    if tracker_id is None:
        _next_worker_id += 1
        return _next_worker_id
    if tracker_id not in _tracker_to_worker:
        _next_worker_id += 1
        _tracker_to_worker[tracker_id] = _next_worker_id
    return _tracker_to_worker[tracker_id]


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
                _model = YOLO(str(model_path), task='detect')
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

# Classes positives du modèle (EPI détectés directement)
EPI_CLASSES = ["helmet", "vest", "Gloves", "Safety Shoe"]

# Classes de violation directe du modèle (préfixe "no ")
VIOLATION_CLASSES = ["no helmet", "no vest", "no Gloves", "no mask"]

# Mapping classe modèle → clé interne utilisée dans les stats/frontend
EPI_KEY_MAP = {
    "helmet":      "hardhat",
    "vest":        "vest",
    "Gloves":      "gloves",
    "Safety Shoe": "safety_boots",
}


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
    Lance YOLO et détermine l'état EPI de chaque personne.
    Classes du modèle : Gloves, Safety Shoe, helmet, no Gloves, no helmet,
                        no mask, no vest, person, vest
    """
    model   = get_model()
    results = model.track(image, persist=True, conf=0.25, iou=0.45, verbose=False)

    persons  = []
    epis     = {}  # class_name → [{"bbox", "conf"}]
    viol_map = {}  # violation_class → [{"bbox", "conf"}]

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
                epis.setdefault(class_name, []).append({"bbox": bbox, "conf": conf})
            elif class_name in VIOLATION_CLASSES:
                viol_map.setdefault(class_name, []).append({"bbox": bbox, "conf": conf})

    detections = []
    workers    = []
    worn_epis  = {cls: [] for cls in EPI_CLASSES}
    free_epis  = {cls: [] for cls in EPI_CLASSES}

    # ── Bboxes des EPIs positifs ──────────────────────────────────────────────
    for epi_class, epi_list in epis.items():
        for epi in epi_list:
            is_worn = any(is_epi_worn(p["bbox"], epi["bbox"]) for p in persons)
            target  = worn_epis if is_worn else free_epis
            target[epi_class].append(epi)
            detections.append({
                "class":      EPI_KEY_MAP.get(epi_class, epi_class),
                "confidence": epi["conf"],
                "bbox":       epi["bbox"],
                "color":      COLORS["worn"] if is_worn else COLORS["present"],
                "status":     "worn" if is_worn else "present",
            })

    # ── Bboxes des violations directes ───────────────────────────────────────
    for viol_class, viol_list in viol_map.items():
        for v in viol_list:
            detections.append({
                "class":      viol_class,
                "confidence": v["conf"],
                "bbox":       v["bbox"],
                "color":      COLORS["missing"],
                "status":     "violation",
            })

    # ── Analyse par personne ──────────────────────────────────────────────────
    for person in persons:
        worker_id = _get_worker_id(person["track_id"])

        # EPI porté : détection positive près de la personne
        person_has = {
            "hardhat":      any(is_epi_worn(person["bbox"], e["bbox"]) for e in epis.get("helmet", [])),
            "vest":         any(is_epi_worn(person["bbox"], e["bbox"]) for e in epis.get("vest", [])),
            "gloves":       any(is_epi_worn(person["bbox"], e["bbox"]) for e in epis.get("Gloves", [])),
            "safety_boots": any(is_epi_worn(person["bbox"], e["bbox"]) for e in epis.get("Safety Shoe", [])),
        }

        # Violation directe près de la personne → force le statut à manquant
        if any(is_epi_worn(person["bbox"], v["bbox"]) for v in viol_map.get("no helmet", [])):
            person_has["hardhat"] = False
        if any(is_epi_worn(person["bbox"], v["bbox"]) for v in viol_map.get("no vest", [])):
            person_has["vest"] = False
        if any(is_epi_worn(person["bbox"], v["bbox"]) for v in viol_map.get("no Gloves", [])):
            person_has["gloves"] = False

        is_compliant = all(person_has.values())

        # Bbox personne avec label "Worker N"
        detections.append({
            "class":      f"Worker {worker_id}",
            "confidence": person["conf"],
            "bbox":       person["bbox"],
            "color":      COLORS["person"] if is_compliant else COLORS["missing"],
            "status":     "compliant" if is_compliant else "missing_epi",
        })

        epi_status_map = {k: ("worn" if v else "missing") for k, v in person_has.items()}
        workers.append({
            "worker_id":     worker_id,
            "bbox":          person["bbox"],
            "confidence":    round(person["conf"], 2),
            "is_compliant":  is_compliant,
            "epis":          epi_status_map,
            "missing_count": sum(1 for s in epi_status_map.values() if s == "missing"),
        })

    # ── Stats globales ────────────────────────────────────────────────────────
    stats = {
        "total":          len(detections),
        "person":         len(persons),
        "hardhat_worn":   len(worn_epis["helmet"]),
        "vest_worn":      len(worn_epis["vest"]),
        "gloves_worn":    len(worn_epis["Gloves"]),
        "boots_worn":     len(worn_epis["Safety Shoe"]),
        "violations":     sum(len(v) for v in viol_map.values()),
    }

    missing_epi = [
        k for k, worn in {
            "hardhat":      stats["hardhat_worn"],
            "vest":         stats["vest_worn"],
            "gloves":       stats["gloves_worn"],
            "safety_boots": stats["boots_worn"],
        }.items()
        if worn == 0 and len(persons) > 0
    ]

    stats["compliance"]            = len(persons) == 0 or len(missing_epi) == 0
    stats["missing_epi"]           = missing_epi
    stats["processingTime"]        = round(
        results[0].speed.get("inference", 0) / 1000, 4
    ) if results else 0.0
    stats["workers"]               = workers
    stats["total_workers"]         = len(workers)
    stats["non_compliant_workers"] = sum(1 for w in workers if not w["is_compliant"])

    return detections, stats