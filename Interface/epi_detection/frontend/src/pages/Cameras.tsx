import { useState, useRef, useEffect } from "react";
import { Camera, CameraOff, AlertTriangle, Maximize2, Volume2, VolumeX, ShieldAlert, Users } from "lucide-react";
import WebcamFeed, { type WorkerDetection } from "@/components/WebcamFeed";
import EPIStatusPanel, { type EPIStatus } from "@/components/EPIStatusPanel";
import BuzzerAlert from "@/components/BuzzerAlert";

const EPI_LABELS: Record<string, string> = {
  hardhat:        "CASQUE",
  vest:           "GILET",
  glass:          "LUNETTES",
  mask:           "MASQUE",
  safety_boots:   "CHAUSSURES",
  ear_protection: "BOUCHONS",
};

const EPI_CLASSES = [
  "ear_protection", "hardhat", "mask",
  "safety_boots", "safety_glasses", "vest",
];

const mockCameras = [
  { pk: 1, id: "CAM-01", name: "Entrée principale", zone: "Zone A", status: "online" },
  { pk: 2, id: "CAM-02", name: "Atelier mécanique", zone: "Zone B", status: "online" },
  { pk: 3, id: "CAM-03", name: "Zone de stockage", zone: "Zone C", status: "online" },
  { pk: 4, id: "CAM-04", name: "Quai de chargement", zone: "Zone D", status: "offline" },
  { pk: 5, id: "CAM-05", name: "Salle machines", zone: "Zone E", status: "online" },
  { pk: 6, id: "CAM-06", name: "Parking engins", zone: "Zone F", status: "online" },
];

// Pour chaque caméra, stocker la liste des EPI à surveiller (avec criticité)

type EpiCriticite = { epi: string; criticite: string };
type HSERule = {
  id: number;
  name: string;
  epi_criticites: EpiCriticite[];
  [key: string]: any;
};
type CameraType = {
  pk?: number;
  id: number | string;
  name: string;
  zone?: string;
  status?: string;
  hse_rules?: HSERule[];
  [key: string]: any;
};

