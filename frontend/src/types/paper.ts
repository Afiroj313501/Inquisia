export interface PaperItem {
  openalex_id: string;
  title: string;
  authors: string[];
  publication_year: number | null;
  venue: string | null;
  cited_by_count: number;
  doi: string | null;
  url: string | null;
  open_access_url: string | null;
  abstract: string | null;
  is_saved: boolean;
}

export interface PaperSearchResponse {
  source: string;
  query: string;
  topic_id: string | null;
  total_count: number;
  results: PaperItem[];
}

export interface SavePaperRequest {
  openalex_id: string;
  topic_id: string | null;
  title: string;
  authors: string[];
  publication_year: number | null;
  venue: string | null;
  cited_by_count: number;
  doi: string | null;
  url: string | null;
  open_access_url: string | null;
  abstract: string | null;
}

export interface SavedPaperResponse {
  id: number;
  openalex_id: string;
  topic_id: string | null;
  title: string;
  authors: string[];
  publication_year: number | null;
  venue: string | null;
  cited_by_count: number;
  doi: string | null;
  url: string | null;
  open_access_url: string | null;
  abstract: string | null;
  created_at: string;
}

export interface LiteratureSynthesisResponse {
  paper_count: number;
  paper_titles: string[];
  model: string;
  common_themes: string[];
  methodological_gaps: string[];
  next_step_recommendation: string;
  ai_generated_notice: string;
}
