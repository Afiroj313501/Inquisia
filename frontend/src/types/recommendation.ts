import type { ResearchExperienceLevel } from "./profile";

export interface ScoreBreakdown {
  interest_alignment: number;
  skill_feasibility: number;
  methodology_fit: number;
  semantic_similarity: number;
  explanation: string;
}

export interface TopicRecommendation {
  id: string;
  title: string;
  description: string;
  keywords: string[];
  domain_tags: string[];
  methodology_tags: string[];
  min_experience_level: ResearchExperienceLevel;
  min_weekly_hours: number;
  hybrid_score: number;
  score_breakdown: ScoreBreakdown;
  is_bookmarked: boolean;
  user_rating: number | null;
}

export interface RecommendationSetResponse {
  id: number;
  user_id: number;
  interest_profile_id: number;
  methodology_note: string;
  results: TopicRecommendation[];
  created_at: string;
  updated_at: string;
}

export interface BookmarkResponse {
  id: number;
  topic_id: string;
  title: string;
  domain_tags: string[];
  created_at: string;
}

export interface FeedbackResponse {
  id: number;
  topic_id: string;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export const DOMAIN_TAG_LABELS: Record<string, string> = {
  ai_ml: "AI & ML",
  nlp: "NLP & IR",
  systems_security: "Systems & Security",
  hci: "HCI & EdTech",
  bio_health: "Bio & Health",
  data_science: "Data Science",
};

export function formatDomainTag(tag: string): string {
  return DOMAIN_TAG_LABELS[tag] ?? tag;
}
