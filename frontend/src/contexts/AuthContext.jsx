import React, { createContext, useContext, useState, useEffect } from "react";
import { MOCK_USERS } from "../config/mockData";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

const USE_MOCK =
  import.meta.env.VITE_USE_MOCK === "true" ||
  !import.meta.env.VITE_COGNITO_POOL_ID ||
  import.meta.env.VITE_COGNITO_POOL_ID.includes("XXXXXXXXX");

function deriveRole(groups = []) {
  if (groups.includes("admin"))          return "admin";
  if (groups.includes("seller"))         return "seller";
  if (groups.includes("delivery_agent")) return "delivery_agent";
  return "customer";
}

export function AuthProvider({ children }) {
  const [user,      setUser]      = useState(null);
  const [role,      setRole]      = useState(null);
  const [idToken,   setIdToken]   = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // ── Session restore on mount ──────────────────────────────────────────────
  useEffect(() => {
    if (USE_MOCK) {
      try {
        const saved = localStorage.getItem("returniq_user");
        if (saved) {
          const parsed = JSON.parse(saved);
          setUser({ username: parsed.username, name: parsed.name, email: parsed.email });
          setRole(parsed.role);
        }
      } catch (_) { /* ignore */ }
      setIsLoading(false);
      return;
    }
    // Real Cognito path
    import("aws-amplify/auth").then(({ getCurrentUser, fetchAuthSession }) => {
      getCurrentUser()
        .then(async (cognitoUser) => {
          const session = await fetchAuthSession();
          const token   = session.tokens?.idToken?.toString();
          const groups  = session.tokens?.idToken?.payload?.["cognito:groups"] || [];
          setUser({ username: cognitoUser.username, name: cognitoUser.username, email: "" });
          setRole(deriveRole(groups));
          setIdToken(token);
        })
        .catch(() => { /* not logged in */ })
        .finally(() => setIsLoading(false));
    });
  }, []);

  // ── login ─────────────────────────────────────────────────────────────────
  async function login(username, password) {
    if (USE_MOCK) {
      const record = MOCK_USERS[username];
      if (!record || record.password !== password) {
        throw new Error("Incorrect username or password.");
      }
      const userData = { username, role: record.role, name: record.name, email: record.email };
      localStorage.setItem("returniq_user", JSON.stringify(userData));
      setUser({ username, name: record.name, email: record.email });
      setRole(record.role);
      return record.role;
    }
    // Real Cognito
    const { signIn, fetchAuthSession } = await import("aws-amplify/auth");
    await signIn({ username, password });
    const session = await fetchAuthSession();
    const token   = session.tokens?.idToken?.toString();
    const groups  = session.tokens?.idToken?.payload?.["cognito:groups"] || [];
    const derived = deriveRole(groups);
    setUser({ username, name: username, email: "" });
    setRole(derived);
    setIdToken(token);
    return derived;
  }

  // ── logout ────────────────────────────────────────────────────────────────
  async function logout() {
    if (USE_MOCK) {
      localStorage.removeItem("returniq_user");
    } else {
      const { signOut } = await import("aws-amplify/auth");
      await signOut();
    }
    setUser(null);
    setRole(null);
    setIdToken(null);
  }

  // ── Loading screen ────────────────────────────────────────────────────────
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
