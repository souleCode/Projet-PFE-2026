from django.conf import settings
from ultralytics import YOLO
import threading

_model = None
_lock  = threading.Lock()


def get_model() -> YOLO:
    """
    Charge le modèle YOLO une seule fois (singleton thread-safe).
    Appelé au premier /detect, pas au démarrage du serveur.
    """
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                model_path = settings.YOLO_MODEL_PATH
                print(f"[YOLO] Chargement du modèle depuis {model_path} …")
                _model = YOLO(str(model_path))
                print(f"[YOLO] Modèle chargé. Classes : {_model.names}")
    return _model


# Couleurs par classe (peut être surchargé dans settings)
CLASS_COLORS = {
    "glass":   "#eab308",
    "hardhat": "#10b981",
    "vest":    "#f59e0b",
    "person":  "#3b82f6",
    "safety_boots": "#f97316",
    "mask":    "#8b5cf6",
}
DEFAULT_COLOR = "#6b7280"

# EPI obligatoires pour la conformité
REQUIRED_EPI = ["hardhat", "vest"]


def run_detection_dynamic(image, watched_epis):
    """
    Lance la détection YOLO sur une image PIL.
    watched_epis: liste dynamique d'EPI à surveiller
    Retourne (detections, stats).
    """
    model   = get_model()
    results = model(image)

    detections = []
    stats      = {name: 0 for name in model.names.values()}
    stats["total"] = 0

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])

            if cls_id not in model.names:
                continue

            class_name = model.names[cls_id]
            conf       = round(float(box.conf[0]), 4)
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append({
                "class":      class_name,
                "confidence": conf,
                "bbox":       [x1, y1, x2, y2],
                "color":      CLASS_COLORS.get(class_name, DEFAULT_COLOR),
            })

            stats[class_name] = stats.get(class_name, 0) + 1
            stats["total"]   += 1

    # Conformité : tous les EPI cochés présents ?
    stats["compliance"]     = all(stats.get(epi, 0) > 0 for epi in watched_epis)
    stats["missing_epi"]    = [epi for epi in watched_epis if stats.get(epi, 0) == 0]
    stats["processingTime"] = round(
        results[0].speed.get("inference", 0) / 1000, 4
    ) if results else 0.0

    return detections, stats