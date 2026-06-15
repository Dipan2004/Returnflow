import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { products } from "../../data/products";
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

export default function PickupGradingFlow() {
  const { return_id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [step, setStep] = useState(1);
  const [returnData, setReturnData] = useState(null);

  // Step 1: Verify Product state
  const [selectedProductId, setSelectedProductId] = useState("");
  const [verificationImage, setVerificationImage] = useState(null);
  const [verified, setVerified] = useState(false);
  const [mismatch, setMismatch] = useState(false);
  const [verificationDone, setVerificationDone] = useState(false);
  const verifyFileRef = useRef(null);

  // Step 3: Condition photos
  const [previews, setPreviews] = useState([null, null, null]);
  const fileInputRef1 = useRef(null);
  const fileInputRef2 = useRef(null);
  const fileInputRef3 = useRef(null);
  const fileInputRefs = [fileInputRef1, fileInputRef2, fileInputRef3];

  useEffect(() => {
    const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    const found = current.find((r) => r.return_id === return_id);
    if (found) {
      setReturnData(found);
    } else {
      setReturnData({
        return_id: return_id,
        product_name: "Nike Air Max 270",
        sku_id: "1",
        grade: "A",
        address: "Patia, Bhubaneswar, 751024",
      });
    }
  }, [return_id]);

  // Find expected product from products.js
  const expectedProduct = returnData
    ? products.find(
        (p) =>
          p.id.toString() === (returnData.sku_id || "").toString() ||
          p.name === returnData.product_name
      )
    : null;

  // Get top 8 products for selection (same category first)
  const productOptions = (() => {
    if (!expectedProduct) return products.slice(0, 8);
    const sameCategory = products.filter((p) => p.category === expectedProduct.category && p.id !== expectedProduct.id);
    const others = products.filter((p) => p.category !== expectedProduct.category);
    return [expectedProduct, ...sameCategory, ...others].slice(0, 8);
  })();

  function handleVerifyImageChange(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => setVerificationImage(event.target.result);
      reader.readAsDataURL(file);
    }
  }

  function handleVerifyProceed() {
    const selectedId = Number(selectedProductId);
    const isMatch = expectedProduct && selectedId === expectedProduct.id;
    setVerified(true);
    setMismatch(!isMatch);
    setVerificationDone(true);
    setStep(2);
  }

  function handleMismatchProceed() {
    setVerified(true);
    setVerificationDone(true);
    setStep(2);
  }

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
    // Update localStorage for backwards compat
    const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    const updated = current.map((r) => {
      if (r.return_id === return_id) {
        return { ...r, status: "PICKED_UP", grade: returnData.grade || "A" };
      }
      return r;
    });
    localStorage.setItem("returniq_returns", JSON.stringify(updated));

    try {
      await apiFetch(`${BASE}/delivery/${return_id}/confirm`, {
        method: "POST",
        body: JSON.stringify({
          return_id,
          verified,
          mismatch,
          agent_id: user?.name || "agent",
        }),
      });
      alert("✅ Confirmed. Pickup recorded.");
    } catch {
      alert("✅ Pickup recorded locally (offline mode).");
    }

    navigate("/delivery");
  }

  if (!returnData) return null;

  const productName = expectedProduct?.name || returnData.product_name || "Product";
  const productImage = expectedProduct?.image || "https://via.placeholder.com/200x200?text=Product";
  const grade = returnData.grade || "B";
  const isPhotosUploaded = previews.every((p) => p !== null);

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

              {/* Expected product display */}
              <div style={{ display: "flex", gap: 16, marginBottom: 20, backgroundColor: "#fafafa", padding: 12, borderRadius: 4, border: "1px solid #eee" }}>
                <img src={productImage} alt={productName} style={{ width: 80, height: 80, objectFit: "contain", border: "1px solid #ddd", borderRadius: 4 }} />
                <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                  <strong>Expected Item:</strong> {productName}
                  <br />
                  <strong>Return ID:</strong> {return_id}
                  <br />
                  <span style={{ color: "#565959" }}>Confirm this is the item you are collecting</span>
                </div>
              </div>

              {/* Product selection dropdown */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  Select the product you see physically:
                </label>
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", border: "1px solid #ccc", borderRadius: 4, fontSize: 14 }}
                >
                  <option value="">-- Select product --</option>
                  {productOptions.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} ({p.brand})</option>
                  ))}
                </select>
              </div>

              {/* Verification image */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
                  Take one photo of the item:
                </label>
                <div
                  onClick={() => verifyFileRef.current.click()}
                  style={{
                    width: "100%", height: 160,
                    border: "2px dashed #aaa", borderRadius: 8,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    cursor: "pointer", backgroundColor: "#fcfcfc", overflow: "hidden",
                    position: "relative",
                  }}
                >
                  {verificationImage ? (
                    <img src={verificationImage} alt="Verification" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                  ) : (
                    <div style={{ textAlign: "center", color: "#666" }}>
                      <span style={{ fontSize: 28 }}>📷</span>
                      <p style={{ margin: "4px 0 0 0", fontSize: 12 }}>Click to capture / upload</p>
                    </div>
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    ref={verifyFileRef}
                    onChange={handleVerifyImageChange}
                    style={{ display: "none" }}
                  />
                </div>
              </div>

              {/* Verify button */}
              <button
                disabled={!selectedProductId || !verificationImage}
                onClick={handleVerifyProceed}
                style={{
                  width: "100%",
                  backgroundColor: selectedProductId && verificationImage ? "#27726b" : "#e7e9ec",
                  border: "none",
                  color: selectedProductId && verificationImage ? "white" : "#888",
                  padding: "12px 0",
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: "bold",
                  cursor: selectedProductId && verificationImage ? "pointer" : "not-allowed",
                }}
              >
                Verify & Proceed
              </button>
            </div>
          )}

          {/* Mismatch confirmation (shown inline if mismatch detected) */}
          {step === 2 && mismatch && !verificationDone && (
            <div style={{ backgroundColor: "#fff3cd", border: "1px solid #ffeeba", padding: 16, borderRadius: 4, marginBottom: 16 }}>
              <p style={{ fontSize: 13, color: "#856404", margin: "0 0 12px 0" }}>
                ⚠️ Product mismatch detected. The item you selected does not match the return order. Do you want to proceed anyway?
              </p>
              <button
                onClick={handleMismatchProceed}
                style={{
                  backgroundColor: "#ffa41c", border: "1px solid #ff9900",
                  color: "#111", padding: "8px 20px", borderRadius: 4,
                  fontSize: 13, fontWeight: 600, cursor: "pointer",
                }}
              >
                Proceed Anyway
              </button>
            </div>
          )}

          {/* STEP 2: AI Grade Display */}
          {step === 2 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>AI Grade Result</h2>

              {/* Verification status */}
              <div style={{
                backgroundColor: mismatch ? "#fff3cd" : "#d4edda",
                border: `1px solid ${mismatch ? "#ffeeba" : "#c3e6cb"}`,
                padding: 10, borderRadius: 4, marginBottom: 16, fontSize: 13,
                color: mismatch ? "#856404" : "#155724",
              }}>
                {mismatch ? "⚠️ Product mismatch flagged – proceeding with collection" : "✅ Product verified successfully"}
              </div>

              <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 20 }}>
                <div style={{
                  width: 64, height: 64, borderRadius: "50%",
                  backgroundColor: GRADE_COLORS[grade] || "#767676",
                  color: "white", display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 24, fontWeight: "bold",
                }}>
                  {grade}
                </div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: "bold" }}>Grade {grade} Assessed</div>
                  <div style={{ fontSize: 12, color: "#666" }}>AI-verified condition grade</div>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => setStep(3)}
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

          {/* STEP 3: Condition Photos */}
          {step === 3 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 8px 0" }}>Capture Condition Photos</h2>
              <p style={{ fontSize: 13, color: "#666", margin: "0 0 16px 0" }}>
                Take 3 photos: front, back, and damage area (if any).
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
                      type="file"
                      accept="image/*"
                      capture="environment"
                      ref={fileInputRefs[idx]}
                      onChange={(e) => handleConditionPhoto(idx, e)}
                      style={{ display: "none" }}
                    />
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <button
                  onClick={() => setStep(2)}
                  style={{ backgroundColor: "white", border: "1px solid #aaa", padding: "8px 24px", borderRadius: 4, fontSize: 14, cursor: "pointer" }}
                >
                  Back
                </button>
                <button
                  disabled={!isPhotosUploaded}
                  onClick={() => setStep(4)}
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

          {/* STEP 4: Confirm Pickup */}
          {step === 4 && (
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>Confirm Collection</h2>

              {/* Summary */}
              <div style={{ backgroundColor: "#fafafa", border: "1px solid #eee", borderRadius: 4, padding: 16, marginBottom: 20, fontSize: 13, lineHeight: 1.6 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span>{mismatch ? "⚠️" : "✅"}</span>
                  <strong>Product Verification:</strong>
                  <span style={{ color: mismatch ? "#856404" : "#155724" }}>
                    {mismatch ? "Mismatch flagged" : "Verified"}
                  </span>
                </div>
                <div style={{ marginBottom: 6 }}>
                  <strong>Grade:</strong>{" "}
                  <span style={{ backgroundColor: GRADE_COLORS[grade] || "#767676", color: "white", padding: "2px 8px", borderRadius: 10, fontSize: 11, fontWeight: "bold" }}>
                    Grade {grade}
                  </span>
                </div>
                <div>
                  <strong>📍 Address:</strong> {returnData.address || "Patia, Bhubaneswar, 751024"}
                </div>
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
