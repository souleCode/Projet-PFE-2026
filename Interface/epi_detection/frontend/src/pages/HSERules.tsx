import { useState, useEffect } from "react";
import { Shield, Plus, Pencil, Trash2, ToggleLeft, ToggleRight, Clock, MapPin, AlertTriangle } from "lucide-react";

interface HSERule {
  id: number;
  name: string;
  description: string;
  epi_type?: string;
  is_active: boolean;
  zone?: string;
  delay?: number;
}

const epiTypeLabel: Record<string, string> = {
  hardhat: "Casque",
  vest: "Gilet",
  mask: "Masque",
  gloves: "Gants",
  safety_glasses: "Lunettes",
  ear_protection: "Protection auditive",
};

const HSERules = () => {


  const [rules, setRules] = useState<HSERule[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    epi_criticites: [{ epi: "hardhat", criticite: "Moyenne" }],
    is_active: true,
    zone: "",
    delay: 3,
    cameras: [] as number[],
  });
  const [allCameras, setAllCameras] = useState<{id:number, name:string}[]>([]);
    // Charger la liste des caméras
    // API_BASE_URL doit être déclaré avant utilisation
    useEffect(() => {
      fetch(`${API_BASE_URL}/api/cameras/`, { credentials: "include" })
        .then(res => res.json())
        .then(data => setAllCameras(Array.isArray(data) ? data : data.results || []));
    }, []);
  const [editId, setEditId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const fetchRules = () => {
    fetch(`${API_BASE_URL}/api/rules/hse-rules/`, { credentials: "include" })
      .then(res => res.json())
      .then(data => setRules(Array.isArray(data) ? data : data.results || []));
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const activeCount = rules.filter((r) => r.is_active).length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Règles HSE</h1>
          <p className="text-sm text-muted-foreground font-mono">
            Configuration des règles de sécurité — {activeCount}/{rules.length} actives
          </p>
        </div>
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
          onClick={() => { setShowForm(true); setEditId(null); setForm({ name: "", description: "", epi_criticites: [{ epi: "hardhat", criticite: "Moyenne" }], is_active: true, zone: "", delay: 3, cameras: [] }); setError(null); }}
        >
          <Plus size={16} />
          Nouvelle règle
        </button>
            {/* Modal Formulaire d'ajout */}
            {showForm && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
                <div className="bg-white dark:bg-background rounded-lg shadow-lg p-6 w-full max-w-md relative">
                  <button
                    className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
                    onClick={() => setShowForm(false)}
                  >
                    ×
                  </button>
                  <h2 className="text-lg font-bold mb-4">{editId ? "Modifier la règle" : "Nouvelle règle HSE"}</h2>
                  {error && <div className="text-destructive text-sm mb-2">{error}</div>}
                  <form
                    onSubmit={async (e) => {
                      e.preventDefault();
                      setLoading(true);
                      setError(null);
                      try {
                        let payload = { ...form };
                        // Pour compatibilité backend, si epi_types est un tableau d'un seul élément, envoie-le quand même comme tableau
                        let res;
                        if (editId) {
                          res = await fetch(`${API_BASE_URL}/api/rules/hse-rules/${editId}/`, {
                            method: "PATCH",
                            headers: { "Content-Type": "application/json" },
                            credentials: "include",
                            body: JSON.stringify(payload),
                          });
                        } else {
                          res = await fetch(`${API_BASE_URL}/api/rules/hse-rules/`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            credentials: "include",
                            body: JSON.stringify(payload),
                          });
                        }
                        if (!res.ok) throw new Error("Erreur lors de la sauvegarde");
                        setShowForm(false);
                        setEditId(null);
                        setForm({ name: "", description: "", epi_criticites: [{ epi: "hardhat", criticite: "Moyenne" }], is_active: true, zone: "", delay: 3, cameras: [] });
                        fetchRules();
                      } catch (err) {
                        setError("Impossible de sauvegarder la règle.");
                      } finally {
                        setLoading(false);
                      }
                    }}
                  >
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Nom</label>
                      <input
                        className="w-full border rounded px-2 py-1"
                        required
                        value={form.name}
                        onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                      />
                    </div>
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Description</label>
                      <textarea
                        className="w-full border rounded px-2 py-1"
                        value={form.description}
                        onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                      />
                    </div>
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Types EPI & Criticité</label>
                      <div className="flex flex-col gap-2">
                        {Object.entries(epiTypeLabel).map(([value, label]) => {
                          const idx = form.epi_criticites.findIndex(ec => ec.epi === value);
                          const checked = idx !== -1;
                          return (
                            <div key={value} className="flex items-center gap-2">
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={e => {
                                  setForm(f => {
                                    let epi_criticites = [...f.epi_criticites];
                                    if (e.target.checked) {
                                      epi_criticites.push({ epi: value, criticite: "Moyenne" });
                                    } else {
                                      epi_criticites = epi_criticites.filter(ec => ec.epi !== value);
                                    }
                                    return { ...f, epi_criticites };
                                  });
                                }}
                              />
                              <span>{label}</span>
                              {checked && (
                                <select
                                  className="border rounded px-1 py-0.5 text-xs"
                                  value={form.epi_criticites[idx].criticite}
                                  onChange={e => {
                                    setForm(f => {
                                      const epi_criticites = f.epi_criticites.map((ec, i) =>
                                        i === idx ? { ...ec, criticite: e.target.value } : ec
                                      );
                                      return { ...f, epi_criticites };
                                    });
                                  }}
                                >
                                  <option value="Faible">Faible</option>
                                  <option value="Moyenne">Moyenne</option>
                                  <option value="Haute">Haute</option>
                                </select>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Caméras concernées</label>
                      <div className="flex flex-wrap gap-2">
                        {allCameras.map(cam => (
                          <label key={cam.id} className="flex items-center gap-1 text-xs">
                            <input
                              type="checkbox"
                              checked={form.cameras.includes(cam.id)}
                              onChange={e => {
                                setForm(f => {
                                  const cameras = e.target.checked
                                    ? [...f.cameras, cam.id]
                                    : f.cameras.filter(id => id !== cam.id);
                                  return { ...f, cameras };
                                });
                              }}
                            />
                            {cam.name}
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Zone</label>
                      <input
                        className="w-full border rounded px-2 py-1"
                        value={form.zone}
                        onChange={e => setForm(f => ({ ...f, zone: e.target.value }))}
                      />
                    </div>
                    <div className="mb-2">
                      <label className="block text-xs font-semibold mb-1">Délai (secondes)</label>
                      <input
                        type="number"
                        className="w-full border rounded px-2 py-1"
                        value={form.delay}
                        min={1}
                        onChange={e => setForm(f => ({ ...f, delay: Number(e.target.value) }))}
                      />
                    </div>
                    <div className="mb-4 flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={form.is_active}
                        onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
                        id="active"
                      />
                      <label htmlFor="active" className="text-xs">Active</label>
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-primary text-primary-foreground rounded px-4 py-2 font-semibold"
                      disabled={loading}
                    >
                      {loading ? "Ajout..." : "Ajouter"}
                    </button>
                  </form>
                </div>
              </div>
            )}
      </div>

      {/* Rules list */}
      <div className="space-y-3">
        {rules.map((rule) => (
          <div
            key={rule.id}
            className={`rounded-lg border bg-card p-4 transition-opacity ${
              rule.is_active ? "border-border" : "border-border opacity-50"
            }`}
          >
            <div className="flex items-start gap-4">
              {/* Toggle (à implémenter plus tard) */}
              <span className="mt-0.5 shrink-0">
                {rule.is_active ? (
                  <ToggleRight size={28} className="text-success" />
                ) : (
                  <ToggleLeft size={28} className="text-muted-foreground" />
                )}
              </span>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-sm">{rule.name}</h3>
                  {rule.epi_type && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold border bg-muted text-muted-foreground">
                      {epiTypeLabel[rule.epi_type] || rule.epi_type}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mb-2">{rule.description}</p>
                <div className="flex flex-wrap gap-3 text-xs font-mono text-muted-foreground">
                  {rule.zone && (
                    <span className="flex items-center gap-1">
                      <MapPin size={10} />
                      {rule.zone}
                    </span>
                  )}
                  {/* Caméras associées */}
                  {Array.isArray((rule as any).cameras) && (rule as any).cameras.length > 0 && (
                    <span className="flex items-center gap-1">
                      {((rule as any).cameras as number[])
                        .map(cid => {
                          const cam = allCameras.find(c => c.id === cid);
                          return cam ? cam.name : `Caméra ${cid}`;
                        })
                        .join(", ")}
                    </span>
                  )}
                  {rule.delay && (
                    <span className="flex items-center gap-1">
                      <Clock size={10} />
                      Délai: {rule.delay}s
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-1 shrink-0">
                <button
                  className="p-2 rounded-md hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    setShowForm(true);
                    setEditId(rule.id);
                    setForm({
                      name: rule.name,
                      description: rule.description,
                      epi_criticites: Array.isArray((rule as any).epi_criticites) ? (rule as any).epi_criticites : [],
                      is_active: rule.is_active,
                      zone: rule.zone || "",
                      delay: rule.delay || 3,
                      cameras: Array.isArray((rule as any).cameras) ? (rule as any).cameras : [],
                    });
                    setError(null);
                  }}
                >
                  <Pencil size={14} />
                </button>
                <button
                  className="p-2 rounded-md hover:bg-destructive/10 transition-colors text-muted-foreground hover:text-destructive"
                  onClick={async () => {
                    if (!window.confirm("Supprimer cette règle ?")) return;
                    setLoading(true);
                    try {
                      await fetch(`${API_BASE_URL}/api/rules/hse-rules/${rule.id}/`, {
                        method: "DELETE",
                        credentials: "include",
                      });
                      fetchRules();
                    } finally {
                      setLoading(false);
                    }
                  }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HSERules;
