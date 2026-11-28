import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";

vi.mock("recharts", async () => {
  const actual = await vi.importActual<typeof import("recharts")>("recharts");
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: ReactNode }) => (
      <div style={{ width: 600, height: 300 }}>{children}</div>
    ),
  };
});

function renderInterestsRoute() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/interests"]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

const sampleProfile = {
  id: 3,
  user_id: 1,
  session_id: 5,
  domain_scores: [
    {
      key: "nlp",
      label: "Natural Language Processing & Information Retrieval",
      score: 88,
      contributions: [
        {
          source: "assessment:q_domains_interest",
          reason: "Selected 'Natural Language Processing & Information Retrieval'",
          weight: 1.0,
        },
      ],
    },
  ],
  dimension_scores: [
    {
      key: "empirical_experimentation",
      label: "Empirical Experimentation & Benchmarking",
      score: 82,
      contributions: [
        {
          source: "assessment:q_problem_solving_style",
          reason: "Selected 'Designing experiments, running benchmarks, and analyzing real datasets'",
          weight: 1.0,
        },
      ],
    },
  ],
  skill_confidence: {
    math_comfort: 4,
    coding_comfort: 5,
    experience_level: "intermediate",
    technical_skills_count: 2,
    programming_languages_count: 2,
    overall_confidence: 80,
  },
  top_domains: ["nlp"],
  limitations_note:
    "These scores are deterministic, preference-weighted indicators and are not scientifically validated psychometric assessments.",
  created_at: "2026-11-27T00:00:00Z",
  updated_at: "2026-11-27T00:00:00Z",
};

describe("InterestsPage", () => {
  beforeEach(() => {
    localStorage.setItem("inquisia_access_token", "valid-jwt");
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("prompts to generate when 404 and renders profile after POST /analyze", async () => {
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

      if (url.endsWith("/api/v1/interests/latest")) {
        return new Response(
          JSON.stringify({ detail: "No interest profile has been generated yet." }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/interests/analyze") && init?.method === "POST") {
        return new Response(JSON.stringify(sampleProfile), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/v1/interests/niche-summary") && (!init?.method || init.method === "GET")) {
        return new Response(JSON.stringify({ detail: "Not cached" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.includes("/api/v1/interests/niche-summary") && init?.method === "POST") {
        return new Response(
          JSON.stringify({
            interest_profile_id: 3,
            top_domains: ["Natural Language Processing & Information Retrieval"],
            model: "gemini-2.5-flash",
            niche_title: "Empirical Scientific NLP",
            summary: "Blends NLP retrieval with empirical benchmarking.",
            example_directions: ["Citation-grounded QA"],
            ai_generated_notice: "AI-generated exploratory niche synthesis.",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      throw new Error(`Unexpected request: ${url}`);
    });

    renderInterestsRoute();

    await waitFor(() => {
      expect(
        screen.getByText("No Interest Profile Generated Yet")
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Generate Interest Profile" })
    );

    await waitFor(() => {
      expect(screen.getByText("80%")).toBeInTheDocument();
      expect(
        screen.getByText("Natural Language Processing & Information Retrieval")
      ).toBeInTheDocument();
      expect(
        screen.getByText(/not scientifically validated psychometric assessments/i)
      ).toBeInTheDocument();
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Generate AI Niche Summary" })
    );

    await waitFor(() => {
      expect(screen.getByText("Empirical Scientific NLP")).toBeInTheDocument();
    });
  });
});
