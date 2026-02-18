import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import time

# Simuler la détection (à remplacer par votre API backend)
def simulate_detection(image):
    time.sleep(1.5)
    mock_detections = [
        {
            "class": "casque",
            "confidence": 0.95,
            "bbox": [120, 50, 200, 150],
            "color": "#10b981"
        },
        {
            "class": "gilet",
            "confidence": 0.88,
            "bbox": [100, 200, 250, 400],
            "color": "#f59e0b"
        },
        {
            "class": "personne",
            "confidence": 0.92,
            "bbox": [80, 30, 300, 500],
            "color": "#3b82f6"
        }
    ]
    mock_stats = {
        "total": 3,
        "casque": 1,
        "gilet": 1,
        "personne": 1,
        "compliance": True,
        "processingTime": 0.15
    }
    return mock_detections, mock_stats

def draw_bboxes(image, detections):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for det in detections:
        x, y, w, h = det["bbox"]
        color = det["color"]
        draw.rectangle([x, y, w, h], outline=color, width=3)
        draw.rectangle([x, y-25, x+120, y], fill=color)
        label = f"{det['class']} {int(det['confidence']*100)}%"
        draw.text((x+5, y-20), label, fill="white", font=font)
    return img

st.set_page_config(page_title="Détection EPI", layout="wide")
st.title(" Détection d'Équipements de Protection Individuelle (EPI)")
st.caption("Système de détection d'équipements de protection individuelle")

mode = st.sidebar.radio("Mode", ["Image Test", "Webcam Test", "Vidéo Test "])

if mode == "Image Test":
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Image sélectionnée", width="content")
        if st.button("Détecter"):
            with st.spinner("Analyse en cours..."):
                detections, stats = simulate_detection(image)
                result_img = draw_bboxes(image, detections)
                st.image(result_img, caption="Résultat de la détection", width="content")
                st.success("Détection terminée !")
                st.write("**Statistiques :**")
                st.json(stats)
                st.write("**Détails des détections :**")
                for det in detections:
                    st.markdown(f"- **{det['class']}** : {det['confidence']*100:.1f}%")
                # Téléchargement du résultat
                buf = io.BytesIO()
                result_img.save(buf, format="JPEG")
                st.download_button("Télécharger le résultat", buf.getvalue(), "detection-result.jpg", "image/jpeg")
elif mode == "Webcam Test":
    st.info("La capture webcam ")
    picture = st.camera_input("Prenez une photo")
    if picture:
        image = Image.open(picture).convert("RGB")
        st.image(image, caption="Image capturée", width="content")
        if st.button("Détecter"):
            with st.spinner("Analyse en cours..."):
                detections, stats = simulate_detection(image)
                result_img = draw_bboxes(image, detections)
                st.image(result_img, caption="Résultat de la détection", width="content")
                st.success("Détection terminée !")
                st.write("**Statistiques :**")
                st.json(stats)
                st.write("**Détails des détections :**")
                for det in detections:
                    st.markdown(f"- **{det['class']}** : {det['confidence']*100:.1f}%")
                buf = io.BytesIO()
                result_img.save(buf, format="JPEG")
                st.download_button("Télécharger le résultat", buf.getvalue(), "detection-result.jpg", "image/jpeg")
else:
    st.warning("Le mode vidéo")

st.markdown("---")
st.caption("© 2026 Système de Détection EPI - Tous droits réservés")