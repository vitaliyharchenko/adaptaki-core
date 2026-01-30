import type { User } from "../auth";
import { Link } from "react-router-dom";

type Props = {
  user: User;
};

export default function AuthedHome({ user }: Props) {
  const isStudent = user.role === "student";

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-8">
        <div className="card shadow-sm">
          <div className="card-body">
            <h1 className="h4 mb-2">Личный кабинет</h1>
            <p className="mb-0 text-body-secondary">
              Вы авторизованы как <span className="fw-semibold">{user.username}</span> (роль: {user.role}).
            </p>
          </div>
        </div>

        {isStudent ? (
          <div className="card shadow-sm mt-3">
            <div className="card-body">
              <h2 className="h6 mb-2">Практика в рандомном режиме</h2>
              <p className="text-body-secondary mb-3">
                Перейдите к странице со случайными заданиями и начните тренировку.
              </p>
              <Link className="btn btn-primary" to="/random">
                Перейти к заданиям
              </Link>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
