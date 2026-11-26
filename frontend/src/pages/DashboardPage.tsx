import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import type { HealthResponse } from "../types/auth";

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: () => apiRequest<HealthResponse>("/api/v1/health"),
  });

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-slate-900">
              Inquisia
            </h1>
            <p className="text-sm text-slate-600">
              Discover Your Research Interests. Find Your Direction.
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-sm">
              {healthQuery.isPending && (
                <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">
                  Checking API...
                </span>
              )}
              {healthQuery.isSuccess && (
                <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                  API: {healthQuery.data.status}
                </span>
              )}
              {healthQuery.isError && (
                <span className="inline-flex items-center rounded-full bg-rose-50 px-3 py-1 font-medium text-rose-700 ring-1 ring-inset ring-rose-600/20">
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

      <main className="mx-auto max-w-5xl px-6 py-10">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            Welcome, {user?.full_name}
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Signed in as <span className="font-medium">{user?.email}</span>
          </p>

          <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-700">
              Authentication is active. Upcoming modules will add your Academic
              Profile, Adaptive Research Assessment, and Hybrid Topic
              Recommendations here.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
