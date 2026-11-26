import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AppLayout } from "../components/AppLayout";
import { ApiError, apiRequest } from "../lib/api";
import type { InterestProfile, ScoreEntry } from "../types/interest";

export async function fetchLatestInterestProfile(): Promise<InterestProfile | null> {
  try {
    return await apiRequest<InterestProfile>("/api/v1/interests/latest");
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

function ContributionSection({
  title,
  entries,
}: {
  title: string;
  entries: ScoreEntry[];
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <div className="mt-4 space-y-4">
        {entries.map((entry) => (
          <div
            key={entry.key}
            className="rounded-lg border border-slate-200 bg-slate-50 p-4"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-medium text-slate-900">
                {entry.label}
              </span>
              <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-800 ring-1 ring-inset ring-slate-200">
                {entry.score} / 100
              </span>
            </div>

            {entry.contributions.length > 0 ? (
              <ul className="mt-2.5 space-y-1 text-xs text-slate-600">
                {entry.contributions.map((item, idx) => (
                  <li key={`${entry.key}-${idx}`} className="flex justify-between gap-4">
                    <span>• {item.reason}</span>
                    <span className="shrink-0 font-mono text-slate-500">
                      +{item.weight.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-xs text-slate-500">
                No direct signals recorded for this category.
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function InterestsPage() {
  const queryClient = useQueryClient();

  const interestQuery = useQuery({
    queryKey: ["interests", "latest"],
    queryFn: fetchLatestInterestProfile,
  });

  const analyzeMutation = useMutation({
    mutationFn: () =>
      apiRequest<InterestProfile>("/api/v1/interests/analyze", {
        method: "POST",
      }),
    onSuccess: (profile) => {
      queryClient.setQueryData(["interests", "latest"], profile);
    },
  });

  const profile = interestQuery.data;

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Explainable Research Interest Profile
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Transparent breakdown of your research domains, methodology
                preferences, and technical readiness.
              </p>
            </div>

            <button
              type="button"
              disabled={analyzeMutation.isPending}
              onClick={() => analyzeMutation.mutate()}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {analyzeMutation.isPending
                ? "Analyzing..."
                : profile
                ? "Recompute Profile"
                : "Generate Interest Profile"}
            </button>
          </div>

          {analyzeMutation.isError && (
            <div
              role="alert"
              className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
            >
              {analyzeMutation.error instanceof ApiError
                ? analyzeMutation.error.message
                : "Unable to analyze interests right now."}
            </div>
          )}
        </section>

        {interestQuery.isPending && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm text-slate-600">
              Loading your interest profile...
            </p>
          </div>
        )}

        {interestQuery.isSuccess && !profile && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <h3 className="text-base font-semibold text-slate-900">
              No Interest Profile Generated Yet
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Complete the Adaptive Research Assessment first, then click{" "}
              <strong>Generate Interest Profile</strong> above to view your
              explainable breakdown.
            </p>
            <Link
              to="/assessment"
              className="mt-4 inline-block rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              Go to Assessment
            </Link>
          </div>
        )}

        {profile && (
          <>
            <div className="grid gap-6 lg:grid-cols-2">
              <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="text-base font-semibold text-slate-900">
                  Research Domain Scores
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  Normalized 0–100 preference strength across core research
                  areas.
                </p>
                <div className="mt-4 h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={profile.domain_scores}
                      layout="vertical"
                      margin={{ top: 8, right: 20, left: 10, bottom: 8 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
                      <YAxis
                        type="category"
                        dataKey="label"
                        width={175}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Bar dataKey="score" fill="#0f172a" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="text-base font-semibold text-slate-900">
                  Methodology & Problem-Solving Profile
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  Balance across theoretical rigor, experimentation,
                  engineering, and human-centered inquiry.
                </p>
                <div className="mt-4 h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={profile.dimension_scores}>
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis
                        dataKey="label"
                        tick={{ fontSize: 10 }}
                      />
                      <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                      <Radar
                        name="Score"
                        dataKey="score"
                        stroke="#0f172a"
                        fill="#0f172a"
                        fillOpacity={0.25}
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </div>

            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-base font-semibold text-slate-900">
                Skill & Readiness Confidence
              </h3>
              <dl className="mt-4 grid gap-4 sm:grid-cols-4">
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <dt className="text-xs font-medium text-slate-500">
                    Overall Readiness
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-900">
                    {profile.skill_confidence.overall_confidence}%
                  </dd>
                </div>
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <dt className="text-xs font-medium text-slate-500">
                    Math Comfort
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-900">
                    {profile.skill_confidence.math_comfort} / 5
                  </dd>
                </div>
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <dt className="text-xs font-medium text-slate-500">
                    Coding Comfort
                  </dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-900">
                    {profile.skill_confidence.coding_comfort} / 5
                  </dd>
                </div>
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <dt className="text-xs font-medium text-slate-500">
                    Research Experience
                  </dt>
                  <dd className="mt-1 text-lg font-semibold capitalize text-slate-900">
                    {profile.skill_confidence.experience_level}
                  </dd>
                </div>
              </dl>
            </section>

            <div className="grid gap-6 lg:grid-cols-2">
              <ContributionSection
                title="Domain Score Explanations"
                entries={profile.domain_scores}
              />
              <ContributionSection
                title="Methodology & Preference Explanations"
                entries={profile.dimension_scores}
              />
            </div>

            <section className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-xs leading-relaxed text-amber-950">
              <strong className="font-semibold">
                Methodology & Limitations:
              </strong>{" "}
              {profile.limitations_note}
            </section>
          </>
        )}
      </div>
    </AppLayout>
  );
}
