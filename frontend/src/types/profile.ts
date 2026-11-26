export type EducationLevel =
  | "high_school"
  | "undergraduate"
  | "masters"
  | "phd"
  | "postdoc"
  | "industry"
  | "other";

export type ResearchExperienceLevel =
  | "none"
  | "beginner"
  | "intermediate"
  | "experienced";

export interface AcademicProfile {
  id: number;
  user_id: number;
  education_level: EducationLevel;
  degree_program: string;
  academic_background: string | null;
  technical_skills: string[];
  programming_languages: string[];
  preferred_research_domains: string[];
  research_experience_level: ResearchExperienceLevel;
  research_experience_summary: string | null;
  career_goals: string | null;
  weekly_hours_available: number | null;
  created_at: string;
  updated_at: string;
}

export interface AcademicProfileUpsert {
  education_level: EducationLevel;
  degree_program: string;
  academic_background: string | null;
  technical_skills: string[];
  programming_languages: string[];
  preferred_research_domains: string[];
  research_experience_level: ResearchExperienceLevel;
  research_experience_summary: string | null;
  career_goals: string | null;
  weekly_hours_available: number | null;
}

export const EDUCATION_LEVEL_OPTIONS: ReadonlyArray<{
  value: EducationLevel;
  label: string;
}> = [
  { value: "high_school", label: "High School" },
  { value: "undergraduate", label: "Undergraduate" },
  { value: "masters", label: "Master's" },
  { value: "phd", label: "PhD / Doctoral" },
  { value: "postdoc", label: "Postdoctoral" },
  { value: "industry", label: "Industry Researcher" },
  { value: "other", label: "Other" },
];

export const EXPERIENCE_LEVEL_OPTIONS: ReadonlyArray<{
  value: ResearchExperienceLevel;
  label: string;
}> = [
  { value: "none", label: "No prior research experience" },
  { value: "beginner", label: "Beginner (course projects / literature review)" },
  { value: "intermediate", label: "Intermediate (assisted on projects / thesis)" },
  { value: "experienced", label: "Experienced (publications / independent research)" },
];

export function formatEducationLevel(level: EducationLevel): string {
  return (
    EDUCATION_LEVEL_OPTIONS.find((opt) => opt.value === level)?.label ?? level
  );
}

export function formatExperienceLevel(level: ResearchExperienceLevel): string {
  return (
    EXPERIENCE_LEVEL_OPTIONS.find((opt) => opt.value === level)?.label ?? level
  );
}
