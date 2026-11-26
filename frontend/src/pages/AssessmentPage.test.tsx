import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";

function renderAssessmentRoute() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/assessment"]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

const baseQuestions = [
  {
    id: "q_domains_interest",
    prompt: "Which research areas spark your curiosity the most?",
    question_type: "multiple_choice",
    category: "Subject Interest",
    help_text: "Select up to 3 areas.",
    options: [
      { id: "ai_ml", label: "Artificial Intelligence & ML", description: null },
      { id: "hci_edtech", label: "Human-Computer Interaction", description: null },
    ],
    min_value: null,
    max_value: null,
    min_label: null,
    max_label: null,
    max_selections: 3,
    is_adaptive: false,
  },
  {
    id: "q_math_comfort",
    prompt: "How comfortable are you with formal math?",
    question_type: "rating_scale",
    category: "Skill Confidence",
    help_text: null,
    options: [],
    min_value: 1,
    max_value: 5,
    min_label: "Minimal",
    max_label: "Very comfortable",
    max_selections: null,
    is_adaptive: false,
  },
];

const adaptiveQuestion = {
  id: "q_followup_ai_nlp",
  prompt: "Follow-up: Within AI/NLP, which angle appeals to you?",
  question_type: "single_choice",
  category: "Adaptive Follow-up",
  help_text: "Shown because you selected AI/ML.",
  options: [
    { id: "scientific_nlp", label: "Scientific literature mining", description: null },
  ],
  min_value: null,
  max_value: null,
  min_label: null,
  max_label: null,
  max_selections: null,
  is_adaptive: true,
};

describe("AssessmentPage", () => {
  beforeEach(() => {
    localStorage.setItem("inquisia_access_token", "valid-jwt");
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("answers core questions, unlocks adaptive follow-up, and completes assessment", async () => {
    let step = 0;

    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = typeof input === "string" ? input : input.toString();

      if (url.endsWith("/api/v1/auth/me")) {
        return new Response(
          JSON.stringify({
            id: 1,
            email: "ada@example.edu",
            full_name: "Ada Lovelace",
            is_active: true,
            created_at: "2026-11-27T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/health")) {
        return new Response(
          JSON.stringify({ status: "ok", service: "inquisia-api" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/assessments/sessions") && init?.method === "POST") {
        return new Response(
          JSON.stringify({
            id: 5,
            status: "in_progress",
            current_question_id: "q_domains_interest",
            started_at: "2026-11-27T00:00:00Z",
            updated_at: "2026-11-27T00:00:00Z",
            completed_at: null,
            questions: baseQuestions,
            responses: {},
            progress: {
              answered_count: 0,
              total_questions: 2,
              progress_percent: 0,
              next_question_id: "q_domains_interest",
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/assessments/sessions/5/responses") && init?.method === "PUT") {
        step += 1;
        if (step === 1) {
          return new Response(
            JSON.stringify({
              id: 5,
              status: "in_progress",
              current_question_id: "q_math_comfort",
              started_at: "2026-11-27T00:00:00Z",
              updated_at: "2026-11-27T00:00:00Z",
              completed_at: null,
              questions: [...baseQuestions, adaptiveQuestion],
              responses: { q_domains_interest: ["ai_ml"] },
              progress: {
                answered_count: 1,
                total_questions: 3,
                progress_percent: 33,
                next_question_id: "q_math_comfort",
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          );
        }

        if (step === 2) {
          return new Response(
            JSON.stringify({
              id: 5,
              status: "in_progress",
              current_question_id: "q_followup_ai_nlp",
              started_at: "2026-11-27T00:00:00Z",
              updated_at: "2026-11-27T00:00:00Z",
              completed_at: null,
              questions: [...baseQuestions, adaptiveQuestion],
              responses: {
                q_domains_interest: ["ai_ml"],
                q_math_comfort: 4,
              },
              progress: {
                answered_count: 2,
                total_questions: 3,
                progress_percent: 67,
                next_question_id: "q_followup_ai_nlp",
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({
            id: 5,
            status: "in_progress",
            current_question_id: "q_followup_ai_nlp",
            started_at: "2026-11-27T00:00:00Z",
            updated_at: "2026-11-27T00:00:00Z",
            completed_at: null,
            questions: [...baseQuestions, adaptiveQuestion],
            responses: {
              q_domains_interest: ["ai_ml"],
              q_math_comfort: 4,
              q_followup_ai_nlp: "scientific_nlp",
            },
            progress: {
              answered_count: 3,
              total_questions: 3,
              progress_percent: 100,
              next_question_id: null,
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/assessments/sessions/5/complete") && init?.method === "POST") {
        return new Response(
          JSON.stringify({
            id: 5,
            status: "completed",
            current_question_id: null,
            started_at: "2026-11-27T00:00:00Z",
            updated_at: "2026-11-27T00:00:00Z",
            completed_at: "2026-11-27T00:05:00Z",
            questions: [...baseQuestions, adaptiveQuestion],
            responses: {
              q_domains_interest: ["ai_ml"],
              q_math_comfort: 4,
              q_followup_ai_nlp: "scientific_nlp",
            },
            progress: {
              answered_count: 3,
              total_questions: 3,
              progress_percent: 100,
              next_question_id: null,
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      throw new Error(`Unexpected request: ${url}`);
    });

    renderAssessmentRoute();

    // Step 1: multiple_choice
    await waitFor(() => {
      expect(
        screen.getByText("Which research areas spark your curiosity the most?")
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Artificial Intelligence & ML"));
    fireEvent.click(screen.getByRole("button", { name: "Save & Continue" }));

    // Step 2: rating_scale
    await waitFor(() => {
      expect(
        screen.getByText("How comfortable are you with formal math?")
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "4" }));
    fireEvent.click(screen.getByRole("button", { name: "Save & Continue" }));

    // Step 3: unlocked adaptive follow-up
    await waitFor(() => {
      expect(
        screen.getAllByText("Adaptive Follow-up").length
      ).toBeGreaterThanOrEqual(1);
      expect(
        screen.getByText("Follow-up: Within AI/NLP, which angle appeals to you?")
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Scientific literature mining"));
    fireEvent.click(
      screen.getByRole("button", { name: "Complete Assessment" })
    );

    await waitFor(() => {
      expect(
        screen.getByText("Research Interest Assessment Complete")
      ).toBeInTheDocument();
    });
  });
});
