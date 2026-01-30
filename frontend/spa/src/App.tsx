import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import AppHeader from "./components/AppHeader";
import AuthedHome from "./pages/AuthedHome";
import PublicHome from "./pages/PublicHome";
import RandomTaskPage from "./pages/RandomTaskPage";

function App() {
  const { user, login, register, logout } = useAuth();
  const navigate = useNavigate();
  const isStudent = user?.role === "student";

  return (
    <>
      <AppHeader
        user={user}
        onLogout={logout}
        showRandomLink={isStudent}
      />
      <main className="container py-4">
        <Routes>
          <Route
            path="/"
            element={
              user ? (
                <AuthedHome user={user} />
              ) : (
                <PublicHome login={login} register={register} />
              )
            }
          />
          <Route
            path="/random"
            element={
              user ? (
                isStudent ? (
                  <RandomTaskPage onBack={() => navigate("/")} />
                ) : (
                  <div className="alert alert-warning" role="alert">
                    Раздел доступен только ученикам.
                  </div>
                )
              ) : (
                <Navigate to="/" replace />
              )
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
