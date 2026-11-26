export type QuestionType =
  | "single_choice"
  | "multiple_choice"
  | "rating_scale"
  | "scenario"
  | "technical_preference";

export type AnswerValue = string | string[] | number;

export interface QuestionOption {
  id: string;
  label: string;
  description: string | null;
}

export interface AssessmentQuestion {
  id: string;
  prompt: string;
  question_type: QuestionType;
  category: string;
  help_text: string | null;
  options: QuestionOption[];
  min_value: number | null;
  max_value: number | null;
  min_label: string | null;
  max_label: string | null;
  max_selections: number | null;
  is_adaptive: boolean;
}

export interface AssessmentProgress {
  answered_count: number;
  total_questions: number;
  progress_percent: number;
  next_question_id: string | null;
}

export interface AssessmentSessionDetail {
  id: number;
  status: "in_progress" | "completed";
  current_question_id: string | null;
  started_at: string;
  updated_at: string;
  completed_at: string | null;
  questions: AssessmentQuestion[];
  responses: Record<string, AnswerValue>;
  progress: AssessmentProgress;
}
