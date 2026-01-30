import type { ReactNode } from "react";

export type SummaryItem = {
  attempt_id: number;
  task_id: number;
  task_type: string;
  prompt: string;
  answer_payload: Record<string, unknown>;
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
                Сумма баллов: {summary.total_score} из {summary.max_score} (
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
                      <th scope="col">Ключ</th>
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
                        <td>
                          <pre className="mb-0 small bg-body-tertiary rounded p-2">
                            {JSON.stringify(item.answer_payload ?? {}, null, 2)}
                          </pre>
                        </td>
                        <td className="small">{item.solution_text ?? "—"}</td>
                        <td>
                          {item.score} / {item.max_score}
                        </td>
                        <td>
                          {item.is_correct ? (
                            <span className="badge text-bg-success">Верно</span>
                          ) : (
                            <span className="badge text-bg-warning">Неверно</span>
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
