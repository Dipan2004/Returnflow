import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "../../components/layout/Header";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "returniq-dev-key-2026";

const GRADE_COLORS = {
  A: { bg: "#d4edda", color: "#155724", label: "Grade A — Like New" },
  B: { bg: "#fff3cd", color: "#856404", label: "Grade B — Good" },
  C: { bg: "#f8d7da", color: "#721c24", label: "Grade C — Fair" },
  D: { bg: "#f5c6cb", color: "#721c24", label: "Grade D — Damaged" },
};

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(options.headers || {}),
    },
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export default function DeliveryAgentView() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ pickups: 0, graded: 0, flagged: 0 });

  useEffect(() => {
    let mounted = true;
    async function loadQueue() {
      try {
        const data = await apiFetch(`${BASE}/delivery/queue`);
        if (mounted) {
          setQueue(data);
          setLoading(false);
          setStats((prev) => ({ ...prev, pickups: data.length }));
        }
      } catch {
        if (mounted) setLoading(false);
      }
    }
    loadQueue();
    const t = setInterval(loadQueue, 3000);
    return () => { mounted = false; clearInterval(t); };
  }, []);

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 80 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 700, margin: "0 auto" }}>

          {/* Section Header */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
            <h2 style={{ fontSize: 20, fontWeight: 700, color: "#131921", margin: 0 }}>
              Pending Pickups
            </h2>
            <span style={{
              backgroundColor: "#fff3cd", color: "#856404",
              padding: "3px 10px", borderRadius: 12, fontSize: 12, fontWeight: "bold",
            }}>
              {queue.length} in queue
            </span>
          </div>

          {/* Loading */}
          {loading && (
            <div style={{ textAlign: "center", padding: 40, color: "#565959", fontSize: 14 }}>
              Loading queue...
            </div>
          )}

          {/* Empty State */}
          {!loading && queue.length === 0 && (
            <div style={{
              backgroundColor: "white", border: "1px solid #ddd", borderRadius: 8,
              padding: 40, textAlign: "center",
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>✅</div>
              <p style={{ fontSize: 15, color: "#565959", margin: 0 }}>
                No pending pickups. Check back soon.
              </p>
            </div>
          )}

          {/* Queue Cards */}
          {queue.map((item) => {
            const gradeInfo = GRADE_COLORS[item.grade] || GRADE_COLORS.B;
            return (
              <div
                key={item.return_id}
                style={{
                  backgroundColor: "white",
                  border: "1px solid #ddd",
                  borderLeft: "4px solid #27726b",
                  borderRadius: 4,
                  padding: 20,
                  marginBottom: 14,
                  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                }}
              >
                {/* Product Name + Grade */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <span style={{ fontSize: 16, fontWeight: 700, color: "#111" }}>
                    {item.product_name || item.sku_id || "Product"}
                  </span>
                  <span style={{
                    backgroundColor: gradeInfo.bg,
                    color: gradeInfo.color,
                    padding: "4px 12px",
                    borderRadius: 12,
                    fontSize: 11,
                    fontWeight: "bold",
                  }}>
                    {gradeInfo.label}
                  </span>
                </div>

                {/* Pickup Address */}
                <div style={{ fontSize: 13, color: "#555", marginBottom: 6 }}>
                  📍 <strong>Address:</strong> {item.pickup_address || item.address || "Customer address"}
                </div>

                {/* Pickup Window */}
                <div style={{ fontSize: 13, color: "#555", marginBottom: 14 }}>
                  🕐 <strong>Window:</strong> {item.pickup_window || "Scheduled"}
                </div>

                {/* Start Pickup Button */}
                <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                  <button
                    onClick={async () => {
                      setQueue((prev) => prev.filter((q) => q.return_id !== item.return_id));
                      try {
                        await apiFetch(`${BASE}/delivery/${item.return_id}/confirm`, {
                          method: "POST",
                          body: JSON.stringify({ return_id: item.return_id }),
                        });
                      } catch {}
                    }}
                    style={{
                      backgroundColor: "#ffa41c",
                      color: "#111",
                      border: "1px solid #ff9900",
                      padding: "9px 18px",
                      borderRadius: 4,
                      fontSize: 13,
                      fontWeight: "bold",
                      cursor: "pointer",
                    }}
                  >
                    📦 PICKED UP
                  </button>
                  <Link
                    to={`/delivery/pickup/${item.return_id}`}
                    state={{ returnData: item }}
                    style={{
                      backgroundColor: "#27726b",
                      color: "white",
                      border: "none",
                      padding: "9px 22px",
                      borderRadius: 4,
                      fontSize: 13,
                      fontWeight: "bold",
                      textDecoration: "none",
                      textAlign: "center",
                    }}
                  >
                    Detailed Pickup →
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* Stats Footer */}
      <footer style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: "#131921",
        color: "white",
        padding: "14px 24px",
        display: "flex",
        justifyContent: "space-around",
        zIndex: 50,
        borderTop: "2px solid #27726b",
        fontFamily: "monospace",
        fontSize: 13,
      }}>
        <span>In queue: <strong>{queue.length}</strong></span>
        <span>Picked today: <strong>{stats.pickups}</strong></span>
        <span>Flagged: <strong>{stats.flagged}</strong></span>
      </footer>
    </div>
  );
}
