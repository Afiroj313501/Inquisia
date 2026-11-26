import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { AppLayout } from "../components/AppLayout";
import { TagInput } from "../components/TagInput";
import { ApiError, apiRequest } from "../lib/api";
import {
  EDUCATION_LEVEL_OPTIONS,
  EXPERIENCE_LEVEL_OPTIONS,
  type AcademicProfile,
  type AcademicProfileUpsert,
} from "../types/profile";

const profileSchema = z.object({
  education_level: z.enum([
    "high_school",
    "undergraduate",
    "masters",
    "phd",
    "postdoc",
    "industry",
    "other",
  ]),
  degree_program: z
    .string()
    .trim()
    .min(2, "Degree or program must be at least 2 characters")
    .max(160, "Degree or program must be 160 characters or fewer"),
  academic_background: z
    .string()
    .max(2000, "Academic background must be 2000 characters or fewer")
    .optional(),
  technical_skills: z.array(z.string()),
  programming_languages: z.array(z.string()),
  preferred_research_domains: z.array(z.string()),
  research_experience_level: z.enum([
    "none",
    "beginner",
    "intermediate",
    "experienced",
  ]),
  research_experience_summary: z
    .string()
    .max(2000, "Experience summary must be 2000 characters or fewer")
    .optional(),
  career_goals: z
    .string()
    .max(2000, "Career goals must be 2000 characters or fewer")
    .optional(),
  weekly_hours_available: z
    .union([
      z.literal(""),
      z.coerce
        .number()
        .int("Enter a whole number of hours")
        .min(1, "Minimum is 1 hour per week")
        .max(80, "Maximum is 80 hours per week"),
    ])
    .optional(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

export async function fetchAcademicProfile(): Promise<AcademicProfile | null> {
  try {
    return await apiRequest<AcademicProfile>("/api/v1/profile");
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export function ProfilePage() {
  const queryClient = useQueryClient();
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: fetchAcademicProfile,
  });

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      education_level: "undergraduate",
      degree_program: "",
      academic_background: "",
      technical_skills: [],
      programming_languages: [],
      preferred_research_domains: [],
      research_experience_level: "beginner",
      research_experience_summary: "",
      career_goals: "",
      weekly_hours_available: "",
    },
  });

  useEffect(() => {
    if (profileQuery.data) {
      const p = profileQuery.data;
      reset({
        education_level: p.education_level,
        degree_program: p.degree_program,
        academic_background: p.academic_background ?? "",
        technical_skills: p.technical_skills,
        programming_languages: p.programming_languages,
        preferred_research_domains: p.preferred_research_domains,
        research_experience_level: p.research_experience_level,
        research_experience_summary: p.research_experience_summary ?? "",
        career_goals: p.career_goals ?? "",
        weekly_hours_available:
          p.weekly_hours_available !== null ? p.weekly_hours_available : "",
      });
    }
  }, [profileQuery.data, reset]);

  const saveMutation = useMutation({
    mutationFn: (payload: AcademicProfileUpsert) =>
      apiRequest<AcademicProfile>("/api/v1/profile", {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile"], updated);
      setServerError(null);
      setSaveMessage("Academic profile saved.");
    },
    onError: (err) => {
      setSaveMessage(null);
      setServerError(
        err instanceof ApiError
          ? err.message
          : "Unable to save your academic profile."
      );
    },
  });

  function onSubmit(values: ProfileFormValues) {
    setSaveMessage(null);
    setServerError(null);

    const toNullableText = (raw?: string) => {
      const cleaned = raw?.trim();
      return cleaned ? cleaned : null;
    };

    const payload: AcademicProfileUpsert = {
      education_level: values.education_level,
      degree_program: values.degree_program.trim(),
      academic_background: toNullableText(values.academic_background),
      technical_skills: values.technical_skills,
      programming_languages: values.programming_languages,
      preferred_research_domains: values.preferred_research_domains,
      research_experience_level: values.research_experience_level,
      research_experience_summary: toNullableText(
        values.research_experience_summary
      ),
      career_goals: toNullableText(values.career_goals),
      weekly_hours_available:
        values.weekly_hours_available === "" ||
        values.weekly_hours_available === undefined
          ? null
          : Number(values.weekly_hours_available),
    };

    saveMutation.mutate(payload);
  }

  return (
    <AppLayout>
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="border-b border-slate-200 pb-5">
          <h2 className="text-lg font-semibold text-slate-900">
            Academic Profile
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Provide your academic background, technical skills, and research
            goals to inform topic feasibility and personalized recommendations.
          </p>
        </div>

        {profileQuery.isPending && (
          <p className="mt-6 text-sm text-slate-600">
            Loading your academic profile...
          </p>
        )}

        {profileQuery.isError && (
          <div
            role="alert"
            className="mt-6 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
          >
            Failed to load your academic profile. Please refresh and try again.
          </div>
        )}

        {!profileQuery.isPending && !profileQuery.isError && (
          <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-6">
            {saveMessage && (
              <div
                role="status"
                className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
              >
                {saveMessage}
              </div>
            )}

            {serverError && (
              <div
                role="alert"
                className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
              >
                {serverError}
              </div>
            )}

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="education_level"
                  className="block text-sm font-medium text-slate-700"
                >
                  Education level
                </label>
                <select
                  id="education_level"
                  {...register("education_level")}
                  className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                >
                  {EDUCATION_LEVEL_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="degree_program"
                  className="block text-sm font-medium text-slate-700"
                >
                  Degree / academic program
                </label>
                <input
                  id="degree_program"
                  type="text"
                  {...register("degree_program")}
                  placeholder="e.g., B.Sc. in Computer Science"
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                {errors.degree_program && (
                  <p className="mt-1 text-xs text-rose-600">
                    {errors.degree_program.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label
                htmlFor="academic_background"
                className="block text-sm font-medium text-slate-700"
              >
                Academic background & key coursework
              </label>
              <textarea
                id="academic_background"
                rows={3}
                {...register("academic_background")}
                placeholder="Summarize relevant coursework, honors, or domain foundations..."
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              />
            </div>

            <div className="space-y-5">
              <Controller
                name="technical_skills"
                control={control}
                render={({ field }) => (
                  <TagInput
                    id="technical_skills"
                    label="Technical skills & methods"
                    placeholder="e.g., Statistical Modeling, PyTorch, Qualitative Coding"
                    helperText="Press Enter or click Add after each skill."
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />

              <Controller
                name="programming_languages"
                control={control}
                render={({ field }) => (
                  <TagInput
                    id="programming_languages"
                    label="Programming languages & tools"
                    placeholder="e.g., Python, R, SQL, TypeScript"
                    helperText="Press Enter or click Add after each language."
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />

              <Controller
                name="preferred_research_domains"
                control={control}
                render={({ field }) => (
                  <TagInput
                    id="preferred_research_domains"
                    label="Preferred research domains"
                    placeholder="e.g., Natural Language Processing, Computational Biology, HCI"
                    helperText="Press Enter or click Add after each domain."
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="research_experience_level"
                  className="block text-sm font-medium text-slate-700"
                >
                  Research experience level
                </label>
                <select
                  id="research_experience_level"
                  {...register("research_experience_level")}
                  className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                >
                  {EXPERIENCE_LEVEL_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="weekly_hours_available"
                  className="block text-sm font-medium text-slate-700"
                >
                  Weekly hours available for research
                </label>
                <input
                  id="weekly_hours_available"
                  type="number"
                  min={1}
                  max={80}
                  {...register("weekly_hours_available")}
                  placeholder="e.g., 15"
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                {errors.weekly_hours_available && (
                  <p className="mt-1 text-xs text-rose-600">
                    {errors.weekly_hours_available.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label
                htmlFor="research_experience_summary"
                className="block text-sm font-medium text-slate-700"
              >
                Prior research experience summary (optional)
              </label>
              <textarea
                id="research_experience_summary"
                rows={3}
                {...register("research_experience_summary")}
                placeholder="Describe any lab work, capstone projects, or publications..."
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              />
            </div>

            <div>
              <label
                htmlFor="career_goals"
                className="block text-sm font-medium text-slate-700"
              >
                Career & academic goals (optional)
              </label>
              <textarea
                id="career_goals"
                rows={3}
                {...register("career_goals")}
                placeholder="e.g., Publish an undergraduate thesis, apply to ML PhD programs, or transition to R&D..."
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
              />
            </div>

            <div className="flex justify-end border-t border-slate-200 pt-5">
              <button
                type="submit"
                disabled={saveMutation.isPending}
                className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {saveMutation.isPending ? "Saving..." : "Save Academic Profile"}
              </button>
            </div>
          </form>
        )}
      </div>
    </AppLayout>
  );
}
