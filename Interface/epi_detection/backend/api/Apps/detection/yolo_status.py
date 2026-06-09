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
                if pt_path.exists():
                    model_path = pt_path
                    print(f"[YOLO] Chargement modèle PyTorch {model_path}")
                elif onnx_path.exists():
                    model_path = onnx_path
                    print(f"[YOLO] PyTorch absent — fallback ONNX {model_path}")
                else:
                    raise FileNotFoundError(f"Aucun modèle trouvé ({pt_path})")
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


def is_epi_worn(person_bbox, epi_bbox, overlap_threshold=0.25):
    """
    Vérifie si un EPI appartient à une personne.
    Mesure quelle fraction de l'EPI se trouve à l'intérieur de la personne.
    IoU standard est trop bas (helmet petit vs person grand) — on utilise
    intersection / aire_EPI à la place.
    """
    px1, py1, px2, py2 = person_bbox
    ex1, ey1, ex2, ey2 = epi_bbox

    ix = max(0, min(px2, ex2) - max(px1, ex1))
    iy = max(0, min(py2, ey2) - max(py1, ey1))
    inter = ix * iy

    epi_area = max(1, (ex2 - ex1) * (ey2 - ey1))
    return (inter / epi_area) > overlap_threshold


def run_detection_with_status(image):
    """
    Logique :
    1. Détecter toutes les classes YOLO sur l'image
    2. Isoler les personnes
    3. Pour chaque personne, vérifier les EPIs qui se chevauchent avec elle
    4. Déterminer la conformité de chaque personne
    """
    model   = get_model()
    results = model.track(image, persist=True, conf=0.15, iou=0.45, verbose=False)

    # ── Étape 1 : collecter toutes les détections ─────────────────────────────
    persons      = []   # personnes détectées
    other_dets   = []   # tout le reste (EPIs, violations)

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
            else:
                other_dets.append({"class": class_name, "bbox": bbox, "conf": conf})


    # ── Étape 2 : pour chaque personne, vérifier ses EPIs ────────────────────
    detections = []
    workers    = []
    hardhat_worn_count = vest_worn_count = gloves_worn_count = boots_worn_count = 0

    for person in persons:
        worker_id = _get_worker_id(person["track_id"])

        # Trouver tous les EPIs/violations qui chevauchent cette personne
        person_epis   = [d for d in other_dets
                         if d["class"] in EPI_CLASSES and is_epi_worn(person["bbox"], d["bbox"])]
        person_viols  = [d for d in other_dets
                         if d["class"] in VIOLATION_CLASSES and is_epi_worn(person["bbox"], d["bbox"])]

        # Statut de chaque EPI pour cette personne
        has_helmet = any(d["class"] == "helmet"      for d in person_epis)
        has_vest   = any(d["class"] == "vest"        for d in person_epis)
        has_gloves = any(d["class"] == "Gloves"      for d in person_epis)
        has_boots  = any(d["class"] == "Safety Shoe" for d in person_epis)

        # Une violation directe annule le statut positif
        if any(d["class"] == "no helmet" for d in person_viols): has_helmet = False
        if any(d["class"] == "no vest"   for d in person_viols): has_vest   = False
        if any(d["class"] == "no Gloves" for d in person_viols): has_gloves = False

        person_has = {
            "hardhat":      has_helmet,
            "vest":         has_vest,
            "gloves":       has_gloves,
            "safety_boots": has_boots,
        }
        is_compliant = all(person_has.values())

        if has_helmet: hardhat_worn_count += 1
        if has_vest:   vest_worn_count    += 1
        if has_gloves: gloves_worn_count  += 1
        if has_boots:  boots_worn_count   += 1

        # Bbox de la personne
        detections.append({
            "class":      f"Worker {worker_id}",
            "confidence": person["conf"],
            "bbox":       person["bbox"],
            "color":      COLORS["person"] if is_compliant else COLORS["missing"],
            "status":     "compliant" if is_compliant else "missing_epi",
        })

        # Bboxes des EPIs associés à cette personne
        for epi in person_epis:
            detections.append({
                "class":      EPI_KEY_MAP.get(epi["class"], epi["class"]),
                "confidence": epi["conf"],
                "bbox":       epi["bbox"],
                "color":      COLORS["worn"],
                "status":     "worn",
            })

        # Bboxes des violations associées à cette personne
        for viol in person_viols:
            detections.append({
                "class":      viol["class"],
                "confidence": viol["conf"],
                "bbox":       viol["bbox"],
                "color":      COLORS["missing"],
                "status":     "violation",
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
    missing_epi = [
        k for k, worn in {
            "hardhat":      hardhat_worn_count,
            "vest":         vest_worn_count,
            "gloves":       gloves_worn_count,
            "safety_boots": boots_worn_count,
        }.items()
        if worn == 0 and len(persons) > 0
    ]

    stats = {
        "total":                 len(detections),
        "person":                len(persons),
        "hardhat_worn":          hardhat_worn_count,
        "vest_worn":             vest_worn_count,
        "gloves_worn":           gloves_worn_count,
        "boots_worn":            boots_worn_count,
        "compliance":            len(persons) == 0 or len(missing_epi) == 0,
        "missing_epi":           missing_epi,
        "processingTime":        round(results[0].speed.get("inference", 0) / 1000, 4) if results else 0.0,
        "workers":               workers,
        "total_workers":         len(workers),
        "non_compliant_workers": sum(1 for w in workers if not w["is_compliant"]),
    }

    return detections, stats