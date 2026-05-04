import { BookOpen, Bot, KeyRound, LayoutTemplate, Network, ShieldCheck, Users } from "lucide-react";
import { Link } from "react-router-dom";
import SiteFooter from "@/components/SiteFooter";

const roleRows = [
  {
    role: "Admin",
    rights: "Administration complete, creation des comptes, gestion des regles HSE, cameras, audits, exports.",
  },
  {
    role: "Superviseur",
    rights: "Suivi operationnel, mise a jour des alertes, mise a jour partielle des cameras, export CSV des audits.",
  },
  {
    role: "Operateur",
    rights: "Consultation des donnees, detection, creation et consultation des audits selon les ecrans autorises.",
  },
];

const frontendPages = [
  { route: "/", description: "Dashboard global de supervision et KPIs." },
  { route: "/cameras", description: "Consultation et gestion des cameras." },
  { route: "/alerts", description: "Traitement des alertes et ouverture d'audits." },
  { route: "/audits/:auditId", description: "Detail d'un audit, captures, notes et rapport PDF." },
  { route: "/hse-rules", description: "Gestion des regles HSE appliquees aux cameras et zones." },
  { route: "/reporting", description: "Reporting, statistiques et indicateurs metier." },
  { route: "/gemini-analyses", description: "Console admin des analyses contextuelles Gemini, quota, retry et file d'attente." },
  { route: "/admin", description: "Administration generale." },
  { route: "/docs", description: "Reference technique et fonctionnelle integree a l'application." },
];

const apiGroups = [
  {
    title: "Utilisateurs",
    base: "/api/users/",
    endpoints: [
      ["POST", "/login/", "Connexion et creation des cookies JWT", "Public"],
      ["POST", "/logout/", "Deconnexion", "Authentifie"],
      ["POST", "/token/refresh/", "Renouvellement de session", "Public"],
      ["POST", "/register/", "Creation d'un compte", "Admin"],
      ["GET", "/", "Liste des utilisateurs", "Admin, Superviseur"],
      ["GET", "/me/", "Profil courant", "Authentifie"],
      ["PATCH", "/me/", "Mise a jour de son profil", "Authentifie"],
      ["POST", "/change-password/", "Changement mot de passe", "Authentifie"],
      ["GET/PATCH/DELETE", "/:id/", "Detail et gestion d'un utilisateur", "Proprietaire ou Admin"],
    ],
  },
  {
    title: "Cameras",
    base: "/api/cameras/",
    endpoints: [
      ["GET", "/", "Liste des cameras", "Authentifie"],
      ["POST", "/", "Creation d'une camera", "Admin"],
      ["GET", "/active/", "Liste des cameras actives", "Authentifie"],
      ["GET/PATCH/DELETE", "/:id/", "Detail et gestion d'une camera", "Lecture authentifiee, modification selon role"],
      ["PATCH", "/:id/status/", "Mise a jour du statut", "Admin, Superviseur"],
    ],
  },
  {
    title: "Detection",
    base: "/api/detection/",
    endpoints: [
      ["POST", "/detect/", "Analyse d'image et declenchement de detection", "Authentifie"],
      ["GET", "/logs/", "Liste des logs de detection", "Authentifie"],
      ["GET", "/logs/:id/", "Detail d'un log", "Authentifie"],
      ["GET", "/stats/", "Statistiques globales de detection", "Authentifie"],
      ["GET", "/business-kpis/", "KPIs metier avances", "Authentifie"],
      ["GET", "/gemini-analyses/", "Liste admin des analyses contextuelles Gemini", "Admin"],
      ["POST", "/gemini-analyses/process-next/", "Traitement manuel du prochain element Gemini eligible", "Admin"],
    ],
  },
  {
    title: "Alertes",
    base: "/api/alerts/",
    endpoints: [
      ["GET", "/", "Liste des alertes avec filtres", "Authentifie"],
      ["GET", "/stats/", "Statistiques d'alertes", "Authentifie"],
      ["PATCH", "/bulk/", "Mise a jour en masse", "Admin, Superviseur"],
      ["GET", "/:id/", "Detail d'une alerte", "Authentifie"],
      ["PATCH", "/:id/update/", "Statut, affectation, notes", "Admin, Superviseur"],
    ],
  },
  {
    title: "Audits",
    base: "/api/audits/",
    endpoints: [
      ["GET", "/", "Liste des audits", "Authentifie"],
      ["POST", "/", "Creation d'un audit", "Authentifie"],
      ["GET", "/export/", "Export CSV", "Admin, Superviseur"],
      ["GET/PATCH/DELETE", "/:id/", "Detail et gestion d'un audit", "Lecture authentifiee, suppression selon role"],
      ["GET", "/:id/report/", "Rapport PDF", "Authentifie"],
      ["GET/POST", "/:auditId/captures/", "Liste et ajout de captures", "Authentifie"],
      ["DELETE", "/:auditId/captures/:id/", "Suppression d'une capture", "Admin, Superviseur"],
    ],
  },
  {
    title: "Regles HSE",
    base: "/api/rules/hse-rules/",
    endpoints: [
      ["GET", "/", "Liste des regles HSE", "Authentifie"],
      ["POST", "/", "Creation d'une regle HSE", "Admin"],
      ["GET/PATCH/DELETE", "/:id/", "Detail et gestion d'une regle", "Lecture authentifiee, ecriture admin"],
    ],
  },
];

