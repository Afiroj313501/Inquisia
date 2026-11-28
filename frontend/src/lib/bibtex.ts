import type { SavedPaperResponse } from "../types/paper";

function sanitizeBibtexValue(value: string): string {
  return value.replace(/[{}]/g, "").replace(/\s+/g, " ").trim();
}

function buildCiteKey(paper: SavedPaperResponse): string {
  const firstAuthor = paper.authors[0] ?? "inquisia";
  const lastName =
    firstAuthor
      .trim()
      .split(/\s+/)
      .pop()
      ?.toLowerCase()
      .replace(/[^a-z0-9]/g, "") || "ref";
  const year = paper.publication_year ? String(paper.publication_year) : "nd";
  const idSuffix = paper.openalex_id
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(-6);
  return `${lastName}${year}${idSuffix}`;
}

export function formatSavedPapersBibtex(papers: SavedPaperResponse[]): string {
  return papers
    .map((paper) => {
      const key = buildCiteKey(paper);
      const fields: string[] = [
        `  title = {${sanitizeBibtexValue(paper.title)}}`,
      ];

      if (paper.authors.length > 0) {
        const joined = paper.authors.map(sanitizeBibtexValue).join(" and ");
        fields.push(`  author = {${joined}}`);
      }
      if (paper.publication_year) {
        fields.push(`  year = {${paper.publication_year}}`);
      }
      if (paper.venue) {
        fields.push(`  journal = {${sanitizeBibtexValue(paper.venue)}}`);
      }
      if (paper.doi) {
        const cleanDoi = paper.doi.replace(/^https?:\/\/(dx\.)?doi\.org\//i, "");
        fields.push(`  doi = {${sanitizeBibtexValue(cleanDoi)}}`);
      }
      if (paper.url) {
        fields.push(`  url = {${sanitizeBibtexValue(paper.url)}}`);
      }

      return `@article{${key},\n${fields.join(",\n")}\n}`;
    })
    .join("\n\n");
}
