import { useRef, useEffect, useState, useCallback } from "react";
import { detectEPI } from "@/lib/epiDetectionApi";
import { Camera, CameraOff, Upload, X } from "lucide-react";

interface WebcamFeedProps {
  isAlerted: boolean;
  cameraId?: string;
  watchedEpis?: string[];
  onDetection?: (detections: Detection[]) => void;
}

interface Detection {
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
  color: string;
}

const WebcamFeed = ({ isAlerted, cameraId, watchedEpis, onDetection }: WebcamFeedProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [isVideoMode, setIsVideoMode] = useState(false);
  const [videoFileName, setVideoFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const detectionInterval = useRef<NodeJS.Timeout | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "environment" },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsActive(true);
        setIsVideoMode(false);
        setError(null);
        
        detectionInterval.current = setInterval(async () => {
          if (!videoRef.current) return;
          const canvas = document.createElement("canvas");
          canvas.width = videoRef.current.videoWidth;
          canvas.height = videoRef.current.videoHeight;
          const ctx = canvas.getContext("2d");
          if (ctx) {
            ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(async (blob) => {
              if (blob) {
                try {
                  const result = await detectEPI(blob, cameraId, watchedEpis);
                  setDetections(result.detections || []);
                  if (typeof onDetection === "function") onDetection(result.detections || []);
                } catch (e) {
                  setDetections([]);
                  if (typeof onDetection === "function") onDetection([]);
                  console.error("Erreur détection EPI:", e);
                }
              }
            }, "image/jpeg", 0.85);
          }
        }, 2000);
      }
    } catch {
      setError("Impossible d'accéder à la caméra");
    }
  }, [onDetection]);

  const handleVideoUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('video/')) {
      setError("Veuillez sélectionner un fichier vidéo");
      return;
    }

    stopCamera();

    const url = URL.createObjectURL(file);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.src = url;
      videoRef.current.load();
      setIsActive(true);
      setIsVideoMode(true);
      setVideoFileName(file.name);
      setError(null);

      videoRef.current.onloadedmetadata = () => {
        detectionInterval.current = setInterval(async () => {
          if (!videoRef.current) return;
          const canvas = document.createElement("canvas");
          canvas.width = videoRef.current.videoWidth;
          canvas.height = videoRef.current.videoHeight;
          const ctx = canvas.getContext("2d");
          if (ctx) {
            ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(async (blob) => {
              if (blob) {
                try {
                  const result = await detectEPI(blob, cameraId, watchedEpis);
                  setDetections(result.detections || []);
                  if (typeof onDetection === "function") onDetection(result.detections || []);
                } catch (e) {
                  setDetections([]);
                  if (typeof onDetection === "function") onDetection([]);
                  console.error("Erreur détection EPI:", e);
                }
              }
            }, "image/jpeg", 0.85);
          }
        }, 500);
      };
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    if (videoRef.current?.src) {
      URL.revokeObjectURL(videoRef.current.src);
      videoRef.current.src = "";
    }
    setIsActive(false);
    setIsVideoMode(false);
    setVideoFileName(null);
    if (detectionInterval.current) {
      clearInterval(detectionInterval.current);
      detectionInterval.current = null;
    }
    setDetections([]);
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !videoRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!isActive || detections.length === 0) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    console.log("Drawing", detections.length, "detections");
    
    detections.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox;
      console.log("Drawing bbox:", det.class, det.bbox);
      
      ctx.strokeStyle = det.color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      
      ctx.font = "18px monospace";
      ctx.fillStyle = det.color;
      ctx.fillText(`${det.class} ${(det.confidence*100).toFixed(0)}%`, x1 + 4, y1 + 22);
    });
  }, [detections, isActive]);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  return (
    <div className="flex flex-col gap-3 h-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-2.5 h-2.5 rounded-full ${isActive ? (isAlerted ? "bg-destructive animate-pulse-alert" : "bg-success") : "bg-muted-foreground"}`} />
          <span className="font-mono text-sm text-muted-foreground uppercase tracking-wider">
            {isActive ? (isVideoMode ? `Video: ${videoFileName}` : "Live Feed") : "Offline"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleVideoUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-secondary text-secondary-foreground text-sm font-mono hover:bg-primary hover:text-primary-foreground transition-colors"
            disabled={isActive && isVideoMode}
          >
            <Upload size={14} />
            Uploader
          </button>
          
          <button
            onClick={isActive ? stopCamera : startCamera}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-secondary text-secondary-foreground text-sm font-mono hover:bg-primary hover:text-primary-foreground transition-colors"
          >
            {isActive ? (isVideoMode ? <X size={14} /> : <CameraOff size={14} />) : <Camera size={14} />}
            {isActive ? (isVideoMode ? "Fermer" : "Arrêter") : "Démarrer"}
          </button>
        </div>
      </div>

      <div
        className={`relative flex-1 rounded-lg overflow-hidden border-2 transition-colors ${
          isAlerted ? "border-destructive animate-border-glow glow-danger" : isActive ? "border-primary/30" : "border-border"
        }`}
      >
        <div className="relative w-full h-full">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={!isVideoMode}
            controls={isVideoMode}
            loop={isVideoMode}
            className={`w-full h-full object-cover bg-muted ${isActive ? "block" : "hidden"}`}
          />
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
        </div>

        {!isActive && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-muted/50">
            {error ? (
              <p className="text-destructive font-mono text-sm">{error}</p>
            ) : (
              <>
                <div className="flex items-center gap-4">
                  <Camera size={48} className="text-muted-foreground" />
                  <span className="text-muted-foreground">ou</span>
                  <Upload size={48} className="text-muted-foreground" />
                </div>
                <p className="text-muted-foreground font-mono text-sm text-center">
                  Cliquez sur "Démarrer" pour la caméra<br />
                  ou "Uploader" pour analyser une vidéo
                </p>
              </>
            )}
          </div>
        )}

        {isActive && !isVideoMode && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="scan-line absolute inset-0" />
            <div className="absolute top-3 left-3 w-8 h-8 border-t-2 border-l-2 border-primary/60" />
            <div className="absolute top-3 right-3 w-8 h-8 border-t-2 border-r-2 border-primary/60" />
            <div className="absolute bottom-3 left-3 w-8 h-8 border-b-2 border-l-2 border-primary/60" />
            <div className="absolute bottom-3 right-3 w-8 h-8 border-b-2 border-r-2 border-primary/60" />
          </div>
        )}
      </div>
    </div>
  );
};

export default WebcamFeed;