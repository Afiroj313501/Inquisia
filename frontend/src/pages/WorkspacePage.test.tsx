import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";

function renderAppAt(route: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

const SAMPLE_RECS = {
  id: 1,
  user_id: 1,
  interest_profile_id: 2,
  methodology_note: "AI-assisted hybrid recommendations.",
  created_at: "2026-11-27T01:00:00Z",
  updated_at: "2026-11-27T01:00:00Z",
  results: [
    {
      id: "nlp_scientific_rag",
      title: "Citation-Grounded Retrieval-Augmented Generation for Science",
      description: "Building retrieval pipelines grounded in scientific literature.",
      keywords: ["rag", "nlp", "citations"],
      domain_tags: ["nlp", "ai_ml"],
      methodology_tags: ["applied_engineering"],
      min_experience_level: "none",
      min_weekly_hours: 8,
      hybrid_score: 88,
      score_breakdown: {
        interest_alignment: 90,
        skill_feasibility: 92,
        methodology_fit: 84,
        semantic_similarity: 78,
        explanation: "Strong fit.",
      },
      is_bookmarked: true,
      user_rating: 5,
    },
    {
      id: "ai_mechanistic_interpretability",
      title: "Mechanistic Interpretability of Neural Networks",
      description: "Probing internal representations in transformers.",
      keywords: ["interpretability", "pytorch"],
      domain_tags: ["ai_ml"],
      methodology_tags: ["empirical_experimentation"],
      min_experience_level: "beginner",
      min_weekly_hours: 10,
      hybrid_score: 81,
      score_breakdown: {
        interest_alignment: 85,
        skill_feasibility: 80,
        methodology_fit: 78,
        semantic_similarity: 72,
        explanation: "Good fit.",
      },
      is_bookmarked: true,
      user_rating: null,
    },
  ],
};

describe("WorkspacePage", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("inquisia_access_token", "valid-jwt");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("searches OpenAlex papers, saves a paper, and renders comparison & roadmap", async () => {
    let savedList: Array<Record<string, unknown>> = [
      {
        id: 11,
        openalex_id: "W100",
        topic_id: "nlp_scientific_rag",
        title: "Existing Saved Paper",
        authors: ["Ada Researcher"],
        publication_year: 2024,
        venue: "EMNLP",
        cited_by_count: 15,
        doi: null,
        url: null,
        open_access_url: null,
        abstract: "Baseline scientific retrieval study.",
        created_at: "2026-11-27T00:30:00Z",
      },
    ];

    vi.spyOn(globalThis, "fetch").mockImplementation((input, init) => {
      const url = typeof input === "string" ? input : input.toString();
      const method = init?.method ?? "GET";

      if (url.endsWith("/api/v1/auth/me")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 1,
              email: "ada@example.edu",
              full_name: "Ada Lovelace",
              is_active: true,
              created_at: "2026-11-27T00:00:00Z",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/health")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ status: "ok", service: "inquisia-api" }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/recommendations/latest")) {
        return Promise.resolve(
          new Response(JSON.stringify(SAMPLE_RECS), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.endsWith("/api/v1/profile")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 1,
              user_id: 1,
              education_level: "undergraduate",
              degree_program: "B.Sc. CS",
              academic_background: null,
              technical_skills: ["NLP"],
              programming_languages: ["Python"],
              preferred_research_domains: ["NLP"],
              research_experience_level: "beginner",
              research_experience_summary: null,
              career_goals: null,
              weekly_hours_available: 12,
              created_at: "2026-11-27T00:00:00Z",
              updated_at: "2026-11-27T00:00:00Z",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/papers/saved") && method === "GET") {
        return Promise.resolve(
          new Response(JSON.stringify(savedList), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.includes("/api/v1/papers/search")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              source: "OpenAlex",
              query: "Citation-Grounded Retrieval-Augmented Generation",
              topic_id: "nlp_scientific_rag",
              total_count: 1,
              results: [
                {
                  openalex_id: "W999",
                  title: "Grounded Scientific QA with Retrieval",
                  authors: ["Jane Doe"],
                  publication_year: 2025,
                  venue: "ACL",
                  cited_by_count: 19,
                  doi: "https://doi.org/10.1234/acl",
                  url: "https://doi.org/10.1234/acl",
                  open_access_url: "https://arxiv.org/pdf/2501.00001",
                  abstract: "A study on grounded scientific QA.",
                  is_saved: false,
                },
              ],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/papers/saved") && method === "POST") {
        const saved = {
          id: 77,
          openalex_id: "W999",
          topic_id: "nlp_scientific_rag",
          title: "Grounded Scientific QA with Retrieval",
          authors: ["Jane Doe"],
          publication_year: 2025,
          venue: "ACL",
          cited_by_count: 19,
          doi: "https://doi.org/10.1234/acl",
          url: "https://doi.org/10.1234/acl",
          open_access_url: "https://arxiv.org/pdf/2501.00001",
          abstract: "A study on grounded scientific QA.",
          created_at: "2026-11-27T01:10:00Z",
        };
        savedList = [saved, ...savedList];
        return Promise.resolve(
          new Response(JSON.stringify(saved), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.endsWith("/api/v1/recommendations/nlp_scientific_rag/brief") && method === "GET") {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: "Not cached" }), {
            status: 404,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.endsWith("/api/v1/papers/synthesize/latest") && method === "GET") {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: "Not cached" }), {
            status: 404,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.includes("/api/v1/recommendations/nlp_scientific_rag/brief") && method === "POST") {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              topic_id: "nlp_scientific_rag",
              topic_title:
                "Citation-Grounded Retrieval-Augmented Generation for Science",
              model: "gemini-2.5-flash",
              problem_framing: "Evaluate citation fidelity in scientific RAG.",
              research_questions: ["RQ1: How often do citations entail claims?"],
              suggested_methodology: "Compare BM25 + dense retrieval baselines.",
              ai_generated_notice: "AI-generated exploratory research brief.",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.includes("/api/v1/papers/synthesize") && method === "POST") {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              paper_count: 2,
              paper_titles: ["Grounded Scientific QA with Retrieval", "Existing Saved Paper"],
              model: "gemini-2.5-flash",
              common_themes: ["Scientific retrieval grounding"],
              methodological_gaps: ["Cross-domain citation verification"],
              next_step_recommendation: "Compare citation precision across both baselines.",
              ai_generated_notice: "AI-generated synthesis grounded strictly in your saved OpenAlex papers.",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    renderAppAt("/workspace");

    await waitFor(() => {
      expect(
        screen.getByText("Side-by-Side Topic Comparison")
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "Skill Gap & Exploratory Roadmap: Citation-Grounded Retrieval-Augmented Generation for Science"
        )
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(
        screen.getByText("Grounded Scientific QA with Retrieval")
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Save Paper" }));

    await waitFor(() => {
      expect(screen.getByText("Saved Literature (2)")).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Synthesize Saved Papers" })
    );

    await waitFor(() => {
      expect(
        screen.getByText("Scientific retrieval grounding")
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Generate AI Research Brief" })
    );

    await waitFor(() => {
      expect(
        screen.getByText("RQ1: How often do citations entail claims?")
      ).toBeInTheDocument();
    });
  });
});
