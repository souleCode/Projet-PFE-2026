import { useState, useRef, useEffect } from "react";
import { Camera, CameraOff, AlertTriangle, Maximize2, Volume2, VolumeX } from "lucide-react";
import WebcamFeed from "@/components/WebcamFeed";
import EPIStatusPanel, { type EPIStatus } from "@/components/EPIStatusPanel";
import BuzzerAlert from "@/components/BuzzerAlert";

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

  const handleDetection = (detections: any[]) => {
    setDetectionActive(true);
    setEpiStatuses((prev) =>
      prev.map((epi) => {
        const det = detections.find((d: any) => d.class === epi.id);
        let detected = false;
        if (det) {
          detected = det.status === "worn";
        }
        return { ...epi, detected };
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

        {/* Sidebar - Detection */}
        <aside className="rounded-lg border border-border bg-card p-4 flex flex-col gap-4 overflow-auto">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Détection EPI
            </h2>
          </div>

          {/* Affiche uniquement les EPI liés à la caméra (via la règle) */}
          <div className="mb-2">
            <div className="text-xs font-mono text-muted-foreground mb-1">
              EPI surveillés pour cette caméra :
            </div>
            <div className="flex flex-wrap gap-2">
              {selectedEpiCriticites.length === 0 ? (
                <span className="text-xs text-muted-foreground">Aucune règle HSE associée</span>
              ) : (
                selectedEpiCriticites.map(ec => (
                  <span key={ec.epi + '-' + ec.criticite} className="px-2 py-0.5 rounded bg-muted text-xs font-mono">
                    {ec.epi} <span className="italic">({ec.criticite})</span>
                  </span>
                ))
              )}
            </div>
          </div>

          <EPIStatusPanel statuses={filteredEpiStatuses} />
        </aside>
      </div>
    </div>
  );
};

export default Cameras;