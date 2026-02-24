import { FileSpreadsheet } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const dailyIncidents = Array.from({ length: 30 }, (_, i) => ({
  date: `${i + 1}/02`,
  incidents: Math.floor(Math.random() * 20 + 3),
  resolved: Math.floor(Math.random() * 15 + 2),
}));

const zoneData = [
  { cam: "CAM-01", incidents: 45, color: "hsl(0, 72%, 51%)" },
  { cam: "CAM-02", incidents: 32, color: "hsl(32, 95%, 52%)" },
  { cam: "CAM-03", incidents: 28, color: "hsl(45, 93%, 47%)" },
  { cam: "CAM-04", incidents: 15, color: "hsl(142, 72%, 42%)" },
  { cam: "CAM-05", incidents: 38, color: "hsl(220, 15%, 55%)" },
  { cam: "CAM-06", incidents: 22, color: "hsl(32, 70%, 40%)" },
];

const typeData = [
  { type: "Sans casque", count: 45 },
  { type: "Sans gilet", count: 32 },
  { type: "Proximité", count: 18 },
  { type: "Sans lunettes", count: 15 },
  { type: "Sans gants", count: 12 },
  { type: "Sans masque", count: 8 },
];

const heatmapData = [
  ["CAM-01", 8, 12, 15, 5, 3, 2, 0],
  ["CAM-02", 3, 5, 8, 12, 6, 1, 0],
  ["CAM-03", 5, 7, 10, 3, 2, 0, 0],
  ["CAM-04", 1, 2, 3, 2, 1, 0, 0],
  ["CAM-05", 6, 9, 14, 8, 4, 1, 0],
  ["CAM-06", 2, 4, 6, 4, 2, 0, 0],
];
const days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

const tooltipStyle = {
  background: "hsl(220, 18%, 12%)",
  border: "1px solid hsl(220, 15%, 20%)",
  borderRadius: "8px",
  fontSize: "12px",
};

const Reporting = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reporting & Analytics</h1>
          <p className="text-sm text-muted-foreground font-mono">
            Statistiques de conformité et d'incidents
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => window.open("/api/reports/pdf", "_blank")}
            className="btn btn-primary"
          >
            Télécharger le rapport PDF
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { label: "Total incidents (mois)", value: "180"},
          { label: "Taux conformité", value: "87%"},
          { label: "Alertes critiques", value: "23"},
        ].map((kpi) => (
          <div key={kpi.label} className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{kpi.label}</p>
            <p className="text-2xl font-bold mt-1">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* By type */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Incidents par type</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={typeData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis type="number" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis dataKey="type" type="category" tick={{ fontSize: 11, fill: "hsl(220, 10%, 55%)" }} width={100} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="hsl(32, 95%, 52%)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* By zone */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Incidents par Caméra</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={zoneData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis dataKey="cam" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="incidents" fill="hsl(32, 95%, 52%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Reporting;
