import cv2
import json
import queue
import threading
import base64
import time
import asyncio
import aiohttp
import os
from datetime import datetime
from ultralytics import YOLO
import google.generativeai as genai
from pathlib import Path


# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

YOLO_MODEL_PATH = "models/best.pt"   # Ton modèle entraîné
CONFIDENCE_THRESHOLD = 0.80              # En dessous → envoyer au LLM
FRAME_INTERVAL = 3                       # (conservé pour compatibilité)
LLM_MIN_INTERVAL = 1.5                   # Intervalle minimum entre soumissions Gemini (s)
PERSISTENCE_MINUTES = 5                  # Non-conformité persistante avant soumission LLM
GEMINI_DAILY_LIMIT = 5                   # Nombre max de traitements Gemini par jour
INCIDENT_LOG_PATH = "logs/incidents.json"

# 🎥 Configuration vidéo de test
TEST_VIDEO_PATH = "videos/test.mp4"  # Chemin vers la vidéo de test
USE_TEST_VIDEO = True                      # Activer par défaut (vraie configuration)

# Classes EPI que ton modèle YOLO détecte
YOLO_CLASSES = {
    0: "person",
    1: "helmet",
    2: "vest",
    3: "gloves",
    4: "boots"
}

# Équipements obligatoires par zone
REQUIRED_EPI = {
    "construction": ["helmet", "vest"],
    "welding":      ["helmet", "vest", "gloves"],
    "default":      ["helmet"]
}


# ─────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None


def load_yolo(model_path: str = YOLO_MODEL_PATH) -> YOLO:
    """Charge le modèle YOLO (télécharge yolov8n si modèle custom absent)."""
    path = Path(model_path)
    if not path.exists():
        print(f"[YOLO] Modèle custom introuvable → chargement de yolov8n.pt (base)")
        return YOLO("yolov8n.pt")
    return YOLO(str(path))


def get_video_source(use_test_video: bool = False, test_video_path: str = TEST_VIDEO_PATH, custom_video_path: str = None, uploaded_video_path: str = None) -> int | str:
    """
    Determine and validate the video source to use.
    
    Args:
        use_test_video (bool): If True, use the configured test video path.
        test_video_path (str): Path to the default test video.
        custom_video_path (str): Custom video path provided via CLI.
        uploaded_video_path (str): Path to the uploaded video.

    Returns:
        int | str: 0 for webcam, or absolute path to the video file.
    """
    base_dir = Path.cwd()

    # Priority 1: Uploaded video
    if uploaded_video_path:
        video_path = Path(uploaded_video_path)
        if video_path.exists():
            abs_path = str(video_path.resolve())
            print(f"[VIDEO] \u2713 Using uploaded video")
            print(f"[VIDEO]   Path: {abs_path}")
            return abs_path
        else:
            raise FileNotFoundError(f"Uploaded video not found: {uploaded_video_path}")

    # Priority 2: Custom video
    if custom_video_path:
        video_path = Path(custom_video_path)
        if not video_path.is_absolute():
            video_path = base_dir / video_path
        if video_path.exists():
            abs_path = str(video_path.resolve())
            print(f"[VIDEO] \u2713 Using custom video")
            print(f"[VIDEO]   Path: {abs_path}")
            return abs_path
        else:
            raise FileNotFoundError(f"Custom video not found: {custom_video_path}")

    # Priority 3: Test video
    if use_test_video:
        video_path = Path(test_video_path)
        if not video_path.is_absolute():
            video_path = base_dir / video_path
        if video_path.exists():
            abs_path = str(video_path.resolve())
            print(f"[VIDEO] \u2713 Using test video")
            print(f"[VIDEO]   Path: {abs_path}")
            return abs_path
        else:
            print(f"[VIDEO] \u26a0 Test video not found:")
            print(f"[VIDEO]   Expected path: {video_path}")
            print(f"[VIDEO]   Current directory: {base_dir}")
            print(f"[VIDEO]   \u2192 Defaulting to webcam (source=0)")
            return 0

    # Default: Webcam
    print("[VIDEO] Using webcam (source=0)")
    return 0


# ─────────────────────────────────────────
# ÉTAPE 1 : DÉTECTION YOLO
# ─────────────────────────────────────────

