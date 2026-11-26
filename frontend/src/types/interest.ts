export interface ContributionItem {
  source: string;
  reason: string;
  weight: number;
}

export interface ScoreEntry {
  key: string;
  label: string;
  score: number;
  contributions: ContributionItem[];
}

export interface SkillConfidenceSummary {
  math_comfort: number;
  coding_comfort: number;
  experience_level: string;
  technical_skills_count: number;
  programming_languages_count: number;
  overall_confidence: number;
}

export interface InterestProfile {
  id: number;
  user_id: number;
  session_id: number;
  domain_scores: ScoreEntry[];
  dimension_scores: ScoreEntry[];
  skill_confidence: SkillConfidenceSummary;
  top_domains: string[];
  limitations_note: string;
  created_at: string;
  updated_at: string;
}
