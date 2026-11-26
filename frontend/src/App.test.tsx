import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders Inquisia branding and healthy API status", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok", service: "inquisia-api" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    render(<App />);

    expect(screen.getByText("Inquisia")).toBeInTheDocument();
    expect(
      screen.getByText("Discover Your Research Interests. Find Your Direction.")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("API: ok")).toBeInTheDocument();
    });
  });

  it("renders error badge when API health check fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(
      new Error("Network error")
    );

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("API unavailable (Network error)")
      ).toBeInTheDocument();
    });
  });
});
