import { useState, type KeyboardEvent } from "react";

interface TagInputProps {
  id: string;
  label: string;
  placeholder: string;
  value: string[];
  onChange: (next: string[]) => void;
  helperText?: string;
}

export function TagInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  helperText,
}: TagInputProps) {
  const [draft, setDraft] = useState("");

  function addTag(raw: string) {
    const cleaned = raw.trim();
    if (!cleaned) {
      return;
    }
    const exists = value.some(
      (item) => item.toLowerCase() === cleaned.toLowerCase()
    );
    if (!exists) {
      onChange([...value, cleaned]);
    }
    setDraft("");
  }

  function removeTag(indexToRemove: number) {
    onChange(value.filter((_, idx) => idx !== indexToRemove));
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      addTag(draft);
    }
  }

  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-slate-700">
        {label}
      </label>

      <div className="mt-1 flex gap-2">
        <input
          id={id}
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
        />
        <button
          type="button"
          onClick={() => addTag(draft)}
          className="shrink-0 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
        >
          Add
        </button>
      </div>

      {helperText && (
        <p className="mt-1 text-xs text-slate-500">{helperText}</p>
      )}

      {value.length > 0 && (
        <div className="mt-2.5 flex flex-wrap gap-2">
          {value.map((tag, idx) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-800"
            >
              {tag}
              <button
                type="button"
                aria-label={`Remove ${tag}`}
                onClick={() => removeTag(idx)}
                className="text-slate-500 transition hover:text-slate-900"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