const accountSteps = [
  "Creer le premier administrateur avec la commande Django createsuperuser.",
  "Se connecter sur l'application avec email et mot de passe.",
  "Utiliser l'endpoint POST /api/users/register/ pour creer les autres comptes.",
  "Attribuer un role parmi admin, superviseur ou operateur.",
  "Verifier le profil via GET /api/users/me/.",
];

const sectionCards = [
  {
    icon: ShieldCheck,
    title: "Vision fonctionnelle",
    text: "La plateforme supervise la conformite EPI, transforme les non-conformites en alertes puis en audits actionnables.",
  },
  {
    icon: KeyRound,
    title: "Authentification",
    text: "Le frontend consomme une API Django securisee par JWT en cookies HttpOnly avec credentials include.",
  },
  {
    icon: Network,
    title: "API centralisee",
    text: "Toutes les ressources sont exposees sous /api/ avec une separation claire par domaine fonctionnel.",
  },
  {
    icon: LayoutTemplate,
    title: "Reference produit",
    text: "La page Docs sert de guide d'onboarding, de reference d'integration et de support pour les soutenances.",
  },
  {
    icon: Bot,
    title: "Couche Gemini Vision",
    text: "Une analyse contextuelle LLM est declenchee apres persistance d'une non-conformite, avec file d'attente, quota et reprise apres cooldown.",
  },
];

const geminiHighlights = [
  "Le suivi des 5 minutes n'est plus base seulement sur la camera : il suit une personne localement via ses bounding boxes et un matching IoU entre frames.",
  "Une analyse Gemini est demandee seulement quand la non-conformite persiste pour une meme personne sur la meme camera.",
  "Les analyses Gemini sont reservees a l'administrateur via la page /gemini-analyses.",
  "Le free tier Gemini peut imposer un 429 temporaire. Dans ce cas, l'analyse reste en file et un prochain essai estime est calcule automatiquement.",
  "Le bouton de traitement manuel est desactive tant qu'aucune analyse n'est eligible a un nouvel essai.",
];

