import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { useAuth } from "../context/AuthContext";
import { fetchLatestAssessmentSession } from "./AssessmentPage";
import { fetchAcademicProfile } from "./ProfilePage";
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

  const latestSession = assessmentQuery.data;

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            Welcome, {user?.full_name}
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Signed in as <span className="font-medium">{user?.email}</span>
          </p>
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
