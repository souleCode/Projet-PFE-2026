import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertRecord, AlertStatus, AuditRecord, alertApi, auditApi } from "@/lib/api";

const STATUS_LABELS = {
  nouveau: "Nouveau",
  en_cours: "En cours",
  resolu: "Résolu",
  ignore: "Ignoré",
};

const STATUS_ORDER: AlertStatus[] = ["nouveau", "en_cours", "resolu"];

export default function Alerts() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [auditsByAlertId, setAuditsByAlertId] = useState<Record<number, AuditRecord[]>>({});
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [auditLoading, setAuditLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditSuccess, setAuditSuccess] = useState<string | null>(null);
  const [auditTarget, setAuditTarget] = useState<AlertRecord | null>(null);
  const [auditForm, setAuditForm] = useState({
    title: "",
    notes: "",
  });

  const unwrapResults = <T,>(payload: T[] | { results?: T[] } | null | undefined): T[] => {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
  };

  useEffect(() => {
    let cancelled = false;

    async function loadAlertsAndAudits() {
      setLoading(true);
      setError(null);

      try {
        const alertsPayload = await alertApi.list(page, pageSize);
        const nextAlerts = Array.isArray(alertsPayload) ? alertsPayload : alertsPayload.results || [];
        const nextCount = alertsPayload.count || (Array.isArray(alertsPayload) ? alertsPayload.length : 0);

        if (cancelled) return;

        setAlerts(nextAlerts);
        setCount(nextCount);

        const visibleAlertIds = nextAlerts.map((alert) => alert.id);
        if (visibleAlertIds.length === 0) {
          setAuditsByAlertId({});
          return;
        }

        const auditsPayloadByAlert = await Promise.all(
          visibleAlertIds.map((alertId) => auditApi.list({ page: 1, pageSize: 20, alertId }))
        );
        if (cancelled) return;

        const linkedAudits = auditsPayloadByAlert.flatMap((payload) => unwrapResults<AuditRecord>(payload));

        const nextAuditsByAlertId = linkedAudits.reduce<Record<number, AuditRecord[]>>((accumulator, audit) => {
          if (!audit.alert) return accumulator;
          const key = audit.alert;
          accumulator[key] = accumulator[key] ? [...accumulator[key], audit] : [audit];
          accumulator[key].sort((left, right) => right.id - left.id);
          return accumulator;
        }, {});

        setAuditsByAlertId(nextAuditsByAlertId);
      } catch (loadError) {
        if (!cancelled) {
          setAlerts([]);
          setCount(0);
          setAuditsByAlertId({});
          setError(loadError instanceof Error ? loadError.message : "Impossible de charger les alertes.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAlertsAndAudits();

    return () => {
      cancelled = true;
    };
  }, [page, pageSize]);

  const updateStatus = async (id: number, status: AlertStatus) => {
    setUpdatingId(id);
    setError(null);

    try {
      const updatedAlert = await alertApi.update(id, { status });
      setAlerts((prev) =>
        prev.map((alert) => (alert.id === id ? updatedAlert : alert))
      );
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Impossible de mettre à jour l'alerte.");
    } finally {
      setUpdatingId(null);
    }
  };

  const openAuditModal = (alert: AlertRecord) => {
    setError(null);
    setAuditSuccess(null);
    setAuditTarget(alert);
    setAuditForm({
      title: `Audit - ${alert.camera_name || `Caméra ${alert.camera}`}`,
      notes: `Ouverture suite à l'alerte #${alert.id}${alert.epi_missing.length > 0 ? ` - EPI manquants: ${alert.epi_missing.join(", ")}` : ""}`,
    });
  };

  const closeAuditModal = () => {
    if (auditLoading) return;
    setAuditTarget(null);
    setAuditForm({ title: "", notes: "" });
  };

  const createAudit = async () => {
    if (!auditTarget) return;

    setAuditLoading(true);
    setError(null);
    setAuditSuccess(null);

    try {
      const createdAudit = await auditApi.create({
        title: auditForm.title,
        camera: typeof auditTarget.camera === "number" ? auditTarget.camera : Number(auditTarget.camera),
        alert: auditTarget.id,
        notes: auditForm.notes,
      });

      setAuditsByAlertId((prev) => ({
        ...prev,
        [auditTarget.id]: [createdAudit as AuditRecord, ...(prev[auditTarget.id] || [])],
      }));

      if (auditTarget.status === "nouveau") {
        try {
          const updatedAlert = await alertApi.update(auditTarget.id, { status: "en_cours" });
          setAlerts((prev) => prev.map((alert) => (alert.id === auditTarget.id ? updatedAlert : alert)));
        } catch {
          setAuditSuccess("Audit créé, mais le statut de l'alerte doit être ajusté manuellement.");
        }
      }

      closeAuditModal();
      navigate(`/audits/${(createdAudit as AuditRecord).id}`);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Impossible de créer l'audit.");
    } finally {
      setAuditLoading(false);
    }
  };

  const totalPages = Math.ceil(count / pageSize);

  return (
    <div className="p-4">
      <h2 className="font-bold text-2xl mb-6 text-primary">Alertes</h2>
      <div className="mb-4 flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Page {page} / {totalPages || 1}</span>
        <button
          className="px-2 py-1 rounded bg-muted text-muted-foreground border hover:bg-primary/10 disabled:opacity-50"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1 || loading}
        >Précédent</button>
        <button
          className="px-2 py-1 rounded bg-muted text-muted-foreground border hover:bg-primary/10 disabled:opacity-50"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages || loading}
        >Suivant</button>
        <label className="ml-4 text-sm">Taille page:
          <select
            className="ml-2 border rounded px-1 py-0.5"
            value={pageSize}
            onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
            disabled={loading}
          >
            {[5, 10, 20, 50].map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </label>
        {loading && <span className="ml-4 text-xs text-muted-foreground">Chargement...</span>}
      </div>
      {error && (
        <div className="mb-4 rounded border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}
      {auditSuccess && (
        <div className="mb-4 rounded border border-emerald-300 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {auditSuccess}
        </div>
      )}
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
                <td className="px-4 py-2 font-mono text-xs">{alert.camera_name || alert.camera}</td>
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
                  {alert.image_url ? (
                    <a
                      href={alert.image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline text-primary hover:text-primary/80"
                    >
                      <img src={alert.image_url} alt="Capture incident" className="h-10 w-16 object-cover rounded border" />
                    </a>
                  ) : (
                    <span className="text-muted-foreground text-xs">—</span>
                  )}
                </td>
                <td className="px-4 py-2">
                  <span className={
                    alert.status === "nouveau"
                      ? "bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-semibold"
                      : alert.status === "en_cours"
                      ? "bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-xs font-semibold"
                      : alert.status === "ignore"
                      ? "bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs font-semibold"
                      : "bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-semibold"
                  }>
                    {STATUS_LABELS[alert.status] || alert.status}
                  </span>
                </td>
                <td className="px-4 py-2">
                  {auditsByAlertId[alert.id]?.[0] && (
                    <div className="mb-2 rounded border border-border bg-muted/40 px-2 py-2 text-xs">
                      <div className="font-semibold">Audit lié</div>
                      <div className="mt-1 flex items-center justify-between gap-2">
                        <span>#{auditsByAlertId[alert.id][0].id}</span>
                        <span className="rounded bg-background px-2 py-0.5 font-medium">
                          {auditsByAlertId[alert.id][0].status === "clos"
                            ? "Clos"
                            : auditsByAlertId[alert.id][0].status === "en_cours"
                              ? "En cours"
                              : "Ouvert"}
                        </span>
                      </div>
                    </div>
                  )}

                  {auditsByAlertId[alert.id]?.[0] ? (
                    <button
                      className="mb-2 mr-2 rounded border border-primary px-2 py-1 text-xs font-semibold text-primary hover:bg-primary/10"
                      onClick={() => navigate(`/audits/${auditsByAlertId[alert.id][0].id}`)}
                      disabled={updatingId === alert.id || auditLoading}
                    >
                      Voir audit
                    </button>
                  ) : null}

                  <button
                    className="mb-2 mr-2 rounded bg-slate-700 px-2 py-1 text-xs font-semibold text-white hover:bg-slate-800"
                    onClick={() => openAuditModal(alert)}
                    disabled={updatingId === alert.id || auditLoading || Boolean(auditsByAlertId[alert.id]?.some((audit) => audit.status !== "clos"))}
                  >
                    {auditsByAlertId[alert.id]?.length ? "Nouvel audit" : "Ouvrir audit"}
                  </button>
                  {STATUS_ORDER.map((s) =>
                    s !== alert.status ? (
                      <button
                        key={s}
                        className={
                          "px-2 py-1 rounded text-xs font-mono font-semibold mr-1 disabled:cursor-not-allowed disabled:opacity-50 " +
                          (s === "resolu"
                            ? "bg-green-500 text-white hover:bg-green-600"
                            : s === "en_cours"
                            ? "bg-orange-500 text-white hover:bg-orange-600"
                            : "bg-blue-500 text-white hover:bg-blue-600")
                        }
                        onClick={() => updateStatus(alert.id, s)}
                        disabled={updatingId === alert.id}
                      >
                        {STATUS_LABELS[s]}
                      </button>
                    ) : null
                  )}
                  {updatingId === alert.id && (
                    <span className="text-xs text-muted-foreground">Mise a jour...</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {auditTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4">
          <div className="w-full max-w-lg rounded-lg border border-border bg-background p-6 shadow-lg">
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold">Ouvrir un audit</h3>
                <p className="text-sm text-muted-foreground">
                  Alerte #{auditTarget.id} - {auditTarget.camera_name || auditTarget.camera}
                </p>
              </div>
              <button
                className="text-sm text-muted-foreground hover:text-foreground"
                onClick={closeAuditModal}
                disabled={auditLoading}
              >
                Fermer
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium">Titre</label>
                <input
                  className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
                  value={auditForm.title}
                  onChange={(e) => setAuditForm((prev) => ({ ...prev, title: e.target.value }))}
                  placeholder="Titre de l'audit"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">Notes</label>
                <textarea
                  className="min-h-28 w-full rounded border border-border bg-background px-3 py-2 text-sm"
                  value={auditForm.notes}
                  onChange={(e) => setAuditForm((prev) => ({ ...prev, notes: e.target.value }))}
                  placeholder="Contexte de l'ouverture de l'audit"
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  className="rounded border border-border px-4 py-2 text-sm hover:bg-muted"
                  onClick={closeAuditModal}
                  disabled={auditLoading}
                >
                  Annuler
                </button>
                <button
                  className="rounded bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                  onClick={createAudit}
                  disabled={auditLoading || !auditForm.title.trim()}
                >
                  {auditLoading ? "Création..." : "Créer l'audit"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}