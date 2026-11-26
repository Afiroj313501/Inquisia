import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  service: string;
}

type HealthState =
  | { kind: "loading" }
  | { kind: "ok"; data: HealthResponse }
  | { kind: "error"; message: string };

export default function App() {
  const [health, setHealth] = useState<HealthState>({ kind: "loading" });

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      try {
        const res = await fetch("/api/v1/health");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = (await res.json()) as HealthResponse;
        if (active) {
          setHealth({ kind: "ok", data });
        }
      } catch (err) {
        if (active) {
          const message =
            err instanceof Error ? err.message : "Unable to reach API";
          setHealth({ kind: "error", message });
        }
      }
    }

    void checkHealth();

    return () => {
      active = false;
    };
  }, []);

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
          <div className="text-sm">
            {health.kind === "loading" && (
              <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">
                Checking API...
              </span>
            )}
            {health.kind === "ok" && (
              <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                API: {health.data.status}
              </span>
            )}
            {health.kind === "error" && (
              <span className="inline-flex items-center rounded-full bg-rose-50 px-3 py-1 font-medium text-rose-700 ring-1 ring-inset ring-rose-600/20">
                API unavailable ({health.message})
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-12">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            Platform Foundation Ready
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            Inquisia is initialized with a FastAPI modular monolith backend and a
            React + TypeScript + Tailwind CSS frontend. Core modules
            (authentication, academic profile, adaptive questionnaire, and
            hybrid research recommendations) will be added incrementally.
          </p>
        </section>
      </main>
    </div>
  );
}
