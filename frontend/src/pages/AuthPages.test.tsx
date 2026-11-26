import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";

function renderAt(route: string) {
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

describe("Auth pages", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("validates login form and signs in successfully", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/api/v1/auth/login")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              access_token: "jwt-token",
              token_type: "bearer",
              user: {
                id: 1,
                email: "ada@example.edu",
                full_name: "Ada Lovelace",
                is_active: true,
                created_at: "2026-11-27T00:00:00Z",
              },
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
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    renderAt("/login");

    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "ada@example.edu" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "StrongPassword123!" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(screen.getByText("Welcome, Ada Lovelace")).toBeInTheDocument();
    });
    expect(localStorage.getItem("inquisia_access_token")).toBe("jwt-token");
  });

  it("registers a new user and logs out cleanly", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/api/v1/auth/register")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              access_token: "reg-token",
              token_type: "bearer",
              user: {
                id: 2,
                email: "grace@example.edu",
                full_name: "Grace Hopper",
                is_active: true,
                created_at: "2026-11-27T00:00:00Z",
              },
            }),
            { status: 201, headers: { "Content-Type": "application/json" } }
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
      if (url.endsWith("/api/v1/auth/logout")) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ message: "Successfully logged out." }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          )
        );
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`));
    });

    renderAt("/register");

    fireEvent.change(screen.getByLabelText("Full name"), {
      target: { value: "Grace Hopper" },
    });
    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "grace@example.edu" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "StrongPassword123!" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    await waitFor(() => {
      expect(screen.getByText("Welcome, Grace Hopper")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Sign out" }));

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Sign in" })
      ).toBeInTheDocument();
    });
    expect(localStorage.getItem("inquisia_access_token")).toBeNull();
  });
});
