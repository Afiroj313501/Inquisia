import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { useAuth } from "../context/AuthContext";
import { fetchLatestAssessmentSession } from "./AssessmentPage";
import { fetchLatestInterestProfile } from "./InterestsPage";
import { fetchAcademicProfile } from "./ProfilePage";
import { fetchLatestRecommendations } from "./RecommendationsPage";
import {
  formatEducationLevel,
  formatExperienceLevel,
} from "../types/profile";

export function DashboardPage() {
  const { user } = useAuth();

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: fetchAcademicProfile,
  });

  const assessmentQuery = useQuery({
    queryKey: ["assessment", "latest"],
    queryFn: fetchLatestAssessmentSession,
  });

  const interestQuery = useQuery({
    queryKey: ["interests", "latest"],
    queryFn: fetchLatestInterestProfile,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations", "latest"],
    queryFn: fetchLatestRecommendations,
  });

  const latestSession = assessmentQuery.data;
  const interestProfile = interestQuery.data;
  const recommendationSet = recommendationsQuery.data;

  const journeySteps = [
    {
      label: "Academic Profile",
      done: Boolean(profileQuery.data),
      to: "/profile",
    },
    {
      label: "Assessment",
      done: latestSession?.status === "completed",
      to: "/assessment",
    },
    {
      label: "Interest Profile",
      done: Boolean(interestProfile),
      to: "/interests",
    },
    {
      label: "Topic Recommendations",
      done: Boolean(recommendationSet),
      to: "/recommendations",
    },
  ];
  const completedSteps = journeySteps.filter((s) => s.done).length;
  const nextStep = journeySteps.find((s) => !s.done);

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Welcome, {user?.full_name}
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Signed in as <span className="font-medium">{user?.email}</span>
              </p>
            </div>
            {nextStep && (
              <Link
                to={nextStep.to}
                className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-medium text-white shadow-sm transition hover:bg-slate-800"
              >
                Next: {nextStep.label}
              </Link>
            )}
          </div>

          <div className="mt-6 border-t border-slate-200 pt-5">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span className="font-medium text-slate-700">Research Journey</span>
              <span>
                {completedSteps} of {journeySteps.length} completed
              </span>
            </div>
            <div className="mt-3 grid gap-2 sm:grid-cols-4">
              {journeySteps.map((step, idx) => (
                <Link
                  key={step.to}
                  to={step.to}
                  className={
                    step.done
                      ? "flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50/70 px-3 py-2 text-xs font-medium text-emerald-900"
                      : "flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100"
                  }
                >
                  <span
                    className={
                      step.done
                        ? "flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-[11px] font-semibold text-white"
                        : "flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-200 text-[11px] font-semibold text-slate-700"
                    }
                  >
                    {step.done ? "✓" : idx + 1}
                  </span>
                  <span className="truncate">{step.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Adaptive Research Assessment
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                Discover your research interests, methodology preferences, and
                problem-solving style.
              </p>
            </div>
            <Link
              to="/assessment"
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
            >
              {latestSession?.status === "completed"
                ? "View / Retake"
                : latestSession
                ? "Resume Assessment"
                : "Start Assessment"}
            </Link>
          </div>

          {assessmentQuery.isPending && (
            <p className="mt-4 text-sm text-slate-500">
              Checking assessment status...
            </p>
          )}

          {assessmentQuery.isSuccess && latestSession && (
            <div className="mt-5 border-t border-slate-200 pt-4">
              <div className="flex items-center justify-between text-xs text-slate-600">
                <span>
                  Status:{" "}
                  <strong className="font-medium text-slate-900">
                    {latestSession.status === "completed"
                      ? "Completed"
                      : "In progress"}
                  </strong>
                </span>
                <span>
                  {latestSession.progress.answered_count} /{" "}
                  {latestSession.progress.total_questions} answered (
                  {latestSession.progress.progress_percent}%)
                </span>
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-slate-900"
                  style={{
                    width: `${latestSession.progress.progress_percent}%`,
                  }}
                />
              </div>
            </div>
          )}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Explainable Interest Profile
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                View your domain scores, methodology preferences, and skill
                readiness breakdown.
              </p>
            </div>
            <Link
              to="/interests"
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              {interestProfile ? "View Interest Profile" : "Analyze Interests"}
            </Link>
          </div>

          {interestQuery.isSuccess && interestProfile && (
            <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-4">
              <span className="text-xs font-medium text-slate-500">
                Top domains:
              </span>
              {interestProfile.domain_scores.slice(0, 3).map((d) => (
                <span
                  key={d.key}
                  className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-800"
                >
                  {d.label} ({d.score}%)
                </span>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Topic Recommendations
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                AI-assisted hybrid research topic matches, bookmarks, and
                explainable fit scores.
              </p>
            </div>
            <Link
              to="/recommendations"
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              {recommendationSet ? "View Recommendations" : "Explore Topics"}
            </Link>
          </div>

          {recommendationsQuery.isSuccess && recommendationSet && (
            <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-4">
              <span className="text-xs font-medium text-slate-500">
                Top matches:
              </span>
              {recommendationSet.results.slice(0, 2).map((topic) => (
                <span
                  key={topic.id}
                  className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-800"
                >
                  {topic.title} ({topic.hybrid_score}/100)
                </span>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Research Workspace
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                Search real OpenAlex literature, compare candidate topics, and
                review your skill-gap roadmap.
              </p>
            </div>
            <Link
              to="/workspace"
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              Open Workspace
            </Link>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Academic Profile
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                Your background, skills, and research goals guide topic
                matching and feasibility analysis.
              </p>
            </div>
            <Link
              to="/profile"
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              {profileQuery.data ? "Edit Profile" : "Complete Profile"}
            </Link>
          </div>

          {profileQuery.isPending && (
            <p className="mt-4 text-sm text-slate-500">
              Checking academic profile...
            </p>
          )}

          {profileQuery.isError && (
            <p className="mt-4 text-sm text-rose-600">
              Unable to load academic profile status.
            </p>
          )}

          {profileQuery.isSuccess && !profileQuery.data && (
            <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
              Your academic profile is not set up yet. Complete it to unlock
              personalized research topic feasibility scoring.
            </div>
          )}

          {profileQuery.isSuccess && profileQuery.data && (
            <dl className="mt-6 grid gap-4 border-t border-slate-200 pt-5 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Education & Program
                </dt>
                <dd className="mt-1 text-sm font-medium text-slate-900">
                  {formatEducationLevel(profileQuery.data.education_level)} —{" "}
                  {profileQuery.data.degree_program}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Research Experience
                </dt>
                <dd className="mt-1 text-sm text-slate-900">
                  {formatExperienceLevel(
                    profileQuery.data.research_experience_level
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Technical Skills
                </dt>
                <dd className="mt-1 text-sm text-slate-700">
                  {profileQuery.data.technical_skills.length > 0
                    ? profileQuery.data.technical_skills.join(", ")
                    : "None listed"}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Preferred Domains
                </dt>
                <dd className="mt-1 text-sm text-slate-700">
                  {profileQuery.data.preferred_research_domains.length > 0
                    ? profileQuery.data.preferred_research_domains.join(", ")
                    : "None listed"}
                </dd>
              </div>
            </dl>
          )}
        </section>
      </div>
    </AppLayout>
  );
}
