import { Download, FileSpreadsheet, FileText } from "lucide-react";
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
  AreaChart,
  Area,
} from "recharts";

const dailyIncidents = Array.from({ length: 30 }, (_, i) => ({
  date: `${i + 1}/02`,
  incidents: Math.floor(Math.random() * 20 + 3),
  resolved: Math.floor(Math.random() * 15 + 2),
}));

const zoneData = [
  { zone: "Zone A", incidents: 45, color: "hsl(0, 72%, 51%)" },
  { zone: "Zone B", incidents: 32, color: "hsl(32, 95%, 52%)" },
  { zone: "Zone C", incidents: 28, color: "hsl(45, 93%, 47%)" },
  { zone: "Zone D", incidents: 15, color: "hsl(142, 72%, 42%)" },
  { zone: "Zone E", incidents: 38, color: "hsl(220, 15%, 55%)" },
  { zone: "Zone F", incidents: 22, color: "hsl(32, 70%, 40%)" },
];

const typeData = [
  { type: "Sans casque", count: 45 },
  { type: "Sans gilet", count: 32 },
  { type: "Zone interdite", count: 22 },
  { type: "Proximité", count: 18 },
  { type: "Sans lunettes", count: 15 },
  { type: "Sans gants", count: 12 },
  { type: "Sans masque", count: 8 },
];

const heatmapData = [
  ["Zone A", 8, 12, 15, 5, 3, 2, 0],
  ["Zone B", 3, 5, 8, 12, 6, 1, 0],
  ["Zone C", 5, 7, 10, 3, 2, 0, 0],
  ["Zone D", 1, 2, 3, 2, 1, 0, 0],
  ["Zone E", 6, 9, 14, 8, 4, 1, 0],
  ["Zone F", 2, 4, 6, 4, 2, 0, 0],
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
          <button className="flex items-center gap-2 px-3 py-2 rounded-md bg-secondary text-secondary-foreground text-xs font-mono hover:bg-secondary/80 transition-colors">
            <FileSpreadsheet size={14} />
            Export Excel
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Total incidents (mois)", value: "180"},
          { label: "Taux conformité", value: "87%"},
          { label: "Temps moyen résolution", value: "24 min"},
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
          <h3 className="text-sm font-semibold mb-4">Incidents par zone</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={zoneData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis dataKey="zone" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="incidents" fill="hsl(32, 95%, 52%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Heatmap */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Heatmap zones × jours</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr>
                  <th className="text-left p-1 text-muted-foreground">Zone</th>
                  {days.map((d) => (
                    <th key={d} className="p-1 text-center text-muted-foreground">{d}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {heatmapData.map((row) => (
                  <tr key={row[0] as string}>
                    <td className="p-1 text-muted-foreground">{row[0]}</td>
                    {(row.slice(1) as number[]).map((val, i) => {
                      const intensity = Math.min(val / 15, 1);
                      return (
                        <td key={i} className="p-1">
                          <div
                            className="w-full h-8 rounded flex items-center justify-center text-[10px] font-semibold"
                            style={{
                              backgroundColor: `hsl(0, 72%, 51%, ${intensity * 0.6 + 0.05})`,
                              color: intensity > 0.4 ? "white" : "hsl(220, 10%, 55%)",
                            }}
                          >
                            {val}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reporting;
