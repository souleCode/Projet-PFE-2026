import { useState, useRef } from "react";
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


// Pour chaque caméra, stocker la liste des EPI à surveiller
type CamEPIConfig = Record<string, string[]>; //

const Cameras = () => {
  const [selectedCam, setSelectedCam] = useState<number>(mockCameras[0].pk);
  const [muted, setMuted] = useState(false);
  const [detectionActive, setDetectionActive] = useState(false);
  const [epiStatuses, setEpiStatuses] = useState<EPIStatus[]>(
    EPI_CLASSES.map((id) => ({ id, label: id, detected: true }))
  );
  // Config EPI par caméra (par défaut tous activés)
  const [camEpiConfig, setCamEpiConfig] = useState<CamEPIConfig>(() => {
    const initial: CamEPIConfig = {};
    mockCameras.forEach(cam => { initial[cam.pk] = [...EPI_CLASSES]; });
    return initial;
  });


  // EPI à surveiller pour la caméra sélectionnée
  const selectedEpis = camEpiConfig[selectedCam] || [];

  // Filtrer les statuts EPI selon la config de la caméra
  const filteredEpiStatuses = epiStatuses.filter(s => selectedEpis.includes(s.id));

  const missingCount = filteredEpiStatuses.filter((s) => !s.detected).length;
  const isAlerted = detectionActive && missingCount > 0;

  
  // Synchronise les statuts EPI avec la détection backend (statut/couleur)
  const handleDetection = (detections: any[]) => {
    setDetectionActive(true);
    setEpiStatuses((prev) =>
      prev.map((epi) => {
        // Cherche la détection correspondante
        const det = detections.find((d: any) => d.class === epi.id);
        // Statut backend : worn (vert), present (jaune), missing_epi (rouge)
        let detected = false;
        if (det) {
          detected = det.status === "worn";
        }
        return {
          ...epi,
          detected,
          // Optionnel : on pourrait aussi ajouter une propriété "color" si besoin
        };
      })
    );
  };

  // Handler pour changer la config EPI d'une caméra
  const handleEpiConfigChange = (epiId: string) => {
    setCamEpiConfig((prev) => {
      const current = prev[selectedCam] || [];
      let next: string[];
      if (current.includes(epiId)) {
        next = current.filter((id) => id !== epiId);
      } else {
        next = [...current, epiId];
      }
      return { ...prev, [selectedCam]: next };
    });
  };

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
            <WebcamFeed isAlerted={isAlerted} cameraId={selectedCam.toString()} watchedEpis={selectedEpis} onDetection={handleDetection} />
          </div>

          {/* Camera grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {mockCameras.map((cam) => (
              <button
                key={cam.pk}
                onClick={() => setSelectedCam(cam.pk)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  selectedCam === cam.pk
                    ? "border-primary bg-primary/5"
                    : "border-border bg-card hover:border-primary/30"
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

          {/* Config EPI à surveiller */}
          <div className="mb-2">
            <div className="text-xs font-mono text-muted-foreground mb-1">
              Configurer les EPI à surveiller :
            </div>
            <div className="flex flex-wrap gap-2">
              {EPI_CLASSES.map((epi) => (
                <label key={epi} className="flex items-center gap-1 text-xs cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={selectedEpis.includes(epi)}
                    onChange={() => handleEpiConfigChange(epi)}
                    className="accent-primary"
                  />
                  <span>{epi}</span>
                </label>
              ))}
            </div>
          </div>

          <EPIStatusPanel statuses={filteredEpiStatuses} />
        </aside>
      </div>
    </div>
  );
};

export default Cameras;
