import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { Users, Cpu, Cloud, Shield, UserPlus, Settings } from "lucide-react";

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: "admin" | "operateur" | "superviseur";
  lastLogin: string;
  active: boolean;
}

const mockUsers: User[] = [
  { id: 1, first_name: "Ahmed", last_name: "Benali", email: "ahmed@site.dz", role: "admin", lastLogin: "2026-02-12 08:30", active: true },
  { id: 2, first_name: "Karim", last_name: "Djellal", email: "karim@site.dz", role: "operateur", lastLogin: "2026-02-12 07:45", active: true },
  { id: 3, first_name: "Sarah", last_name: "Bouzid", email: "sarah@site.dz", role: "superviseur", lastLogin: "2026-02-11 16:20", active: true },
  { id: 4, first_name: "Yacine Hamidi", last_name: "Hamidi", email: "yacine@site.dz", role: "operateur", lastLogin: "2026-02-10 09:00", active: false },
];

const roleConfig = {
  admin:       { label: "Administrateur",  color: "bg-primary/20 text-primary" },
  superviseur: { label: "Superviseur",     color: "bg-success/20 text-success" },
  operateur:   { label: "Opérateur",       color: "bg-muted text-muted-foreground" },
};
const edgeDevices = [
  { id: "EDGE-01", name: "Jetson Orin - Entrée", status: "online", gpu: "78%", temp: "62°C", cameras: 2 },
  { id: "EDGE-02", name: "Jetson Orin - Atelier", status: "online", gpu: "65%", temp: "58°C", cameras: 2 },
];

