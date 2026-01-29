import { useState } from "react";
import { useAuth } from "./auth";

function App() {
  const { user, login, register, logout } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  if (user) {
    return (
      <div>
        <h1>Adaptaki</h1>
        <p>Привет, {user.username}</p>
        <p>Роль: {user.role}</p>
        <button onClick={logout}>Выйти</button>
      </div>
    );
  }

  return (
    <div>
      <h1>Adaptaki</h1>

      <input
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <br />

      <input
        placeholder="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br />

      <button onClick={() => login(username, password)}>Login</button>
      <button onClick={() => register(username, password)}>Register</button>
    </div>
  );
}

export default App;