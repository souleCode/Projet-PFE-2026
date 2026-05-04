import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import AppLayout from "@/components/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Cameras from "@/pages/Cameras";
import Alerts from "@/pages/Alerts";
import HSERules from "@/pages/HSERules";
import Reporting from "@/pages/Reporting";
import AuditDetail from "@/pages/AuditDetail";
import Admin from "@/pages/Admin";
import Docs from "@/pages/Docs";
import ArchitectureTechnique from "@/pages/ArchitectureTechnique";
import GeminiAnalyses from "@/pages/GeminiAnalyses";
import NotFound from "./pages/NotFound";
import LoginPage from "./pages/userss/login";
import RegisterPage from "./pages/userss/register";
import { AuthProvider, useAuth } from "@/context/AuthContext";


const queryClient = new QueryClient();

function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/architecture-technique" element={<ArchitectureTechnique />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/cameras" element={<Cameras />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/audits/:auditId" element={<AuditDetail />} />
                <Route path="/hse-rules" element={<HSERules />} />
                <Route path="/reporting" element={<Reporting />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/gemini-analyses" element={<GeminiAnalyses />} />
              </Route>
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
