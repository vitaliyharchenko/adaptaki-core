import { useMemo, useState } from "react";

type Props = {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
};

type Mode = "login" | "register";

export default function PublicHome({ login, register }: Props) {
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const title = useMemo(() => (mode === "login" ? "Вход" : "Регистрация"), [mode]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password);
      }
    } catch (err) {
      const maybeMessage = err instanceof Error ? err.message : null;
      setError(maybeMessage ?? "Не удалось выполнить операцию. Проверьте данные и попробуйте ещё раз.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-8">
        <div className="p-4 p-md-5 mb-4 bg-body rounded-3 border shadow-sm">
          <h1 className="display-6 mb-2">Adaptaki</h1>
          <p className="lead mb-0 text-body-secondary">
            Платформа для обучения и экзаменов: создавайте задания, отслеживайте прогресс, проводите тестирование и
            анализируйте результаты.
          </p>
        </div>

        <div className="card shadow-sm">
          <div className="card-body">
            <div className="d-flex align-items-center justify-content-between gap-3 flex-wrap">
              <h2 className="h5 mb-0">{title}</h2>
              <div className="btn-group" role="group" aria-label="Вход или регистрация">
                <button
                  type="button"
                  className={`btn ${mode === "login" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={() => setMode("login")}
                >
                  Вход
                </button>
                <button
                  type="button"
                  className={`btn ${mode === "register" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={() => setMode("register")}
                >
                  Регистрация
                </button>
              </div>
            </div>

            <hr className="my-4" />

            {error ? (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            ) : null}

            <form onSubmit={onSubmit} className="vstack gap-3">
              <div>
                <label className="form-label" htmlFor="username">
                  Имя пользователя
                </label>
                <input
                  id="username"
                  className="form-control"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div>
                <label className="form-label" htmlFor="password">
                  Пароль
                </label>
                <input
                  id="password"
                  className="form-control"
                  type="password"
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="d-flex gap-2">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting || !username.trim() || !password.trim()}
                >
                  {isSubmitting ? "Подождите…" : title}
                </button>
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  disabled={isSubmitting}
                  onClick={() => {
                    setUsername("");
                    setPassword("");
                    setError(null);
                  }}
                >
                  Очистить
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

