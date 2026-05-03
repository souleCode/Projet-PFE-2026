import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileSpreadsheet, FileText } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { apiFetch } from "@/lib/api";

interface DetectionStatsResponse {
  total: number;
  compliant: number;
  non_compliant: number;
  compliance_rate: number;
  weekly_incidents: Array<{ day: string; incidents: number }>;
  incident_types: Array<{ name: string; value: number; color: string }>;
}

interface AlertStatsResponse {
  total: number;
  nouveau: number;
  en_cours: number;
  resolu: number;
  faible: number;
  moyenne: number;
  elevee: number;
}

interface AlertItem {
  id: number;
  camera_name?: string;
  criticity: string;
  status: string;
  timestamp: string;
}

interface AuditItem {
  id: number;
  title: string;
  camera_name?: string;
  status: string;
  captures_count: number;
  created_at: string;
}

interface RecurrenceItem {
  name: string;
  total_alerts: number;
  repeat_alerts: number;
  recurrence_rate: number;
}

interface ComplianceByHourItem {
  hour: number;
  label: string;
  total: number;
  compliant: number;
  compliance_rate: number;
}

interface ComplianceByRuleItem {
  rule_id: number;
  rule_name: string;
  camera_count: number;
  total: number;
  compliant: number;
  compliance_rate: number;
}

interface BusinessKpisResponse {
  mtta_minutes: number;
  mttr_minutes: number;
  overall_camera_recurrence_rate: number;
  overall_zone_recurrence_rate: number;
  recurrence_by_camera: RecurrenceItem[];
  recurrence_by_zone: RecurrenceItem[];
  compliance_by_hour: ComplianceByHourItem[];
  compliance_by_rule: ComplianceByRuleItem[];
}

interface ReportingData {
  detectionStats: DetectionStatsResponse;
  alertStats: AlertStatsResponse;
  businessKpis: BusinessKpisResponse;
  zoneData: Array<{ cam: string; incidents: number }>;
  audits: AuditItem[];
}

const emptyDetectionStats: DetectionStatsResponse = {
  total: 0,
  compliant: 0,
  non_compliant: 0,
  compliance_rate: 0,
  weekly_incidents: [],
  incident_types: [],
};

const emptyAlertStats: AlertStatsResponse = {
  total: 0,
  nouveau: 0,
  en_cours: 0,
  resolu: 0,
  faible: 0,
  moyenne: 0,
  elevee: 0,
};

const emptyBusinessKpis: BusinessKpisResponse = {
  mtta_minutes: 0,
  mttr_minutes: 0,
  overall_camera_recurrence_rate: 0,
  overall_zone_recurrence_rate: 0,
  recurrence_by_camera: [],
  recurrence_by_zone: [],
  compliance_by_hour: [],
  compliance_by_rule: [],
};

function unwrapResults<T>(payload: T[] | { results?: T[] } | null | undefined): T[] {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.results)) return payload.results;
  return [];
}

