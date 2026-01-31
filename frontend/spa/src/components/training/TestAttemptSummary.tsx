import type { ReactNode } from "react";

export type SummaryItem = {
  attempt_id: number;
  task_id: number;
  task_type: string;
  prompt: string;
  answer_payload: Record<string, unknown>;
  answer_key?: Record<string, unknown>;
  is_correct: boolean;
  score: string;
  max_score: string;
  submitted_at: string;
  solution_text: string | null;
};

export type TestAttemptSummaryData = {
  test_attempt_id: number;
  status: string;
  started_at: string;
  finished_at: string | null;
  total_score: string;
  max_score: string;
  items: SummaryItem[];
};

type Props = {
  summary: TestAttemptSummaryData | null;
  state: "idle" | "loading" | "error" | "ready";
  error?: string | null;
  onStartNew: () => void;
  onGoHome?: () => void;
  footer?: ReactNode;
};

const formatAnswerPayload = (answerPayload?: Record<string, unknown>) => {
  if (!answerPayload) return null;
  const value = answerPayload.value ?? answerPayload.choice ?? answerPayload.id;
  if (value !== undefined && value !== null) return String(value);
  const values = answerPayload.values;
  if (Array.isArray(values)) return values.map((item) => String(item)).join(", ");
  const pairs = answerPayload.pairs;
  if (pairs && typeof pairs === "object" && !Array.isArray(pairs)) {
    const entries = Object.entries(pairs as Record<string, unknown>);
    if (entries.length === 0) return null;
    return entries.map(([key, val]) => `${key}: ${String(val)}`).join(", ");
  }
  return null;
};

const formatAnswerKey = (answerKey?: unknown) => {
  if (answerKey === undefined || answerKey === null) return null;
  if (Array.isArray(answerKey)) {
    return answerKey.map((item) => String(item)).join(", ");
  }
  if (typeof answerKey !== "object") return String(answerKey);

  const correct = (answerKey as { correct?: unknown }).correct;
  if (correct !== undefined && correct !== null) {
    if (Array.isArray(correct)) {
      return correct.map((item) => String(item)).join(", ");
    }
    if (typeof correct === "object") {
      const entries = Object.entries(correct as Record<string, unknown>);
      if (entries.length === 0) return null;
      return entries.map(([key, val]) => `${key}: ${String(val)}`).join(", ");
    }
    return String(correct);
  }

  return formatAnswerPayload(answerKey as Record<string, unknown>);
};

const formatScoreValue = (value: string) => {
  const parsed = Number.parseFloat(value);
  if (Number.isNaN(parsed)) return value;
  return String(Math.round(parsed));
};

export default function TestAttemptSummary({
  summary,
  state,
  error,
  onStartNew,
  onGoHome,
  footer,
}: Props) {
  return (
    <div className="card shadow-sm">
      <div className="card-body">
        <h2 className="h5 mb-3">Результаты попытки</h2>
        {state === "loading" ? (
          <p className="text-body-secondary mb-0">Загружаем результаты...</p>
        ) : null}
        {state === "error" ? (
          <div className="alert alert-danger mb-3" role="alert">
            {error}
          </div>
        ) : null}
        {summary ? (
          <>
            <div className="mb-4">
              <div className="h5 mb-0">
                Сумма баллов: {formatScoreValue(summary.total_score)} из{" "}
                {formatScoreValue(summary.max_score)} (
                {Number(summary.max_score) > 0
                  ? Math.round((Number(summary.total_score) / Number(summary.max_score)) * 100)
                  : 0}
                %)
              </div>
            </div>
            {summary.items.length === 0 ? (
              <p className="text-body-secondary mb-4">
                Вы ещё не отправляли ответы в этой попытке.
              </p>
            ) : (
              <div className="table-responsive mb-4">
                <table className="table table-sm align-middle">
                  <thead>
                    <tr>
                      <th scope="col">№</th>
                      <th scope="col">Задание</th>
                      <th scope="col">Ваш ответ</th>
                      <th scope="col">Правильный ответ</th>
                      <th scope="col">Балл</th>
                      <th scope="col">Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.items.map((item, index) => (
                      <tr key={item.attempt_id}>
                        <td>{index + 1}</td>
                        <td className="text-truncate" style={{ maxWidth: 320 }}>
                          {item.prompt}
                        </td>
                        <td className="small">
                          {formatAnswerPayload(item.answer_payload) ?? "—"}
                        </td>
                        <td className="small">{formatAnswerKey(item.answer_key) ?? "—"}</td>
                        <td>
                          {formatScoreValue(item.score)} / {formatScoreValue(item.max_score)}
                        </td>
                        <td>
                          {item.is_correct ? (
                            <span className="badge text-bg-success">Верно</span>
                          ) : (
                            <span className="badge text-bg-danger">Неверно</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        ) : null}
        {footer ?? (
          <div className="d-flex flex-wrap gap-2">
            <button type="button" className="btn btn-primary" onClick={onStartNew}>
              Попробовать снова
            </button>
            {onGoHome ? (
              <button type="button" className="btn btn-outline-secondary" onClick={onGoHome}>
                На главную
              </button>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
