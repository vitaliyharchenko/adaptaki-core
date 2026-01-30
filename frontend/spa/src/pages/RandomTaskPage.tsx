import { useEffect, useState } from "react";
import api from "../api";
import TestAttemptSummary, {
  type TestAttemptSummaryData,
} from "../components/training/TestAttemptSummary";
import TrainingTaskSolve from "../components/training/TrainingTaskSolve";

type RandomTask = {
  id: number;
  subject_id: number;
  task_type: string;
  prompt: string;
  type_payload: Record<string, unknown>;
  test_attempt_id: number;
};

type SubjectOption = {
  id: number;
  title: string;
};

type TaskTypeOption = {
  value: string;
  label: string;
};

type SubmitResult = {
  attempt_id: number;
  task_id: number;
  is_correct: boolean;
  score: string;
  max_score: string;
  submitted_at: string;
  solution_text: string | null;
};


type FetchState = "idle" | "loading" | "error" | "ready";
type SubmitState = "idle" | "loading" | "error" | "success";

type Props = {
  onBack?: () => void;
};

export default function RandomTaskPage({ onBack }: Props) {
  const [subjectId, setSubjectId] = useState("");
  const [taskType, setTaskType] = useState("");
  const [task, setTask] = useState<RandomTask | null>(null);
  const [state, setState] = useState<FetchState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [testAttemptId, setTestAttemptId] = useState<number | null>(null);
  const [answerValue, setAnswerValue] = useState("");
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [subjects, setSubjects] = useState<SubjectOption[]>([]);
  const [taskTypes, setTaskTypes] = useState<TaskTypeOption[]>([]);
  const [filtersState, setFiltersState] = useState<FetchState>("idle");
  const [filtersError, setFiltersError] = useState<string | null>(null);
  const [finishState, setFinishState] = useState<SubmitState>("idle");
  const [showSolution, setShowSolution] = useState(false);
  const [summary, setSummary] = useState<TestAttemptSummaryData | null>(null);
  const [summaryState, setSummaryState] = useState<FetchState>("idle");
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(false);

  useEffect(() => {
    const loadFilters = async () => {
      setFiltersState("loading");
      setFiltersError(null);
      try {
        const [subjectsRes, taskTypesRes] = await Promise.all([
          api.get<{ subjects: SubjectOption[] }>("/graph/subjects/"),
          api.get<{ task_types: TaskTypeOption[] }>("/tasks/task-types/"),
        ]);
        setSubjects(subjectsRes.data.subjects ?? []);
        setTaskTypes(taskTypesRes.data.task_types ?? []);
        setFiltersState("ready");
      } catch (err: any) {
        const message =
          err?.response?.data?.error || "Не удалось загрузить варианты фильтров.";
        setFiltersError(message);
        setFiltersState("error");
      }
    };
    loadFilters();
  }, []);

  const fetchTask = async (startNewSession: boolean) => {
    setState("loading");
    setError(null);

    const params: Record<string, string | number> = {};
    if (subjectId.trim()) {
      params.subject_id = Number(subjectId);
    }
    if (taskType.trim()) {
      params.task_type = taskType.trim();
    }
    if (!startNewSession && testAttemptId) {
      params.test_attempt_id = testAttemptId;
    }

    try {
      const res = await api.get<RandomTask>("/training/random-task/", { params });
      setTask(res.data);
      setTestAttemptId(res.data.test_attempt_id);
      setAnswerValue("");
      setSubmitState("idle");
      setSubmitError(null);
      setSubmitResult(null);
      setShowSolution(false);
      setStartedAt(Date.now());
      setSummary(null);
      setSummaryState("idle");
      setSummaryError(null);
      setShowSummary(false);
      setState("ready");
    } catch (err: any) {
      const message = err?.response?.data?.error || "Не удалось получить задание.";
      setError(message);
      setState("error");
    }
  };

  const submitAnswer = async () => {
    if (!task) return;
    setSubmitState("loading");
    setSubmitError(null);

    const durationMs = startedAt ? Math.max(0, Date.now() - startedAt) : null;

    try {
      const res = await api.post<SubmitResult>("/training/submit-answer/", {
        task_id: task.id,
        answer_payload: { value: answerValue },
        duration_ms: durationMs,
        test_attempt_id: testAttemptId ?? undefined,
      });
      setSubmitResult(res.data);
      setSubmitState("success");
      setShowSolution(false);
    } catch (err: any) {
      const message = err?.response?.data?.error || "Не удалось отправить ответ.";
      setSubmitError(message);
      setSubmitState("error");
    }
  };

  const finishAttempt = async () => {
    if (!testAttemptId) return;
    setFinishState("loading");
    try {
      await api.post("/training/random-session/finish/", {
        test_attempt_id: testAttemptId,
        status: "finished",
      });
      setShowSummary(true);
      setSummaryState("loading");
      setSummaryError(null);
      const summaryRes = await api.get<TestAttemptSummaryData>("/training/test-attempt/summary/", {
        params: { test_attempt_id: testAttemptId },
      });
      setSummary(summaryRes.data);
      setSummaryState("ready");
      setTask(null);
      setTestAttemptId(null);
      setAnswerValue("");
      setSubmitState("idle");
      setSubmitError(null);
      setSubmitResult(null);
      setShowSolution(false);
      setStartedAt(null);
      setFinishState("idle");
      setState("idle");
    } catch {
      setFinishState("error");
      setShowSummary(true);
      setSummaryState("error");
      setSummaryError("Не удалось загрузить результаты попытки.");
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-9">
        <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
          <div>
            <h1 className="h4 mb-1">Случайное задание</h1>
            <p className="text-body-secondary mb-0">
              Получайте задания по предмету и типу, чтобы практиковаться в рандомном режиме.
            </p>
          </div>
          {task ? (
            <button
              type="button"
              className="btn btn-outline-danger"
              onClick={finishAttempt}
              disabled={finishState === "loading"}
            >
              Закончить попытку
            </button>
          ) : null}
        </div>

        {showSummary ? (
          <TestAttemptSummary
            summary={summary}
            state={summaryState}
            error={summaryError}
            onStartNew={() => {
              setSummary(null);
              setShowSummary(false);
            }}
            onGoHome={onBack}
          />
        ) : !task ? (
          <div className="card shadow-sm mb-3">
            <div className="card-body">
              <div className="row g-3">
                <div className="col-12 col-md-4">
                  <label className="form-label" htmlFor="random-subject-id">
                    Предмет
                  </label>
                  <select
                    id="random-subject-id"
                    className="form-control"
                    value={subjectId}
                    onChange={(event) => setSubjectId(event.target.value)}
                    disabled={filtersState === "loading"}
                  >
                    <option value="">Все предметы</option>
                    {subjects.map((subject) => (
                      <option key={subject.id} value={String(subject.id)}>
                        {subject.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-12 col-md-4">
                  <label className="form-label" htmlFor="random-task-type">
                    Тип задания
                  </label>
                  <select
                    id="random-task-type"
                    className="form-control"
                    value={taskType}
                    onChange={(event) => setTaskType(event.target.value)}
                    disabled={filtersState === "loading"}
                  >
                    <option value="">Все типы</option>
                    {taskTypes.map((item) => (
                      <option key={item.value} value={item.value}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-12 col-md-4 d-flex align-items-end">
                  <button
                    type="button"
                    className="btn btn-primary w-100"
                    onClick={() => fetchTask(true)}
                    disabled={state === "loading"}
                  >
                    Начать тест
                  </button>
                </div>
              </div>
              {filtersState === "error" ? (
                <div className="alert alert-danger mt-3 mb-0" role="alert">
                  {filtersError}
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        {state === "loading" || state === "error" || task ? (
          <div className="card shadow-sm">
            <div className="card-body">
              {state === "loading" ? (
                <p className="mb-0">Загрузка задания...</p>
              ) : null}
              {state === "error" ? (
                <div className="alert alert-danger mb-0" role="alert">
                  {error}
                </div>
              ) : null}
              {task ? (
                <TrainingTaskSolve
                  prompt={task.prompt}
                  answerValue={answerValue}
                  onAnswerChange={setAnswerValue}
                  onSubmit={submitAnswer}
                  submitDisabled={!answerValue.trim()}
                  submitState={submitState}
                  submitError={submitError}
                  submitResult={submitResult}
                  showSolution={showSolution}
                  onToggleSolution={() => setShowSolution((prev) => !prev)}
                  actionButtons={
                    <button
                      type="button"
                      className="btn btn-primary w-100"
                      onClick={() => fetchTask(false)}
                      disabled={state === "loading"}
                    >
                      Далее
                    </button>
                  }
                />
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
