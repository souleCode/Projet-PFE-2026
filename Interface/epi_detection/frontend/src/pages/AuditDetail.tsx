import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AlertStatus, AuditCaptureRecord, AuditRecord, AuditStatus, alertApi, auditApi } from "@/lib/api";

const AUDIT_STATUS_LABELS: Record<AuditStatus, string> = {
  ouvert: "Ouvert",
  en_cours: "En cours",
  clos: "Clos",
};

const AUDIT_STATUS_FLOW: AuditStatus[] = ["ouvert", "en_cours", "clos"];

const ALERT_STATUS_BY_AUDIT_STATUS: Partial<Record<AuditStatus, AlertStatus>> = {
  en_cours: "en_cours",
  clos: "resolu",
};

function formatDateTime(value?: string) {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function AuditDetail() {
  const navigate = useNavigate();
  const { auditId } = useParams();
  const parsedAuditId = Number(auditId);
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const [audit, setAudit] = useState<AuditRecord | null>(null);
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingCapture, setUploadingCapture] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [captureFile, setCaptureFile] = useState<File | null>(null);
  const [captureDescription, setCaptureDescription] = useState("");

  useEffect(() => {
    if (!Number.isFinite(parsedAuditId)) {
      setError("Audit invalide.");
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function loadAudit() {
      setLoading(true);
      setError(null);

      try {
        const data = await auditApi.get(parsedAuditId);
        if (cancelled) return;

        setAudit(data as AuditRecord);
        setTitle((data as AuditRecord).title || "");
        setNotes((data as AuditRecord).notes || "");
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Impossible de charger l'audit.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAudit();

    return () => {
      cancelled = true;
    };
  }, [parsedAuditId]);

  const orderedStatuses = useMemo(() => {
    if (!audit) return [];
    return AUDIT_STATUS_FLOW.filter((status) => status !== audit.status);
  }, [audit]);

  const syncLinkedAlertStatus = async (nextStatus: AuditStatus, linkedAlertId?: number) => {
    const linkedAlertStatus = ALERT_STATUS_BY_AUDIT_STATUS[nextStatus];
    if (!linkedAlertId || !linkedAlertStatus) return;

    await alertApi.update(linkedAlertId, { status: linkedAlertStatus });
  };

  const saveAudit = async (changes: { title?: string; notes?: string; status?: AuditStatus }, successMessage: string) => {
    if (!audit) return;

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updatedAudit = (await auditApi.update(audit.id, changes)) as AuditRecord;
      setAudit(updatedAudit);
      setTitle(updatedAudit.title || "");
      setNotes(updatedAudit.notes || "");

      if (changes.status) {
        try {
          await syncLinkedAlertStatus(changes.status, audit.alert);
        } catch {
          setSuccess("Audit mis à jour, mais le statut de l'alerte liée n'a pas pu être synchronisé.");
          return;
        }
      }

      setSuccess(successMessage);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Impossible de mettre à jour l'audit.");
    } finally {
      setSaving(false);
    }
  };

  const handleCaptureSelection = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setCaptureFile(file);
  };

  const uploadCapture = async () => {
    if (!audit || !captureFile) return;

    setUploadingCapture(true);
    setError(null);
    setSuccess(null);

    try {
      const createdCapture = (await auditApi.addCapture(audit.id, {
        image: captureFile,
        description: captureDescription.trim(),
      })) as AuditCaptureRecord;

      setAudit((previousAudit) => {
        if (!previousAudit) return previousAudit;

        const nextCaptures = [createdCapture, ...(previousAudit.captures || [])];
        return {
          ...previousAudit,
          captures: nextCaptures,
          captures_count: nextCaptures.length,
        };
      });
      setCaptureFile(null);
      setCaptureDescription("");
      setSuccess("Capture ajoutée à l'audit.");
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Impossible d'ajouter la capture.");
    } finally {
      setUploadingCapture(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-sm text-muted-foreground">Chargement de l'audit...</div>;
  }

  if (!audit) {
    return (
      <div className="p-6 space-y-4">
        <div className="rounded border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error || "Audit introuvable."}
        </div>
        <button
          className="rounded border border-border px-4 py-2 text-sm hover:bg-muted"
          onClick={() => navigate("/alerts")}
        >
          Retour aux alertes
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <button
            className="mb-3 text-sm text-primary underline underline-offset-4"
            onClick={() => navigate("/alerts")}
          >
            Retour aux alertes
          </button>
          <h1 className="text-2xl font-bold tracking-tight">Audit #{audit.id}</h1>
          <p className="text-sm text-muted-foreground">
            {audit.camera_name || "Caméra inconnue"} · créé le {formatDateTime(audit.created_at)}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span
            className={
              "rounded px-3 py-1 text-xs font-semibold " +
              (audit.status === "clos"
                ? "bg-green-100 text-green-700"
                : audit.status === "en_cours"
                  ? "bg-orange-100 text-orange-700"
                  : "bg-blue-100 text-blue-700")
            }
          >
            {AUDIT_STATUS_LABELS[audit.status]}
          </span>

          <button
            className="rounded border border-border px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
            onClick={() => window.open(`${apiBaseUrl}/api/audits/${audit.id}/report/`, "_blank")}
            disabled={saving}
          >
            Rapport PDF
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {success}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <section className="rounded-lg border border-border bg-card p-5 shadow-sm space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Titre</label>
            <input
              className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={saving}
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Notes de suivi</label>
            <textarea
              className="min-h-40 w-full rounded border border-border bg-background px-3 py-2 text-sm"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              disabled={saving}
              placeholder="Constat, actions correctives, décision de clôture..."
            />
          </div>

          <div className="flex flex-wrap justify-end gap-2">
            <button
              className="rounded border border-border px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
              onClick={() => {
                setTitle(audit.title || "");
                setNotes(audit.notes || "");
                setSuccess(null);
                setError(null);
              }}
              disabled={saving}
            >
              Réinitialiser
            </button>
            <button
              className="rounded bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50"
              onClick={() => saveAudit({ title: title.trim(), notes }, "Audit mis à jour.")}
              disabled={saving || !title.trim()}
            >
              {saving ? "Enregistrement..." : "Enregistrer"}
            </button>
          </div>
        </section>

        <section className="space-y-6">
          <div className="rounded-lg border border-border bg-card p-5 shadow-sm space-y-4">
            <div>
              <h2 className="text-base font-semibold">Cycle métier</h2>
              <p className="text-sm text-muted-foreground">
                Faites évoluer l'audit jusqu'à sa clôture. La clôture synchronise aussi l'alerte liée.
              </p>
            </div>

            <div className="space-y-2">
              {orderedStatuses.map((status) => (
                <button
                  key={status}
                  className={
                    "w-full rounded px-4 py-2 text-sm font-semibold disabled:opacity-50 " +
                    (status === "clos"
                      ? "bg-green-600 text-white hover:bg-green-700"
                      : status === "en_cours"
                        ? "bg-orange-500 text-white hover:bg-orange-600"
                        : "bg-blue-500 text-white hover:bg-blue-600")
                  }
                  onClick={() => saveAudit({ status }, `Audit passé au statut ${AUDIT_STATUS_LABELS[status].toLowerCase()}.`)}
                  disabled={saving}
                >
                  Passer en {AUDIT_STATUS_LABELS[status]}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-5 shadow-sm space-y-3 text-sm">
            <h2 className="text-base font-semibold">Contexte</h2>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Alerte liée</span>
              <span className="font-medium">{audit.alert ? `#${audit.alert}` : "Aucune"}</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Criticité</span>
              <span className="font-medium">{audit.alert_criticity || "-"}</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Créé par</span>
              <span className="font-medium">{audit.created_by_name || "-"}</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Dernière mise à jour</span>
              <span className="font-medium">{formatDateTime(audit.updated_at)}</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Captures</span>
              <span className="font-medium">{audit.captures_count || audit.captures?.length || 0}</span>
            </div>
          </div>
        </section>
      </div>

      <section className="rounded-lg border border-border bg-card p-5 shadow-sm space-y-4">
        <div>
          <h2 className="text-base font-semibold">Captures d'audit</h2>
          <p className="text-sm text-muted-foreground">Historique des preuves et observations déjà rattachées.</p>
        </div>

        <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-4">
          <div>
            <h3 className="text-sm font-semibold">Ajouter une capture</h3>
            <p className="text-xs text-muted-foreground">Envoyez une image et un commentaire terrain sans quitter l'audit.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <div>
              <label className="mb-1 block text-sm font-medium">Image</label>
              <input
                type="file"
                accept="image/*"
                className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
                onChange={handleCaptureSelection}
                disabled={uploadingCapture}
              />
              {captureFile && <p className="mt-1 text-xs text-muted-foreground">{captureFile.name}</p>}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">Description</label>
              <input
                className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
                value={captureDescription}
                onChange={(event) => setCaptureDescription(event.target.value)}
                placeholder="Ex: photo avant correction"
                disabled={uploadingCapture}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              className="rounded bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50"
              onClick={uploadCapture}
              disabled={uploadingCapture || !captureFile}
            >
              {uploadingCapture ? "Envoi..." : "Ajouter la capture"}
            </button>
          </div>
        </div>

        {!audit.captures || audit.captures.length === 0 ? (
          <div className="rounded border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
            Aucune capture n'est encore attachée à cet audit.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {audit.captures.map((capture) => (
              <article key={capture.id} className="rounded-lg border border-border p-3 space-y-3">
                {capture.image_url ? (
                  <a href={capture.image_url} target="_blank" rel="noopener noreferrer">
                    <img
                      src={capture.image_url}
                      alt={capture.description || `Capture ${capture.id}`}
                      className="h-40 w-full rounded object-cover border"
                    />
                  </a>
                ) : (
                  <div className="flex h-40 items-center justify-center rounded border border-dashed border-border text-xs text-muted-foreground">
                    Image indisponible
                  </div>
                )}
                <div className="space-y-1 text-sm">
                  <p className="font-medium">{capture.description || "Sans description"}</p>
                  <p className="text-muted-foreground">{formatDateTime(capture.taken_at)}</p>
                  <p className="text-muted-foreground">{capture.taken_by_name || "Auteur inconnu"}</p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}