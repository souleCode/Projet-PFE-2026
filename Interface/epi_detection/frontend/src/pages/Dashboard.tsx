import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  ShieldX,
  Camera,
  Cpu,
  User as UserIcon,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const statsTemplate = [
  {
    label: "Détections totales",
    value: 0,
    icon: AlertTriangle,
    color: "text-primary",
    bg: "bg-primary/10 border-primary/20",
  },
  {
    label: "Conformités EPI",
    value: 0,
    icon: ShieldX,
    color: "text-success",
    bg: "bg-success/10 border-success/20",
  },
  {
    label: "Non-conformités EPI",
    value: 0,
    icon: ShieldX,
    color: "text-destructive",
    bg: "bg-destructive/10 border-destructive/20",
  },
  {
    label: "Taux conformité (%)",
    value: 0,
    icon: Cpu,
    color: "text-warning",
    bg: "bg-warning/10 border-warning/20",
  },
  {
    label: "Caméras actives",
    value: 0,
    icon: Camera,
    color: "text-info",
    bg: "bg-info/10 border-info/20",
  },
];

const weeklyIncidents = [];
const incidentTypes = [];
const recentAlerts = [];
const cameras = [];
const edgeDevices = [];

const Dashboard = () => {
  const { user } = useAuth();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://pfe-api.digiscia.me";

  // States pour les données dynamiques
  const [stats, setStats] = useState(statsTemplate);
  const [weeklyIncidents, setWeeklyIncidents] = useState([]);
  const [incidentTypes, setIncidentTypes] = useState([]);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [edgeDevices, setEdgeDevices] = useState([]);

  useEffect(() => {
    // Récupérer stats incidents/détections
    fetch(`${API_BASE_URL}/api/detection/stats/`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        setStats(prev => [
          { ...prev[0], value: data.total || 0 },
          { ...prev[1], value: data.compliant || 0 },
          { ...prev[2], value: data.non_compliant || 0 },
          { ...prev[3], value: data.compliance_rate || 0 },
          { ...prev[4], value: prev[4].value }, // On ne touche pas à la stat Caméras actives ici
        ]);
        setWeeklyIncidents(data.weekly_incidents || []);
        setIncidentTypes(data.incident_types || []);
      });

    // Récupérer alertes récentes
    fetch(`${API_BASE_URL}/api/alerts/`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => setRecentAlerts(data.results || []));

    // Récupérer caméras actives
    fetch(`${API_BASE_URL}/api/cameras/active/`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        let cams = [];
        if (Array.isArray(data)) {
          cams = data;
        } else if (Array.isArray(data.results)) {
          cams = data.results;
        }
        setCameras(cams);
        // Mettre à jour la stat "Caméras actives" après avoir reçu la liste
        setStats(prev => {
          const updated = [...prev];
          if (updated[4]) updated[4].value = cams.length;
          return updated;
        });
      });

   
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Profil utilisateur */}
      {user && (
        <div className="flex items-center gap-4 mb-2 p-4 rounded-lg border border-border bg-muted/40">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <UserIcon size={28} className="text-primary" />
          </div>
          <div>
            <div className="font-semibold text-lg">{user.first_name} {user.last_name}</div>
            <div className="text-xs text-muted-foreground font-mono">{user.email}</div>
            <div className="text-xs text-muted-foreground font-mono">Rôle : {user.role}</div>
          </div>
        </div>
      )}
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground font-mono">
          Vue globale de la sécurité du site — {new Date().toLocaleDateString("fr-FR")}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div
            key={s.label}
            className={`rounded-lg border p-4 ${s.bg} flex items-start gap-4`}
          >
            <div className={`p-2 rounded-md ${s.bg}`}>
              <s.icon size={22} className={s.color} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
                {s.label}
              </p>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{s.value}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Bar chart */}
        <div className="lg:col-span-2 rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Incidents cette semaine</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={weeklyIncidents}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis dataKey="day" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <Tooltip
                contentStyle={{
                  background: "hsl(220, 18%, 12%)",
                  border: "1px solid hsl(220, 15%, 20%)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="incidents" fill="hsl(32, 95%, 52%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie chart */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Types d'incidents</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={incidentTypes}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                stroke="none"
              >
                {incidentTypes.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "hsl(220, 18%, 12%)",
                  border: "1px solid hsl(220, 15%, 20%)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1 mt-2">
            {incidentTypes.map((t) => (
              <div key={t.name} className="flex items-center gap-2 text-xs">
                <div className="w-2 h-2 rounded-full" style={{ background: t.color }} />
                <span className="text-muted-foreground">{t.name}</span>
                <span className="ml-auto font-mono">{t.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Caméras actives */}
      <div className="rounded-lg border border-border bg-card p-6 mb-6">
        <div className="font-semibold mb-2">Caméras actives</div>
        <div className="flex gap-4">
          {Array.isArray(cameras) && cameras.length > 0 ? (
            cameras.map((cam) => (
              <div
                key={cam.id}
                className={`px-4 py-2 rounded border ${
                  cam.active ? "border-green-500 bg-green-50" : "border-gray-300 bg-gray-100 text-gray-400"
                }`}
              >
                <div className="font-bold text-black">{cam.name}</div>
                <div className="text-xs text-gray-600">{cam.id}</div>
                <div className={`mt-1 w-2 h-2 rounded-full inline-block ${cam.active ? "bg-green-500" : "bg-gray-400"}`}></div>
              </div>
            ))
          ) : (
            <div className="text-muted-foreground text-xs">Aucune caméra active</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