const Docs = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b border-border bg-card/70 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-10">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-primary/30 bg-primary/10 shadow-[0_12px_40px_rgba(245,158,11,0.15)]">
              <BookOpen className="text-primary" size={26} />
            </div>
            <div className="space-y-3">
              <span className="inline-flex rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
                Docs projet
              </span>
              <div>
                <h1 className="text-4xl font-black tracking-tight text-foreground">
                  Documentation technique et fonctionnelle
                </h1>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                  Reference integree du projet EPI Guard : architecture, roles, authentification, ecrans frontend,
                  workflow metier et catalogue des endpoints API utilises par l'application.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {sectionCards.map((card) => (
              <div
                key={card.title}
                className="rounded-2xl border border-border bg-background/80 p-5 shadow-sm transition-transform duration-200 hover:-translate-y-1"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-secondary text-foreground">
                  <card.icon size={20} />
                </div>
                <h2 className="text-base font-bold text-foreground">{card.title}</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{card.text}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-2xl border border-primary/20 bg-primary/5 p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-lg font-bold text-foreground">Besoin d'une vue plus structurelle ?</h2>
                <p className="mt-1 text-sm leading-6 text-muted-foreground">
                  La page conception architecturelle decrit les couches, les zones de figures, la maintenance,
                  l'administration et les trajectoires d'evolution technique du systeme.
                </p>
              </div>
              <Link
                to="/architecture-technique"
                className="inline-flex items-center justify-center rounded-xl border border-primary/30 bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
              >
                Ouvrir la conception architecturelle
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-7xl flex-1 gap-8 px-6 py-8 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="h-fit rounded-2xl border border-border bg-card p-4 lg:sticky lg:top-6">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            Navigation
          </p>
          <nav className="space-y-2 text-sm">
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#overview">Vue d'ensemble</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#roles">Roles</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#auth">Authentification</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#accounts">Creation de compte</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#frontend">Pages frontend</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#gemini">Gemini Vision</a>
            <a className="block rounded-lg px-3 py-2 hover:bg-secondary" href="#api">Endpoints API</a>
          </nav>
        </aside>

        <div className="space-y-8">
          <section id="overview" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4 flex items-center gap-3">
              <Network className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Vue d'ensemble</h2>
            </div>
            <p className="max-w-4xl text-sm leading-7 text-muted-foreground">
              Le projet combine un backend Django REST, un frontend React TypeScript, un moteur de detection EPI
              et un workflow de traitement HSE. La chaine metier principale suit le parcours detection, creation
              d'alerte, qualification, audit, puis reporting. Le stockage des images peut s'appuyer sur S3 quand
              l'environnement AWS est configure. Une couche Gemini Vision vient completer YOLO pour qualifier
              contextuellement les non-conformites persistantes.
            </p>
          </section>

          <section id="roles" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Users className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Roles et responsabilites</h2>
            </div>
            <div className="overflow-hidden rounded-xl border border-border">
              <table className="w-full text-left text-sm">
                <thead className="bg-secondary/70 text-foreground">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Role</th>
                    <th className="px-4 py-3 font-semibold">Responsabilites principales</th>
                  </tr>
                </thead>
                <tbody>
                  {roleRows.map((row) => (
                    <tr key={row.role} className="border-t border-border align-top">
                      <td className="px-4 py-3 font-semibold">{row.role}</td>
                      <td className="px-4 py-3 text-muted-foreground">{row.rights}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section id="auth" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <KeyRound className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Authentification</h2>
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-xl border border-border bg-background p-5">
                <h3 className="font-bold">Mecanisme</h3>
                <ul className="mt-3 space-y-2 text-sm leading-6 text-muted-foreground">
                  <li>JWT stocke dans des cookies HttpOnly.</li>
                  <li>Access token dans `access_token`.</li>
                  <li>Refresh token dans `refresh_token`.</li>
                  <li>Le frontend doit envoyer les requetes avec `credentials: include`.</li>
                </ul>
              </div>
              <div className="rounded-xl border border-border bg-background p-5">
                <h3 className="font-bold">Endpoints clefs</h3>
                <div className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <p><span className="font-semibold text-foreground">POST</span> /api/users/login/</p>
                  <p><span className="font-semibold text-foreground">POST</span> /api/users/logout/</p>
                  <p><span className="font-semibold text-foreground">POST</span> /api/users/token/refresh/</p>
                  <p><span className="font-semibold text-foreground">GET</span> /api/users/me/</p>
                </div>
              </div>
            </div>
          </section>

          <section id="accounts" className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-2xl font-bold">Creation de compte</h2>
            <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
              <div className="rounded-xl border border-border bg-background p-5">
                <h3 className="font-bold">Processus recommande</h3>
                <ol className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                  {accountSteps.map((step, index) => (
                    <li key={step} className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                        {index + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
              <div className="rounded-xl border border-border bg-slate-950 p-5 text-slate-100">
                <h3 className="font-bold">Exemple de payload</h3>
                <pre className="mt-4 overflow-x-auto text-xs leading-6 text-slate-300">
{`{
  "email": "operateur@example.com",
  "first_name": "Ali",
  "last_name": "Khaldi",
  "role": "operateur",
  "password": "Password123",
  "password2": "Password123"
}`}
                </pre>
              </div>
            </div>
          </section>

          <section id="frontend" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <LayoutTemplate className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Pages frontend</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {frontendPages.map((page) => (
                <div key={page.route} className="rounded-xl border border-border bg-background p-4">
                  <p className="font-mono-tech text-sm font-semibold text-primary">{page.route}</p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{page.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="gemini" className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <Bot className="text-primary" size={20} />
              <h2 className="text-2xl font-bold">Gemini Vision et reprise automatique</h2>
            </div>

            <div className="grid gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
              <div className="rounded-xl border border-border bg-background p-5">
                <h3 className="font-bold">Logique metier</h3>
                <ul className="mt-4 space-y-3 text-sm leading-6 text-muted-foreground">
                  {geminiHighlights.map((item) => (
                    <li key={item} className="flex gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-border bg-background p-5">
                <h3 className="font-bold">Cycle d'une analyse</h3>
                <div className="mt-4 space-y-3 text-sm text-muted-foreground">
                  <p><span className="font-semibold text-foreground">1.</span> YOLO detecte une non-conformite.</p>
                  <p><span className="font-semibold text-foreground">2.</span> Le backend suit la meme personne dans le temps.</p>
                  <p><span className="font-semibold text-foreground">3.</span> Une entree Gemini est mise en file si la persistance est confirmee.</p>
                  <p><span className="font-semibold text-foreground">4.</span> L'admin traite la file depuis /gemini-analyses.</p>
                  <p><span className="font-semibold text-foreground">5.</span> En cas de quota temporaire, un prochain essai estime est enregistre et affiche.</p>
                </div>
              </div>
            </div>
          </section>

          <section id="api" className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-2xl font-bold">Endpoints API</h2>
            <div className="mt-6 space-y-6">
              {apiGroups.map((group) => (
                <div key={group.title} className="rounded-2xl border border-border bg-background p-5">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-bold">{group.title}</h3>
                      <p className="font-mono-tech text-xs text-muted-foreground">Base: {group.base}</p>
                    </div>
                  </div>

                  <div className="overflow-x-auto rounded-xl border border-border">
                    <table className="w-full min-w-[720px] text-left text-sm">
                      <thead className="bg-secondary/70">
                        <tr>
                          <th className="px-4 py-3 font-semibold">Methode</th>
                          <th className="px-4 py-3 font-semibold">Endpoint</th>
                          <th className="px-4 py-3 font-semibold">Description</th>
                          <th className="px-4 py-3 font-semibold">Acces</th>
                        </tr>
                      </thead>
                      <tbody>
                        {group.endpoints.map(([method, endpoint, description, access]) => (
                          <tr key={`${group.title}-${method}-${endpoint}`} className="border-t border-border align-top">
                            <td className="px-4 py-3 font-mono-tech text-xs font-semibold text-primary">{method}</td>
                            <td className="px-4 py-3 font-mono-tech text-xs text-foreground">{endpoint}</td>
                            <td className="px-4 py-3 text-muted-foreground">{description}</td>
                            <td className="px-4 py-3 text-muted-foreground">{access}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
      <SiteFooter />
    </div>
  );
};

export default Docs;