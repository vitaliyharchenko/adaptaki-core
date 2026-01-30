import type { ReactNode } from "react";

type Props = {
  prompt: string;
  answerValue: string;
  onAnswerChange: (value: string) => void;
  onSubmit: () => void;
  submitDisabled: boolean;
  submitState: "idle" | "loading" | "error" | "success";
  submitError?: string | null;
  submitResult?: {
    is_correct: boolean;
    score: string;
    max_score: string;
    solution_text: string | null;
    answer_key?: Record<string, unknown>;
  } | null;
  showSolution: boolean;
  onToggleSolution: () => void;
  actionButtons: ReactNode;
};

const formatCorrectAnswer = (answerKey?: Record<string, unknown>) => {
  if (!answerKey) return null;
  const correct = (answerKey as { correct?: unknown }).correct;
  if (correct === undefined || correct === null) return null;
  if (Array.isArray(correct)) {
    return correct.map((item) => String(item)).join(", ");
  }
  return String(correct);
};

export default function TrainingTaskSolve({
  prompt,
  answerValue,
  onAnswerChange,
  onSubmit,
  submitDisabled,
  submitState,
  submitError,
  submitResult,
  showSolution,
  onToggleSolution,
  actionButtons,
}: Props) {
  let inputStateClass = "";
  const correctAnswerText = formatCorrectAnswer(submitResult?.answer_key);
  if (submitResult) {
    const score = Number.parseFloat(submitResult.score);
    const maxScore = Number.parseFloat(submitResult.max_score);
    if (!Number.isNaN(score) && !Number.isNaN(maxScore)) {
      if (score >= maxScore && maxScore > 0) {
        inputStateClass = "is-valid";
      } else if (score > 0) {
        inputStateClass = "border-warning bg-warning-subtle";
      } else {
        inputStateClass = "is-invalid";
      }
    } else if (submitResult.is_correct) {
      inputStateClass = "is-valid";
    } else {
      inputStateClass = "is-invalid";
    }
  }

  return (
    <div>
      <h2 className="h6 text-uppercase text-body-secondary">Условие</h2>
      <p className="mb-4">{prompt}</p>
      <div className="card border-0 bg-body-tertiary mb-4">
        <div className="card-body">
          <h3 className="h6 text-uppercase text-body-secondary">Ваш ответ (строка)</h3>
          <div className="row g-2 align-items-end">
            <div className="col-12 col-md-8">
              <label className="form-label" htmlFor="answer-input">
                Ответ
              </label>
              <input
                id="answer-input"
                className={`form-control ${inputStateClass}`}
                value={answerValue}
                onChange={(event) => onAnswerChange(event.target.value)}
                placeholder="Введите ответ"
                disabled={submitState === "success"}
                autoComplete="off"
              />
            </div>
            <div className="col-12 col-md-4 d-flex">
              {submitState === "success" ? (
                <div className="d-flex gap-2 w-100">{actionButtons}</div>
              ) : (
                <div className="d-flex gap-2 w-100">
                  <button
                    type="button"
                    className="btn btn-success w-100"
                    onClick={onSubmit}
                    disabled={submitDisabled || submitState === "loading"}
                  >
                    Проверить
                  </button>
                </div>
              )}
            </div>
          </div>
          {submitState === "error" ? (
            <div className="alert alert-danger mt-3 mb-0" role="alert">
              {submitError}
            </div>
          ) : null}
          {submitResult ? (
            <div className="mt-3 text-body-secondary">
              <div>
                Балл: {submitResult.score} / {submitResult.max_score}
              </div>
              {!submitResult.is_correct && correctAnswerText ? (
                <div className="mt-1">
                  Верный ответ: <span className="text-body">{correctAnswerText}</span>
                </div>
              ) : null}
              {submitResult.solution_text ? (
                <div className="mt-2">
                  <a
                    href="#"
                    className="link-primary text-decoration-none"
                    onClick={(event) => {
                      event.preventDefault();
                      onToggleSolution();
                    }}
                  >
                    {showSolution ? "Скрыть решение" : "Показать решение"}
                  </a>
                  {showSolution ? (
                    <div className="mt-2 text-body">{submitResult.solution_text}</div>
                  ) : null}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
