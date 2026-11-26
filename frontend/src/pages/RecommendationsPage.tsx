import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { ApiError, apiRequest } from "../lib/api";
import {
  DOMAIN_TAG_LABELS,
  formatDomainTag,
  type BookmarkResponse,
  type FeedbackResponse,
  type RecommendationSetResponse,
  type TopicRecommendation,
} from "../types/recommendation";
import { formatExperienceLevel } from "../types/profile";

export async function fetchLatestRecommendations(): Promise<RecommendationSetResponse | null> {
  try {
    return await apiRequest<RecommendationSetResponse>(
      "/api/v1/recommendations/latest"
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span>{label}</span>
        <span className="font-medium text-slate-900">{value} / 100</span>
      </div>
      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full bg-slate-800"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function TopicCard({
  topic,
  onToggleBookmark,
  onRate,
  isBookmarkPending,
  isRatingPending,
}: {
  topic: TopicRecommendation;
  onToggleBookmark: (topic: TopicRecommendation) => void;
  onRate: (topicId: string, rating: number) => void;
  isBookmarkPending: boolean;
  isRatingPending: boolean;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {topic.domain_tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700"
              >
                {formatDomainTag(tag)}
              </span>
            ))}
            <span className="text-xs text-slate-500">
              Min level:{" "}
              <strong className="font-medium text-slate-700">
                {formatExperienceLevel(topic.min_experience_level)}
              </strong>{" "}
              · ~{topic.min_weekly_hours} hrs/wk
            </span>
          </div>

          <h3 className="mt-2 text-base font-semibold text-slate-900">
            {topic.title}
          </h3>
          <p className="mt-1.5 text-sm leading-relaxed text-slate-600">
            {topic.description}
          </p>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3.5 py-2 text-center">
            <div className="text-[11px] font-medium uppercase tracking-wide text-slate-500">
              Hybrid Match
            </div>
            <div className="text-xl font-bold text-slate-900">
              {topic.hybrid_score}
              <span className="text-xs font-normal text-slate-500">/100</span>
            </div>
          </div>

          <button
            type="button"
            disabled={isBookmarkPending}
            onClick={() => onToggleBookmark(topic)}
            aria-pressed={topic.is_bookmarked}
            className={
              topic.is_bookmarked
                ? "rounded-lg border border-slate-900 bg-slate-900 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-slate-800 disabled:opacity-60"
                : "rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            }
          >
            {topic.is_bookmarked ? "Bookmarked" : "Bookmark"}
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-1.5">
        {topic.keywords.map((kw) => (
          <span
            key={kw}
            className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600"
          >
            {kw}
          </span>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-4">
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="text-xs font-medium text-slate-700 underline underline-offset-2 hover:text-slate-900"
        >
          {expanded ? "Hide score breakdown" : "Show score breakdown"}
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Rate relevance:</span>
          <div className="flex items-center gap-1" role="group" aria-label={`Rate ${topic.title}`}>
            {[1, 2, 3, 4, 5].map((star) => {
              const active = topic.user_rating === star;
              return (
                <button
                  key={star}
                  type="button"
                  disabled={isRatingPending}
                  onClick={() => onRate(topic.id, star)}
                  aria-label={`Rate ${star} out of 5`}
                  aria-pressed={active}
                  className={
                    active
                      ? "h-7 w-7 rounded-md bg-slate-900 text-xs font-semibold text-white"
                      : "h-7 w-7 rounded-md border border-slate-200 bg-white text-xs font-medium text-slate-700 hover:bg-slate-50"
                  }
                >
                  {star}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs text-slate-600">
            {topic.score_breakdown.explanation}
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <ScoreBar
              label="Interest Alignment (40%)"
              value={topic.score_breakdown.interest_alignment}
            />
            <ScoreBar
              label="Skill & Time Feasibility (20%)"
              value={topic.score_breakdown.skill_feasibility}
            />
            <ScoreBar
              label="Methodology Fit (20%)"
              value={topic.score_breakdown.methodology_fit}
            />
            <ScoreBar
              label="Profile Text Similarity (20%)"
              value={topic.score_breakdown.semantic_similarity}
            />
          </div>
        </div>
      )}
    </article>
  );
}

export function RecommendationsPage() {
  const queryClient = useQueryClient();
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const [domainFilter, setDomainFilter] = useState<string>("all");

  const recQuery = useQuery({
    queryKey: ["recommendations", "latest"],
    queryFn: fetchLatestRecommendations,
  });

  const generateMutation = useMutation({
    mutationFn: () =>
      apiRequest<RecommendationSetResponse>("/api/v1/recommendations/generate", {
        method: "POST",
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(["recommendations", "latest"], data);
    },
  });

  const bookmarkMutation = useMutation({
    mutationFn: async (topic: TopicRecommendation) => {
      if (topic.is_bookmarked) {
        await apiRequest<void>(`/api/v1/recommendations/bookmarks/${topic.id}`, {
          method: "DELETE",
        });
        return { topicId: topic.id, bookmarked: false };
      }
      await apiRequest<BookmarkResponse>("/api/v1/recommendations/bookmarks", {
        method: "POST",
        body: JSON.stringify({ topic_id: topic.id }),
      });
      return { topicId: topic.id, bookmarked: true };
    },
    onSuccess: ({ topicId, bookmarked }) => {
      queryClient.setQueryData<RecommendationSetResponse | null>(
        ["recommendations", "latest"],
        (prev) =>
          prev
            ? {
                ...prev,
                results: prev.results.map((item) =>
                  item.id === topicId
                    ? { ...item, is_bookmarked: bookmarked }
                    : item
                ),
              }
            : prev
      );
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: ({ topicId, rating }: { topicId: string; rating: number }) =>
      apiRequest<FeedbackResponse>(
        `/api/v1/recommendations/feedback/${topicId}`,
        {
          method: "PUT",
          body: JSON.stringify({ rating }),
        }
      ),
    onSuccess: (fb) => {
      queryClient.setQueryData<RecommendationSetResponse | null>(
        ["recommendations", "latest"],
        (prev) =>
          prev
            ? {
                ...prev,
                results: prev.results.map((item) =>
                  item.id === fb.topic_id
                    ? { ...item, user_rating: fb.rating }
                    : item
                ),
              }
            : prev
      );
    },
  });

  const recSet = recQuery.data;

  const filteredTopics = useMemo(() => {
    if (!recSet) return [];
    return recSet.results.filter((topic) => {
      if (bookmarkedOnly && !topic.is_bookmarked) return false;
      if (domainFilter !== "all" && !topic.domain_tags.includes(domainFilter)) {
        return false;
      }
      return true;
    });
  }, [recSet, bookmarkedOnly, domainFilter]);

  const bookmarkedCount = useMemo(
    () => (recSet ? recSet.results.filter((t) => t.is_bookmarked).length : 0),
    [recSet]
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-600/20">
                AI-Assisted Hybrid Engine
              </span>
              <h2 className="mt-2 text-lg font-semibold text-slate-900">
                Personalized Research Topic Recommendations
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Ranked research directions blending your interest scores,
                feasibility, methodology fit, and profile text similarity.
              </p>
            </div>

            <button
              type="button"
              disabled={generateMutation.isPending}
              onClick={() => generateMutation.mutate()}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {generateMutation.isPending
                ? "Generating..."
                : recSet
                ? "Refresh Recommendations"
                : "Generate Recommendations"}
            </button>
          </div>

          {generateMutation.isError && (
            <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
              {generateMutation.error instanceof Error
                ? generateMutation.error.message
                : "Unable to generate recommendations."}{" "}
              <Link to="/interests" className="font-medium underline">
                Go to Interest Profile
              </Link>
            </div>
          )}
        </section>

        {recQuery.isPending && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-600 shadow-sm">
            Loading topic recommendations...
          </div>
        )}

        {recQuery.isSuccess && !recSet && (
          <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <h3 className="text-base font-semibold text-slate-900">
              No Recommendations Generated Yet
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Once you have generated your explainable interest profile, click{" "}
              <strong>Generate Recommendations</strong> above to rank topics
              from the catalog.
            </p>
          </section>
        )}

        {recSet && (
          <>
            <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs leading-relaxed text-amber-950">
              <strong className="font-semibold">AI-Generated Notice:</strong>{" "}
              {recSet.methodology_note}
            </section>

            <section className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white px-6 py-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-3">
                <label className="text-xs font-medium text-slate-600">
                  Domain:
                  <select
                    value={domainFilter}
                    onChange={(e) => setDomainFilter(e.target.value)}
                    className="ml-2 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-900"
                  >
                    <option value="all">All domains</option>
                    {Object.entries(DOMAIN_TAG_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </label>

                <button
                  type="button"
                  onClick={() => setBookmarkedOnly((prev) => !prev)}
                  aria-pressed={bookmarkedOnly}
                  className={
                    bookmarkedOnly
                      ? "rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                      : "rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  }
                >
                  Bookmarked ({bookmarkedCount})
                </button>
              </div>

              <span className="text-xs text-slate-500">
                Showing {filteredTopics.length} of {recSet.results.length} topics
              </span>
            </section>

            <div className="space-y-4">
              {filteredTopics.length === 0 ? (
                <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-sm">
                  No topics match the current filter.
                </div>
              ) : (
                filteredTopics.map((topic) => (
                  <TopicCard
                    key={topic.id}
                    topic={topic}
                    onToggleBookmark={(t) => bookmarkMutation.mutate(t)}
                    onRate={(topicId, rating) =>
                      feedbackMutation.mutate({ topicId, rating })
                    }
                    isBookmarkPending={bookmarkMutation.isPending}
                    isRatingPending={feedbackMutation.isPending}
                  />
                ))
              )}
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
}
