import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { QuestionRenderer } from "../components/QuestionRenderer";
import { ApiError, apiRequest } from "../lib/api";
import type {
  AnswerValue,
  AssessmentSessionDetail,
} from "../types/assessment";

export async function fetchLatestAssessmentSession(): Promise<AssessmentSessionDetail | null> {
  try {
    return await apiRequest<AssessmentSessionDetail>(
      "/api/v1/assessments/sessions/latest"
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

function isAnswerProvided(value: AnswerValue | undefined): boolean {
  if (value === undefined) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "string") return value.trim().length > 0;
  return typeof value === "number";
}

export function AssessmentPage() {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<AssessmentSessionDetail | null>(null);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [draftAnswer, setDraftAnswer] = useState<AnswerValue | undefined>(
    undefined
  );
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);

  async function initSession(resumeIfActive: boolean) {
    setIsInitializing(true);
    setLoadError(null);
    setActionError(null);

    try {
      const data = await apiRequest<AssessmentSessionDetail>(
        "/api/v1/assessments/sessions",
        {
          method: "POST",
          body: JSON.stringify({ resume_if_active: resumeIfActive }),
        }
      );
      setSession(data);
      queryClient.setQueryData(["assessment", "latest"], data);

      const nextId = data.progress.next_question_id;
      const nextIdx = nextId
        ? data.questions.findIndex((q) => q.id === nextId)
        : 0;
      const resolvedIdx = nextIdx >= 0 ? nextIdx : 0;
      setCurrentIndex(resolvedIdx);

      const q = data.questions[resolvedIdx];
      setDraftAnswer(q ? data.responses[q.id] : undefined);
    } catch (err) {
      setLoadError(
        err instanceof ApiError
          ? err.message
          : "Unable to load your assessment session."
      );
    } finally {
      setIsInitializing(false);
    }
  }

  useEffect(() => {
    void initSession(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentQuestion = session?.questions[currentIndex] ?? null;

  useEffect(() => {
    if (!session || !currentQuestion) return;
    setDraftAnswer(session.responses[currentQuestion.id]);
    setActionError(null);
  }, [currentIndex, currentQuestion?.id, session]);

  const saveMutation = useMutation({
    mutationFn: async (params: {
      sessionId: number;
      questionId: string;
      answerValue: AnswerValue;
    }) => {
      return apiRequest<AssessmentSessionDetail>(
        `/api/v1/assessments/sessions/${params.sessionId}/responses`,
        {
          method: "PUT",
          body: JSON.stringify({
            question_id: params.questionId,
            answer_value: params.answerValue,
          }),
        }
      );
    },
    onSuccess: (updated) => {
      setSession(updated);
      queryClient.setQueryData(["assessment", "latest"], updated);
      setActionError(null);

      const nextId = updated.progress.next_question_id;
      if (nextId) {
        const nextIdx = updated.questions.findIndex((q) => q.id === nextId);
        if (nextIdx >= 0) {
          setCurrentIndex(nextIdx);
          return;
        }
      }
      if (currentIndex < updated.questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
      }
    },
    onError: (err) => {
      setActionError(
        err instanceof ApiError ? err.message : "Failed to save response."
      );
    },
  });

  const completeMutation = useMutation({
    mutationFn: async (params: {
      sessionId: number;
      lastQuestionId?: string;
      lastAnswer?: AnswerValue;
    }) => {
      if (params.lastQuestionId && params.lastAnswer !== undefined) {
        await apiRequest<AssessmentSessionDetail>(
          `/api/v1/assessments/sessions/${params.sessionId}/responses`,
          {
            method: "PUT",
            body: JSON.stringify({
              question_id: params.lastQuestionId,
              answer_value: params.lastAnswer,
            }),
          }
        );
      }
      return apiRequest<AssessmentSessionDetail>(
        `/api/v1/assessments/sessions/${params.sessionId}/complete`,
        { method: "POST" }
      );
    },
    onSuccess: (completed) => {
      setSession(completed);
      queryClient.setQueryData(["assessment", "latest"], completed);
      setActionError(null);
    },
    onError: (err) => {
      setActionError(
        err instanceof ApiError
          ? err.message
          : "Unable to complete assessment."
      );
    },
  });

  function handleSaveAndNext() {
    if (!session || !currentQuestion || !isAnswerProvided(draftAnswer)) return;
    saveMutation.mutate({
      sessionId: session.id,
      questionId: currentQuestion.id,
      answerValue: draftAnswer!,
    });
  }

  function handleComplete() {
    if (!session) return;
    completeMutation.mutate({
      sessionId: session.id,
      lastQuestionId: currentQuestion?.id,
      lastAnswer: isAnswerProvided(draftAnswer) ? draftAnswer : undefined,
    });
  }

  const isLastStep =
    session !== null && currentIndex === session.questions.length - 1;
  const allOtherAnswered =
    session !== null &&
    currentQuestion !== null &&
    session.questions.every(
      (q) => q.id === currentQuestion.id || q.id in session.responses
    );

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl">
        {isInitializing && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm text-slate-600">
              Loading your adaptive research assessment...
            </p>
          </div>
        )}

        {loadError && (
          <div
            role="alert"
            className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700"
          >
            {loadError}
          </div>
        )}

        {!isInitializing && session && session.status === "completed" && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
            <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
              Assessment Completed
            </span>
            <h2 className="mt-4 text-xl font-semibold text-slate-900">
              Research Interest Assessment Complete
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              You answered all {session.progress.total_questions} questions
              (including adaptive follow-ups tailored to your selections). Your
              explainable interest profile and topic recommendations will build
              directly on these responses.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                to="/interests"
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
              >
                View Interest Profile
              </Link>
              <Link
                to="/dashboard"
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
              >
                Back to Dashboard
              </Link>
              <button
                type="button"
                onClick={() => void initSession(false)}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
              >
                Retake Assessment
              </button>
            </div>
          </div>
        )}

        {!isInitializing &&
          session &&
          session.status === "in_progress" &&
          currentQuestion && (
            <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {currentQuestion.category}
                </span>
                <div className="flex items-center gap-2">
                  {currentQuestion.is_adaptive && (
                    <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-600/20">
                      Adaptive Follow-up
                    </span>
                  )}
                  <span className="text-xs font-medium text-slate-600">
                    Question {currentIndex + 1} of {session.questions.length}
                  </span>
                </div>
              </div>

              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-slate-900 transition-all duration-300"
                  style={{ width: `${session.progress.progress_percent}%` }}
                />
              </div>
              <p className="mt-1.5 text-right text-xs text-slate-500">
                {session.progress.answered_count} of{" "}
                {session.progress.total_questions} answered (
                {session.progress.progress_percent}%)
              </p>

              <h2 className="mt-6 text-lg font-semibold text-slate-900">
                {currentQuestion.prompt}
              </h2>
              {currentQuestion.help_text && (
                <p className="mt-1 text-sm text-slate-600">
                  {currentQuestion.help_text}
                </p>
              )}

              {actionError && (
                <div
                  role="alert"
                  className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
                >
                  {actionError}
                </div>
              )}

              <div className="mt-6">
                <QuestionRenderer
                  question={currentQuestion}
                  value={draftAnswer}
                  onChange={setDraftAnswer}
                />
              </div>

              <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-5">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    disabled={currentIndex === 0}
                    onClick={() => setCurrentIndex((idx) => Math.max(0, idx - 1))}
                    className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <Link
                    to="/dashboard"
                    className="text-sm font-medium text-slate-600 underline underline-offset-4 hover:text-slate-900"
                  >
                    Save & Resume Later
                  </Link>
                </div>

                {isLastStep && allOtherAnswered ? (
                  <button
                    type="button"
                    disabled={
                      !isAnswerProvided(draftAnswer) ||
                      completeMutation.isPending
                    }
                    onClick={handleComplete}
                    className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {completeMutation.isPending
                      ? "Completing..."
                      : "Complete Assessment"}
                  </button>
                ) : (
                  <button
                    type="button"
                    disabled={
                      !isAnswerProvided(draftAnswer) || saveMutation.isPending
                    }
                    onClick={handleSaveAndNext}
                    className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saveMutation.isPending ? "Saving..." : "Save & Continue"}
                  </button>
                )}
              </div>
            </div>
          )}
      </div>
    </AppLayout>
  );
}
