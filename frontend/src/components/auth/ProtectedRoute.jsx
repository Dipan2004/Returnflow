import React from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Lock } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

const ROLE_ROOT = {
  customer: "/",
  delivery_agent: "/delivery",
  warehouse: "/warehouse",
  seller: "/seller",
  admin: "/admin",
};

export default function ProtectedRoute({ allowedRoles, children }) {
  const { user, role, isLoading } = useAuth();
  const navigate = useNavigate();

  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!allowedRoles.includes(role)) {
    return (
      <div style={{ background: "#f3f3f3", minHeight: "100vh" }}>
        <div style={{
          maxWidth: 420, margin: "100px auto", padding: 32,
          background: "white", borderRadius: 4, border: "1px solid #ddd", textAlign: "center",
        }}>
          <Lock size={48} color="#767676" style={{ margin: "0 auto" }} />
          <h2 style={{ fontSize: 20, fontWeight: 400, marginTop: 12 }}>Access restricted</h2>
          <p style={{ color: "#767676", fontSize: 14, marginTop: 8 }}>
            You don't have permission to view this page.
          </p>
          <button
            onClick={() => navigate(ROLE_ROOT[role] || "/")}
            style={{
              width: "100%", background: "#ffd814", border: "1px solid #c59a08", borderRadius: 4,
              padding: 10, fontSize: 14, cursor: "pointer", marginTop: 20, fontWeight: 600,
            }}
          >
            Go to my dashboard
          </button>
        </div>
      </div>
    );
  }
  return children;
}
