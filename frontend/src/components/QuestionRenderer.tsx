import type { AnswerValue, AssessmentQuestion } from "../types/assessment";

interface QuestionRendererProps {
  question: AssessmentQuestion;
  value: AnswerValue | undefined;
  onChange: (value: AnswerValue) => void;
}

export function QuestionRenderer({
  question,
  value,
  onChange,
}: QuestionRendererProps) {
  if (
    question.question_type === "single_choice" ||
    question.question_type === "scenario" ||
    question.question_type === "technical_preference"
  ) {
    const selected = typeof value === "string" ? value : "";
    return (
      <div className="space-y-3" role="radiogroup" aria-label={question.prompt}>
        {question.options.map((opt) => {
          const isChecked = selected === opt.id;
          return (
            <label
              key={opt.id}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition ${
                isChecked
                  ? "border-slate-900 bg-slate-50 ring-1 ring-slate-900"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <input
                type="radio"
                name={question.id}
                value={opt.id}
                checked={isChecked}
                onChange={() => onChange(opt.id)}
                className="mt-1 h-4 w-4 border-slate-300 text-slate-900 focus:ring-slate-900"
              />
              <div>
                <span className="block text-sm font-medium text-slate-900">
                  {opt.label}
                </span>
                {opt.description && (
                  <span className="mt-0.5 block text-xs text-slate-600">
                    {opt.description}
                  </span>
                )}
              </div>
            </label>
          );
        })}
      </div>
    );
  }

  if (question.question_type === "multiple_choice") {
    const selectedList = Array.isArray(value) ? value : [];
    const maxSel = question.max_selections;

    function toggleOption(optionId: string) {
      if (selectedList.includes(optionId)) {
        onChange(selectedList.filter((id) => id !== optionId));
        return;
      }
      if (maxSel !== null && selectedList.length >= maxSel) {
        return;
      }
      onChange([...selectedList, optionId]);
    }

    return (
      <div className="space-y-3">
        {question.options.map((opt) => {
          const isChecked = selectedList.includes(opt.id);
          const atLimit =
            !isChecked && maxSel !== null && selectedList.length >= maxSel;

          return (
            <label
              key={opt.id}
              className={`flex items-start gap-3 rounded-lg border p-4 transition ${
                isChecked
                  ? "border-slate-900 bg-slate-50 ring-1 ring-slate-900"
                  : atLimit
                  ? "cursor-not-allowed border-slate-200 bg-slate-50 opacity-60"
                  : "cursor-pointer border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                disabled={atLimit}
                onChange={() => toggleOption(opt.id)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
              />
              <div>
                <span className="block text-sm font-medium text-slate-900">
                  {opt.label}
                </span>
                {opt.description && (
                  <span className="mt-0.5 block text-xs text-slate-600">
                    {opt.description}
                  </span>
                )}
              </div>
            </label>
          );
        })}
      </div>
    );
  }

  if (question.question_type === "rating_scale") {
    const minVal = question.min_value ?? 1;
    const maxVal = question.max_value ?? 5;
    const ratings = Array.from(
      { length: maxVal - minVal + 1 },
      (_, idx) => minVal + idx
    );
    const currentRating = typeof value === "number" ? value : null;

    return (
      <div>
        <div className="grid grid-cols-5 gap-3">
          {ratings.map((num) => {
            const isSelected = currentRating === num;
            return (
              <button
                key={num}
                type="button"
                aria-pressed={isSelected}
                onClick={() => onChange(num)}
                className={`rounded-lg border py-3 text-sm font-semibold transition ${
                  isSelected
                    ? "border-slate-900 bg-slate-900 text-white shadow-sm"
                    : "border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50"
                }`}
              >
                {num}
              </button>
            );
          })}
        </div>
        {(question.min_label || question.max_label) && (
          <div className="mt-2.5 flex justify-between text-xs text-slate-500">
            <span>{question.min_label ?? ""}</span>
            <span>{question.max_label ?? ""}</span>
          </div>
        )}
      </div>
    );
  }

  return null;
}
