import React, { useEffect, useState } from "react";

type Alert = {
  id: number;
  camera: number | string;
  camera_name?: string;
  timestamp: string;
  epi_missing: string[];
  criticity: string;
  image_url?: string;
  status: string;
};

const STATUS_LABELS = {
  nouveau: "Nouveau",
  en_cours: "En cours",
  résolu: "Résolu",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE_URL}/api/alerts/?page=${page}&page_size=${pageSize}`, { credentials: "include" })
      .then(res => res.json())
      .then(data => {
        setAlerts(Array.isArray(data) ? data : data.results || []);
        setCount(data.count || (Array.isArray(data) ? data.length : 0));
      })
      .catch(() => {
        setAlerts([]);
        setCount(0);
      })
      .finally(() => setLoading(false));
  }, [page, pageSize]);

  // Simule le changement de statut localement
  const updateStatus = (id: number, status: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status } : a))
    );
  };

  const totalPages = Math.ceil(count / pageSize);

  return (
    <div className="p-4">
      <h2 className="font-bold text-2xl mb-6 text-primary">Alertes</h2>
      <div className="mb-4 flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Page {page} / {totalPages || 1}</span>
        <button
          className="px-2 py-1 rounded bg-muted text-muted-foreground border hover:bg-primary/10 disabled:opacity-50"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1 || loading}
        >Précédent</button>
        <button
          className="px-2 py-1 rounded bg-muted text-muted-foreground border hover:bg-primary/10 disabled:opacity-50"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages || loading}
        >Suivant</button>
        <label className="ml-4 text-sm">Taille page:
          <select
            className="ml-2 border rounded px-1 py-0.5"
            value={pageSize}
            onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
            disabled={loading}
          >
            {[5, 10, 20, 50].map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </label>
        {loading && <span className="ml-4 text-xs text-muted-foreground">Chargement...</span>}
      </div>
      <div className="overflow-x-auto rounded-lg border border-border bg-card shadow">
        <table className="min-w-full text-sm">
          <thead className="bg-muted text-muted-foreground">
            <tr>
              <th className="px-4 py-2 text-left">Caméra</th>
              <th className="px-4 py-2 text-left">Manque EPI</th>
              <th className="px-4 py-2 text-left">Criticité</th>
              <th className="px-4 py-2 text-left">Image</th>
              <th className="px-4 py-2 text-left">Statut</th>
              <th className="px-4 py-2 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id} className="border-b last:border-b-0 hover:bg-primary/5 transition-colors">
                <td className="px-4 py-2 font-mono text-xs">{alert.camera_name || alert.camera}</td>
                <td className="px-4 py-2">
                  {alert.epi_missing.map((epi) => (
                    <span key={epi} className="inline-block bg-yellow-100 text-yellow-800 rounded px-2 py-0.5 text-xs font-semibold mr-1 mb-1">
                      {epi}
                    </span>
                  ))}
                </td>
                <td className="px-4 py-2">
                  <span className={
                    alert.criticity === "élevée"
                      ? "bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-bold"
                      : alert.criticity === "moyenne"
                      ? "bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-xs font-bold"
                      : "bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-bold"
                  }>
                    {alert.criticity}
                  </span>
                </td>
                <td className="px-4 py-2">
                  {alert.image_url ? (
                    <a
                      href={alert.image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline text-primary hover:text-primary/80"
                    >
                      <img src={alert.image_url} alt="Capture incident" className="h-10 w-16 object-cover rounded border" />
                    </a>
                  ) : (
                    <span className="text-muted-foreground text-xs">—</span>
                  )}
                </td>
                <td className="px-4 py-2">
                  <span className={
                    alert.status === "nouveau"
                      ? "bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-semibold"
                      : alert.status === "en_cours"
                      ? "bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-xs font-semibold"
                      : "bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-semibold"
                  }>
                    {STATUS_LABELS[alert.status]}
                  </span>
                </td>
                <td className="px-4 py-2">
                  {["nouveau", "en_cours", "résolu"].map((s) =>
                    s !== alert.status ? (
                      <button
                        key={s}
                        className={
                          "px-2 py-1 rounded text-xs font-mono font-semibold mr-1 " +
                          (s === "résolu"
                            ? "bg-green-500 text-white hover:bg-green-600"
                            : s === "en_cours"
                            ? "bg-orange-500 text-white hover:bg-orange-600"
                            : "bg-blue-500 text-white hover:bg-blue-600")
                        }
                        onClick={() => updateStatus(alert.id, s)}
                      >
                        {STATUS_LABELS[s]}
                      </button>
                    ) : null
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}