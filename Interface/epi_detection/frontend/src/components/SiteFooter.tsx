import { Link } from "react-router-dom";

const SiteFooter = () => {
  return (
    <footer className="border-t border-white/10 bg-[hsl(220_18%_16%)] text-white backdrop-blur">
      <div className="mx-auto max-w-5xl px-6 py-10">

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3 mb-8">

          {/* À propos */}
          <div className="space-y-3">
            <p className="text-xs font-medium uppercase tracking-widest text-white/55">
              À propos
            </p>
            <p className="text-sm font-medium text-white">ALEXSYS Solutions</p>
            <p className="text-xs leading-relaxed text-white/70">
10, Allée des Mûriers, Ain Sebâa, Casablanca
            </p>
            <a
              href="mailto:contact@alexsys.ma"
              className="block text-xs text-[hsl(32_95%_62%)] hover:underline"
            >
              contact@alexsys.ma
            </a>
          </div>

          {/* Développeur */}
          <div className="space-y-3">
            <p className="text-xs font-medium uppercase tracking-widest text-white/55">
              Développeur
            </p>
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-white/10 text-xs font-medium text-[hsl(32_95%_62%)]">
                TS
              </div>
              <div>
                <p className="text-sm font-medium text-white">TRAORE Souleymane</p>
                <p className="text-xs text-white/65">IA/Data Engineer En Formation</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {["Django","YOLO","LLM", "React", "AWS"].map((skill) => (
                <span
                  key={skill}
                  className="rounded bg-white/10 px-2 py-0.5 text-xs text-[hsl(32_95%_62%)]"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Ressources */}
          <div className="space-y-3">
            <p className="text-xs font-medium uppercase tracking-widest text-white/55">
              Ressources
            </p>
            <div className="flex flex-col gap-2">
              <Link
                to="/docs"
                className="flex items-center gap-1.5 text-xs text-white/70 transition-colors hover:text-white"
              >
                Documentation
              </Link>
              <Link
                to="/architecture-technique"
                className="flex items-center gap-1.5 text-xs text-white/70 transition-colors hover:text-white"
              >
                Architecture technique
              </Link>
              <a
                href="mailto:contact@alexsys-solutions.com"
                className="flex items-center gap-1.5 text-xs text-white/70 transition-colors hover:text-white"
              >
                Support
              </a>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 pt-4">
          <p className="text-xs text-white/55">
            © 2026 ALEXSYS Solutions — Tous droits réservés
          </p>
          <p className="text-xs text-white/55">
            Conçu & développé par ALEXSYS Solutions
          </p>
        </div>

      </div>
    </footer>
  );
};

export default SiteFooter;