const Cameras = () => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://pfe-api.digiscia.me";

  // mockCameras comme fallback initial, remplacé si le backend répond
  const [cameras, setCameras] = useState<CameraType[]>(mockCameras);
  const [selectedCam, setSelectedCam] = useState<number | string>(mockCameras[0].id);
  const [muted, setMuted] = useState(false);
  const [detectionActive, setDetectionActive] = useState(false);
  const [workers, setWorkers] = useState<WorkerDetection[]>([]);
  const [detectionStats, setDetectionStats] = useState<Record<string, number>>({});
  const [epiStatuses, setEpiStatuses] = useState<EPIStatus[]>(
    EPI_CLASSES.map((id) => ({ id, label: id, detected: true }))
  );
  // Charger la liste des caméras (avec hse_rules) depuis le backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/cameras/`, { credentials: "include" })
      .then(res => res.json())
      .then(data => {
        console.log('Réponse API /api/cameras/', data);
        const cams = Array.isArray(data) ? data : data.results || [];
        if (cams.length > 0) {
          setCameras(cams);
          setSelectedCam(cams[0].id);
        }
      });
  }, []);


  // Trouver la caméra sélectionnée
  const selectedCamera = cameras.find(cam => String(cam.id) === String(selectedCam));
  // On prend la première règle HSE associée à la caméra (si plusieurs, on peut adapter)
  const selectedEpiCriticites = selectedCamera?.hse_rules?.[0]?.epi_criticites || [];
  // Liste des EPI à surveiller (ids)
  const selectedEpis = selectedEpiCriticites.map(ec => ec.epi);
  // Statuts filtrés
  const filteredEpiStatuses = epiStatuses.filter(s => selectedEpis.includes(s.id));
  const missingCount = filteredEpiStatuses.filter((s) => !s.detected).length;
  const isAlerted = detectionActive && missingCount > 0;

  const handleDetection = (
    detections: any[],
    incomingWorkers: WorkerDetection[],
    stats?: Record<string, unknown>
  ) => {
    setDetectionActive(true);
    setWorkers(incomingWorkers);
    if (stats) {
      setDetectionStats({
        total_workers:         Number(stats.total_workers ?? 0),
        non_compliant_workers: Number(stats.non_compliant_workers ?? 0),
      });
    }
    setEpiStatuses((prev) =>
      prev.map((epi) => {
        const det = detections.find((d: any) => d.class === epi.id);
        return { ...epi, detected: det ? det.status === "worn" : false };
      })
    );
  };


  // Suppression de handleEpiConfigChange : la config EPI vient du backend

  return (
    <div className="p-6 space-y-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Caméras temps réel</h1>
          <p className="text-sm text-muted-foreground font-mono">
            Visualisation des flux vidéo avec détection IA
          </p>
        </div>
        <BuzzerAlert isActive={isAlerted} muted={muted} onToggleMute={() => setMuted((m) => !m)} />
      </div>

      <div className="flex-1 grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-4 min-h-0">
        {/* Main feed */}
        <div className="flex flex-col gap-4 min-h-0">
          {/* Live feed */}
          <div className="flex-1 min-h-[400px]">
            <WebcamFeed isAlerted={isAlerted} cameraId={selectedCamera ? String(selectedCamera.id) : ""} watchedEpis={selectedEpis} onDetection={handleDetection} />
          </div>

          {/* Camera grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {cameras.map((cam) => (
              <button
                key={cam.id}
                onClick={() => setSelectedCam(cam.id)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  String(selectedCam) === String(cam.id) ? "border-primary bg-primary/5" : "border-border bg-card hover:border-primary/30"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      cam.status === "online" ? "bg-success" : "bg-destructive"
                    }`}
                  />
                  <span className="font-mono text-xs">{cam.id}</span>
                </div>
                <p className="text-sm font-medium truncate">{cam.name}</p>
                <p className="text-xs text-muted-foreground font-mono">{cam.zone}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Sidebar - Workers */}
        <aside className="rounded-lg border border-border bg-card flex flex-col gap-0 overflow-hidden">
          {/* Header sidebar */}
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Détection EPI
            </h2>
            {detectionActive && (
              <span className="flex items-center gap-1 text-xs font-mono text-green-600">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                ANALYSE
              </span>
            )}
          </div>

          {/* Source vidéo */}
          <div className="px-4 pt-3 pb-2">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">Source vidéo</p>
            <div className="rounded-md border border-border bg-muted/40 px-3 py-1.5 text-sm font-mono truncate">
              {selectedCamera?.name ?? "—"}
            </div>
          </div>

          {/* EPI surveillés */}
          <div className="px-4 pb-2">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">EPI surveillés</p>
            <div className="rounded-md border border-border bg-muted/40 px-3 py-1.5 flex items-center justify-between">
              <span className="text-sm">
                {selectedEpiCriticites.length === 0 ? "Tous" : selectedEpiCriticites.map(e => EPI_LABELS[e.epi] ?? e.epi).join(", ")}
              </span>
              <span className="text-xs text-muted-foreground font-mono">
                {selectedEpiCriticites.length > 0 ? `${selectedEpiCriticites.length}/6` : "5/5"}
              </span>
            </div>
          </div>

          {/* Stats : travailleurs / non-conformes */}
          {detectionActive && (
            <div className="px-4 pb-3">
              <p className="text-[10px] font-mono uppercase text-muted-foreground mb-2">Statistiques</p>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950/30 dark:border-green-900 p-3 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {detectionStats.total_workers ?? workers.length}
                  </div>
                  <div className="text-[10px] font-mono uppercase text-green-700 mt-0.5">Travailleurs</div>
                </div>
                <div className="rounded-lg border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-900 p-3 text-center">
                  <div className="text-2xl font-bold text-red-500">
                    {detectionStats.non_compliant_workers ?? workers.filter(w => !w.is_compliant).length}
                  </div>
                  <div className="text-[10px] font-mono uppercase text-red-600 mt-0.5">Non-conformes</div>
                </div>
              </div>
            </div>
          )}

          {/* Liste des workers */}
          <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3">
            <p className="text-[10px] font-mono uppercase text-muted-foreground">Travailleurs</p>

            {!detectionActive && (
              <div className="flex flex-col items-center justify-center py-8 gap-2 text-muted-foreground">
                <Users size={32} className="opacity-30" />
                <p className="text-xs font-mono">En attente de détection…</p>
              </div>
            )}

            {detectionActive && workers.length === 0 && (
              <div className="flex flex-col items-center justify-center py-8 gap-2 text-muted-foreground">
                <ShieldAlert size={32} className="opacity-30" />
                <p className="text-xs font-mono">Aucune personne détectée</p>
              </div>
            )}

            {workers.map((worker) => (
              <div
                key={worker.worker_id}
                className={`rounded-lg border p-3 ${
                  worker.is_compliant
                    ? "border-green-200 bg-green-50/50 dark:bg-green-950/20 dark:border-green-900"
                    : "border-red-200 bg-red-50/50 dark:bg-red-950/20 dark:border-red-900"
                }`}
              >
                {/* En-tête travailleur */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold text-white ${
                      worker.is_compliant ? "bg-green-500" : "bg-red-500"
                    }`}>
                      {worker.worker_id}
                    </span>
                    <span className="text-sm font-medium">Worker ID : {worker.worker_id}</span>
                  </div>
                  {worker.missing_count > 0 && (
                    <span className="flex items-center gap-1 text-xs text-red-500 font-mono">
                      <ShieldAlert size={12} />
                      {worker.missing_count} manquant{worker.missing_count > 1 ? "s" : ""}
                    </span>
                  )}
                </div>

                {/* Grille EPI */}
                <div className="grid grid-cols-3 gap-1.5">
                  {Object.entries(worker.epis).map(([epi, status]) => (
                    <div
                      key={epi}
                      className={`flex flex-col items-center gap-0.5 rounded-md px-1 py-2 text-center ${
                        status === "worn"
                          ? "bg-background border border-green-200"
                          : "bg-red-100 dark:bg-red-900/30 border border-red-300"
                      }`}
                    >
                      <span className="text-base leading-none">
                        {epi === "hardhat" ? "⛑" : epi === "vest" ? "🦺" : epi === "glass" ? "🥽" : epi === "mask" ? "😷" : epi === "safety_boots" ? "👢" : "🎧"}
                      </span>
                      <span className={`text-[9px] font-mono font-bold leading-none mt-0.5 ${
                        status === "worn" ? "text-muted-foreground" : "text-red-600"
                      }`}>
                        {EPI_LABELS[epi] ?? epi.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Confiance */}
                <div className="mt-2 text-right text-[10px] font-mono text-muted-foreground">
                  conf. {Math.round(worker.confidence * 100)}%
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Cameras;