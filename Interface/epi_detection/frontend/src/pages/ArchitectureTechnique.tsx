import {
  Blocks,
  BookOpen,
  Bot,
  Database,
  GitBranch,
  HardDrive,
  Network,
  Server,
  Settings,
  Shield,
  Wrench,
} from "lucide-react";
import SiteFooter from "@/components/SiteFooter";

const architectureLayers = [
  {
    title: "Presentation et interaction",
    owner: "Frontend React + TypeScript + Vite",
    detail:
      "Expose les ecrans de supervision, de traitement des alertes, de reporting, de documentation et la page admin dediee aux analyses Gemini. Le routage est gere cote client et les appels passent par l'API REST.",
  },
  {
    title: "Services applicatifs",
    owner: "Backend Django REST Framework",
    detail:
      "Centralise l'authentification, les regles de permissions, la gestion des cameras, des alertes, des audits, des indicateurs metier et la file d'analyses contextuelles Gemini.",
  },
  {
    title: "Analyse de conformite",
    owner: "Module detection + modele YOLO",
    detail:
      "Analyse les images, produit les detections, calcule la conformite EPI et declenche la creation d'alertes selon le contexte camera et les regles HSE. La persistance est suivie par personne via bounding boxes et matching IoU.",
  },
  {
    title: "Analyse contextuelle",
    owner: "Service Gemini Vision + file de reprise",
    detail:
      "Traite les non-conformites persistantes pour une meme personne, applique un quota journalier, gere les rate limits temporaires et calcule un prochain essai estime quand l'API Gemini repond 429.",
  },
  {
    title: "Persistance et media",
    owner: "PostgreSQL ou SQLite + S3/local media",
    detail:
      "Stocke les donnees metier, les journaux de detection, les etats de suivi par personne, les analyses Gemini, les alertes, les audits et les images associees selon le mode local ou AWS active.",
  },
];

const maintenanceAreas = [
  {
    title: "Administration technique",
    items: [
      "Creer les comptes d'administration et gerer les roles backend.",
      "Verifier la disponibilite des cameras et leur statut operationnel.",
      "Superviser la base, les migrations et l'etat des medias.",
      "Controler la configuration S3, CORS, CSRF et JWT selon l'environnement.",
      "Verifier la configuration Gemini, les quotas et la page admin des analyses contextuelles.",
    ],
  },
  {
    title: "Maintenance corrective",
    items: [
      "Diagnostiquer les erreurs reseau, DB ou stockage depuis les journaux backend.",
      "Verifier la creation des alertes a partir des logs de detection.",
      "Analyser les cas de cooldown Gemini, les 429 temporaires et les prochains essais estimes.",
      "Regenerer ou recharger les medias si une image n'est plus accessible.",
      "Executer les migrations ou verifier les incompatibilites de schema apres mise a jour.",
    ],
  },
  {
    title: "Evolution applicative",
    items: [
      "Ajouter un nouveau domaine metier sous forme d'app Django isolee.",
      "Etendre les pages frontend par route dediee et couche API centralisee.",
      "Introduire de nouveaux KPIs sans casser le workflow detection -> alerte -> audit.",
      "Faire evoluer les regles HSE ou les classes EPI en gardant la compatibilite des donnees.",
      "Faire evoluer le suivi de personnes ou la strategie de reessai Gemini sans casser la file existante.",
    ],
  },
];

const runbookCards = [
  {
    icon: Database,
    title: "Base de donnees",
    text:
      "Mode local par defaut sur SQLite. Le passage a PostgreSQL est pilote par USE_POSTGRES et les variables DB_*. Cette separation permet la maintenance locale sans dependance reseau.",
  },
  {
    icon: HardDrive,
    title: "Stockage media",
    text:
      "Les medias peuvent rester locaux ou etre delegues a S3. La couche django-storages et les backends dedies media/static doivent rester la reference unique de stockage.",
  },
  {
    icon: Shield,
    title: "Securite",
    text:
      "Les autorisations ne doivent pas etre gerees seulement en interface. Toute action sensible doit rester protegee dans les permissions DRF et les roles utilisateur.",
  },
  {
    icon: GitBranch,
    title: "Evolution de code",
    text:
      "Les changements doivent rester modulaires: modele, serializer, view, route backend puis integration frontend et documentation associee.",
  },
  {
    icon: Bot,
    title: "Gemini Vision",
    text:
      "La couche contextuelle s'appuie sur une file admin, un cooldown de reessai et un suivi par personne pour eviter les analyses parasites.",
  },
];

