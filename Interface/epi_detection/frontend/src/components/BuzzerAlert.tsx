import { useEffect, useRef, useCallback } from "react";
import { Volume2, VolumeX } from "lucide-react";

interface BuzzerAlertProps {
  isActive: boolean;
  muted: boolean;
  onToggleMute: () => void;
}

const BuzzerAlert = ({ isActive, muted, onToggleMute }: BuzzerAlertProps) => {
  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);

  const startBuzzer = useCallback(() => {
    if (muted) return;
    try {
      const ctx = new AudioContext();
      audioCtxRef.current = ctx;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "square";
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      // Pulsing effect
      const lfo = ctx.createOscillator();
      const lfoGain = ctx.createGain();
      lfo.frequency.setValueAtTime(4, ctx.currentTime);
      lfoGain.gain.setValueAtTime(0.1, ctx.currentTime);
      lfo.connect(lfoGain);
      lfoGain.connect(gain.gain);
      lfo.start();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      oscillatorRef.current = osc;
    } catch {
      // Audio API not available
    }
  }, [muted]);

  const stopBuzzer = useCallback(() => {
    oscillatorRef.current?.stop();
    oscillatorRef.current = null;
    audioCtxRef.current?.close();
    audioCtxRef.current = null;
  }, []);

  useEffect(() => {
    if (isActive) {
      startBuzzer();
    } else {
      stopBuzzer();
    }
    return () => stopBuzzer();
  }, [isActive, startBuzzer, stopBuzzer]);

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={onToggleMute}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-mono transition-colors ${
          muted
            ? "bg-muted text-muted-foreground"
            : "bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground"
        }`}
      >
        {muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
        {muted ? "Son coupé" : "Son actif"}
      </button>

      {isActive && !muted && (
        <span className="text-destructive font-mono text-xs font-semibold animate-pulse-alert uppercase tracking-wider">
          ⚠ ALARME ACTIVE
        </span>
      )}
    </div>
  );
};

export default BuzzerAlert;
