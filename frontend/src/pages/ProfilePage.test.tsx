import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";

function renderProfileRoute() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/profile"]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ProfilePage", () => {
  beforeEach(() => {
    localStorage.setItem("inquisia_access_token", "valid-jwt");
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("creates a new academic profile when GET /profile returns 404", async () => {
    const putBodies: unknown[] = [];

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

      if (url.endsWith("/api/v1/profile") && (!init?.method || init.method === "GET")) {
        return new Response(
          JSON.stringify({ detail: "Academic profile has not been created yet." }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }

      if (url.endsWith("/api/v1/profile") && init?.method === "PUT") {
        const parsed = JSON.parse(String(init.body));
        putBodies.push(parsed);
        return new Response(
          JSON.stringify({
            id: 10,
            user_id: 1,
            ...parsed,
            created_at: "2026-11-27T00:00:00Z",
            updated_at: "2026-11-27T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      throw new Error(`Unexpected request: ${url}`);
    });

    renderProfileRoute();

    await waitFor(() => {
      expect(
        screen.getByLabelText("Degree / academic program")
      ).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText("Degree / academic program"), {
      target: { value: "B.Sc. in Computer Science" },
    });

    const skillsInput = screen.getByLabelText("Technical skills & methods");
    fireEvent.change(skillsInput, { target: { value: "PyTorch" } });
    fireEvent.keyDown(skillsInput, { key: "Enter" });

    expect(screen.getByText("PyTorch")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: "Save Academic Profile" })
    );

    await waitFor(() => {
      expect(screen.getByText("Academic profile saved.")).toBeInTheDocument();
    });

    expect(putBodies).toHaveLength(1);
    expect(putBodies[0]).toMatchObject({
      education_level: "undergraduate",
      degree_program: "B.Sc. in Computer Science",
      technical_skills: ["PyTorch"],
    });
  });

  it("pre-populates existing academic profile data", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
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

      if (url.endsWith("/api/v1/profile")) {
        return new Response(
          JSON.stringify({
            id: 10,
            user_id: 1,
            education_level: "masters",
            degree_program: "M.Sc. in Data Science",
            academic_background: "Statistics and ML",
            technical_skills: ["Causal Inference"],
            programming_languages: ["Python", "R"],
            preferred_research_domains: ["Healthcare AI"],
            research_experience_level: "intermediate",
            research_experience_summary: "Lab assistant",
            career_goals: "PhD application",
            weekly_hours_available: 20,
            created_at: "2026-11-27T00:00:00Z",
            updated_at: "2026-11-27T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      throw new Error(`Unexpected request: ${url}`);
    });

    renderProfileRoute();

    await waitFor(() => {
      expect(
        screen.getByDisplayValue("M.Sc. in Data Science")
      ).toBeInTheDocument();
    });

    expect(screen.getByText("Causal Inference")).toBeInTheDocument();
    expect(screen.getByText("Healthcare AI")).toBeInTheDocument();
  });
});
