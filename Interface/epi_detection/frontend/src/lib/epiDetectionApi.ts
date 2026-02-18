// Service pour appeler l'API de détection EPI
export async function detectEPI(imageBlob: Blob, cameraId?: string, watchedEpis?: string[]) {
  const formData = new FormData();
  formData.append('file', imageBlob, 'frame.jpg');
  if (cameraId) {
    formData.append('camera_id', cameraId);
  }
  if (watchedEpis) {
    formData.append('watched_epis', JSON.stringify(watchedEpis));
  }

  const response = await fetch('http://localhost:8000/api/detection/detect/', {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la détection EPI');
  }

  return response.json();
}
