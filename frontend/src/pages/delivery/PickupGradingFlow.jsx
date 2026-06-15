import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
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

const GRADE_BG = { A: "#d4edda", B: "#fff3cd", C: "#f8d7da", D: "#f5c6cb" };
const GRADE_COLOR = { A: "#155724", B: "#856404", C: "#721c24", D: "#721c24" };

export default function PickupGradingFlow() {
  const { return_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState(1);
  const [returnData, setReturnData] = useState(null);

  // Step 1: Verify state
  const [selectedProduct, setSelectedProduct] = useState("");
  const [matchesOrder, setMatchesOrder] = useState(null);
  const [flaggedMismatch, setFlaggedMismatch] = useState(false);
  const [verifyPhotoPreview, setVerifyPhotoPreview] = useState(null);
  const verifyPhotoRef = useRef(null);

  // Step 2: Condition photos
  const [previews, setPreviews] = useState([null, null, null]);
  const fileInputRef1 = useRef(null);
  const fileInputRef2 = useRef(null);
  const fileInputRef3 = useRef(null);
  const fileInputRefs = [fileInputRef1, fileInputRef2, fileInputRef3];

  // Load return data: router state > API > localStorage > fallback
  useEffect(() => {
    if (location.state?.returnData) {
      setReturnData(location.state.returnData);
      return;
    }
    async function fetchReturn() {
      try {
        const data = await apiFetch(`${BASE}/delivery/queue`);
        const found = data.find((r) => r.return_id === return_id);
        if (found) {
          setReturnData({
            return_id: found.return_id,
            product_name: found.product_name,
            sku_id: found.sku_id,
            grade: found.grade,
            pickup_address: found.pickup_address,
            pickup_window: found.pickup_window,
          });
          return;
        }
      } catch {}
      const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
      const found = current.find((r) => r.return_id === return_id);
      if (found) {
        setReturnData(found);
        return;
      }
      setReturnData({
        return_id: return_id,
        product_name: "Product",
        grade: "B",
        pickup_address: "Customer Address",
        pickup_window: "Tomorrow, 10 AM – 2 PM",
      });
    }
    fetchReturn();
  }, [return_id, location.state]);

  // Auto-detect mismatch from product selector
  useEffect(() => {
    if (!selectedProduct || !returnData) return;
    const matches = selectedProduct === returnData.product_name;
    setMatchesOrder(matches);
    setFlaggedMismatch(!matches);
  }, [selectedProduct, returnData]);

  function handleConditionPhoto(index, e) {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviews((prev) => {
        const next = [...prev];
        next[index] = url;
        return next;
      });
    }
  }

  function handleRemovePhoto(index, e) {
    e.stopPropagation();
    setPreviews((prev) => {
      const next = [...prev];
      next[index] = null;
      return next;
    });
    if (fileInputRefs[index].current) fileInputRefs[index].current.value = "";
  }

  async function handleConfirmPickup() {
    try {
      await apiFetch(`${BASE}/delivery/${return_id}/confirm`, {
        method: "POST",
        body: JSON.stringify({
          return_id,
          verified: matchesOrder,
          mismatch: flaggedMismatch,
          agent_id: "agent1",
          product_name: returnData?.product_name,
          sku_id: returnData?.sku_id,
        }),
      });
    } catch {
      console.warn("Pickup confirm API failed — local only");
    }
    const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    const updated = current.map((r) =>
      r.return_id === return_id ? { ...r, status: "PICKED_UP" } : r
    );
    localStorage.setItem("returniq_returns", JSON.stringify(updated));
    const todayStats = JSON.parse(
      localStorage.getItem("returniq_delivery_stats") || '{"pickups":0,"graded":0,"flagged":0}'
    );
    todayStats.pickups += 1;
    todayStats.graded += 1;
    if (flaggedMismatch) todayStats.flagged += 1;
    localStorage.setItem("returniq_delivery_stats", JSON.stringify(todayStats));
    navigate("/delivery");
  }

  if (!returnData) return null;

  const productName = returnData.product_name || "Product";
  const displayGrade = returnData.grade || "B";
  const isPhotosUploaded = previews.some((p) => p !== null);

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 60 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{
          maxWidth: 600, margin: "0 auto", backgroundColor: "white",
          border: "1px solid #ddd", borderRadius: 4, padding: 24,
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}>
          {/* Header */}
          <div style={{ borderBottom: "1px solid #eee", paddingBottom: 12, marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 11, color: "#767676", textTransform: "uppercase" }}>Pickup & Verification Flow</span>
              <h1 style={{ fontSize: 20, margin: "2px 0 0 0", color: "#111" }}>{productName}</h1>
            </div>
            <span style={{ fontSize: 13, color: "#565959" }}>Step {step} of 4</span>
          </div>

          {/* STEP 1: Verify Product */}
          {step === 1 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>Verify Product Identity</h2>

              <div style={{ display: "flex", gap: 16, marginBottom: 20, backgroundColor: "#fafafa", padding: 12, borderRadius: 4, border: "1px solid #eee" }}>
                <div style={{ width: 60, height: 60, backgroundColor: "#eee", borderRadius: 4, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24 }}>📦</div>
                <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                  <strong>Expected:</strong> {productName}<br />
                  <strong>Return ID:</strong> {return_id}<br />
                  <span style={{ color: "#565959" }}>Confirm this is the item you are collecting</span>
                </div>
              </div>

              {/* Product selector */}
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  Select the product you physically see:
                </label>
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  style={{ width: "100%", padding: "8px 12px", border: "1px solid #aaa", borderRadius: 4, fontSize: 14 }}
                >
                  <option value="">-- Select product --</option>
                  <option value={productName}>{productName}</option>
                  <option value="Nike Air Max 270">Nike Air Max 270</option>
                  <option value="boAt Rockerz 450">boAt Rockerz 450</option>
                  <option value="Puma RS-X Reinvention">Puma RS-X Reinvention</option>
                  <option value="Sony WH-1000XM5">Sony WH-1000XM5</option>
                  <option value="Adidas Ultraboost 22">Adidas Ultraboost 22</option>
                  <option value="Other / Different item">Other / Different item</option>
                </select>
              </div>

              {/* Verification result */}
              {selectedProduct && (
                <div style={{
                  backgroundColor: flaggedMismatch ? "#fff3cd" : "#d4edda",
                  border: `1px solid ${flaggedMismatch ? "#ffeeba" : "#c3e6cb"}`,
                  padding: 10, borderRadius: 4, marginBottom: 16, fontSize: 13,
                  color: flaggedMismatch ? "#856404" : "#155724",
                }}>
                  {flaggedMismatch
                    ? "⚠️ Product mismatch detected — you can still proceed"
                    : "✅ Product verified — matches expected item"}
                </div>
              )}

              {/* Single verification photo */}
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  📷 Take one photo of the item:
                </label>
                <div
                  onClick={() => verifyPhotoRef.current.click()}
                  style={{
                    height: 120, border: "2px dashed #aaa", borderRadius: 6,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    cursor: "pointer", backgroundColor: "#fafafa", overflow: "hidden",
                  }}
                >
                  {verifyPhotoPreview
                    ? <img src={verifyPhotoPreview} alt="Verify" style={{ height: "100%", objectFit: "cover" }} />
                    : <span style={{ color: "#888", fontSize: 13 }}>Click to open camera or upload</span>
                  }
                  <input
                    type="file" accept="image/*" capture="environment"
                    ref={verifyPhotoRef} style={{ display: "none" }}
                    onChange={(e) => {
                      const f = e.target.files[0];
                      if (f) setVerifyPhotoPreview(URL.createObjectURL(f));
                    }}
                  />
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  disabled={!selectedProduct}
                  onClick={() => setStep(2)}
                  style={{
                    backgroundColor: selectedProduct ? "#ffa41c" : "#e7e9ec",
                    border: `1px solid ${selectedProduct ? "#ff9900" : "#adb1b8"}`,
                    color: selectedProduct ? "#111" : "#888",
                    padding: "8px 24px", borderRadius: 4,
                    fontSize: 14, fontWeight: 600,
                    cursor: selectedProduct ? "pointer" : "not-allowed",
                  }}
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Condition Photos */}
          {step === 2 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 8px 0" }}>Capture Condition Photos</h2>
              <p style={{ fontSize: 13, color: "#666", margin: "0 0 16px 0" }}>
                Upload at least 1 photo: front, back, or damage area.
              </p>

              <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
                {[0, 1, 2].map((idx) => (
                  <div
                    key={idx}
                    onClick={() => fileInputRefs[idx].current.click()}
                    style={{
                      flex: 1, height: 140,
                      border: "2px dashed #aaa", borderRadius: 6,
                      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                      cursor: "pointer", position: "relative", overflow: "hidden", backgroundColor: "#fcfcfc",
                    }}
                  >
                    {previews[idx] ? (
                      <>
                        <img src={previews[idx]} alt="Preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                        <button
                          onClick={(e) => handleRemovePhoto(idx, e)}
                          style={{
                            position: "absolute", top: 4, right: 4,
                            width: 18, height: 18, borderRadius: "50%",
                            backgroundColor: "rgba(0,0,0,0.6)", color: "white",
                            border: "none", fontSize: 11, display: "flex",
                            alignItems: "center", justifyContent: "center", cursor: "pointer",
                          }}
                        >
                          &times;
                        </button>
                      </>
                    ) : (
                      <div style={{ textAlign: "center", padding: 6 }}>
                        <span style={{ fontSize: 22 }}>📷</span>
                        <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "#666" }}>
                          {idx === 0 ? "Front" : idx === 1 ? "Back" : "Damage"}
                        </p>
                      </div>
                    )}
                    <input
                      type="file" accept="image/*" capture="environment"
                      ref={fileInputRefs[idx]}
                      onChange={(e) => handleConditionPhoto(idx, e)}
                      style={{ display: "none" }}
                    />
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <button
                  onClick={() => setStep(1)}
                  style={{ backgroundColor: "white", border: "1px solid #aaa", padding: "8px 24px", borderRadius: 4, fontSize: 14, cursor: "pointer" }}
                >
                  Back
                </button>
                <button
                  disabled={!isPhotosUploaded}
                  onClick={() => setStep(3)}
                  style={{
                    backgroundColor: isPhotosUploaded ? "#ffa41c" : "#e7e9ec",
                    border: `1px solid ${isPhotosUploaded ? "#ff9900" : "#adb1b8"}`,
                    color: isPhotosUploaded ? "#111" : "#888",
                    padding: "8px 24px", borderRadius: 4,
                    fontSize: 14, fontWeight: 600,
                    cursor: isPhotosUploaded ? "pointer" : "not-allowed",
                  }}
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Grade Display */}
          {step === 3 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>AI Grade Result</h2>

              <div style={{
                backgroundColor: flaggedMismatch ? "#fff3cd" : "#d4edda",
                border: `1px solid ${flaggedMismatch ? "#ffeeba" : "#c3e6cb"}`,
                padding: 10, borderRadius: 4, marginBottom: 16, fontSize: 13,
                color: flaggedMismatch ? "#856404" : "#155724",
              }}>
                {flaggedMismatch ? "⚠️ Product mismatch flagged" : "✅ Product verified"}
              </div>

              <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 20 }}>
                <div style={{
                  width: 64, height: 64, borderRadius: "50%",
                  backgroundColor: GRADE_BG[displayGrade] || "#eee",
                  color: GRADE_COLOR[displayGrade] || "#333",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 24, fontWeight: "bold",
                }}>
                  {displayGrade}
                </div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: "bold" }}>Grade {displayGrade} Assessed</div>
                  <div style={{ fontSize: 12, color: "#666" }}>AI-verified condition grade</div>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <button
                  onClick={() => setStep(2)}
                  style={{ backgroundColor: "white", border: "1px solid #aaa", padding: "8px 24px", borderRadius: 4, fontSize: 14, cursor: "pointer" }}
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(4)}
                  style={{
                    backgroundColor: "#ffa41c", border: "1px solid #ff9900",
                    color: "#111", padding: "8px 24px", borderRadius: 4,
                    fontSize: 14, fontWeight: 600, cursor: "pointer",
                  }}
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Confirm Pickup */}
          {step === 4 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>Confirm Collection</h2>

              <div style={{ backgroundColor: "#fafafa", border: "1px solid #eee", borderRadius: 4, padding: 16, marginBottom: 20, fontSize: 13, lineHeight: 1.6 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span>{flaggedMismatch ? "⚠️" : "✅"}</span>
                  <strong>Verification:</strong>
                  <span style={{ color: flaggedMismatch ? "#856404" : "#155724" }}>
                    {flaggedMismatch ? "Mismatch flagged" : "Verified"}
                  </span>
                </div>
                <div style={{ marginBottom: 6 }}>
                  <strong>Grade:</strong>{" "}
                  <span style={{
                    backgroundColor: GRADE_BG[displayGrade] || "#eee",
                    color: GRADE_COLOR[displayGrade] || "#333",
                    padding: "2px 8px", borderRadius: 10, fontSize: 11, fontWeight: "bold",
                  }}>
                    Grade {displayGrade}
                  </span>
                </div>
                <div><strong>📍 Address:</strong> {returnData.pickup_address || "Patia, Bhubaneswar, 751024"}</div>
              </div>

              <div style={{ border: "1px solid #bce1dd", backgroundColor: "#f0faf8", padding: 16, borderRadius: 6, marginBottom: 20 }}>
                <div style={{ fontSize: 11, color: "#27726b", textTransform: "uppercase", fontWeight: "bold" }}>Status</div>
                <div style={{ fontSize: 15, fontWeight: "bold", color: "#27726b", margin: "4px 0" }}>✅ Ready for collection</div>
                <p style={{ margin: 0, fontSize: 12, color: "#555" }}>
                  Item graded and ready for warehouse processing.
                </p>
              </div>

              <button
                onClick={handleConfirmPickup}
                style={{
                  width: "100%",
                  backgroundColor: "#27726b",
                  border: "none",
                  color: "white",
                  padding: "12px 0",
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: "bold",
                  cursor: "pointer",
                }}
              >
                📦 PICKED UP — Confirm Collection
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
