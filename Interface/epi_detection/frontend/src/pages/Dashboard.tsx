import {AlertTriangle,
  ShieldX,
  Camera,
  Cpu,
  TrendingUp,
  TrendingDown,
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
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const stats = [
  {
    label: "Alertes critiques",
    value: 5,
   
    icon: AlertTriangle,
    color: "text-destructive",
    bg: "bg-destructive/10 border-destructive/20",
  },
  {
    label: "Non-conformités EPI",
    value: 12,
   
    icon: ShieldX,
    color: "text-warning",
    bg: "bg-warning/10 border-warning/20",
  },
  {
    label: "Caméras en ligne",
    value: 6,
  
    icon: Camera,
    color: "text-success",
    bg: "bg-success/10 border-success/20",
  },
  {
    label: "Edge Devices actifs",
    value: 4,
    
    icon: Cpu,
    color: "text-primary",
    bg: "bg-primary/10 border-primary/20",
  },
];

const weeklyIncidents = [
  { day: "Lun", incidents: 8 },
  { day: "Mar", incidents: 5 },
  { day: "Mer", incidents: 12 },
  { day: "Jeu", incidents: 7 },
  { day: "Ven", incidents: 15 },
  { day: "Sam", incidents: 3 },
  { day: "Dim", incidents: 1 },
];

const hourlyTrend = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}h`,
  alerts: Math.floor(Math.random() * 10 + (i > 6 && i < 18 ? 5 : 0)),
}));

const incidentTypes = [
  { name: "Sans casque", value: 35, color: "hsl(0, 72%, 51%)" },
  { name: "Sans gilet", value: 25, color: "hsl(45, 93%, 47%)" },
  { name: "Zone interdite", value: 20, color: "hsl(32, 95%, 52%)" },
  { name: "Proximité engin", value: 15, color: "hsl(220, 15%, 55%)" },
  { name: "Autres", value: 5, color: "hsl(220, 15%, 35%)" },
];

const recentAlerts = [
  { id: 1, type: "Sans casque", camera: "CAM-03", time: "il y a 5 min", severity: "critical" },
  { id: 2, type: "Zone interdite", camera: "CAM-01", time: "il y a 12 min", severity: "critical" },
  { id: 3, type: "Sans gilet", camera: "CAM-05", time: "il y a 23 min", severity: "warning" },
  { id: 4, type: "Proximité engin", camera: "CAM-02", time: "il y a 45 min", severity: "warning" },
  { id: 5, type: "Sans lunettes", camera: "CAM-04", time: "il y a 1h", severity: "info" },
];

const cameras = [
  { id: "CAM-01", name: "Entrée", active: true },
  { id: "CAM-02", name: "Zone stockage", active: false },
  { id: "CAM-03", name: "Sortie", active: true },
];

const edgeDevices = [
  { id: "Edge-01", status: "online" },
  { id: "Edge-02", status: "offline" },
];

const incidents = [{}, {}, {}];
const incidentStats = {
  today: 2,
  week: 5,
  resolved: 3,
  inProgress: 1,
};

const Dashboard = () => {
  const { user } = useAuth();
  const incidents = [{}, {}, {}];

  const stats = [
    {
      label: "Alertes critiques",
      value: 5,
      
      icon: AlertTriangle,
      color: "text-destructive",
      bg: "bg-destructive/10 border-destructive/20",
    },
    {
      label: "Non-conformités EPI",
      value: 12,
      
      icon: ShieldX,
      color: "text-warning",
      bg: "bg-warning/10 border-warning/20",
    },
    {
      label: "Caméras en ligne",
      value: 6,
  
      icon: Camera,
      color: "text-success",
      bg: "bg-success/10 border-success/20",
    },
    {
      label: "Edge Devices actifs",
      value: 4,
     
      icon: Cpu,
      color: "text-primary",
      bg: "bg-primary/10 border-primary/20",
    },
  ];

  const weeklyIncidents = [
    { day: "Lun", incidents: 8 },
    { day: "Mar", incidents: 5 },
    { day: "Mer", incidents: 12 },
    { day: "Jeu", incidents: 7 },
    { day: "Ven", incidents: 15 },
    { day: "Sam", incidents: 3 },
    { day: "Dim", incidents: 1 },
  ];

  const hourlyTrend = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}h`,
    alerts: Math.floor(Math.random() * 10 + (i > 6 && i < 18 ? 5 : 0)),
  }));

  const incidentTypes = [
    { name: "Sans casque", value: 35, color: "hsl(0, 72%, 51%)" },
    { name: "Sans gilet", value: 25, color: "hsl(45, 93%, 47%)" },
    { name: "Zone interdite", value: 20, color: "hsl(32, 95%, 52%)" },
    { name: "Proximité engin", value: 15, color: "hsl(220, 15%, 55%)" },
    { name: "Autres", value: 5, color: "hsl(220, 15%, 35%)" },
  ];

  const recentAlerts = [
    { id: 1, type: "Sans casque", camera: "CAM-03", time: "il y a 5 min", severity: "critical" },
    { id: 2, type: "Zone interdite", camera: "CAM-01", time: "il y a 12 min", severity: "critical" },
    { id: 3, type: "Sans gilet", camera: "CAM-05", time: "il y a 23 min", severity: "warning" },
    { id: 4, type: "Proximité engin", camera: "CAM-02", time: "il y a 45 min", severity: "warning" },
    { id: 5, type: "Sans lunettes", camera: "CAM-04", time: "il y a 1h", severity: "info" },
  ];

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

    

      {/* Nombre d'incidents */}
      <div className="rounded-lg border border-border bg-card p-6 flex flex-col items-center">
        <div className="text-4xl font-bold text-red-600">{incidents.length}</div>
        <div className="text-sm text-gray-500 mt-2">Incidents détectés</div>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        <div className="font-semibold mb-2">Statistiques</div>
        <div className="flex flex-wrap gap-4">
          <div>
            <span className="font-bold">{incidentStats.today}</span>
            <span className="ml-1 text-xs text-gray-500">aujourd'hui</span>
          </div>
          <div>
            <span className="font-bold">{incidentStats.week}</span>
            <span className="ml-1 text-xs text-gray-500">cette semaine</span>
          </div>
          <div>
            <span className="font-bold">{incidentStats.resolved}</span>
            <span className="ml-1 text-xs text-green-600">résolus</span>
          </div>
          <div>
            <span className="font-bold">{incidentStats.inProgress}</span>
            <span className="ml-1 text-xs text-orange-500">en cours</span>
          </div>
        </div>
      </div>

      {/* Caméras actives */}
      <div className="rounded-lg border border-border bg-card p-6 mb-6">
        <div className="font-semibold mb-2">Caméras actives</div>
        <div className="flex gap-4">
          {cameras.map((cam) => (
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
          ))}
        </div>
      </div>

      {/* Statut des Edge devices */}
      <div className="rounded-lg border border-border bg-card p-6">
        <div className="font-semibold mb-2">Statut des Edge devices</div>
        <div className="flex gap-4">
          {edgeDevices.map((ed) => (
            <div key={ed.id} className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${ed.status === "online" ? "bg-green-500" : "bg-red-500"}`}></span>
              <span className="font-mono">{ed.id}</span>
              <span className="text-xs text-gray-500">{ed.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
