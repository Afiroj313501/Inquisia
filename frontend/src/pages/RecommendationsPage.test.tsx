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

const SAMPLE_SET = {
  id: 1,
  user_id: 1,
  interest_profile_id: 3,
  methodology_note:
    "AI-assisted hybrid recommendations combining weighted interest alignment, skill and time feasibility, methodology fit, and TF-IDF semantic similarity.",
  created_at: "2026-11-27T01:00:00Z",
  updated_at: "2026-11-27T01:00:00Z",
  results: [
    {
      id: "nlp_scientific_rag",
      title: "Citation-Grounded Retrieval-Augmented Generation for Science",
      description:
        "Building retrieval and verification pipelines grounded in scientific literature.",
      keywords: ["rag", "information retrieval", "nlp"],
      domain_tags: ["nlp", "ai_ml"],
      methodology_tags: ["applied_engineering", "empirical_experimentation"],
      min_experience_level: "none",
      min_weekly_hours: 8,
      hybrid_score: 86,
      score_breakdown: {
        interest_alignment: 90,
        skill_feasibility: 92,
        methodology_fit: 82,
        semantic_similarity: 74,
        explanation:
          "Interest alignment 90/100, skill feasibility 92/100, methodology fit 82/100, and profile text similarity 74/100.",
      },
      is_bookmarked: false,
      user_rating: null,
    },
  ],
};

describe("RecommendationsPage", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("inquisia_access_token", "valid-jwt");
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("generates recommendations, expands breakdown, bookmarks, and rates a topic", async () => {
    let hasGenerated = false;

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
        if (!hasGenerated) {
          return Promise.resolve(
            new Response(
              JSON.stringify({ detail: "No topic recommendations have been generated yet." }),
              { status: 404, headers: { "Content-Type": "application/json" } }
            )
          );
        }
        return Promise.resolve(
          new Response(JSON.stringify(SAMPLE_SET), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.endsWith("/api/v1/recommendations/generate") && method === "POST") {
        hasGenerated = true;
        return Promise.resolve(
          new Response(JSON.stringify(SAMPLE_SET), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          })
        );
      }
      if (url.endsWith("/api/v1/recommendations/bookmarks") && method === "POST") {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 10,
              topic_id: "nlp_scientific_rag",
              title: SAMPLE_SET.results[0].title,
              domain_tags: ["nlp", "ai_ml"],
              created_at: "2026-11-27T01:02:00Z",
            }),
            { status: 201, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (
        url.endsWith("/api/v1/recommendations/feedback/nlp_scientific_rag") &&
        method === "PUT"
      ) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: 20,
              topic_id: "nlp_scientific_rag",
              rating: 5,
              comment: null,
              created_at: "2026-11-27T01:03:00Z",
              updated_at: "2026-11-27T01:03:00Z",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    renderAppAt("/recommendations");

    await waitFor(() => {
      expect(
        screen.getByText("No Recommendations Generated Yet")
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Generate Recommendations" })
    );

    await waitFor(() => {
      expect(
        screen.getByText(
          "Citation-Grounded Retrieval-Augmented Generation for Science"
        )
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Show score breakdown" })
    );
    expect(
      screen.getByText("Interest Alignment (40%)")
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Bookmark" }));
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Bookmarked" })
      ).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Rate 5 out of 5" }));
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Rate 5 out of 5" })
      ).toHaveAttribute("aria-pressed", "true");
    });
  });
});
