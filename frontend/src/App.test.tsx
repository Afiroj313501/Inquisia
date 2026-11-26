import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";

function renderApp(initialEntries: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("App routing and protection", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("redirects unauthenticated users from /dashboard to /login", async () => {
    renderApp(["/dashboard"]);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Sign in" })
      ).toBeInTheDocument();
    });
  });

  it("renders dashboard when session restores via /api/v1/auth/me", async () => {
    localStorage.setItem("inquisia_access_token", "valid-jwt");

    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = typeof input === "string" ? input : input.toString();
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
      if (url.endsWith("/api/v1/profile")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ detail: "Academic profile has not been created yet." }),
            { status: 404, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/assessments/sessions/latest")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ detail: "No assessment session found." }),
            { status: 404, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      if (url.endsWith("/api/v1/interests/latest")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ detail: "No interest profile has been generated yet." }),
            { status: 404, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    renderApp(["/dashboard"]);

    await waitFor(() => {
      expect(screen.getByText("Welcome, Ada Lovelace")).toBeInTheDocument();
      expect(screen.getByText("API: ok")).toBeInTheDocument();
    });
  });
});
