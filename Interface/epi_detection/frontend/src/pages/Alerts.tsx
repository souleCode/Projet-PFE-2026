import React, { useEffect, useState } from "react";
import axios from "axios";

type Alert = {
  id: number;
  camera_id: string;
  timestamp: string;
  epi_missing: string[];
  criticity: string;
  image_path?: string;
  status: string;
};

const STATUS_LABELS = {
  nouveau: "Nouveau",
  en_cours: "En cours",
  résolu: "Résolu",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: 1,
      camera_id: "CAM-01",
      timestamp: "2026-02-16T10:15:00Z",
      epi_missing: ["hardhat", "gloves"],
      criticity: "élevée",
      image_path: "incidents/incident1.jpg",
      status: "nouveau",
    },
    {
      id: 2,
      camera_id: "CAM-02",
      timestamp: "2026-02-16T11:20:00Z",
      epi_missing: ["safety_vest"],
      criticity: "moyenne",
      image_path: "incidents/incident2.jpg",
      status: "en_cours",
    },
    {
      id: 3,
      camera_id: "CAM-03",
      timestamp: "2026-02-16T12:30:00Z",
      epi_missing: ["mask"],
      criticity: "faible",
      image_path: "incidents/incident3.jpg",
      status: "résolu",
    },
  ]);

  // Simule le changement de statut localement
  const updateStatus = (id: number, status: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status } : a))
    );
  };

  return (
    <div className="p-4">
      <h2 className="font-bold text-2xl mb-6 text-primary">Alertes</h2>
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
                <td className="px-4 py-2 font-mono text-xs">{alert.camera_id}</td>
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
                  {alert.image_path && (
                    <a
                      href={`/${alert.image_path}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline text-primary hover:text-primary/80"
                    >
                      Voir
                    </a>
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