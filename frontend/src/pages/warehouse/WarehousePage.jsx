import React, { useState, useEffect } from "react";
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

const GRADE_COLORS = { A: "#007600", B: "#c45500", C: "#c40000", D: "#767676" };

export default function WarehousePage() {
  const [items, setItems] = useState([]);
  const [toast, setToast] = useState(null);
  const [regrading, setRegrading] = useState({});
  const [scanningBuyers, setScanningBuyers] = useState({});
  const [buyerMatches, setBuyerMatches] = useState({});

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`${BASE}/warehouse/queue`);
        setItems(res);
      } catch {
        setItems([]);
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  }

  async function handleRegrade(returnId) {
    setRegrading((prev) => ({ ...prev, [returnId]: true }));
    try {
      const result = await apiFetch(`${BASE}/grades/process`, {
        method: "POST",
        body: JSON.stringify({ return_id: returnId }),
      });
      setItems((prev) =>
        prev.map((i) =>
          i.return_id === returnId
            ? { ...i, grade: result.grade, condition_description: result.damage_description }
            : i
        )
      );
      showToast(`Re-graded: Grade ${result.grade}`);
    } catch {
      showToast("Re-grade failed");
    } finally {
      setRegrading((prev) => ({ ...prev, [returnId]: false }));
    }
  }

  async function handleBuyerScan(returnId, skuId) {
    setScanningBuyers((prev) => ({ ...prev, [returnId]: true }));
    try {
      const item = items.find((i) => i.return_id === returnId);
      const result = await apiFetch(`${BASE}/buyer-match/compute`, {
        method: "POST",
        body: JSON.stringify({
          return_id: returnId,
          sku_id: skuId,
          pincode: "751024",
          grade: item?.grade || "B",
        }),
      });
      const count = result.matched_buyers?.length || result.match_count || result.estimated_buyers || 0;
      setBuyerMatches((prev) => ({ ...prev, [returnId]: count }));
      showToast(count > 0 ? `✅ ${count} buyer(s) matched nearby` : "⏳ No buyers matched yet");
    } catch {
      showToast("Buyer scan failed");
    } finally {
      setScanningBuyers((prev) => ({ ...prev, [returnId]: false }));
    }
  }

  async function handleApprove(item) {
    setItems((prev) => prev.filter((i) => i.return_id !== item.return_id));
    try {
      await apiFetch(`${BASE}/warehouse/${item.return_id}/approve`, { method: "POST" });
      showToast("Approved – item listed for resale");
    } catch {
      setItems((prev) => [...prev, item]);
      showToast("Error – try again");
    }
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 40 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 700, margin: "0 auto" }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#131921", marginBottom: 6 }}>
            🏭 Warehouse Receiving Queue
          </h1>
          <p style={{ fontSize: 13, color: "#565959", marginBottom: 24 }}>
            Items picked up by delivery agents awaiting warehouse inspection and approval.
          </p>

          {items.length === 0 ? (
            <div style={{
              backgroundColor: "white", border: "1px solid #ddd", borderRadius: 6,
              padding: 40, textAlign: "center", color: "#767676",
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>📦</div>
              <p style={{ fontSize: 15 }}>No items awaiting inspection</p>
            </div>
          ) : (
            items.map((item) => {
              const matchCount = buyerMatches[item.return_id];
              const scanned = matchCount !== undefined;
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
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                    <span style={{ fontSize: 16, fontWeight: 600, color: "#111" }}>
                      {item.product_name || item.sku_id || "Unknown Product"}
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
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
                  </div>

                  <div style={{ fontSize: 12, color: "#767676", marginBottom: 10 }}>
                    Return ID: {item.return_id}
                  </div>

                  {/* Buyer match display */}
                  <div style={{ marginBottom: 14 }}>
                    {scanned ? (
                      matchCount > 0 ? (
                        <span style={{
                          backgroundColor: "#d4edda", color: "#155724",
                          padding: "3px 10px", borderRadius: 12, fontSize: 11, fontWeight: "bold",
                        }}>
                          ✅ {matchCount} buyer{matchCount > 1 ? "s" : ""} matched nearby
                        </span>
                      ) : (
                        <span style={{
                          backgroundColor: "#f0f0f0", color: "#767676",
                          padding: "3px 10px", borderRadius: 12, fontSize: 11, fontWeight: "bold",
                        }}>
                          No buyers found
                        </span>
                      )
                    ) : (
                      <button
                        onClick={() => handleBuyerScan(item.return_id, item.sku_id)}
                        disabled={scanningBuyers[item.return_id]}
                        style={{
                          backgroundColor: "#f0faf8",
                          color: "#27726b",
                          border: "1px solid #27726b",
                          padding: "5px 12px",
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: "bold",
                          cursor: scanningBuyers[item.return_id] ? "not-allowed" : "pointer",
                          opacity: scanningBuyers[item.return_id] ? 0.6 : 1,
                        }}
                      >
                        {scanningBuyers[item.return_id] ? "Scanning..." : "🔍 Scan Nearby Buyers"}
                      </button>
                    )}
                  </div>

                  <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                    <button
                      onClick={() => handleRegrade(item.return_id)}
                      disabled={regrading[item.return_id]}
                      style={{
                        backgroundColor: "white",
                        color: "#27726b",
                        border: "1px solid #27726b",
                        padding: "8px 16px",
                        borderRadius: 4,
                        fontSize: 12,
                        fontWeight: "bold",
                        cursor: regrading[item.return_id] ? "not-allowed" : "pointer",
                        opacity: regrading[item.return_id] ? 0.6 : 1,
                      }}
                    >
                      {regrading[item.return_id] ? "⏳ Grading..." : "🔄 Re-grade"}
                    </button>
                    <button
                      onClick={() => handleApprove(item)}
                      style={{
                        backgroundColor: "#27726b",
                        color: "white",
                        border: "none",
                        padding: "8px 20px",
                        borderRadius: 4,
                        fontSize: 13,
                        fontWeight: "bold",
                        cursor: "pointer",
                      }}
                    >
                      ✅ Approve & List for Resale
                    </button>
                  </div>
                </div>
              );
            })
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
