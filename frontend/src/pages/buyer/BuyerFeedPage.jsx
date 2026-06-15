import React, { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
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
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(`${res.status}`);
    err.detail = body.detail || body.error || "";
    throw err;
  }
  return res.json();
}

const GRADE_COLORS = { A: "#007600", B: "#c45500", C: "#c40000" };

const DEMO_ITEMS = [
  { return_id: "bf001", product_name: "Nike Air Max 270", grade: "A", original_price: 8500, resale_price: 5950, condition_description: "Minor toe-box scuff. Fully functional.", original_returner_id: "" },
  { return_id: "bf002", product_name: "boAt Rockerz 450", grade: "B", original_price: 3499, resale_price: 2449, condition_description: "Light ear-pad wear. Audio perfect.", original_returner_id: "" },
];

function discountPercent(original, resale) {
  if (!original || original === 0) return 0;
  return Math.round(((original - resale) / original) * 100);
}

export default function BuyerFeedPage() {
  const [items, setItems] = useState([]);
  const [toast, setToast] = useState(null);
  const { user } = useAuth();
  const currentUser = user?.name || "";

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`${BASE}/buyer-feed`);
        setItems(res.length > 0 ? res : DEMO_ITEMS);
      } catch {
        setItems(DEMO_ITEMS);
      }
    }
    load();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, []);

  async function handleBuy(item) {
    try {
      await apiFetch(`${BASE}/buyer-feed/${item.return_id}/purchase`, {
        method: "POST",
        body: JSON.stringify({ buyer_id: currentUser }),
      });
      setItems((prev) => prev.filter((i) => i.return_id !== item.return_id));
      showToast("🎉 Purchased! Delivery in 2-3 days.");
    } catch (err) {
      if (err.detail && err.detail.includes("own returned")) {
        showToast("❌ Cannot purchase your own returned item");
      } else {
        showToast("❌ Purchase failed – try again");
      }
    }
  }

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 40 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#131921", marginBottom: 4 }}>
            🛒 Available Near You — Certified Returns
          </h1>
          <p style={{ fontSize: 13, color: "#565959", marginBottom: 24 }}>
            AI-graded items verified by ReturnIQ
          </p>

          {items.length === 0 ? (
            <div style={{
              backgroundColor: "white", border: "1px solid #ddd", borderRadius: 6,
              padding: 40, textAlign: "center", color: "#767676",
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>📦</div>
              <p style={{ fontSize: 15 }}>No items available right now. Check back soon!</p>
            </div>
          ) : (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: 18,
            }}>
              {items.map((item) => {
                const resale = item.resale_price || Math.round(item.original_price * 0.7);
                const discount = discountPercent(item.original_price, resale);
                const isOwnReturn = item.original_returner_id && item.original_returner_id === currentUser;

                return (
                  <div
                    key={item.return_id}
                    style={{
                      backgroundColor: "white",
                      border: "1px solid #ddd",
                      borderRadius: 8,
                      padding: 20,
                      boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      position: "relative",
                      opacity: isOwnReturn ? 0.6 : 1,
                    }}
                  >
                    {isOwnReturn && (
                      <div style={{
                        position: "absolute", top: 10, right: 10,
                        backgroundColor: "#565959", color: "white",
                        padding: "3px 10px", borderRadius: 12,
                        fontSize: 10, fontWeight: "bold",
                      }}>
                        You returned this item
                      </div>
                    )}

                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ fontSize: 16, fontWeight: 600, color: "#111" }}>
                          {item.product_name}
                        </span>
                        {item.grade && (
                          <span style={{
                            backgroundColor: GRADE_COLORS[item.grade] || "#767676",
                            color: "white",
                            padding: "3px 10px",
                            borderRadius: 12,
                            fontSize: 11,
                            fontWeight: "bold",
                          }}>
                            Grade {item.grade}
                          </span>
                        )}
                      </div>

                      <p style={{ fontSize: 13, color: "#565959", marginBottom: 12, lineHeight: 1.4 }}>
                        {item.condition_description}
                      </p>

                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                        <span style={{ fontSize: 18, fontWeight: 700, color: "#007600" }}>
                          ₹{resale.toLocaleString()}
                        </span>
                        <span style={{ fontSize: 14, color: "#767676", textDecoration: "line-through" }}>
                          ₹{item.original_price.toLocaleString()}
                        </span>
                        {discount > 0 && (
                          <span style={{
                            backgroundColor: "#cc0c39",
                            color: "white",
                            padding: "2px 8px",
                            borderRadius: 4,
                            fontSize: 11,
                            fontWeight: "bold",
                          }}>
                            {discount}% OFF
                          </span>
                        )}
                      </div>
                    </div>

                    {isOwnReturn ? (
                      <button
                        disabled
                        style={{
                          marginTop: 14,
                          backgroundColor: "#e7e9ec",
                          color: "#888",
                          border: "1px solid #d5d9d9",
                          padding: "10px 0",
                          borderRadius: 20,
                          fontSize: 14,
                          fontWeight: 600,
                          cursor: "not-allowed",
                          width: "100%",
                        }}
                      >
                        Not available for you
                      </button>
                    ) : (
                      <button
                        onClick={() => handleBuy(item)}
                        style={{
                          marginTop: 14,
                          backgroundColor: "#ffd814",
                          color: "#111",
                          border: "1px solid #f5c518",
                          padding: "10px 0",
                          borderRadius: 20,
                          fontSize: 14,
                          fontWeight: 600,
                          cursor: "pointer",
                          width: "100%",
                        }}
                      >
                        Buy Now
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
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
