import type { User } from "../auth";

type Props = {
  user: User;
};

export default function AuthedHome({ user }: Props) {
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
      </div>
    </div>
  );
}

