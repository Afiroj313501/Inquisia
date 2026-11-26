import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { useAuth } from "../context/AuthContext";
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
                Academic Profile
              </h3>
              <p className="mt-1 text-sm text-slate-600">
                Your background, skills, and research goals guide topic
                matching and feasibility analysis.
              </p>
            </div>
            <Link
              to="/profile"
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
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