def detect_yolo(model: YOLO, frame) -> dict:
    """
    Détecte les EPI sur une frame.
    Retourne un dict structuré avec les résultats YOLO.
    """
    results = model(frame, verbose=False)[0]

    detections = {
        "person": False,
        "helmet": False,
        "vest": False,
        "gloves": False,
        "boots": False,
        "raw": [],
        "min_confidence": 1.0,
        "timestamp": datetime.now().isoformat()
    }

    for box in results.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = YOLO_CLASSES.get(class_id, "unknown")

        detections["raw"].append({
            "class": class_name,
            "confidence": round(confidence, 3),
            "bbox": box.xyxy[0].tolist()
        })

        if class_name in detections:
            detections[class_name] = True

        if confidence < detections["min_confidence"]:
            detections["min_confidence"] = confidence

    return detections


# ─────────────────────────────────────────
# ÉTAPE 2 : FILTRE INTELLIGENT
# ─────────────────────────────────────────

def needs_llm_validation(yolo_result: dict, zone: str = "default") -> tuple[bool, str]:
    """
    Décide si la frame doit être envoyée au LLM.
    Retourne (bool, raison).
    """
    # Pas de personne détectée → rien à valider
    if not yolo_result["person"]:
        return False, "no_person"

    # Confiance faible → validation LLM
    if yolo_result["min_confidence"] < CONFIDENCE_THRESHOLD:
        return True, f"low_confidence ({yolo_result['min_confidence']:.2f})"

    # Équipement manquant → validation LLM
    required = REQUIRED_EPI.get(zone, REQUIRED_EPI["default"])
    missing = [epi for epi in required if not yolo_result.get(epi, False)]

    if missing:
        return True, f"missing_epi: {missing}"

    return False, "ok"


# ─────────────────────────────────────────
# ÉTAPE 3 : ANALYSE GEMINI VISION
# ─────────────────────────────────────────

def encode_frame_to_base64(frame) -> str:
    """Encode une frame OpenCV en base64 JPEG."""
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode("utf-8")


def build_gemini_prompt(yolo_result: dict, zone: str, reason: str) -> str:
    """Construit le prompt contextuel pour Gemini."""
    detected_items = [k for k in ["helmet", "vest", "gloves", "boots"] if yolo_result.get(k)]
    required = REQUIRED_EPI.get(zone, REQUIRED_EPI["default"])

    return f"""Tu es un système expert en sécurité sur chantier.

YOLO a analysé cette image et a détecté :
- Personne présente : {yolo_result['person']}
- Casque : {yolo_result['helmet']}
- Gilet : {yolo_result['vest']}
- Gants : {yolo_result['gloves']}
- Confiance minimale : {yolo_result['min_confidence']:.2f}
- Raison d'envoi au LLM : {reason}

Zone de travail : {zone}
Équipements requis : {required}

Analyse l'image attentivement et réponds UNIQUEMENT en JSON valide :
{{
  "incident": true/false,
  "confirmed_epi": ["liste des EPI visibles confirmés"],
  "missing_epi": ["liste des EPI manquants confirmés"],
  "severity": "low/medium/high",
  "confidence": 0.0-1.0,
  "explanation": "description courte en français",
  "action": "ALERT/MONITOR/OK"
}}"""


