import { useState } from "react";
import { Shield, Plus, Pencil, Trash2, ToggleLeft, ToggleRight, Clock, MapPin, AlertTriangle } from "lucide-react";

interface HSERule {
  id: number;
  name: string;
  description: string;
  condition: string;
  zone: string;
  severity: "critical" | "warning" | "info";
  active: boolean;
  delay?: number;
}

const initialRules: HSERule[] = [
  { id: 1, name: "Casque obligatoire", description: "Alerte si personne détectée sans casque", condition: "no_hardhat > 3s", zone: "Toutes zones", severity: "critical", active: true, delay: 3 },
  { id: 2, name: "Gilet obligatoire", description: "Alerte si personne sans gilet de sécurité", condition: "no_safety_vest > 3s", zone: "Toutes zones", severity: "critical", active: true, delay: 3 },
  { id: 3, name: "Zone interdite", description: "Alerte si personne entre dans une zone rouge", condition: "person_in_restricted_zone", zone: "Zone C, Zone D", severity: "critical", active: true },
  { id: 4, name: "Proximité engin", description: "Alerte si personne à moins de 2m d'un chariot", condition: "person_near_forklift < 2m", zone: "Zone B, Zone F", severity: "warning", active: true },
  { id: 5, name: "Lunettes obligatoires", description: "Alerte si absence de lunettes de protection", condition: "no_safety_glasses > 5s", zone: "Zone E", severity: "warning", active: true, delay: 5 },
  { id: 6, name: "Masque obligatoire", description: "Alerte si absence de masque en zone poussière", condition: "no_mask > 3s", zone: "Zone E", severity: "warning", active: false, delay: 3 },
  { id: 7, name: "Gants obligatoires", description: "Alerte si manipulation sans gants", condition: "no_gloves > 2s", zone: "Zone B", severity: "info", active: false, delay: 2 },
];

const severityConfig = {
  critical: { label: "Critique", color: "bg-destructive/20 text-destructive border-destructive/30" },
  warning: { label: "Avertissement", color: "bg-warning/20 text-warning border-warning/30" },
  info: { label: "Information", color: "bg-primary/20 text-primary border-primary/30" },
};

const HSERules = () => {
  const [rules, setRules] = useState(initialRules);

  const toggleRule = (id: number) => {
    setRules((prev) => prev.map((r) => (r.id === id ? { ...r, active: !r.active } : r)));
  };

  const activeCount = rules.filter((r) => r.active).length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Règles HSE</h1>
          <p className="text-sm text-muted-foreground font-mono">
            Configuration des règles de sécurité — {activeCount}/{rules.length} actives
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity">
          <Plus size={16} />
          Nouvelle règle
        </button>
      </div>

      {/* Rules list */}
      <div className="space-y-3">
        {rules.map((rule) => {
          const sev = severityConfig[rule.severity];
          return (
            <div
              key={rule.id}
              className={`rounded-lg border bg-card p-4 transition-opacity ${
                rule.active ? "border-border" : "border-border opacity-50"
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Toggle */}
                <button
                  onClick={() => toggleRule(rule.id)}
                  className="mt-0.5 shrink-0"
                >
                  {rule.active ? (
                    <ToggleRight size={28} className="text-success" />
                  ) : (
                    <ToggleLeft size={28} className="text-muted-foreground" />
                  )}
                </button>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-sm">{rule.name}</h3>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${sev.color}`}>
                      {sev.label}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{rule.description}</p>
                  <div className="flex flex-wrap gap-3 text-xs font-mono text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <AlertTriangle size={10} />
                      {rule.condition}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin size={10} />
                      {rule.zone}
                    </span>
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
                  <button className="p-2 rounded-md hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground">
                    <Pencil size={14} />
                  </button>
                  <button className="p-2 rounded-md hover:bg-destructive/10 transition-colors text-muted-foreground hover:text-destructive">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HSERules;
