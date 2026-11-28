import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const WORKFLOW_STEPS = [
  {
    step: "01",
    title: "Academic Profile",
    description:
      "Capture your degree background, technical skills, programming languages, and weekly research availability.",
  },
  {
    step: "02",
    title: "Adaptive Assessment",
    description:
      "Complete a structured questionnaire with dynamic follow-ups tailored to your domain interests and rigor preferences.",
  },
  {
    step: "03",
    title: "Explainable Interest Profile",
    description:
      "Inspect transparent domain and methodology scores with contribution traces rather than black-box predictions.",
  },
  {
    step: "04",
    title: "Hybrid Topics & OpenAlex Literature",
    description:
      "Explore ranked research directions and search real peer-reviewed papers via OpenAlex in your Research Workspace.",
  },
];

export function LandingPage() {
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/75 backdrop-blur-md supports-[backdrop-filter]:bg-white/65">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <span className="text-[15px] font-semibold tracking-tight text-slate-900">
            Inquisia
          </span>

          <div className="flex items-center gap-2.5">
            <Link
              to="/login"
              className="rounded-full px-3.5 py-1.5 text-[13px] font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900"
            >
              Sign in
            </Link>
            <Link
              to="/register"
              className="rounded-full bg-slate-900 px-4 py-1.5 text-[13px] font-medium text-white shadow-sm transition hover:bg-slate-800"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-16">
        <section className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            Research Direction Discovery
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
            Discover your research interests. Find a realistic direction.
          </h1>
          <p className="mt-5 text-base leading-relaxed text-slate-600">
            Inquisia helps students and early-stage researchers move from broad
            curiosity to concrete, literature-backed research topics through
            adaptive assessments, explainable interest scoring, and live OpenAlex
            paper discovery.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              to="/register"
              className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
            >
              Create free account
            </Link>
            <Link
              to="/login"
              className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              Sign in
            </Link>
          </div>
        </section>

        <section className="mt-16 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {WORKFLOW_STEPS.map((item) => (
            <div
              key={item.step}
              className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <span className="font-mono text-xs font-semibold text-slate-400">
                {item.step}
              </span>
              <h2 className="mt-2 text-base font-semibold text-slate-900">
                {item.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                {item.description}
              </p>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
