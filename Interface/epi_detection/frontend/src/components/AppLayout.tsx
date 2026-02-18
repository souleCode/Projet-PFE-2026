import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Camera,
  Bell,
  Shield,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/cameras", icon: Camera, label: "Caméra en Direct" },
  { to: "/alerts", icon: Bell, label: "Alertes" },
  { to: "/hse-rules", icon: Shield, label: "Gestion des Règles HSE" },
  { to: "/reporting", icon: BarChart3, label: "Reporting" },
  { to: "/admin", icon: Settings, label: "Control Panel" },
];

const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "flex flex-col border-r border-border bg-card transition-all duration-300 shrink-0",
          collapsed ? "w-16" : "w-60"
        )}
      >
        {/* Brand */}
        <div className="h-16 flex items-center gap-3 px-4 border-b border-border">
          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center shrink-0">
            <ShieldAlert size={18} className="text-primary" />
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <h1 className="text-sm font-bold tracking-tight leading-none">
                EPI<span className="text-primary">Guard</span>
              </h1>
              <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
                Sécurité industrielle
              </p>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 flex flex-col gap-1 px-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )
              }
            >
              <item.icon size={18} className="shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="h-12 flex items-center justify-center border-t border-border text-muted-foreground hover:text-destructive transition-colors gap-2"
        >
          <LogOut size={18} />
          {!collapsed && <span>Déconnexion</span>}
        </button>
        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="h-12 flex items-center justify-center border-t border-border text-muted-foreground hover:text-foreground transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;
