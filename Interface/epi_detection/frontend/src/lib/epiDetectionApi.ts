const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'https://pfe-api.digiscia.me';

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

  const response = await fetch(`${API_URL}/api/detection/detect/`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Erreur lors de la détection EPI');
  }

  return response.json();
}
