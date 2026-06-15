import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const ROLE_ROOT = {
  customer: "/",
  delivery_agent: "/delivery",
  warehouse: "/warehouse",
  admin: "/admin",
};

const EMPLOYEE_ROLES = [
  { label: "Delivery Agent", value: "delivery_agent" },
  { label: "Warehouse Staff", value: "warehouse" },
  { label: "Admin", value: "admin" },
];

export default function LoginPage() {
  const [mode, setMode] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [employeeRole, setEmployeeRole] = useState("delivery_agent");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }
    setLoading(true);
    try {
      const selectedRole = mode === "customer" ? "customer" : employeeRole;
      login(username.trim(), selectedRole);
      navigate(ROLE_ROOT[selectedRole] || "/");
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  const cardStyle = (selected) => ({
    flex: "1 1 200px",
    minWidth: 180,
    padding: "32px 24px",
    background: "white",
    border: selected ? "2px solid #27726b" : "1px solid #ddd",
    borderRadius: 8,
    cursor: "pointer",
    textAlign: "center",
    transition: "all 0.2s",
    boxShadow: selected ? "0 4px 12px rgba(39,114,107,0.15)" : "0 1px 4px rgba(0,0,0,0.06)",
  });

  const inputStyle = {
    width: "100%",
    boxSizing: "border-box",
    border: "1px solid #a6a6a6",
    borderRadius: 4,
    padding: "10px 12px",
    fontSize: 14,
    marginTop: 6,
    outline: "none",
  };

  return (
    <div style={{ background: "#f3f3f3", minHeight: "100vh", paddingBottom: 40 }}>
      <div style={{ textAlign: "center", paddingTop: 28, paddingBottom: 20 }}>
        <div style={{ fontSize: 28, fontWeight: 700, color: "#131921", fontFamily: "sans-serif" }}>
          Return<span style={{ color: "#27726b" }}>IQ</span>
        </div>
        <div style={{ fontSize: 13, color: "#767676", marginTop: 4 }}>
          Intelligent Returns Disposition Engine
        </div>
      </div>

      <div style={{ maxWidth: 520, margin: "0 auto", padding: "0 16px" }}>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 24 }}>
          <div style={cardStyle(mode === "customer")} onClick={() => setMode("customer")}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🛍️</div>
            <div style={{ fontSize: 18, fontWeight: 600, color: "#131921" }}>Customer</div>
            <div style={{ fontSize: 12, color: "#767676", marginTop: 6 }}>
              Return products, view health cards
            </div>
          </div>
          <div style={cardStyle(mode === "employee")} onClick={() => setMode("employee")}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>👷</div>
            <div style={{ fontSize: 18, fontWeight: 600, color: "#131921" }}>Employee</div>
            <div style={{ fontSize: 12, color: "#767676", marginTop: 6 }}>
              Delivery, warehouse, or admin
            </div>
          </div>
        </div>

        {mode && (
          <div style={{
            background: "white",
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 28,
            boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
          }}>
            <h2 style={{ fontSize: 20, fontWeight: 500, marginTop: 0, marginBottom: 20, color: "#131921" }}>
              {mode === "customer" ? "Customer Login" : "Employee Login"}
            </h2>

            {error && (
              <div style={{
                background: "#fff6f6", border: "1px solid #c40000", borderRadius: 4,
                padding: "8px 12px", fontSize: 13, color: "#c40000", marginBottom: 16,
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {mode === "employee" && (
                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontSize: 13, fontWeight: 700, color: "#131921" }}>
                    Role
                    <select
                      value={employeeRole}
                      onChange={(e) => setEmployeeRole(e.target.value)}
                      style={{
                        ...inputStyle,
                        background: "white",
                        cursor: "pointer",
                      }}
                    >
                      {EMPLOYEE_ROLES.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                      ))}
                    </select>
                  </label>
                </div>
              )}

              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: 13, fontWeight: 700, color: "#131921" }}>
                  Username
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={inputStyle}
                    autoFocus
                    placeholder="Enter any username"
                  />
                </label>
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 13, fontWeight: 700, color: "#131921" }}>
                  Password
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={inputStyle}
                    placeholder="Enter any password"
                  />
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "11px 0",
                  background: loading ? "#f7dfa0" : "#ffd814",
                  border: "1px solid #c59a08",
                  borderRadius: 6,
                  fontSize: 15,
                  fontWeight: 600,
                  cursor: loading ? "not-allowed" : "pointer",
                  fontFamily: "sans-serif",
                  color: "#131921",
                }}
              >
                {loading ? "Signing in…" : "Sign in"}
              </button>
            </form>

            <div style={{
              marginTop: 16,
              padding: "10px 14px",
              background: "#f0faf9",
              borderRadius: 4,
              border: "1px solid #c8e6e3",
              fontSize: 12,
              color: "#27726b",
              lineHeight: 1.6,
            }}>
              💡 <strong>Demo credentials (any password works):</strong><br />
              {mode === "customer" ? (
                <>Customer: <strong>rahul</strong> | <strong>priya</strong> | <strong>amit</strong></>
              ) : (
                <>
                  Delivery Agent: <strong>agent1</strong> | <strong>agent2</strong><br />
                  Warehouse: <strong>warehouse1</strong><br />
                  Admin: <strong>admin1</strong>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
