import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { authApi } from "@/lib/api";
import SiteFooter from "@/components/SiteFooter";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [showConfirmPwd, setShowConfirmPwd] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("operateur");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!email || !password || !confirmPwd || !firstName || !lastName) {
      setError("Veuillez remplir tous les champs.");
      return;
    }
    if (password !== confirmPwd) {
      setError("Les mots de passe ne correspondent pas.");
      return;
    }
    setLoading(true);
    try {
      await authApi.register({
        email,
        first_name: firstName,
        last_name: lastName,
        password,
        password2: confirmPwd,
      });
      setSuccess("Compte créé avec succès ! Vous pouvez vous connecter.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la création du compte.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-primary/10 to-background">
      <div className="flex flex-1 items-center justify-center px-4 py-8">
        <div className="w-full max-w-md bg-card border border-border rounded-xl shadow-lg p-8 space-y-6">
          <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
            <ShieldCheck size={28} className="text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold leading-tight tracking-tight">
              EPI<span className="text-primary">Guard</span>
            </h1>
            <p className="text-xs text-muted-foreground font-mono">Surveillance des équipements de protection</p>
          </div>
        </div>
          <div className="border-b border-border mb-2" />
          <h2 className="text-lg font-semibold">Créer un compte</h2>
          <p className="text-sm text-muted-foreground mb-4">Inscrivez-vous pour accéder à la plateforme</p>
          {error && (
            <Alert variant="destructive" className="mb-2">
              <AlertTitle>Erreur</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {success && (
            <Alert variant="default" className="mb-2">
              <AlertTitle>Succès</AlertTitle>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
             <div className="space-y-2">
            <Label htmlFor="lastName">Nom de Famille</Label>
            <Input
              id="lastName"
              type="text"
              autoComplete="family-name"
              placeholder="Nom de famille"
              value={lastName}
              onChange={e => setLastName(e.target.value)}
              required
            />
          </div>
           <div className="space-y-2">
            <Label htmlFor="firstName">Prénom(s)</Label>
            <Input
              id="firstName"
              type="text"
              autoComplete="given-name"
              placeholder="Prénom"

              value={firstName}
              onChange={e => setFirstName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Adresse email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="nom@entreprise.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Mot de passe</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPwd ? "text" : "password"}
                autoComplete="new-password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="pr-10"
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                onClick={() => setShowPwd(v => !v)}
                tabIndex={-1}
              >
                {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmPwd">Confirmer le mot de passe</Label>
            <div className="relative">
              <Input
                id="confirmPwd"
                type={showConfirmPwd ? "text" : "password"}
                autoComplete="new-password"
                placeholder="••••••••"
                value={confirmPwd}
                onChange={e => setConfirmPwd(e.target.value)}
                required
                className="pr-10"
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                onClick={() => setShowConfirmPwd(v => !v)}
                tabIndex={-1}
              >
                {showConfirmPwd ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>
          <Button type="submit" className="w-full mt-2" disabled={loading}>
            {loading ? "Création..." : "Créer le compte"}
          </Button>
          </form>
        </div>
      </div>
      <SiteFooter />
    </div>
  );
}
