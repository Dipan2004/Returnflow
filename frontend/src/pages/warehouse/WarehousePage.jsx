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
      ...(options.headers || {}),
    },
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

const GRADE_CONFIG = {
  A: { bg: "#d4edda", color: "#155724", label: "Like New" },
  B: { bg: "#fff3cd", color: "#856404", label: "Good" },
  C: { bg: "#f8d7da", color: "#721c24", label: "Fair" },
  D: { bg: "#f5c6cb", color: "#721c24", label: "Damaged" },
};

export default function WarehousePage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [regrading, setRegrading] = useState({});
  const [approving, setApproving] = useState({});
  const [scanning, setScanning] = useState({});
  const [buyerMatches, setBuyerMatches] = useState({});
  const [toast, setToast] = useState(null);

  function showToast(msg, type = "success") {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const data = await apiFetch(`${BASE}/warehouse/queue`);
        if (mounted) { setItems(data); setLoading(false); }
      } catch {
        if (mounted) setLoading(false);
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => { mounted = false; clearInterval(t); };
  }, []);

  async function handleRegrade(returnId) {
    setRegrading((p) => ({ ...p, [returnId]: true }));
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
      showToast(`Re-graded: Grade ${result.grade} (${result.confidence?.toFixed(1)}% confidence)`);
    } catch {
      showToast("Re-grade failed. Check backend.", "error");
    } finally {
      setRegrading((p) => ({ ...p, [returnId]: false }));
    }
  }

  async function handleBuyerScan(returnId, skuId, grade) {
    setScanning((p) => ({ ...p, [returnId]: true }));
    try {
      const result = await apiFetch(`${BASE}/buyer-match/compute`, {
        method: "POST",
        body: JSON.stringify({ return_id: returnId, sku_id: skuId, pincode: "751024", grade }),
      });
      const count = result.match_count ?? result.matched_buyers?.length ?? 0;
      setBuyerMatches((p) => ({ ...p, [returnId]: count }));
      showToast(
        count > 0 ? `✅ ${count} buyer(s) matched nearby` : "⏳ No buyers matched yet",
        count > 0 ? "success" : "info"
      );
    } catch {
      showToast("Buyer scan failed", "error");
    } finally {
      setScanning((p) => ({ ...p, [returnId]: false }));
    }
  }

  async function handleApprove(returnId) {
    const item = items.find((i) => i.return_id === returnId);
    setItems((prev) => prev.filter((i) => i.return_id !== returnId));
    setApproving((p) => ({ ...p, [returnId]: true }));
    try {
      await apiFetch(`${BASE}/warehouse/${returnId}/approve`, { method: "POST" });
      showToast("✅ Approved — item listed for resale");
    } catch {
      setItems((prev) => [...prev, item]);
      showToast("Approval failed — try again", "error");
    } finally {
      setApproving((p) => ({ ...p, [returnId]: false }));
    }
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 40 }}>
      <Header onReturnClick={() => {}} />

      {toast && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 999,
          backgroundColor: toast.type === "error" ? "#c0392b" : toast.type === "info" ? "#0056b3" : "#27726b",
          color: "white", padding: "12px 20px", borderRadius: 6, fontSize: 14, fontWeight: 600,
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        }}>
          {toast.msg}
        </div>
      )}

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 24 }}>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, color: "#111" }}>
              🏭 Warehouse Receiving Queue
            </h1>
            <span style={{
              backgroundColor: "#fff3cd", color: "#856404",
              padding: "3px 10px", borderRadius: 12, fontSize: 12, marginLeft: 12, fontWeight: "bold",
            }}>
              {items.length} awaiting inspection
            </span>
          </div>

          {loading && <p style={{ color: "#666", fontSize: 14 }}>Loading queue...</p>}

          {!loading && items.length === 0 && (
            <div style={{ textAlign: "center", padding: "60px 0", color: "#666" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>✅</div>
              <p style={{ fontSize: 16 }}>Warehouse queue is clear.</p>
            </div>
          )}

          {items.map((item) => {
            const gc = GRADE_CONFIG[item.grade] || GRADE_CONFIG["B"];
            const matchCount = buyerMatches[item.return_id];
            const isRegrading = regrading[item.return_id];
            const isScanning = scanning[item.return_id];
            const isApproving = approving[item.return_id];

            return (
              <div key={item.return_id} style={{
                backgroundColor: "white", border: "1px solid #ddd", borderLeft: "4px solid #27726b",
                borderRadius: 4, padding: 20, marginBottom: 16,
                boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: "#111" }}>{item.product_name}</div>
                    <div style={{ fontSize: 12, color: "#767676", marginTop: 2 }}>Return ID: {item.return_id}</div>
                  </div>
                  <span style={{
                    backgroundColor: gc.bg, color: gc.color,
                    padding: "4px 14px", borderRadius: 12, fontSize: 13, fontWeight: 700,
                  }}>
                    Grade {item.grade} — {gc.label}
                  </span>
                </div>

                {item.condition_description && (
                  <div style={{ fontSize: 13, color: "#555", marginBottom: 12, fontStyle: "italic", borderLeft: "3px solid #27726b", paddingLeft: 10 }}>
                    {item.condition_description}
                  </div>
                )}

                {matchCount !== undefined && (
                  <div style={{
                    display: "inline-block",
                    backgroundColor: matchCount > 0 ? "#d4edda" : "#f8f9fa",
                    color: matchCount > 0 ? "#155724" : "#666",
                    padding: "4px 12px", borderRadius: 12, fontSize: 12, fontWeight: 600, marginBottom: 12,
                  }}>
                    {matchCount > 0 ? `✅ ${matchCount} buyer(s) matched nearby` : "⏳ No buyers found yet"}
                  </div>
                )}

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <button
                    onClick={() => handleRegrade(item.return_id)}
                    disabled={isRegrading}
                    style={{
                      padding: "8px 16px", borderRadius: 4, fontSize: 13, fontWeight: 600,
                      cursor: isRegrading ? "not-allowed" : "pointer",
                      backgroundColor: "white", border: "1px solid #27726b", color: "#27726b",
                    }}
                  >
                    {isRegrading ? "⏳ Grading..." : "🔄 Re-grade Item"}
                  </button>
                  <button
                    onClick={() => handleBuyerScan(item.return_id, item.sku_id, item.grade)}
                    disabled={isScanning}
                    style={{
                      padding: "8px 16px", borderRadius: 4, fontSize: 13, fontWeight: 600,
                      cursor: isScanning ? "not-allowed" : "pointer",
                      backgroundColor: "white", border: "1px solid #0056b3", color: "#0056b3",
                    }}
                  >
                    {isScanning ? "⏳ Scanning..." : "🔍 Scan Nearby Buyers"}
                  </button>
                  <button
                    onClick={() => handleApprove(item.return_id)}
                    disabled={isApproving}
                    style={{
                      padding: "8px 20px", borderRadius: 4, fontSize: 13, fontWeight: 700,
                      cursor: isApproving ? "not-allowed" : "pointer",
                      backgroundColor: "#27726b", border: "none", color: "white", marginLeft: "auto",
                    }}
                  >
                    {isApproving ? "Approving..." : "✅ Approve & List for Resale"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
