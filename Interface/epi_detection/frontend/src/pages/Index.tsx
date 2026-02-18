import { useState, useCallback } from "react";
import { ShieldAlert, Activity } from "lucide-react";
import WebcamFeed from "@/components/WebcamFeed";
import EPIStatusPanel, { type EPIStatus } from "@/components/EPIStatusPanel";
import BuzzerAlert from "@/components/BuzzerAlert";

const EPI_CLASSES = [
  "ear_protection",
  "gloves",
  "hardhat",
  "mask",
  "safety_boots",
  "safety_glasses",
  "safety_vest",
];

const Index = () => {
  const [muted, setMuted] = useState(false);
  const [detectionActive, setDetectionActive] = useState(false);

  // Simulated EPI statuses — in production, these come from your detection model
  const [epiStatuses, setEpiStatuses] = useState<EPIStatus[]>(
    EPI_CLASSES.map((id) => ({ id, label: id, detected: true }))
  );

  const missingCount = epiStatuses.filter((s) => !s.detected).length;
  const isAlerted = detectionActive && missingCount > 0;

  const toggleEPI = useCallback((id: string) => {
    setEpiStatuses((prev) =>
      prev.map((s) => (s.id === id ? { ...s, detected: !s.detected } : s))
    );
  }, []);

  const simulateRandomDetection = useCallback(() => {
    setDetectionActive(true);
    setEpiStatuses((prev) =>
      prev.map((s) => ({ ...s, detected: Math.random() > 0.35 }))
    );
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
            <ShieldAlert size={22} className="text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">
              EPI<span className="text-primary">Guard</span>
            </h1>
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
              Détection des Équipements de Protection
            </p>
          </div>
        </div>
        <BuzzerAlert isActive={isAlerted} muted={muted} onToggleMute={() => setMuted((m) => !m)} />
      </header>

      {/* Main */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-0">
        {/* Webcam Area */}
        <div className="p-6 flex flex-col min-h-[500px]">
          <WebcamFeed isAlerted={isAlerted} />
        </div>

        {/* Sidebar */}
        <aside className="border-l border-border p-6 flex flex-col gap-6 bg-card">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Activity size={16} />
              Statut des EPI
            </h2>
            <button
              onClick={simulateRandomDetection}
              className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-xs font-mono font-semibold hover:opacity-90 transition-opacity"
            >
              Simuler détection
            </button>
          </div>

          <EPIStatusPanel statuses={epiStatuses} />

          {/* Manual toggle (demo) */}
          <div className="mt-auto pt-4 border-t border-border">
            <p className="text-xs font-mono text-muted-foreground mb-3 uppercase tracking-wider">
              Mode démo — Cliquer pour basculer
            </p>
            <div className="flex flex-wrap gap-1.5">
              {epiStatuses.map((s) => (
                <button
                  key={s.id}
                  onClick={() => {
                    setDetectionActive(true);
                    toggleEPI(s.id);
                  }}
                  className={`text-xs font-mono px-2 py-1 rounded border transition-colors ${
                    s.detected
                      ? "border-success/30 text-success bg-success/5 hover:bg-success/10"
                      : "border-destructive/30 text-destructive bg-destructive/5 hover:bg-destructive/10"
                  }`}
                >
                  {s.id.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default Index;
