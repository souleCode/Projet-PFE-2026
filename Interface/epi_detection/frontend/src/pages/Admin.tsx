import { useState } from "react";
import { Users, Cpu, Cloud, Shield, UserPlus, Settings } from "lucide-react";

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "hse" | "observer";
  lastLogin: string;
  active: boolean;
}

const mockUsers: User[] = [
  { id: 1, name: "Ahmed Benaissa", email: "ahmed@site.dz", role: "admin", lastLogin: "2026-02-12 08:30", active: true },
  { id: 2, name: "Karim Medjdoub", email: "karim@site.dz", role: "hse", lastLogin: "2026-02-12 07:45", active: true },
  { id: 3, name: "Sarah Boudiaf", email: "sarah@site.dz", role: "hse", lastLogin: "2026-02-11 16:20", active: true },
  { id: 4, name: "Yacine Hamidi", email: "yacine@site.dz", role: "observer", lastLogin: "2026-02-10 09:00", active: false },
];

const roleConfig = {
  admin: { label: "Administrateur", color: "bg-primary/20 text-primary" },
  hse: { label: "Responsable HSE", color: "bg-success/20 text-success" },
  observer: { label: "Observateur", color: "bg-muted text-muted-foreground" },
};

const edgeDevices = [
  { id: "EDGE-01", name: "Jetson Orin - Entrée", status: "online", gpu: "78%", temp: "62°C", cameras: 2 },
  { id: "EDGE-02", name: "Jetson Orin - Atelier", status: "online", gpu: "65%", temp: "58°C", cameras: 2 },
  { id: "EDGE-03", name: "Jetson Nano - Stockage", status: "online", gpu: "45%", temp: "55°C", cameras: 1 },
  { id: "EDGE-04", name: "Jetson Nano - Quai", status: "offline", gpu: "-", temp: "-", cameras: 1 },
];

const Admin = () => {
  const [tab, setTab] = useState<"users" | "edge" | "cloud">("users");

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Administration</h1>
        <p className="text-sm text-muted-foreground font-mono">
          Gestion utilisateurs, Edge devices & paramètres Cloud
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border pb-px">
        {([
          { key: "users", icon: Users, label: "Utilisateurs" },
          { key: "edge", icon: Cpu, label: "Edge Devices" },
          { key: "cloud", icon: Cloud, label: "Cloud / Azure" },
        ] as const).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <t.icon size={16} />
            {t.label}
          </button>
        ))}
      </div>

      {/* Users */}
      {tab === "users" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90">
              <UserPlus size={16} />
              Ajouter utilisateur
            </button>
          </div>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="text-left p-3 font-medium text-muted-foreground">Nom</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Email</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Rôle</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Dernière connexion</th>
                  <th className="text-left p-3 font-medium text-muted-foreground">Statut</th>
                </tr>
              </thead>
              <tbody>
                {mockUsers.map((u) => (
                  <tr key={u.id} className="border-b border-border last:border-0 hover:bg-muted/20">
                    <td className="p-3 font-medium">{u.name}</td>
                    <td className="p-3 font-mono text-xs text-muted-foreground">{u.email}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${roleConfig[u.role].color}`}>
                        {roleConfig[u.role].label}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-xs text-muted-foreground">{u.lastLogin}</td>
                    <td className="p-3">
                      <div className={`w-2 h-2 rounded-full ${u.active ? "bg-success" : "bg-muted-foreground"}`} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Edge Devices */}
      {tab === "edge" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {edgeDevices.map((d) => (
            <div key={d.id} className="rounded-lg border border-border bg-card p-4">
              <div className="flex items-center gap-3 mb-3">
                <Cpu size={20} className={d.status === "online" ? "text-success" : "text-muted-foreground"} />
                <div>
                  <h3 className="font-semibold text-sm">{d.name}</h3>
                  <span className="font-mono text-xs text-muted-foreground">{d.id}</span>
                </div>
                <div className={`ml-auto w-2 h-2 rounded-full ${d.status === "online" ? "bg-success" : "bg-destructive"}`} />
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                <div className="rounded-md bg-muted/30 p-2 text-center">
                  <p className="text-muted-foreground">GPU</p>
                  <p className="font-semibold">{d.gpu}</p>
                </div>
                <div className="rounded-md bg-muted/30 p-2 text-center">
                  <p className="text-muted-foreground">Temp</p>
                  <p className="font-semibold">{d.temp}</p>
                </div>
                <div className="rounded-md bg-muted/30 p-2 text-center">
                  <p className="text-muted-foreground">Caméras</p>
                  <p className="font-semibold">{d.cameras}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Cloud */}
      {tab === "cloud" && (
        <div className="space-y-4">
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <Cloud size={24} className="text-primary" />
              <h3 className="font-semibold">Configuration Azure</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { label: "Azure IoT Hub", value: "epiguard-iothub.azure-devices.net", status: "Connecté" },
                { label: "Blob Storage", value: "epiguardstorage.blob.core.windows.net", status: "Connecté" },
                { label: "Azure SQL", value: "epiguard-db.database.windows.net", status: "Connecté" },
                { label: "Azure Functions", value: "epiguard-functions.azurewebsites.net", status: "Actif" },
              ].map((c) => (
                <div key={c.label} className="rounded-md border border-border p-3">
                  <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{c.label}</p>
                  <p className="text-sm font-mono mt-1 truncate">{c.value}</p>
                  <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-success/20 text-success">
                    {c.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin;
