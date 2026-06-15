import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../components/layout/Header";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "returniq-dev-key-2026";

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

const GRADE_COLORS = { A: "#007600", B: "#c45500", C: "#c40000" };

const DEFAULT_MOCK_PICKUPS = [
  {
    return_id: "d001",
    product: "Nike Air Max 270",
    grade: "A",
    address: "Patia, Bhubaneswar, 751024",
    pickup_window: "Tomorrow, 10 AM – 2 PM",
  },
];

export default function DeliveryAgentView() {
  const [pickups, setPickups] = useState([]);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`${BASE}/delivery/queue`);
        setPickups(res.length > 0 ? res : DEFAULT_MOCK_PICKUPS);
      } catch {
        setPickups(DEFAULT_MOCK_PICKUPS);
      }
    }
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, []);

  async function handlePickedUp(item) {
    const removedItem = item;
    setPickups((prev) => prev.filter((i) => i.return_id !== item.return_id));

    try {
      await apiFetch(`${BASE}/delivery/${item.return_id}/confirm`, { method: "POST" });
      setToast("✅ Picked up – item sent to warehouse");
      setTimeout(() => setToast(null), 3000);
    } catch {
      setPickups((prev) => [...prev, removedItem]);
      setToast("❌ Error – try again");
      setTimeout(() => setToast(null), 3000);
    }
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 40 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 700, margin: "0 auto" }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#131921", marginBottom: 6 }}>
            📦 Delivery Agent Queue
          </h1>
          <p style={{ fontSize: 13, color: "#565959", marginBottom: 24 }}>
            Items pending pickup from customers.
          </p>

          {pickups.length === 0 ? (
            <div style={{
              backgroundColor: "white", border: "1px solid #ddd", borderRadius: 6,
              padding: 40, textAlign: "center", color: "#767676",
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>📭</div>
              <p style={{ fontSize: 15 }}>No pickups scheduled right now</p>
            </div>
          ) : (
            pickups.map((item) => (
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
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                  <span style={{ fontSize: 16, fontWeight: 600, color: "#111" }}>
                    {item.product_name || item.product || item.sku_id || "Product"}
                  </span>
                  {item.grade && (
                    <span style={{
                      backgroundColor: GRADE_COLORS[item.grade] || "#767676",
                      color: "white",
                      padding: "3px 10px",
                      borderRadius: 12,
                      fontSize: 12,
                      fontWeight: "bold",
                    }}>
                      Grade {item.grade}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 13, color: "#565959", marginBottom: 6 }}>
                  📍 {item.pickup_address || item.address || "Customer address"}
                </div>
                <div style={{ fontSize: 12, color: "#767676", marginBottom: 14 }}>
                  🕐 {item.pickup_window || "Scheduled"}
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button
                    onClick={() => handlePickedUp(item)}
                    style={{
                      backgroundColor: "#27726b",
                      color: "white",
                      border: "none",
                      padding: "9px 22px",
                      borderRadius: 4,
                      fontSize: 13,
                      fontWeight: "bold",
                      cursor: "pointer",
                    }}
                  >
                    📦 PICKED UP
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {toast && (
        <div style={{
          position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)",
          backgroundColor: "#131921", color: "white", padding: "10px 24px",
          borderRadius: 6, fontSize: 14, fontWeight: 500, zIndex: 999,
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        }}>
          {toast}
        </div>
      )}
    </div>
  );
}
