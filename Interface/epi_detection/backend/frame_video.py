import cv2
import os
from pathlib import Path

def extract_and_filter(video_path, output_dir, interval=5, max_images=500):
    """
    Extrait des frames et s'arrête après max_images.
    """
    # Vérifier que le fichier existe
    if not os.path.exists(video_path):
        print(f"❌ Erreur : Fichier '{video_path}' introuvable")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    
    # Vérifier que la vidéo s'ouvre correctement
    if not cap.isOpened():
        print(f"❌ Erreur : Impossible d'ouvrir '{video_path}'")
        print("Vérifiez que :")
        print("  - Le fichier n'est pas corrompu")
        print("  - Le codec est supporté")
        print("  - OpenCV est bien installé : pip install opencv-python")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Vérifier que le FPS est valide
    if fps == 0 or fps is None:
        print(f"⚠️  FPS invalide détecté, utilisation de 30 FPS par défaut")
        fps = 30.0
    
    if total_frames == 0:
        print(f"⚠️  Durée inconnue, extraction jusqu'à la fin")
        duration_sec = None
    else:
        duration_sec = total_frames / fps
        print(f"📹 Vidéo : {duration_sec/60:.1f}min, {fps:.1f} FPS, {total_frames} frames")
    
    print(f"🎯 Extraction : 1 image / {interval}s (max {max_images})")
    
    frame_interval = int(fps * interval)
    frame_count = 0
    saved_count = 0
    
    try:
        while saved_count < max_images:
            ret, frame = cap.read()
            if not ret:
                print(f"\n⚠️  Fin de vidéo atteinte à {frame_count} frames")
                break
            
            if frame_count % frame_interval == 0:
                output_path = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
                success = cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                if success:
                    saved_count += 1
                    if saved_count % 50 == 0:
                        print(f"✓ {saved_count}/{max_images}")
                else:
                    print(f"❌ Erreur d'écriture : {output_path}")
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrompu par l'utilisateur")
    
    finally:
        cap.release()
        print(f"\n✅ {saved_count} images extraites dans '{output_dir}'")

# Utilisation
if __name__ == "__main__":
    extract_and_filter(
        video_path="video.mp4",  # ← Changez le nom ici
        output_dir="dataset/images",
        interval=5,
        max_images=500
    )