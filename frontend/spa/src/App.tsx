import { useAuth } from "./auth";
import AppHeader from "./components/AppHeader";
import AuthedHome from "./pages/AuthedHome";
import PublicHome from "./pages/PublicHome";

function App() {
  const { user, login, register, logout } = useAuth();

  return (
    <>
      <AppHeader user={user} onLogout={logout} />
      <main className="container py-4">
        {user ? <AuthedHome user={user} /> : <PublicHome login={login} register={register} />}
      </main>
    </>
  );
}

export default App;
