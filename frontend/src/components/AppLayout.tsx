import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import type { HealthResponse } from "../types/auth";

export function AppLayout({ children }: { children: ReactNode }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: () => apiRequest<HealthResponse>("/api/v1/health"),
  });

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? "whitespace-nowrap rounded-full bg-white px-3 py-1 text-[13px] font-medium text-slate-900 shadow-sm"
      : "whitespace-nowrap rounded-full px-3 py-1 text-[13px] font-medium text-slate-600 transition-colors hover:text-slate-900";

  const navItems = [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/profile", label: "Academic Profile" },
    { to: "/assessment", label: "Assessment" },
    { to: "/interests", label: "Interest Profile" },
    { to: "/recommendations", label: "Recommendations" },
    { to: "/workspace", label: "Workspace" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/75 backdrop-blur-md supports-[backdrop-filter]:bg-white/65 print:hidden">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6">
          <NavLink
            to="/dashboard"
            className="shrink-0 text-[15px] font-semibold tracking-tight text-slate-900"
          >
            Inquisia
          </NavLink>

          <nav
            aria-label="Primary"
            className="hidden items-center gap-0.5 rounded-full border border-slate-200/80 bg-slate-100/70 p-1 md:flex"
          >
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex shrink-0 items-center gap-3">
            <div className="hidden items-center gap-1.5 text-xs text-slate-500 sm:flex">
              {healthQuery.isPending && (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                  <span className="whitespace-nowrap">Checking API...</span>
                </>
              )}
              {healthQuery.isSuccess && (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span className="whitespace-nowrap">
                    API: {healthQuery.data.status}
                  </span>
                </>
              )}
              {healthQuery.isError && (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
                  <span className="whitespace-nowrap text-rose-600">
                    API unavailable
                  </span>
                </>
              )}
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="whitespace-nowrap rounded-full border border-slate-200/90 bg-white/80 px-3.5 py-1.5 text-[13px] font-medium text-slate-700 transition hover:bg-slate-100/80 hover:text-slate-900"
            >
              Sign out
            </button>
          </div>
        </div>

        <nav
          aria-label="Primary mobile"
          className="flex items-center gap-1 overflow-x-auto border-t border-slate-200/60 px-6 py-2 md:hidden"
        >
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={navLinkClass}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}
