import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const ROLE_ROOT = {
  customer: "/", delivery_agent: "/delivery", seller: "/seller", admin: "/admin",
};

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const { login } = useAuth();
  const navigate  = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const role = await login(username.trim(), password);
      navigate(ROLE_ROOT[role] || "/");
    } catch (err) {
      setError(err.message || "Sign in failed.");
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    width: "100%", boxSizing: "border-box",
    border: "1px solid #a6a6a6", borderRadius: 3,
    padding: "7px 10px", fontSize: 14, marginTop: 4,
    outline: "none",
  };

  return (
    <div style={{ background: "#f3f3f3", minHeight: "100vh", paddingBottom: 40 }}>
      {/* Logo */}
      <div style={{ textAlign: "center", paddingTop: 20, paddingBottom: 16 }}>
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
          alt="Amazon"
          style={{ width: 100 }}
        />
      </div>

      {/* Card */}
      <div style={{
        maxWidth: 350, margin: "0 auto", padding: 24,
        background: "white", border: "1px solid #ddd", borderRadius: 4,
      }}>
        <h1 style={{ fontSize: 28, fontWeight: 400, marginTop: 0, marginBottom: 16 }}>
          Sign in
        </h1>

        {/* Error banner */}
        {error && (
          <div style={{
            background: "#fff6f6", border: "1px solid #c40000", borderRadius: 4,
            padding: "8px 12px", fontSize: 13, color: "#c40000", marginBottom: 12,
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label style={{ fontSize: 13, fontWeight: 700 }}>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={inputStyle}
              autoFocus
            />
          </label>

          <label style={{ fontSize: 13, fontWeight: 700, display: "block", marginTop: 12 }}>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={inputStyle}
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%", marginTop: 16, padding: "8px 0",
              background: loading ? "#f7ca75" : "#eb9834",
              border: "1px solid #a88734", borderRadius: 3,
              fontSize: 14, cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "sans-serif",
            }}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>

      {/* Demo creds hint */}
      <div style={{
        maxWidth: 350, margin: "12px auto", padding: "12px 16px",
        background: "white", border: "1px solid #ddd", borderRadius: 4, fontSize: 12,
      }}>
        <strong>Demo credentials (password: Demo1234!):</strong>
        <br />
        <code>archi_customer</code> · <code>archi_delivery</code> · <code>archi_seller</code> · <code>archi_admin</code>
      </div>
    </div>
  );
}