const figureZones = [
  {
    title: "Figure A - Vue logique globale",
    caption:
      "Zone prevue pour un schema couches: frontend, API, detection, base de donnees, stockage media et dependances externes.",
  },
  {
    title: "Figure B - Flux detection vers alerte",
    caption:
      "Zone prevue pour un diagramme de sequence illustrant image -> detection -> log -> suivi par personne -> alerte -> file Gemini -> audit.",
  },
  {
    title: "Figure C - Deploiement et exploitation",
    caption:
      "Zone prevue pour une vue d'infrastructure locale ou cloud: frontend, backend, DB, S3, IAM, reseau, observabilite et dependance Gemini API.",
  },
];

const technicalActions = [
  {
    title: "Administration",
    actions: [
      "Activer ou desactiver PostgreSQL via USE_POSTGRES selon l'environnement.",
      "Mettre a jour les variables S3 et verifier la generation des URLs media.",
      "Piloter les utilisateurs et verifier les roles critiques admin/superviseur.",
      "Surveiller le quota journalier Gemini et le cooldown des analyses en attente.",
    ],
  },
  {
    title: "Maintenance",
    actions: [
      "Verifier la sante applicative avec runserver, les migrations et les erreurs de l'editeur.",
      "Analyser les endpoints critiques: login, detection, alertes, audits, export, reporting et Gemini process-next.",
      "Surveiller les regressions sur les images, le stockage et les permissions backend.",
      "Verifier que les retries Gemini ne restent pas bloques apres un 429 ou un verrouillage local SQLite.",
    ],
  },
  {
    title: "Evolution",
    actions: [
      "Ajouter des modules sans coupler la logique de presentation et la logique metier.",
      "Conserver des contrats API stables et documentes avant toute refonte frontend.",
      "Mettre a jour la documentation technique a chaque changement de schema, role ou workflow.",
      "Prevoir une transition vers un worker asynchrone si le traitement Gemini sort du mode manuel admin.",
    ],
  },
];

