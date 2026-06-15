import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [idToken, setIdToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("returniq_user");
      if (saved) {
        const parsed = JSON.parse(saved);
        setUser({ username: parsed.username, name: parsed.name || parsed.username });
        setRole(parsed.role);
      }
    } catch (_) {}
    setIsLoading(false);
  }, []);

  function login(username, selectedRole) {
    const userData = { username, name: username, role: selectedRole };
    localStorage.setItem("returniq_user", JSON.stringify(userData));
    setUser({ username, name: username });
    setRole(selectedRole);
    return selectedRole;
  }

  function logout() {
    localStorage.removeItem("returniq_user");
    setUser(null);
    setRole(null);
    setIdToken(null);
  }

  if (isLoading) {
    return (
      <div style={{
        position: "fixed", inset: 0, background: "#131921",
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: "50%",
          border: "4px solid #27726b", borderTopColor: "transparent",
          animation: "spin 1s linear infinite",
        }} />
        <span style={{ color: "white", fontSize: 18, marginTop: 12, fontFamily: "sans-serif" }}>
          ReturnIQ
        </span>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, role, idToken, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