const Admin = () => {
  const { user, loading } = useAuth();
  const [tab, setTab] = useState<"users" | "edge" | "cloud">("users");
  const [users, setUsers] = useState<User[]>([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password2: '',
    role: 'operateur',
  });
  const [addError, setAddError] = useState<string | null>(null);
  const [addLoading, setAddLoading] = useState(false);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    if (tab === "users") {
      setUsersLoading(true);
      fetch(`${API_BASE_URL}/api/users/`, { credentials: "include" })
        .then(res => res.json())
        .then(data => {
          setUsers(Array.isArray(data) ? data : data.results || []);
        })
        .finally(() => setUsersLoading(false));
    }
  }, [tab]);

  if (loading) return <div className="p-6">Chargement...</div>;
  if (!user || user.role !== "admin") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background to-muted">
      <div className="rounded-lg border border-border bg-card p-8 shadow-lg max-w-md w-full">
        <div className="flex justify-center mb-4">
        <Shield size={48} className="text-destructive" />
        </div>
        <h1 className="text-2xl font-bold text-center mb-2">Accès Refusé</h1>
        <p className="text-muted-foreground text-center text-sm mb-6">
        Cette section est réservée aux administrateurs. Vous n'avez pas les permissions nécessaires pour accéder à ce panneau de contrôle.
        </p>
        <div className="bg-destructive/10 border border-destructive/30 rounded-md p-4 text-center">
        <p className="text-xs font-mono text-destructive font-semibold">
          {user?.role?.toUpperCase() || 'UNKNOWN'} - ACCÈS NON AUTORISÉ
        </p>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-6">
        Contactez un administrateur pour plus d'informations.
        </p>
      </div>
      </div>
    );
  }

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

      {tab === "users" && (
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              {/* Utilisateurs */}
            </h2>
            <button
              className="inline-flex items-center gap-1 px-4 py-2 rounded bg-primary text-white hover:bg-primary/90 shadow transition focus:outline-none focus:ring-2 focus:ring-primary/50"
              onClick={() => setShowAddModal(true)}
            >
              <UserPlus className="w-4 h-4" /> Ajouter
            </button>
          </div>
          {/* Modal for adding user */}
          {showAddModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-black/40">
              <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md relative animate-fade-in border border-primary/20">
                <button
                  className="absolute top-3 right-3 text-xl text-muted-foreground hover:text-destructive bg-muted/40 rounded-full w-8 h-8 flex items-center justify-center transition"
                  onClick={() => { setShowAddModal(false); setAddError(null); }}
                  aria-label="Fermer"
                  type="button"
                  tabIndex={0}
                >
                  ×
                </button>
                <div className="flex items-center gap-2 mb-4">
                  <UserPlus className="w-6 h-6 text-primary" />
                  <h3 className="text-xl font-bold tracking-tight">Créer un utilisateur</h3>
                </div>
                <form
                  className="space-y-4"
                  autoComplete="off"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    setAddLoading(true);
                    setAddError(null);
                    if (addForm.password !== addForm.password2) {
                      setAddError("Les mots de passe ne correspondent pas.");
                      setAddLoading(false);
                      return;
                    }
                    try {
                      const res = await fetch(`${API_BASE_URL}/api/users/register/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(addForm),
                      });
                      if (!res.ok) {
                        const err = await res.json().catch(() => ({}));
                        throw new Error(err.detail || 'Erreur lors de la création');
                      }
                      setShowAddModal(false);
                      setAddForm({ first_name: '', last_name: '', email: '', password: '', password2: '', role: 'observer' });
                      setUsersLoading(true);
                      // Refresh user list
                      fetch(`${API_BASE_URL}/api/users/`, { credentials: "include" })
                        .then(res => res.json())
                        .then(data => setUsers(Array.isArray(data) ? data : data.results || []))
                        .finally(() => setUsersLoading(false));
                    } catch (err: any) {
                      setAddError(err.message);
                    } finally {
                      setAddLoading(false);
                    }
                  }}
                >
                  <div className="flex flex-col gap-2 md:flex-row">
                    <div className="flex-1">
                      <label className="block text-xs font-semibold mb-1 text-muted-foreground">Prénom *</label>
                      <input
                        className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                        placeholder="Prénom"
                        value={addForm.first_name}
                        onChange={e => setAddForm(f => ({ ...f, first_name: e.target.value }))}
                        required
                        autoFocus
                      />
                    </div>
                    <div className="flex-1">
                      <label className="block text-xs font-semibold mb-1 text-muted-foreground">Nom</label>
                      <input
                        className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                        placeholder="Nom"
                        value={addForm.last_name}
                        onChange={e => setAddForm(f => ({ ...f, last_name: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1 text-muted-foreground">Email *</label>
                    <input
                      className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                      type="email"
                      placeholder="Email"
                      value={addForm.email}
                      onChange={e => setAddForm(f => ({ ...f, email: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-2 md:flex-row">
                    <div className="flex-1">
                      <label className="block text-xs font-semibold mb-1 text-muted-foreground">Mot de passe *</label>
                      <input
                        className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                        type="password"
                        placeholder="Mot de passe"
                        value={addForm.password}
                        onChange={e => setAddForm(f => ({ ...f, password: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="flex-1">
                      <label className="block text-xs font-semibold mb-1 text-muted-foreground">Confirmer le mot de passe *</label>
                      <input
                        className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                        type="password"
                        placeholder="Confirmer le mot de passe"
                        value={addForm.password2}
                        onChange={e => setAddForm(f => ({ ...f, password2: e.target.value }))}
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1 text-muted-foreground">Rôle *</label>
                    <select
                      className="w-full px-3 py-2 border border-border rounded bg-white focus:outline-none focus:ring-2 focus:ring-primary/40 text-base"
                      value={addForm.role}
                      onChange={e => setAddForm(f => ({ ...f, role: e.target.value }))}
                      required
                    >
                      <option value="operateur">Opérateur</option>
                      <option value="superviseur">Superviseur</option>
                      <option value="admin">Administrateur</option>
                    </select>
                  </div>
                  {addError && <div className="text-destructive text-sm font-semibold border border-destructive/30 bg-destructive/10 rounded p-2 mt-2 text-center">{addError}</div>}
                  <button
                    type="submit"
                    className="btn btn-primary w-full mt-4 py-2 text-base font-semibold shadow-lg"
                    disabled={addLoading}
                  >
                    {addLoading ? 'Création...' : 'Créer'}
                  </button>
                </form>
              </div>
            </div>
          )}
          <div className="overflow-x-auto rounded-lg border border-border">
            {usersLoading ? (
              <div className="p-4 text-center text-muted-foreground">Chargement...</div>
            ) : (
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-muted text-muted-foreground">
                    <th className="px-4 py-2 text-left">Nom</th>
                    <th className="px-4 py-2 text-left">Prénom(s)</th>
                    <th className="px-4 py-2 text-left">Email</th>
                    <th className="px-4 py-2 text-left">Rôle</th>
              
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-t">
                      <td className="px-4 py-2 font-medium">{u.last_name || '-'}</td>
                      <td className="px-4 py-2">{u.first_name || '-'}</td>
                      <td className="px-4 py-2">{u.email}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-mono ${roleConfig[u.role]?.color || ''}`}>{roleConfig[u.role]?.label || u.role}</span>
                      </td>
                  
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
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
