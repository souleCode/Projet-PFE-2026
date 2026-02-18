import { ShieldCheck, ShieldAlert, Ear, Hand, HardHat, Shield, Footprints, Glasses, Shirt, User } from "lucide-react";
import type { ReactNode } from "react";

export interface EPIStatus {
  id: string;
  label: string;
  detected: boolean;
}

interface EPIStatusPanelProps {
  statuses: EPIStatus[];
}

const iconMap: Record<string, ReactNode> = {
  ear_protection: <Ear size={20} />,
  person: <User size={20} />,
  hardhat: <HardHat size={20} />,
  mask: <Shield size={20} />,
  safety_boots: <Footprints size={20} />,
  safety_glasses: <Glasses size={20} />,
  vest: <Shirt size={20} />,
};

const labelMap: Record<string, string> = {
  ear_protection: "Protection auditive",
  person: "Agent",
  hardhat: "Casque",
  mask: "Masque",
  safety_boots: "Chaussures de sécurité",
  safety_glasses: "Lunettes de protection",
  vest: "Gilet de sécurité",
};

const EPIStatusPanel = ({ statuses }: EPIStatusPanelProps) => {
  const detected = statuses.filter((s) => s.detected).length;
  const total = statuses.length;
  const allGood = detected === total;

  return (
    <div className="flex flex-col gap-4">
      {/* Summary */}
      <div className={`flex items-center gap-3 p-4 rounded-lg border ${allGood ? "border-success/30 bg-success/5" : "border-destructive/30 bg-destructive/5"}`}>
        {allGood ? <ShieldCheck size={24} className="text-success" /> : <ShieldAlert size={24} className="text-destructive animate-pulse-alert" />}
        <div>
          <p className="font-semibold text-sm">
            {allGood ? "Tous les EPI à détecter" : ``}
          </p>
         
        </div>
      </div>

      {/* Individual items */}
      <div className="grid gap-2">
        {statuses.map((status) => (
          <div
            key={status.id}
            className={`flex items-center gap-3 p-3 rounded-md border transition-colors ${
              status.detected
                ? "border-success/20 bg-success/5"
                : "border-destructive/20 bg-destructive/5"
            }`}
          >
            <div className={status.detected ? "text-success" : "text-destructive"}>
              {iconMap[status.id] || <Shield size={20} />}
            </div>
            <span className="font-mono text-sm flex-1">
              {labelMap[status.id] || status.label}
            </span>
           
          </div>
        ))}
      </div>
    </div>
  );
};

export default EPIStatusPanel;
