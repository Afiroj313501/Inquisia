import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { apiRequest } from "../lib/api";
import type {
  PaperItem,
  PaperSearchResponse,
  SavedPaperResponse,
} from "../types/paper";
import {
  formatExperienceLevel,
  type ResearchExperienceLevel,
} from "../types/profile";
import {
  formatDomainTag,
  type ResearchBriefResponse,
} from "../types/recommendation";
import { fetchAcademicProfile } from "./ProfilePage";
import { fetchLatestRecommendations } from "./RecommendationsPage";

const EXP_ORDER: Record<ResearchExperienceLevel, number> = {
  none: 0,
  beginner: 1,
  intermediate: 2,
  experienced: 3,
};

export function WorkspacePage() {
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const initialTopicParam = searchParams.get("topic") ?? "";

  const recQuery = useQuery({
    queryKey: ["recommendations", "latest"],
    queryFn: fetchLatestRecommendations,
  });

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: fetchAcademicProfile,
  });

  const savedPapersQuery = useQuery({
    queryKey: ["papers", "saved"],
    queryFn: () => apiRequest<SavedPaperResponse[]>("/api/v1/papers/saved"),
  });

  const topics = recQuery.data?.results ?? [];
  const bookmarkedTopics = useMemo(
    () => topics.filter((t) => t.is_bookmarked),
    [topics]
  );

  const [selectedTopicId, setSelectedTopicId] = useState<string>(initialTopicParam);
  const [customQuery, setCustomQuery] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"relevance" | "cited_by_count">("relevance");
  const [comparedIds, setComparedIds] = useState<string[]>([]);

  useEffect(() => {
    if (!selectedTopicId && topics.length > 0) {
      setSelectedTopicId((bookmarkedTopics[0] ?? topics[0]).id);
    }
  }, [selectedTopicId, topics, bookmarkedTopics]);

  useEffect(() => {
    if (comparedIds.length === 0 && topics.length > 0) {
      const defaults = (bookmarkedTopics.length >= 2 ? bookmarkedTopics : topics)
        .slice(0, 2)
        .map((t) => t.id);
      setComparedIds(defaults);
    }
  }, [comparedIds.length, topics, bookmarkedTopics]);

  const activeTopic = useMemo(
    () => topics.find((t) => t.id === selectedTopicId) ?? topics[0] ?? null,
    [topics, selectedTopicId]
  );

  const searchMutation = useMutation({
    mutationFn: (params: {
      topicId?: string;
      query?: string;
      sort: "relevance" | "cited_by_count";
    }) => {
      const qs = new URLSearchParams();
      if (params.query && params.query.trim()) {
        qs.set("query", params.query.trim());
      } else if (params.topicId) {
        qs.set("topic_id", params.topicId);
      }
      qs.set("sort", params.sort);
      qs.set("limit", "6");
      return apiRequest<PaperSearchResponse>(`/api/v1/papers/search?${qs.toString()}`);
    },
  });

  useEffect(() => {
    if (initialTopicParam) {
      searchMutation.mutate({ topicId: initialTopicParam, sort: "relevance" });
    }
    // Run once on mount when deep-linked from /recommendations?topic=...
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialTopicParam]);

  const savePaperMutation = useMutation({
    mutationFn: (paper: PaperItem) =>
      apiRequest<SavedPaperResponse>("/api/v1/papers/saved", {
        method: "POST",
        body: JSON.stringify({
          openalex_id: paper.openalex_id,
          topic_id: activeTopic?.id ?? null,
          title: paper.title,
          authors: paper.authors,
          publication_year: paper.publication_year,
          venue: paper.venue,
          cited_by_count: paper.cited_by_count,
          doi: paper.doi,
          url: paper.url,
          open_access_url: paper.open_access_url,
          abstract: paper.abstract,
        }),
      }),
    onSuccess: (saved) => {
      queryClient.setQueryData<SavedPaperResponse[]>(
        ["papers", "saved"],
        (prev) => {
          const list = prev ?? [];
          if (list.some((item) => item.openalex_id === saved.openalex_id)) {
            return list;
          }
          return [saved, ...list];
        }
      );
    },
  });

  const removeSavedMutation = useMutation({
    mutationFn: (savedPaperId: number) =>
      apiRequest<void>(`/api/v1/papers/saved/${savedPaperId}`, {
        method: "DELETE",
      }),
    onSuccess: (_data, deletedId) => {
      queryClient.setQueryData<SavedPaperResponse[]>(
        ["papers", "saved"],
        (prev) => (prev ? prev.filter((item) => item.id !== deletedId) : [])
      );
    },
  });

  const briefMutation = useMutation({
    mutationFn: (topicId: string) =>
      apiRequest<ResearchBriefResponse>(
        `/api/v1/recommendations/${topicId}/brief`,
        { method: "POST" }
      ),
  });

  const savedOpenAlexIds = useMemo(
    () => new Set((savedPapersQuery.data ?? []).map((p) => p.openalex_id)),
    [savedPapersQuery.data]
  );

  const comparedTopics = useMemo(
    () => topics.filter((t) => comparedIds.includes(t.id)),
    [topics, comparedIds]
  );

  function toggleCompare(topicId: string) {
    setComparedIds((prev) => {
      if (prev.includes(topicId)) {
        return prev.filter((id) => id !== topicId);
      }
      if (prev.length >= 3) {
        return [...prev.slice(1), topicId];
      }
      return [...prev, topicId];
    });
  }

  const skillGapAnalysis = useMemo(() => {
    if (!activeTopic) return null;
    const profile = profileQuery.data;
    const userSkillsLower = [
      ...(profile?.technical_skills ?? []),
      ...(profile?.programming_languages ?? []),
    ].map((s) => s.toLowerCase());

    const matchedKeywords = activeTopic.keywords.filter((kw) =>
      userSkillsLower.some((s) => s.includes(kw.toLowerCase()) || kw.toLowerCase().includes(s))
    );
    const gapKeywords = activeTopic.keywords.filter((kw) => !matchedKeywords.includes(kw));

    const userExp = profile?.research_experience_level ?? "none";
    const expMet = EXP_ORDER[userExp] >= EXP_ORDER[activeTopic.min_experience_level];
    const hoursAvailable = profile?.weekly_hours_available ?? null;
    const hoursMet =
      hoursAvailable !== null && hoursAvailable >= activeTopic.min_weekly_hours;

    return {
      matchedKeywords,
      gapKeywords,
      userExp,
      expMet,
      hoursAvailable,
      hoursMet,
    };
  }, [activeTopic, profileQuery.data]);

  function handleDownloadMarkdown() {
    const lines: string[] = [
      "# Inquisia Research Workspace Summary",
      "",
      "## Bookmarked Research Topics",
    ];
    if (bookmarkedTopics.length === 0) {
      lines.push("- No topics bookmarked yet.");
    } else {
      for (const topic of bookmarkedTopics) {
        lines.push(
          `- **${topic.title}** (Hybrid Match: ${topic.hybrid_score}/100) — ${topic.description}`
        );
      }
    }
    lines.push("", "## Saved Literature (OpenAlex)");
    const saved = savedPapersQuery.data ?? [];
    if (saved.length === 0) {
      lines.push("- No papers saved yet.");
    } else {
      for (const paper of saved) {
        lines.push(
          `- **${paper.title}** (${paper.publication_year ?? "n.d."}) — ${paper.authors.join(", ")} ${paper.url ? `[Link](${paper.url})` : ""}`
        );
      }
    }

    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "inquisia-workspace.md";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Research Workspace
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Explore real peer-reviewed literature via OpenAlex, compare
                candidate topics, and plan your skill preparation roadmap.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 print:hidden">
              <button
                type="button"
                onClick={handleDownloadMarkdown}
                className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
              >
                Export Markdown
              </button>
              <button
                type="button"
                onClick={() => window.print()}
                className="rounded-lg bg-slate-900 px-3.5 py-2 text-xs font-medium text-white shadow-sm transition hover:bg-slate-800"
              >
                Print / Save PDF
              </button>
            </div>
          </div>
        </section>

        {/* OpenAlex Paper Discovery */}
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                OpenAlex Literature Discovery
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                Live academic records retrieved from OpenAlex — zero fabricated
                citations.
              </p>
            </div>
          </div>

          <form
            className="mt-5 grid gap-3 sm:grid-cols-12 print:hidden"
            onSubmit={(e) => {
              e.preventDefault();
              searchMutation.mutate({
                topicId: selectedTopicId || undefined,
                query: customQuery,
                sort: sortOrder,
              });
            }}
          >
            <div className="sm:col-span-5">
              <label className="block text-xs font-medium text-slate-600">
                Recommended Topic
                <select
                  value={selectedTopicId}
                  onChange={(e) => setSelectedTopicId(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
                >
                  {topics.length === 0 && (
                    <option value="">No topics generated yet</option>
                  )}
                  {topics.map((topic) => (
                    <option key={topic.id} value={topic.id}>
                      {topic.is_bookmarked ? "★ " : ""}
                      {topic.title} ({topic.hybrid_score}/100)
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="sm:col-span-4">
              <label className="block text-xs font-medium text-slate-600">
                Or Custom Search Query
                <input
                  type="text"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  placeholder="e.g. retrieval augmented generation"
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
                />
              </label>
            </div>

            <div className="sm:col-span-3 flex items-end gap-2">
              <label className="flex-1 text-xs font-medium text-slate-600">
                Sort
                <select
                  value={sortOrder}
                  onChange={(e) =>
                    setSortOrder(e.target.value as "relevance" | "cited_by_count")
                  }
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900"
                >
                  <option value="relevance">Relevance</option>
                  <option value="cited_by_count">Most Cited</option>
                </select>
              </label>
              <button
                type="submit"
                disabled={searchMutation.isPending || (!selectedTopicId && !customQuery.trim())}
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {searchMutation.isPending ? "Searching..." : "Search"}
              </button>
            </div>
          </form>

          {searchMutation.isError && (
            <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
              {searchMutation.error instanceof Error
                ? searchMutation.error.message
                : "Unable to query OpenAlex."}
            </div>
          )}

          {searchMutation.isSuccess && (
            <div className="mt-6 space-y-4">
              <p className="text-xs text-slate-500">
                Showing {searchMutation.data.results.length} results from{" "}
                <strong>{searchMutation.data.source}</strong> for{" "}
                <span className="italic">"{searchMutation.data.query}"</span>
              </p>

              {searchMutation.data.results.length === 0 ? (
                <p className="text-sm text-slate-600">
                  No papers returned for this query. Try broadening your terms.
                </p>
              ) : (
                searchMutation.data.results.map((paper) => {
                  const alreadySaved =
                    paper.is_saved || savedOpenAlexIds.has(paper.openalex_id);
                  return (
                    <article
                      key={paper.openalex_id}
                      className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <h4 className="text-sm font-semibold text-slate-900">
                            {paper.title}
                          </h4>
                          <p className="mt-1 text-xs text-slate-600">
                            {paper.authors.length > 0
                              ? paper.authors.join(", ")
                              : "Unknown authors"}
                            {paper.publication_year ? ` · ${paper.publication_year}` : ""}
                            {paper.venue ? ` · ${paper.venue}` : ""} ·{" "}
                            <strong className="font-medium text-slate-800">
                              {paper.cited_by_count} citations
                            </strong>
                          </p>
                        </div>

                        <button
                          type="button"
                          disabled={alreadySaved || savePaperMutation.isPending}
                          onClick={() => savePaperMutation.mutate(paper)}
                          className={
                            alreadySaved
                              ? "rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20"
                              : "rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                          }
                        >
                          {alreadySaved ? "Saved" : "Save Paper"}
                        </button>
                      </div>

                      {paper.abstract && (
                        <p className="mt-2 line-clamp-3 text-xs leading-relaxed text-slate-600">
                          {paper.abstract}
                        </p>
                      )}

                      <div className="mt-2.5 flex flex-wrap items-center gap-3 text-xs">
                        {paper.url && (
                          <a
                            href={paper.url}
                            target="_blank"
                            rel="noreferrer"
                            className="font-medium text-slate-800 underline"
                          >
                            View Record / DOI
                          </a>
                        )}
                        {paper.open_access_url && (
                          <a
                            href={paper.open_access_url}
                            target="_blank"
                            rel="noreferrer"
                            className="font-medium text-indigo-700 underline"
                          >
                            Open Access PDF
                          </a>
                        )}
                      </div>
                    </article>
                  );
                })
              )}
            </div>
          )}
        </section>

        {/* Saved Literature Library */}
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h3 className="text-base font-semibold text-slate-900">
            Saved Literature ({savedPapersQuery.data?.length ?? 0})
          </h3>
          {savedPapersQuery.isPending && (
            <p className="mt-3 text-sm text-slate-500">Loading saved papers...</p>
          )}
          {savedPapersQuery.isSuccess && savedPapersQuery.data.length === 0 && (
            <p className="mt-3 text-sm text-slate-600">
              No papers saved yet. Search OpenAlex above to save relevant
              literature.
            </p>
          )}
          {savedPapersQuery.isSuccess && savedPapersQuery.data.length > 0 && (
            <ul className="mt-4 space-y-3">
              {savedPapersQuery.data.map((paper) => (
                <li
                  key={paper.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4"
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium text-slate-900">
                      {paper.title}
                    </div>
                    <div className="mt-0.5 text-xs text-slate-600">
                      {paper.authors.join(", ")}
                      {paper.publication_year ? ` (${paper.publication_year})` : ""}
                      {paper.venue ? ` · ${paper.venue}` : ""} ·{" "}
                      {paper.cited_by_count} citations
                    </div>
                  </div>
                  <div className="flex items-center gap-2 print:hidden">
                    {paper.url && (
                      <a
                        href={paper.url}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
                      >
                        Open
                      </a>
                    )}
                    <button
                      type="button"
                      disabled={removeSavedMutation.isPending}
                      onClick={() => removeSavedMutation.mutate(paper.id)}
                      className="rounded border border-rose-200 bg-white px-2.5 py-1 text-xs font-medium text-rose-700 hover:bg-rose-50"
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Side-by-Side Topic Comparison */}
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">
                Side-by-Side Topic Comparison
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                Select up to 3 recommended topics to compare fit and commitment.
              </p>
            </div>
            {topics.length === 0 && (
              <Link
                to="/recommendations"
                className="text-xs font-medium text-slate-800 underline"
              >
                Generate Recommendations
              </Link>
            )}
          </div>

          {topics.length > 0 && (
            <>
              <div className="mt-4 flex flex-wrap gap-2 print:hidden">
                {topics.slice(0, 8).map((topic) => {
                  const selected = comparedIds.includes(topic.id);
                  return (
                    <button
                      key={topic.id}
                      type="button"
                      onClick={() => toggleCompare(topic.id)}
                      className={
                        selected
                          ? "rounded-full bg-slate-900 px-3 py-1 text-xs font-medium text-white"
                          : "rounded-full border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                      }
                    >
                      {topic.title}
                    </button>
                  );
                })}
              </div>

              {comparedTopics.length > 0 && (
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full border-collapse text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="py-2 pr-4 font-medium">Metric</th>
                        {comparedTopics.map((t) => (
                          <th key={t.id} className="py-2 pr-4 font-semibold text-slate-900">
                            {t.title}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      <tr>
                        <td className="py-2 pr-4 text-slate-600">Hybrid Match</td>
                        {comparedTopics.map((t) => (
                          <td key={t.id} className="py-2 pr-4 font-semibold text-slate-900">
                            {t.hybrid_score}/100
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="py-2 pr-4 text-slate-600">Domains</td>
                        {comparedTopics.map((t) => (
                          <td key={t.id} className="py-2 pr-4 text-slate-700">
                            {t.domain_tags.map(formatDomainTag).join(", ")}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="py-2 pr-4 text-slate-600">Interest / Methodology</td>
                        {comparedTopics.map((t) => (
                          <td key={t.id} className="py-2 pr-4 text-slate-700">
                            {t.score_breakdown.interest_alignment} /{" "}
                            {t.score_breakdown.methodology_fit}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="py-2 pr-4 text-slate-600">Min Experience & Hours</td>
                        {comparedTopics.map((t) => (
                          <td key={t.id} className="py-2 pr-4 text-slate-700">
                            {formatExperienceLevel(t.min_experience_level)} ·{" "}
                            {t.min_weekly_hours} hrs/wk
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </section>

        {/* Skill Gap & Exploratory Research Roadmap */}
        {activeTopic && skillGapAnalysis && (
          <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-base font-semibold text-slate-900">
                Skill Gap & Exploratory Roadmap: {activeTopic.title}
              </h3>
              <button
                type="button"
                disabled={briefMutation.isPending}
                onClick={() => briefMutation.mutate(activeTopic.id)}
                className="rounded-lg border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60 print:hidden"
              >
                {briefMutation.isPending
                  ? "Generating Brief..."
                  : "Generate AI Research Brief"}
              </button>
            </div>

            {briefMutation.isError && (
              <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-xs text-amber-900">
                {briefMutation.error instanceof Error
                  ? briefMutation.error.message
                  : "Unable to generate AI research brief."}
              </div>
            )}

            {briefMutation.isSuccess &&
              briefMutation.data.topic_id === activeTopic.id && (
                <div className="mt-4 space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-5 text-xs">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-semibold text-slate-900">
                      AI-Generated Exploratory Brief ({briefMutation.data.model})
                    </span>
                    <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-medium text-amber-900">
                      AI-Generated
                    </span>
                  </div>
                  <p className="leading-relaxed text-slate-700">
                    <strong className="text-slate-900">Problem Framing:</strong>{" "}
                    {briefMutation.data.problem_framing}
                  </p>
                  <div>
                    <strong className="text-slate-900">
                      Starter Research Questions:
                    </strong>
                    <ul className="mt-1 list-disc space-y-1 pl-4 text-slate-700">
                      {briefMutation.data.research_questions.map((rq, idx) => (
                        <li key={idx}>{rq}</li>
                      ))}
                    </ul>
                  </div>
                  <p className="leading-relaxed text-slate-700">
                    <strong className="text-slate-900">
                      Suggested Methodology:
                    </strong>{" "}
                    {briefMutation.data.suggested_methodology}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {briefMutation.data.ai_generated_notice}
                  </p>
                </div>
              )}

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Readiness Check
                </h4>
                <ul className="mt-2 space-y-1.5 text-xs text-slate-700">
                  <li>
                    Experience:{" "}
                    <strong>
                      {formatExperienceLevel(skillGapAnalysis.userExp)}
                    </strong>{" "}
                    vs. recommended{" "}
                    <strong>
                      {formatExperienceLevel(activeTopic.min_experience_level)}
                    </strong>{" "}
                    ({skillGapAnalysis.expMet ? "Ready" : "Stretch goal"})
                  </li>
                  <li>
                    Weekly hours:{" "}
                    <strong>
                      {skillGapAnalysis.hoursAvailable !== null
                        ? `${skillGapAnalysis.hoursAvailable} hrs/wk`
                        : "Not specified"}
                    </strong>{" "}
                    vs. ~{activeTopic.min_weekly_hours} hrs/wk (
                    {skillGapAnalysis.hoursMet ? "Feasible" : "Plan extra buffer"})
                  </li>
                  <li>
                    Matching skills:{" "}
                    {skillGapAnalysis.matchedKeywords.length > 0
                      ? skillGapAnalysis.matchedKeywords.join(", ")
                      : "None directly matched yet"}
                  </li>
                </ul>
              </div>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Topics & Skills to Bridge
                </h4>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {skillGapAnalysis.gapKeywords.length > 0 ? (
                    skillGapAnalysis.gapKeywords.map((kw) => (
                      <span
                        key={kw}
                        className="rounded border border-amber-200 bg-amber-50 px-2 py-0.5 text-xs text-amber-900"
                      >
                        {kw}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-700">
                      Your listed skills cover all core topic keywords.
                    </span>
                  )}
                </div>
              </div>
            </div>

            <ol className="mt-5 grid gap-3 sm:grid-cols-4">
              <li className="rounded-lg border border-slate-200 p-3.5 text-xs">
                <div className="font-semibold text-slate-900">1. Literature Map</div>
                <p className="mt-1 text-slate-600">
                  Save 4–6 OpenAlex papers on {activeTopic.title} and summarize
                  their datasets and open questions.
                </p>
              </li>
              <li className="rounded-lg border border-slate-200 p-3.5 text-xs">
                <div className="font-semibold text-slate-900">2. Skill Bridging</div>
                <p className="mt-1 text-slate-600">
                  Build foundational fluency in{" "}
                  {skillGapAnalysis.gapKeywords.slice(0, 2).join(" & ") ||
                    "core evaluation methods"}
                  .
                </p>
              </li>
              <li className="rounded-lg border border-slate-200 p-3.5 text-xs">
                <div className="font-semibold text-slate-900">3. Pilot Baseline</div>
                <p className="mt-1 text-slate-600">
                  Reproduce one existing baseline or benchmark experiment at
                  small scale.
                </p>
              </li>
              <li className="rounded-lg border border-slate-200 p-3.5 text-xs">
                <div className="font-semibold text-slate-900">4. Hypothesis & Proposal</div>
                <p className="mt-1 text-slate-600">
                  Draft a 1-page research proposal with clear evaluation metrics
                  and share with a mentor.
                </p>
              </li>
            </ol>
          </section>
        )}
      </div>
    </AppLayout>
  );
}