def analyze_with_gemini(frame, yolo_result: dict, zone: str, reason: str) -> dict:
    """
    Envoie la frame à Gemini Vision pour analyse contextuelle.
    """
    try:
        if gemini_model is None:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        import PIL.Image
        import io
        import numpy as np

        # Convertir frame OpenCV → PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = PIL.Image.fromarray(frame_rgb)

        prompt = build_gemini_prompt(yolo_result, zone, reason)
        response = gemini_model.generate_content([prompt, pil_image])

        # Parser le JSON de la réponse
        raw_text = response.text.strip()

        # Nettoyer les balises markdown si présentes
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()

        result = json.loads(raw_text)
        result["source"] = "gemini_vision"
        result["timestamp"] = datetime.now().isoformat()
        return result

    except json.JSONDecodeError as e:
        print(f"[GEMINI] Erreur parsing JSON: {e}")
        return {
            "incident": True,  # Par précaution
            "severity": "medium",
            "confidence": 0.5,
            "explanation": "Erreur d'analyse LLM - vérification manuelle requise",
            "action": "MONITOR",
            "source": "gemini_error",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[GEMINI] Erreur API: {e}")
        return None


# ─────────────────────────────────────────
# ÉTAPE 4 : DÉCISION FINALE
# ─────────────────────────────────────────

def make_decision(yolo_result: dict, llm_result: dict | None, zone: str = "default") -> dict:
    """
    Combine les résultats YOLO + LLM pour une décision finale.
    """
    if llm_result:
        # LLM valide → décision basée sur LLM
        incident = llm_result.get("incident", False)
        severity = llm_result.get("severity", "low")
        action = llm_result.get("action", "OK")
        explanation = llm_result.get("explanation", "")
        source = "hybrid_yolo_gemini"
    else:
        # Pas de validation LLM → décision YOLO seule
        required = REQUIRED_EPI.get(zone, REQUIRED_EPI["default"])
        missing = [epi for epi in required if not yolo_result.get(epi, False)]
        incident = bool(missing) and yolo_result["person"]
        severity = "high" if "helmet" in missing else ("medium" if missing else "low")
        action = "ALERT" if incident else "OK"
        explanation = f"EPI manquants: {missing}" if missing else "Tous les EPI détectés"
        source = "yolo_only"

    return {
        "incident": incident,
        "severity": severity,
        "action": action,
        "explanation": explanation,
        "source": source,
        "yolo_confidence": yolo_result["min_confidence"],
        "llm_confidence": llm_result.get("confidence") if llm_result else None,
        "timestamp": datetime.now().isoformat()
    }


# ─────────────────────────────────────────
# ÉTAPE 5 : LOGGING & ALERTES
# ─────────────────────────────────────────

def log_incident(decision: dict, frame=None, camera_id: str = "cam_01"):
    """Enregistre l'incident dans le fichier JSON et optionnellement sauvegarde la frame."""

    Path("logs").mkdir(exist_ok=True)
    Path("logs/frames").mkdir(exist_ok=True)

    # Charger ou créer le fichier de logs
    log_path = Path(INCIDENT_LOG_PATH)
    if log_path.exists():
        with open(log_path, "r") as f:
            logs = json.load(f)
    else:
        logs = {"incidents": [], "stats": {"total": 0, "alerts": 0}}

    incident_id = f"INC_{int(time.time())}"
    frame_path = None

    # Sauvegarder la frame si incident
    if frame is not None and decision["incident"]:
        frame_path = f"logs/frames/{incident_id}.jpg"
        cv2.imwrite(frame_path, frame)

    entry = {
        "id": incident_id,
        "camera": camera_id,
        "frame_path": frame_path,
        **decision
    }

    logs["incidents"].append(entry)
    logs["stats"]["total"] += 1
    if decision["action"] == "ALERT":
        logs["stats"]["alerts"] += 1

    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    print(f"[LOG] Incident {incident_id} enregistré - Sévérité: {decision['severity']}")
    return incident_id


def send_alert(decision: dict, incident_id: str, camera_id: str):
    """Affiche une alerte console (extensible vers email/webhook)."""
    severity_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    icon = severity_icons.get(decision["severity"], "⚪")

    print(f"\n{'='*60}")
    print(f"{icon} ALERTE SÉCURITÉ - {incident_id}")
    print(f"{'='*60}")
    print(f"Caméra    : {camera_id}")
    print(f"Sévérité  : {decision['severity'].upper()}")
    print(f"Explication: {decision['explanation']}")
    print(f"Source    : {decision['source']}")
    print(f"Heure     : {decision['timestamp']}")
    print(f"{'='*60}\n")


# ─────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────


# ─────────────────────────────────────────
# THREAD GEMINI — consommateur asynchrone
# ─────────────────────────────────────────

class GeminiWorker(threading.Thread):
    """
    Thread dédié à Gemini Vision.

    Consomme une queue de taille 1 :
      - Si Gemini est déjà occupé  → la nouvelle frame est ignorée (skip).
      - Quand la réponse arrive    → stockée dans _latest, partagée avec le
        thread principal via get_latest().

    La vidéo + YOLO ne bloquent jamais sur ce worker.
    """
    def __init__(self, zone: str):
        super().__init__(daemon=True, name="GeminiWorker")
        self.zone = zone
        self.inbox: queue.Queue = queue.Queue(maxsize=1)
        self._latest: dict | None = None
        self._lock = threading.Lock()
        self._running = True
        self.processing = False

    def enqueue(self, frame, yolo_result: dict, reason: str) -> bool:
        """Essaie d'envoyer une frame. Retourne False si Gemini est occupé."""
        try:
            self.inbox.put_nowait((frame.copy(), yolo_result, reason))
            return True
        except queue.Full:
            return False

    def get_latest(self) -> dict | None:
        with self._lock:
            return self._latest

    def stop(self):
        self._running = False
        try:
            self.inbox.put_nowait(None)
        except queue.Full:
            pass

    def run(self):
        print("[GEMINI] Worker prêt ✓")
        while self._running:
            item = self.inbox.get()
            if item is None:
                break
            frame, yolo_result, reason = item
            self.processing = True
            t0 = time.time()
            print(f"[GEMINI] ▶ Envoi — raison: {reason}")
            result = analyze_with_gemini(frame, yolo_result, self.zone, reason)
            elapsed = time.time() - t0
            if result:
                with self._lock:
                    self._latest = result
                print(f"[GEMINI] ✓ {elapsed:.1f}s — {result.get('action','?')} — {result.get('explanation','')[:50]}")
            else:
                print(f"[GEMINI] ✗ Échec après {elapsed:.1f}s")
            self.processing = False
        print("[GEMINI] Worker arrêté")



def run_pipeline(source=0, zone: str = "construction", camera_id: str = "cam_01"):
    """
    Pipeline asynchrone non-bloquant.

      Thread principal → lecture vidéo + YOLO sur chaque frame + décision immédiate
      GeminiWorker     → reçoit les frames éligibles via queue(1), enrichit la
                         décision quand il a terminé, sans jamais bloquer la vidéo.

    La vidéo joue TOUJOURS à pleine vitesse.
    Gemini ne reçoit une nouvelle frame que lorsqu'il a fini la précédente
    ET que LLM_MIN_INTERVAL secondes se sont écoulées (garde-fou).
    """
    print(f"\n{'='*60}")
    print(f"[PIPELINE] Démarrage — mode asynchrone")
    print(f"{'='*60}")
    print(f"Zone            : {zone}")
    print(f"Caméra          : {camera_id}")
    print(f"Seuil confiance : {CONFIDENCE_THRESHOLD}")
    print(f"EPI requis      : {REQUIRED_EPI.get(zone)}")
    print(f"Source          : {'Webcam' if source == 0 else source}")
    print(f"Intervalle LLM  : >= {LLM_MIN_INTERVAL}s (ou latence API Gemini si plus long)")
    print(f"{'='*60}\n")

    model = load_yolo()

    print("[INIT] Ouverture de la source vidéo...", end=" ", flush=True)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir: {source}")
    print("✓")

    if isinstance(source, str):
        fps    = cap.get(cv2.CAP_PROP_FPS) or 25
        n_fr   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[VIDEO] {width}x{height} @ {fps:.1f}fps  —  {n_fr} frames\n")

    # ── Démarrer le worker Gemini ─────────────────────────────────────────
    gemini_worker = GeminiWorker(zone=zone)
    gemini_worker.start()
    print("[PIPELINE] Thread Gemini démarré ✓\n")

    frame_count     = 0
    last_llm_submit = 0.0

    try:
        import ctypes
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    except Exception:
        screen_h = 900
    display_w = 1000

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if isinstance(source, str):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                print("[PIPELINE] Fin du flux")
                break

            frame_count += 1
            now = time.time()

            # ── Étape 1 : YOLO sur chaque frame (jamais sauté) ───────────
            yolo_result = detect_yolo(model, frame)

            # ── Étape 2 : Filtrage ────────────────────────────────────────
            needs_llm, reason = needs_llm_validation(yolo_result, zone)

            # ── Étape 3 : Soumettre à Gemini si éligible, non-bloquant ───
            #   Conditions : frame éligible + délai MIN respecté + queue libre
            if needs_llm and (now - last_llm_submit) >= LLM_MIN_INTERVAL:
                if gemini_worker.enqueue(frame, yolo_result, reason):
                    last_llm_submit = now
                    # si enqueue retourne False → Gemini encore occupé → on skip

            # ── Étape 4 : Décision = YOLO + dernier résultat LLM connu ───
            latest_llm = gemini_worker.get_latest()
            decision   = make_decision(yolo_result, latest_llm, zone)

            # ── Étape 5 : Alerte & log ────────────────────────────────────
            if decision["action"] in ("ALERT", "MONITOR"):
                incident_id = log_incident(decision, frame, camera_id)
                if decision["action"] == "ALERT":
                    send_alert(decision, incident_id, camera_id)

            # ── Affichage ─────────────────────────────────────────────────
            llm_pending = gemini_worker.processing
            annotated   = draw_overlay(frame, yolo_result, decision, reason if needs_llm else "ok")

            window_name = f"Pipeline EPI — {camera_id}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            h, w  = annotated.shape[:2]
            dh    = int(h * (display_w / w))
            if dh > screen_h:
                dh = screen_h
                display_w_adj = int(w * (dh / h))
            else:
                display_w_adj = display_w
            cv2.imshow(window_name, cv2.resize(annotated, (display_w_adj, dh)))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[PIPELINE] Arrêt (Q)")
                break

    finally:
        gemini_worker.stop()
        gemini_worker.join(timeout=5)
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n[PIPELINE] Terminé — {frame_count} frames traitées")


# ─────────────────────────────────────────
# OVERLAY VIDÉO
# ─────────────────────────────────────────

def draw_overlay(frame, yolo_result: dict, decision: dict, filter_reason: str, llm_pending: bool = False):
    """Dessine les informations de détection sur la frame."""
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Couleur selon sévérité
    color_map = {"high": (0, 0, 255), "medium": (0, 165, 255), "low": (0, 255, 0)}
    color = color_map.get(decision["severity"], (255, 255, 255))

    # Bandeau statut en haut
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    status = "⚠ ALERTE" if decision["incident"] else "✓ OK"
    cv2.putText(frame, f"{status} | {decision['explanation'][:50]}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    pend_label = "  [Gemini ▶▶]" if llm_pending else ""
    cv2.putText(frame, f"Source: {decision['source']} | Conf: {yolo_result['min_confidence']:.2f}{pend_label}",
                (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Dessiner les bounding boxes YOLO
    for det in yolo_result.get("raw", []):
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        det_color = (0, 255, 0) if det["class"] != "person" else color
        cv2.rectangle(frame, (x1, y1), (x2, y2), det_color, 2)
        label = f"{det['class']} {det['confidence']:.2f}"
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, det_color, 1)

    return frame


# ─────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Pipeline Hybride YOLO + Gemini EPI",
        epilog="Exemples:\n"
               "  python pipeline.py                          # Utilise la vidéo de test par défaut\n"
               "  python pipeline.py --webcam                 # Utilise la webcam\n"
               "  python pipeline.py --video chemin/video.mp4 # Utilise une vidéo personnalisée\n"
               "  python pipeline.py --video chemin/video.mp4 --zone welding  # Vidéo + zone soudure",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--video", dest="video_path", default=None, 
                        help="Chemin vers un fichier vidéo personnalisé")
    parser.add_argument("--webcam", action="store_true", 
                        help="Force l'utilisation de la webcam (sinon utilise la vidéo de test par défaut)")
    parser.add_argument("--test-video", action="store_true", 
                        help="Utilise explicitement la vidéo de test (défaut)")
    parser.add_argument("--zone", default="construction", choices=list(REQUIRED_EPI.keys()),
                        help="Zone de travail (détermine les EPI requis)")
    parser.add_argument("--camera-id", default="cam_01",
                        help="Identifiant de la caméra")
    parser.add_argument("--llm-interval", dest="llm_interval", type=float, default=LLM_MIN_INTERVAL,
                        help=f"Intervalle minimum entre deux envois à Gemini (défaut: {LLM_MIN_INTERVAL}s)")
    
    args = parser.parse_args()

    LLM_MIN_INTERVAL = args.llm_interval

    # Déterminer la source vidéo avec nouvelle logique par défaut
    try:
        # Priorité 1 : vidéo personnalisée en ligne de commande
        if args.video_path:
            source = get_video_source(
                use_test_video=False,
                custom_video_path=args.video_path
            )
        # Priorité 2 : webcam si --webcam
        elif args.webcam:
            source = 0
        # Priorité 3 : vidéo de test par défaut
        else:
            source = get_video_source(
                use_test_video=True,
                test_video_path=TEST_VIDEO_PATH
            )
    except FileNotFoundError as e:
        print(f"[ERREUR] {e}")
        exit(1)

    print()  # Ligne vide pour la lisibilité
    run_pipeline(source=source, zone=args.zone, camera_id=args.camera_id)