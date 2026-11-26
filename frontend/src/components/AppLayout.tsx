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
      ? "rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-900"
      : "rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-xl font-semibold tracking-tight text-slate-900">
                Inquisia
              </h1>
              <p className="text-xs text-slate-500">
                Discover Your Research Interests. Find Your Direction.
              </p>
            </div>

            <nav aria-label="Primary" className="flex items-center gap-1">
              <NavLink to="/dashboard" className={navLinkClass}>
                Dashboard
              </NavLink>
              <NavLink to="/profile" className={navLinkClass}>
                Academic Profile
              </NavLink>
              <NavLink to="/assessment" className={navLinkClass}>
                Assessment
              </NavLink>
              <NavLink to="/interests" className={navLinkClass}>
                Interest Profile
              </NavLink>
              <NavLink to="/recommendations" className={navLinkClass}>
                Recommendations
              </NavLink>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-sm">
              {healthQuery.isPending && (
                <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  Checking API...
                </span>
              )}
              {healthQuery.isSuccess && (
                <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                  API: {healthQuery.data.status}
                </span>
              )}
              {healthQuery.isError && (
                <span className="inline-flex items-center rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-700 ring-1 ring-inset ring-rose-600/20">
                  API unavailable
                </span>
              )}
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg border border-slate-300 bg-white px-3.5 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
    </div>
  );
}