function formatMinutes(minutes: number) {
  if (!minutes) return "0 min";
  if (minutes < 60) return `${Math.round(minutes)} min`;

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = Math.round(minutes % 60);
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

const tooltipStyle = {
  background: "hsl(220, 18%, 12%)",
  border: "1px solid hsl(220, 15%, 20%)",
  borderRadius: "8px",
  fontSize: "12px",
};

const Reporting = () => {
  const navigate = useNavigate();
  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ReportingData>({
    detectionStats: emptyDetectionStats,
    alertStats: emptyAlertStats,
    businessKpis: emptyBusinessKpis,
    zoneData: [],
    audits: [],
  });

  useEffect(() => {
    let cancelled = false;

    async function loadReporting() {
      setLoading(true);
      setError(null);

      try {
        const [detectionStats, alertStats, businessKpis, alertsPayload, auditsPayload] = await Promise.all([
          apiFetch("/api/detection/stats/"),
          apiFetch("/api/alerts/stats/"),
          apiFetch("/api/detection/business-kpis/"),
          apiFetch("/api/alerts/?page=1&page_size=100"),
          apiFetch("/api/audits/?page=1&page_size=100"),
        ]);

        if (cancelled) {
          return;
        }

        const alerts = unwrapResults<AlertItem>(alertsPayload);
        const audits = unwrapResults<AuditItem>(auditsPayload);
        const incidentsByCamera = alerts.reduce<Record<string, number>>((acc, alert) => {
          const cameraName = alert.camera_name || "Caméra inconnue";
          acc[cameraName] = (acc[cameraName] || 0) + 1;
          return acc;
        }, {});

        const zoneData = Object.entries(incidentsByCamera)
          .map(([cam, incidents]) => ({ cam, incidents }))
          .sort((left, right) => right.incidents - left.incidents)
          .slice(0, 8);

        setData({
          detectionStats: detectionStats as DetectionStatsResponse,
          alertStats: alertStats as AlertStatsResponse,
          businessKpis: businessKpis as BusinessKpisResponse,
          zoneData,
          audits,
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Impossible de charger le reporting.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadReporting();

    return () => {
      cancelled = true;
    };
  }, []);

  const latestAudit = data.audits[0];
  const kpis = [
    { label: "Total incidents", value: data.alertStats.total },
    { label: "Taux conformité", value: `${data.detectionStats.compliance_rate}%` },
    { label: "Alertes critiques", value: data.alertStats.elevee },
    { label: "Audits ouverts", value: data.audits.filter((audit) => audit.status !== "clos").length },
    { label: "MTTA", value: formatMinutes(data.businessKpis.mtta_minutes) },
    { label: "MTTR", value: formatMinutes(data.businessKpis.mttr_minutes) },
    { label: "Récidive caméras", value: `${data.businessKpis.overall_camera_recurrence_rate}%` },
    { label: "Récidive zones", value: `${data.businessKpis.overall_zone_recurrence_rate}%` },
  ];

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
            onClick={() => window.open(`${API_BASE_URL}/api/audits/export/`, "_blank")}
            className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            <FileSpreadsheet size={16} />
            Export CSV audits
          </button>
          {latestAudit && (
            <button
              onClick={() => window.open(`${API_BASE_URL}/api/audits/${latestAudit.id}/report/`, "_blank")}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90"
            >
              <FileText size={16} />
              PDF dernier audit
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{kpi.label}</p>
            <p className="text-2xl font-bold mt-1">{loading ? "..." : kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* By type */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Incidents par type</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              data={data.detectionStats.incident_types.map((item) => ({
                type: item.name,
                count: item.value,
              }))}
              layout="vertical"
            >
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
            <BarChart data={data.zoneData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis dataKey="cam" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="incidents" fill="hsl(32, 95%, 52%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Conformité par tranche horaire</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.businessKpis.compliance_by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis dataKey="label" tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} interval={2} />
              <YAxis tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} domain={[0, 100]} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${value}%`, "Conformité"]} />
              <Bar dataKey="compliance_rate" fill="hsl(142, 72%, 42%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Conformité par règle HSE</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={data.businessKpis.compliance_by_rule.map((item) => ({
                rule: item.rule_name,
                compliance_rate: item.compliance_rate,
              }))}
              layout="vertical"
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis dataKey="rule" type="category" tick={{ fontSize: 11, fill: "hsl(220, 10%, 55%)" }} width={120} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${value}%`, "Conformité"]} />
              <Bar dataKey="compliance_rate" fill="hsl(220, 70%, 58%)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Taux de récidive par caméra</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={data.businessKpis.recurrence_by_camera.map((item) => ({
                name: item.name,
                recurrence_rate: item.recurrence_rate,
              }))}
              layout="vertical"
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "hsl(220, 10%, 55%)" }} width={120} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${value}%`, "Récidive"]} />
              <Bar dataKey="recurrence_rate" fill="hsl(12, 85%, 60%)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-4">Taux de récidive par zone</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={data.businessKpis.recurrence_by_zone.map((item) => ({
                name: item.name,
                recurrence_rate: item.recurrence_rate,
              }))}
              layout="vertical"
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 15%, 20%)" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12, fill: "hsl(220, 10%, 55%)" }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "hsl(220, 10%, 55%)" }} width={120} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${value}%`, "Récidive"]} />
              <Bar dataKey="recurrence_rate" fill="hsl(32, 95%, 52%)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Derniers audits</h3>
          <span className="text-xs font-mono text-muted-foreground">{data.audits.length} audit(s)</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted-foreground">
              <tr className="border-b border-border">
                <th className="px-3 py-2">Titre</th>
                <th className="px-3 py-2">Caméra</th>
                <th className="px-3 py-2">Statut</th>
                <th className="px-3 py-2">Captures</th>
                <th className="px-3 py-2">Créé le</th>
                <th className="px-3 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {data.audits.map((audit) => (
                <tr key={audit.id} className="border-b border-border/60 last:border-b-0">
                  <td className="px-3 py-2 font-medium">{audit.title}</td>
                  <td className="px-3 py-2">{audit.camera_name || "-"}</td>
                  <td className="px-3 py-2">{audit.status}</td>
                  <td className="px-3 py-2">{audit.captures_count}</td>
                  <td className="px-3 py-2">{new Date(audit.created_at).toLocaleString("fr-FR")}</td>
                  <td className="px-3 py-2">
                    <button
                      className="rounded border border-primary px-3 py-1 text-xs font-semibold text-primary hover:bg-primary/10"
                      onClick={() => navigate(`/audits/${audit.id}`)}
                    >
                      Voir détail
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && data.audits.length === 0 && (
                <tr>
                  <td className="px-3 py-4 text-muted-foreground" colSpan={6}>
                    Aucun audit disponible.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Reporting;
