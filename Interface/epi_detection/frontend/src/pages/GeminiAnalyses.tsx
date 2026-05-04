import { useEffect, useState } from "react";
import { Bot, Shield } from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import { GeminiContextAnalysisRecord, geminiAnalysisApi } from "@/lib/api";

const GeminiAnalyses = () => {
  const { user, loading } = useAuth();
  const [geminiAnalyses, setGeminiAnalyses] = useState<GeminiContextAnalysisRecord[]>([]);
  const [geminiLoading, setGeminiLoading] = useState(false);
  const [geminiProcessing, setGeminiProcessing] = useState(false);
  const [geminiError, setGeminiError] = useState<string | null>(null);
  const [geminiInfo, setGeminiInfo] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const loadGeminiAnalyses = async () => {
    setGeminiLoading(true);
    setGeminiError(null);
    try {
      const data = await geminiAnalysisApi.list();
      setGeminiAnalyses(Array.isArray(data) ? data : data.results || []);
    } catch (err: any) {
      setGeminiError(err.message || "Impossible de charger les analyses Gemini.");
    } finally {
      setGeminiLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role === "admin") {
      loadGeminiAnalyses();
    }
  }, [user?.role]);

  const geminiQueued = geminiAnalyses.filter((item) => item.status === "queued").length;
  const geminiCompleted = geminiAnalyses.filter((item) => item.status === "completed").length;
  const geminiFailed = geminiAnalyses.filter((item) => item.status === "failed").length;
  const readyQueuedAnalyses = geminiAnalyses.filter((item) => {
    if (item.status !== "queued") return false;
    if (!item.next_retry_at) return true;
    return new Date(item.next_retry_at).getTime() <= now;
  });
  const nextBlockedAnalysis = geminiAnalyses
    .filter((item) => item.status === "queued" && item.next_retry_at && new Date(item.next_retry_at).getTime() > now)
    .sort((left, right) => new Date(left.next_retry_at!).getTime() - new Date(right.next_retry_at!).getTime())[0];
  const nextRetryCountdown = nextBlockedAnalysis?.next_retry_at
    ? Math.max(0, Math.ceil((new Date(nextBlockedAnalysis.next_retry_at).getTime() - now) / 1000))
    : null;
  const processButtonDisabled = geminiProcessing || (readyQueuedAnalyses.length === 0 && !!nextBlockedAnalysis);

  const processNextGeminiItem = async () => {
    setGeminiProcessing(true);
    setGeminiError(null);
    setGeminiInfo(null);
    try {
      const data = await geminiAnalysisApi.processNext();
      setGeminiInfo(
        data.detail === "processed"
          ? "Une analyse Gemini a été traitée."
          : data.detail === "daily_limit_reached"
            ? "Quota quotidien Gemini atteint."
            : data.detail === "rate_limited"
              ? `Quota Gemini temporairement dépassé. Nouvel essai estimé dans ${data.retry_in_seconds || 0}s.`
            : data.detail === "retry_scheduled"
              ? `Le prochain traitement sera disponible dans ${data.retry_in_seconds || 0}s.`
            : data.detail === "empty_queue"
              ? "Aucune analyse en attente dans la file."
              : `État du traitement: ${data.detail}`
      );
      await loadGeminiAnalyses();
    } catch (err: any) {
      setGeminiError(err.message || "Impossible de traiter la file Gemini.");
    } finally {
      setGeminiProcessing(false);
    }
  };

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
            Cette section est réservée aux administrateurs. Vous n'avez pas les permissions nécessaires pour accéder aux analyses Gemini.
          </p>
          <div className="bg-destructive/10 border border-destructive/30 rounded-md p-4 text-center">
            <p className="text-xs font-mono text-destructive font-semibold">
              {user?.role?.toUpperCase() || "UNKNOWN"} - ACCÈS NON AUTORISÉ
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analyses contextuelles Gemini</h1>
        <p className="text-sm text-muted-foreground font-mono">
          File d'attente, quota journalier et résultats d'analyse contextuelle Vision
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">En file</p>
          <p className="mt-2 text-2xl font-bold">{geminiQueued}</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Terminées</p>
          <p className="mt-2 text-2xl font-bold">{geminiCompleted}</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Échecs</p>
          <p className="mt-2 text-2xl font-bold">{geminiFailed}</p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="font-semibold">Gestion de la file Gemini</h3>
          <p className="text-sm text-muted-foreground">
            Les demandes restent en file d'attente et sont limitées à 5 traitements par jour.
          </p>
          {nextBlockedAnalysis && readyQueuedAnalyses.length === 0 && nextRetryCountdown !== null && (
            <p className="text-xs font-mono text-amber-600 mt-2">
              Prochain essai estimé dans {nextRetryCountdown}s.
            </p>
          )}
        </div>
        <button
          className="inline-flex items-center gap-2 px-4 py-2 rounded bg-primary text-white hover:bg-primary/90 disabled:opacity-60"
          onClick={processNextGeminiItem}
          disabled={processButtonDisabled}
        >
          <Bot className="w-4 h-4" />
          {geminiProcessing ? "Traitement..." : nextBlockedAnalysis && readyQueuedAnalyses.length === 0 && nextRetryCountdown !== null ? `Réessai dans ${nextRetryCountdown}s` : "Traiter le prochain élément"}
        </button>
      </div>

      {geminiError && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          {geminiError}
        </div>
      )}
      {geminiInfo && (
        <div className="rounded-lg border border-primary/30 bg-primary/10 p-3 text-sm text-primary">
          {geminiInfo}
        </div>
      )}

      <div className="rounded-lg border border-border bg-card overflow-hidden">
        {geminiLoading ? (
          <div className="p-4 text-center text-muted-foreground">Chargement des analyses...</div>
        ) : geminiAnalyses.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">Aucune analyse contextuelle disponible.</div>
        ) : (
          <div className="divide-y divide-border">
            {geminiAnalyses.map((analysis) => (
              <div key={analysis.id} className="p-4 grid gap-4 lg:grid-cols-[160px_minmax(0,1fr)]">
                <div className="rounded-lg border border-border bg-muted/20 overflow-hidden min-h-[120px] flex items-center justify-center">
                  {analysis.image_url ? (
                    <img src={analysis.image_url} alt={`Analyse Gemini ${analysis.id}`} className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-xs text-muted-foreground text-center px-3">Aucune image disponible</span>
                  )}
                </div>
                <div className="space-y-3 min-w-0">
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <h4 className="font-semibold">Analyse #{analysis.id} - {analysis.camera_name || `Caméra ${analysis.camera}`}</h4>
                      <p className="text-xs text-muted-foreground font-mono">Demandée le {new Date(analysis.requested_at).toLocaleString("fr-FR")}</p>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs font-mono">
                      <span className="px-2 py-1 rounded bg-secondary text-foreground">{analysis.status}</span>
                      {analysis.severity && <span className="px-2 py-1 rounded bg-warning/20 text-warning">{analysis.severity}</span>}
                      {analysis.action && <span className="px-2 py-1 rounded bg-primary/20 text-primary">{analysis.action}</span>}
                    </div>
                  </div>

                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-md border border-border p-3">
                      <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Motif</p>
                      <p className="mt-2 text-sm">{analysis.request_reason || "-"}</p>
                    </div>
                    <div className="rounded-md border border-border p-3">
                      <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">EPI manquants</p>
                      <p className="mt-2 text-sm">{analysis.missing_epi?.length ? analysis.missing_epi.join(", ") : "-"}</p>
                    </div>
                  </div>

                  <div className="rounded-md border border-border p-3">
                    <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Analyse contextuelle</p>
                    <p className="mt-2 text-sm text-muted-foreground">{analysis.explanation || analysis.error_message || "En attente de traitement Gemini."}</p>
                    {analysis.next_retry_at && analysis.status === "queued" && new Date(analysis.next_retry_at).getTime() > now && (
                      <p className="mt-2 text-xs font-mono text-amber-600">
                        Prochain essai estimé le {new Date(analysis.next_retry_at).toLocaleString("fr-FR")}
                        {typeof analysis.retry_in_seconds === "number" ? ` (${analysis.retry_in_seconds}s)` : ""}
                      </p>
                    )}
                    {typeof analysis.llm_confidence === "number" && (
                      <p className="mt-2 text-xs font-mono text-muted-foreground">Confiance LLM : {(analysis.llm_confidence * 100).toFixed(1)}%</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GeminiAnalyses;