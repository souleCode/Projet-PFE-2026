const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "https://pfe-api.digiscia.me";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const isFormDataBody = typeof FormData !== "undefined" && options.body instanceof FormData;

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include", // Envoie les cookies HttpOnly
    headers: {
      ...options.headers,
      ...(isFormDataBody ? {} : { "Content-Type": "application/json" }),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const firstFieldError = Object.values(error).find((value) => Array.isArray(value) && value.length > 0);
    throw new Error(
      error.detail ||
      (Array.isArray(firstFieldError) ? String(firstFieldError[0]) : null) ||
      "Erreur serveur"
    );
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

export type AlertStatus = "nouveau" | "en_cours" | "resolu" | "ignore";
export type AuditStatus = "ouvert" | "en_cours" | "clos";
export type GeminiAnalysisStatus = "queued" | "processing" | "completed" | "failed" | "quota_skipped";

export interface AlertRecord {
  id: number;
  camera: number | string;
  camera_name?: string;
  timestamp: string;
  epi_missing: string[];
  criticity: string;
  image_url?: string;
  status: AlertStatus;
  notes?: string;
}

export interface AuditCaptureRecord {
  id: number;
  audit: number;
  image: string;
  image_url?: string;
  description?: string;
  taken_at: string;
  taken_by?: number;
  taken_by_name?: string;
}

export interface AuditRecord {
  id: number;
  title: string;
  camera?: number;
  camera_name?: string;
  alert?: number;
  alert_criticity?: string;
  created_by?: number;
  created_by_name?: string;
  status: AuditStatus;
  notes?: string;
  captures?: AuditCaptureRecord[];
  captures_count?: number;
  created_at: string;
  updated_at: string;
}

export interface GeminiContextAnalysisRecord {
  id: number;
  camera: number;
  camera_name?: string;
  alert?: number | null;
  alert_id?: number | null;
  detection_log?: number | null;
  non_compliance_state?: number | null;
  status: GeminiAnalysisStatus;
  missing_epi: string[];
  request_reason?: string;
  image_url?: string | null;
  severity?: string;
  action?: string;
  explanation?: string;
  llm_confidence?: number | null;
  result_json?: Record<string, unknown>;
  error_message?: string;
  requested_at: string;
  started_at?: string | null;
  next_retry_at?: string | null;
  retry_in_seconds?: number | null;
  processed_at?: string | null;
}

export interface GeminiProcessNextResponse {
  detail: string;
  daily_limit: number;
  analysis?: GeminiContextAnalysisRecord;
  next_retry_at?: string | null;
  retry_in_seconds?: number | null;
}

export const alertApi = {
  list: (page: number, pageSize: number) =>
    apiFetch(`/api/alerts/?page=${page}&page_size=${pageSize}`),

  update: (id: number, data: { status?: AlertStatus; assigned_to?: number; notes?: string }) =>
    apiFetch(`/api/alerts/${id}/update/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

export const auditApi = {
  list: (params?: { page?: number; pageSize?: number; status?: AuditStatus; cameraId?: number; alertId?: number }) => {
    const searchParams = new URLSearchParams();

    if (params?.page) searchParams.set("page", String(params.page));
    if (params?.pageSize) searchParams.set("page_size", String(params.pageSize));
    if (params?.status) searchParams.set("status", params.status);
    if (params?.cameraId) searchParams.set("camera_id", String(params.cameraId));
    if (params?.alertId) searchParams.set("alert_id", String(params.alertId));

    const query = searchParams.toString();
    return apiFetch(`/api/audits/${query ? `?${query}` : ""}`);
  },

  get: (id: number) => apiFetch(`/api/audits/${id}/`),

  create: (data: { title: string; camera?: number; alert?: number; notes?: string }) =>
    apiFetch("/api/audits/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: { title?: string; status?: AuditStatus; notes?: string }) =>
    apiFetch(`/api/audits/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  addCapture: (auditId: number, data: { image: File; description?: string }) => {
    const body = new FormData();
    body.append("image", data.image);
    if (data.description) {
      body.append("description", data.description);
    }

    return apiFetch(`/api/audits/${auditId}/captures/`, {
      method: "POST",
      body,
    });
  },
};

export const geminiAnalysisApi = {
  list: (params?: { status?: GeminiAnalysisStatus; cameraId?: number }) => {
    const searchParams = new URLSearchParams();

    if (params?.status) searchParams.set("status", params.status);
    if (params?.cameraId) searchParams.set("camera_id", String(params.cameraId));

    const query = searchParams.toString();
    return apiFetch(`/api/detection/gemini-analyses/${query ? `?${query}` : ""}`);
  },

  processNext: () =>
    apiFetch("/api/detection/gemini-analyses/process-next/", {
      method: "POST",
    }) as Promise<GeminiProcessNextResponse>,
};
