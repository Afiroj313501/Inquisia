import { describe, expect, it } from "vitest";
import { formatSavedPapersBibtex } from "./bibtex";

describe("formatSavedPapersBibtex", () => {
  it("formats saved OpenAlex papers into valid BibTeX entries", () => {
    const bib = formatSavedPapersBibtex([
      {
        id: 1,
        openalex_id: "W4200000001",
        topic_id: "nlp_scientific_rag",
        title: "Citation-Grounded Retrieval for Science",
        authors: ["Jane Doe", "John Smith"],
        publication_year: 2024,
        venue: "ACL Findings",
        cited_by_count: 42,
        doi: "https://doi.org/10.1234/rag.2024",
        url: "https://doi.org/10.1234/rag.2024",
        open_access_url: null,
        abstract: null,
        created_at: "2026-11-27T01:00:00Z",
      },
    ]);

    expect(bib).toContain("@article{doe2024000001,");
    expect(bib).toContain("title = {Citation-Grounded Retrieval for Science}");
    expect(bib).toContain("author = {Jane Doe and John Smith}");
    expect(bib).toContain("year = {2024}");
    expect(bib).toContain("journal = {ACL Findings}");
    expect(bib).toContain("doi = {10.1234/rag.2024}");
  });
});
