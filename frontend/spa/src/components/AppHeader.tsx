import { Link } from "react-router-dom";
import type { User } from "../auth";

type Props = {
  user: User | null;
  onLogout: () => void;
  showRandomLink?: boolean;
};

export default function AppHeader({ user, onLogout, showRandomLink }: Props) {
  return (
    <header className="container py-3">
      <div className="row">
        <div className="col-12">
          <nav className="navbar navbar-expand bg-body border rounded-3 px-3">
            <div className="container-fluid px-0">
              <Link className="navbar-brand fw-semibold" to="/">
                Adaptaki
              </Link>

              {user ? (
                <div className="d-flex align-items-center gap-3">
                  <span className="text-body-secondary">Привет, {user.username}!</span>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={onLogout}
                  >
                    Выйти
                  </button>
                </div>
              ) : null}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
