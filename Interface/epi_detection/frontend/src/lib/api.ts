const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function apiFetch(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include", // Envoie les cookies HttpOnly
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Erreur serveur");
  }

  if (response.status === 204) return null;
  return response.json();
}

export const authApi = {
  login: (email: string, password: string) =>
    apiFetch("/api/users/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    apiFetch("/api/users/logout/", { method: "POST" }),

  me: () => apiFetch("/api/users/me/"),

  register: (data: object) =>
    apiFetch("/api/users/register/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