const ArchitectureTechnique = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b border-border bg-card/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-4xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-primary">
                <Blocks size={14} />
                Conception architecturelle
              </div>
              <h1 className="mt-4 text-4xl font-black tracking-tight text-foreground">
                Architecture technique, administration et maintenance
              </h1>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-muted-foreground">
                Cette page decrit la structure technique du systeme, les points d'administration, les trajectoires
                d'evolution et les zones a utiliser pour inserer des figures d'architecture. Elle sert de support
                pour l'exploitation, la maintenance corrective et l'evolution applicative. Elle couvre aussi la
                couche Gemini Vision ajoutee au-dessus du pipeline YOLO pour les non-conformites persistantes.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-4 lg:w-[560px]">
              <div className="rounded-2xl border border-border bg-background/80 p-4">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Front</div>
                <div className="mt-2 text-lg font-bold">React SPA</div>
              </div>
              <div className="rounded-2xl border border-border bg-background/80 p-4">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Back</div>
                <div className="mt-2 text-lg font-bold">Django REST</div>
              </div>
              <div className="rounded-2xl border border-border bg-background/80 p-4">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Data</div>
                <div className="mt-2 text-lg font-bold">DB + S3</div>
              </div>
              <div className="rounded-2xl border border-border bg-background/80 p-4">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">LLM</div>
                <div className="mt-2 text-lg font-bold">Gemini Vision</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-7xl flex-1 gap-8 px-6 py-8 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="h-fit rounded-2xl border border-border bg-card p-4 lg:sticky lg:top-6">
          <div className="mb-4 text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            Architecture
          </div>
          <nav className="space-y-2 text-sm">
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#principes">Principes</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#couches">Couches</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#figures">Zones de figures</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#maintenance">Maintenance</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#runbooks">Runbooks</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#gouvernance">Gouvernance technique</a>
          </nav>
        </aside>

        <div className="space-y-8">
          <section id="principes" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Network className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Principes de conception</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {runbookCards.map((card) => (
                <div key={card.title} className="rounded-2xl border border-border bg-background p-5">
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <card.icon size={20} />
                  </div>
                  <h3 className="text-base font-bold">{card.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{card.text}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="couches" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Server className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Decoupage par couches</h2>
            </div>
            <div className="space-y-4">
              {architectureLayers.map((layer, index) => (
                <div key={layer.title} className="rounded-2xl border border-border bg-background p-5">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                        Couche {index + 1}
                      </div>
                      <h3 className="mt-1 text-lg font-bold">{layer.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">{layer.detail}</p>
                    </div>
                    <div className="rounded-xl border border-border bg-card px-4 py-3 text-sm font-semibold text-foreground">
                      {layer.owner}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section id="figures" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <BookOpen className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Zones pour les figures techniques</h2>
            </div>
            <div className="grid gap-5 xl:grid-cols-3">
              {figureZones.map((figure) => (
                <div key={figure.title} className="rounded-2xl border border-border bg-background p-5">
                  <h3 className="text-base font-bold">{figure.title}</h3>
                  {figure.title === "Figure A - Vue logique globale" ? (
                    <div className="mt-4 overflow-hidden rounded-2xl border border-border bg-card">
                      <img
                        src="/arch-Finale.png"
                        alt="Architecture globale du systeme EPI Guard"
                        className="h-auto w-full object-contain"
                      />
                    </div>
                  ) : figure.title === "Figure B - Flux detection vers alerte" ? (
                    <div className="mt-4 overflow-hidden rounded-2xl border border-border bg-card">
                      <img
                        src="/FigureB.png"
                        alt="Flux de detection EPI, suivi par personne, alerte, file Gemini et audit"
                        className="h-auto w-full object-contain"
                      />
                    </div>
                  ) : figure.title === "Figure C - Deploiement et exploitation" ? (
                    <div className="mt-4 overflow-hidden rounded-2xl border border-border bg-card">
                      <img
                        src="/FigureC.png"
                        alt="Vue de deploiement et exploitation EPI Guard avec frontend, backend, DB, S3 et Gemini API"
                        className="h-auto w-full object-contain"
                      />
                    </div>
                  ) : (
                    <div className="mt-4 flex min-h-[220px] items-center justify-center rounded-2xl border-2 border-dashed border-primary/30 bg-primary/5 text-center text-sm font-medium text-muted-foreground">
                      Inserer ici la figure
                    </div>
                  )}
                  <p className="mt-4 text-sm leading-6 text-muted-foreground">{figure.caption}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="maintenance" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Wrench className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Maintenance, exploitation et evolution</h2>
            </div>
            <div className="grid gap-4 xl:grid-cols-3">
              {maintenanceAreas.map((area) => (
                <div key={area.title} className="rounded-2xl border border-border bg-background p-5">
                  <h3 className="text-lg font-bold">{area.title}</h3>
                  <ul className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                    {area.items.map((item) => (
                      <li key={item} className="rounded-xl border border-border px-3 py-2">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>

          <section id="runbooks" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Settings className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Actions techniques envisageables</h2>
            </div>
            <div className="grid gap-4 xl:grid-cols-3">
              {technicalActions.map((block) => (
                <div key={block.title} className="rounded-2xl border border-border bg-background p-5">
                  <h3 className="text-lg font-bold">{block.title}</h3>
                  <ul className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                    {block.actions.map((action) => (
                      <li key={action} className="rounded-xl border border-border px-3 py-2">
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>

          <section id="gouvernance" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <GitBranch className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Gouvernance technique</h2>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="rounded-2xl border border-border bg-background p-5">
                <h3 className="text-lg font-bold">Regles de maintenance</h3>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                  <li>Documenter tout changement de role, endpoint, schema de donnees ou mecanisme d'authentification.</li>
                  <li>Executer une validation locale apres toute modification backend ou frontend critique.</li>
                  <li>Conserver les bascules d'environnement explicites pour la DB et le stockage afin d'eviter les incidents locaux.</li>
                  <li>Maintenir les permissions backend comme source de verite pour les actions sensibles.</li>
                  <li>Traiter les quotas et retries Gemini comme des evenements d'exploitation documentes, pas comme des erreurs silencieuses.</li>
                </ul>
              </div>
              <div className="rounded-2xl border border-primary/20 bg-primary/5 p-5">
                <h3 className="text-lg font-bold text-foreground">Usage cible</h3>
                <p className="mt-4 text-sm leading-7 text-muted-foreground">
                  Cette page doit permettre a un profil technique d'identifier rapidement ou intervenir pour administrer,
                  corriger ou faire evoluer le systeme. Elle constitue une base de maintenance exploitable, pas seulement
                  une description academique.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
      <SiteFooter />
    </div>
  );
};

export default ArchitectureTechnique;