from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()

# Autoriser CORS pour le frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle une seule fois
model = YOLO("models/best.pt")
CLASS_NAMES = ["glass", "hardhat", "vest", "person"]
CLASS_COLORS = ["#eab308", "#10b981", "#f59e0b", "#3b82f6"]

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list
    color: str

class DetectionResponse(BaseModel):
    detections: list
    stats: dict

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = model(image)
    detections = []
    stats = {name: 0 for name in CLASS_NAMES}
    stats["total"] = 0

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = CLASS_NAMES[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox = [x1, y1, x2, y2]
            color = CLASS_COLORS[cls_id]
            detections.append({
                "class": class_name,
                "confidence": conf,
                "bbox": bbox,
                "color": color
            })
            stats[class_name] += 1
            stats["total"] += 1

    # Compliance simple: au moins 1 hardhat, 1 vest, 1 person
    stats["compliance"] = stats["hardhat"] > 0 and stats["vest"] > 0 and stats["person"] > 0
    stats["processingTime"] = round(results[0].speed["inference"]/1000, 2) if hasattr(results[0], "speed") else 0.0

    return {"detections": detections, "stats": stats}