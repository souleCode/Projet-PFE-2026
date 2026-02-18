import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests

# URL de l'API FastAPI
API_URL = "http://localhost:8000/detect"

def detect_via_api(image):
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)
    files = {"file": ("image.jpg", buf, "image/jpeg")}
    response = requests.post(API_URL, files=files)
    response.raise_for_status()
    data = response.json()
    return data["detections"], data["stats"]

def draw_bboxes(image, detections):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        color = det["color"]
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        draw.rectangle([x1, y1-25, x1+120, y1], fill=color)
        label = f"{det['class']} {int(det['confidence']*100)}%"
        draw.text((x1+5, y1-20), label, fill="white", font=font)
    return img

st.set_page_config(page_title="Détection EPI", layout="wide")
st.title(" Détection d'Équipements de Protection Individuelle (EPI)")
st.caption("Système de détection d'équipements de protection individuelle - Projet PFE 2026")

mode = st.sidebar.radio("Mode", ["Image", "Webcam (expérimental)", "Vidéo (non supporté)"])

if mode == "Image":
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Image sélectionnée", width="content")
        if st.button("Détecter"):
            with st.spinner("Analyse en cours..."):
                try:
                    detections, stats = detect_via_api(image)
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
                except Exception as e:
                    st.error(f"Erreur lors de la détection : {e}")
elif mode == "Webcam (expérimental)":
    st.info("La capture webcam fonctionne uniquement sur certains navigateurs et environnements Streamlit.")
    picture = st.camera_input("Prenez une photo")
    if picture:
        image = Image.open(picture).convert("RGB")
        st.image(image, caption="Image capturée", width="content")
        if st.button("Détecter"):
            with st.spinner("Analyse en cours..."):
                try:
                    detections, stats = detect_via_api(image)
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
                except Exception as e:
                    st.error(f"Erreur lors de la détection : {e}")
else:
    st.warning("Le mode vidéo n'est pas encore supporté dans cette démo Streamlit.")

st.markdown("---")
st.caption("© 2026 Système de Détection EPI - Projet PFE | Modèle: YOLOv8s | mAP50: 92.19% | Recall: 100%")
