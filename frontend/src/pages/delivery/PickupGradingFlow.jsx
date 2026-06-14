import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Header from "../../components/layout/Header";

const CATALOG_IMAGES = {
  "Nike Air Max 270": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&fit=crop&auto=format",
  "boAt Rockerz 450": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&fit=crop&auto=format",
  "Puma T-Shirt": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=400&fit=crop&auto=format",
};

export default function PickupGradingFlow() {
  const { return_id } = useParams();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [returnData, setReturnData] = useState(null);

  // Step 1: Verify state
  const [matchesOrder, setMatchesOrder] = useState(null); // yes, no
  const [flaggedMismatch, setFlaggedMismatch] = useState(false);

  // Step 2: Photos state
  const [previews, setPreviews] = useState([null, null, null]);
  const fileInputRef1 = useRef(null);
  const fileInputRef2 = useRef(null);
  const fileInputRef3 = useRef(null);
  const fileInputRefs = [fileInputRef1, fileInputRef2, fileInputRef3];

  // Step 3: Spinner state
  const [analysisMsgIndex, setAnalysisMsgIndex] = useState(0);

  // Step 4: Grading state
  const [confidenceRate, setConfidenceRate] = useState(91.2); // Default to High

  useEffect(() => {
    // Load matching return from local storage
    const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    const found = current.find((r) => r.return_id === return_id);
    if (found) {
      setReturnData(found);
    } else {
      // Fallback fallback return
      setReturnData({
        return_id: return_id,
        product_name: "Nike Air Max 270",
        order_id: "#402-1234567",
        customer_name: "Archi",
        pickup_window: "Tomorrow, 10 AM – 2 PM",
        mrp: 850,
      });
    }
  }, [return_id]);

  // Step 3 auto-advance
  useEffect(() => {
    if (step !== 3) return;
    const t1 = setTimeout(() => setAnalysisMsgIndex(1), 1000);
    const t2 = setTimeout(() => {
      setStep(4);
    }, 2200);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [step]);

  function handleFileChange(index, e) {
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
    if (fileInputRefs[index].current) {
      fileInputRefs[index].current.value = "";
    }
  }

  function handleConfirmPickup() {
    const isHighConf = confidenceRate >= 87;

    // Update return status in storage
    const current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    const updated = current.map((r) => {
      if (r.return_id === return_id) {
        return {
          ...r,
          status: isHighConf ? "P2P_MATCHED" : "PENDING_HUMAN_REVIEW",
          grade: "A",
          recovery_value: 552,
          value_delta: 510,
          route: "P2P",
          route_reason: "Buyer 2.3km away has this SKU on wishlist",
          damage_description: "Minor surface scratch on toe box area. Clean soles.",
        };
      }
      return r;
    });
    localStorage.setItem("returniq_returns", JSON.stringify(updated));

    // Update picked statistics for courier agent
    const todayStats = JSON.parse(localStorage.getItem("returniq_delivery_stats") || '{"pickups":0,"graded":0,"flagged":0}');
    todayStats.pickups += 1;
    todayStats.graded += 1;
    if (flaggedMismatch) todayStats.flagged += 1;
    localStorage.setItem("returniq_delivery_stats", JSON.stringify(todayStats));

    // Fire simulated buyer & customer notifications
    if (isHighConf) {
      localStorage.setItem(
        "returniq_notification",
        JSON.stringify({
          visible: true,
          message: "Your Nike Air Max 270 return has been assessed as Grade A. A refund of ₹552 has been initiated.",
        })
      );
    }

    alert(
      isHighConf
        ? "✓ Item collected. Buyer matched & notified."
        : "✓ Item collected. Sent to manual review."
    );
    navigate("/delivery");
  }

  if (!returnData) return null;

  const productImg = CATALOG_IMAGES[returnData.product_name] || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&fit=crop&auto=format";
  const isPhotosUploaded = previews.every((p) => p !== null);

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 60 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div
          style={{
            maxWidth: 600,
            margin: "0 auto",
            backgroundColor: "white",
            border: "1px solid #ddd",
            borderRadius: 4,
            padding: 24,
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          }}
        >
          {/* Header */}
          <div style={{ borderBottom: "1px solid #eee", paddingBottom: 12, marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 11, color: "#767676", textTransform: "uppercase" }}>Pickup & Grading Flow</span>
              <h1 style={{ fontSize: 20, margin: "2px 0 0 0", color: "#111" }}>{returnData.product_name}</h1>
            </div>
            <span style={{ fontSize: 13, color: "#565959" }}>Step {step} of 4</span>
          </div>

          {/* STEP 1: Verify Checklist */}
          {step === 1 && (
            <div>
              <div style={{ display: "flex", gap: 16, marginBottom: 20, backgroundColor: "#fafafa", padding: 12, borderRadius: 4, border: "1px solid #eee" }}>
                <img src={productImg} alt={returnData.product_name} style={{ width: 80, height: 80, objectFit: "contain", border: "1px solid #ddd", borderRadius: 4 }} />
                <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                  <strong>Expected Item:</strong> {returnData.product_name} <br />
                  <strong>Order ID:</strong> {returnData.order_id || "#402-1234567"} <br />
                  <strong>Customer Name:</strong> {returnData.customer_name || "Archi"}
                </div>
              </div>

              <div style={{ marginBottom: 24 }}>
                <p style={{ fontSize: 14, fontWeight: "bold", margin: "0 0 12px 0" }}>
                  Confirm the item matches the order details:
                </p>
                <div style={{ display: "flex", gap: 12 }}>
                  <button
                    onClick={() => {
                      setMatchesOrder(true);
                      setFlaggedMismatch(false);
                    }}
                    style={{
                      flex: 1,
                      padding: 12,
                      border: matchesOrder === true ? "2px solid #27726b" : "1px solid #aaa",
                      backgroundColor: matchesOrder === true ? "#f0faf8" : "white",
                      color: matchesOrder === true ? "#27726b" : "#333",
                      borderRadius: 4,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer",
                      outline: "none",
                    }}
                  >
                    Yes, matches
                  </button>
                  <button
                    onClick={() => {
                      setMatchesOrder(false);
                      setFlaggedMismatch(true);
                    }}
                    style={{
                      flex: 1,
                      padding: 12,
                      border: matchesOrder === false ? "2px solid #c0392b" : "1px solid #aaa",
                      backgroundColor: matchesOrder === false ? "#fff5f5" : "white",
                      color: matchesOrder === false ? "#c0392b" : "#333",
                      borderRadius: 4,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer",
                      outline: "none",
                    }}
                  >
                    No, item mismatch
                  </button>
                </div>
              </div>

              {flaggedMismatch && (
                <div style={{ backgroundColor: "#fff3cd", border: "1px solid #ffeeba", padding: 12, borderRadius: 4, fontSize: 13, color: "#856404", marginBottom: 24 }}>
                  ⚠️ Mismatch flagged. The item will be routed for manual review at the warehouse, but you will still proceed with physical collection.
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  disabled={matchesOrder === null}
                  onClick={() => setStep(2)}
                  style={{
                    backgroundColor: matchesOrder !== null ? "#ffa41c" : "#e7e9ec",
                    border: `1px solid ${matchesOrder !== null ? "#ff9900" : "#adb1b8"}`,
                    color: matchesOrder !== null ? "#111" : "#888",
                    padding: "8px 24px",
                    borderRadius: 4,
                    fontSize: 14,
                    cursor: matchesOrder !== null ? "pointer" : "not-allowed",
                    fontWeight: 600,
                  }}
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Take Photos */}
          {step === 2 && (
            <div>
              <p style={{ fontSize: 13, color: "#666", margin: "0 0 16px 0" }}>
                Capture required photos. Open mobile camera or drop files.
              </p>

              <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
                {[0, 1, 2].map((idx) => (
                  <div
                    key={idx}
                    onClick={() => fileInputRefs[idx].current.click()}
                    style={{
                      flex: 1,
                      height: 140,
                      border: "2px dashed #aaa",
                      borderRadius: 6,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      cursor: "pointer",
                      position: "relative",
                      overflow: "hidden",
                      backgroundColor: "#fcfcfc",
                    }}
                  >
                    {previews[idx] ? (
                      <>
                        <img src={previews[idx]} alt="Preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                        <button
                          onClick={(e) => handleRemovePhoto(idx, e)}
                          style={{
                            position: "absolute",
                            top: 4,
                            right: 4,
                            width: 18,
                            height: 18,
                            borderRadius: "50%",
                            backgroundColor: "rgba(0,0,0,0.6)",
                            color: "white",
                            border: "none",
                            fontSize: 11,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          &times;
                        </button>
                      </>
                    ) : (
                      <div style={{ textAlign: "center", padding: 6 }}>
                        <span style={{ fontSize: 22 }}>📷</span>
                        <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "#666" }}>
                          {idx === 0 ? "Front" : idx === 1 ? "Back" : "Damage area"}
                        </p>
                      </div>
                    )}
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      ref={fileInputRefs[idx]}
                      onChange={(e) => handleFileChange(idx, e)}
                      style={{ display: "none" }}
                    />
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <button
                  onClick={() => setStep(1)}
                  style={{
                    backgroundColor: "white",
                    border: "1px solid #aaa",
                    padding: "8px 24px",
                    borderRadius: 4,
                    fontSize: 14,
                    cursor: "pointer",
                  }}
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
                    padding: "8px 24px",
                    borderRadius: 4,
                    fontSize: 14,
                    cursor: isPhotosUploaded ? "pointer" : "not-allowed",
                    fontWeight: 600,
                  }}
                >
                  Submit for Grading
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Grading in Progress */}
          {step === 3 && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 0" }}>
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
                alt="Amazon"
                style={{ width: 90, marginBottom: 20 }}
              />
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: "50%",
                  border: "4px solid #f3f3f3",
                  borderTopColor: "#27726b",
                  animation: "spin 1s linear infinite",
                  marginBottom: 20,
                }}
              />
              <p style={{ fontSize: 15, color: "#111", fontWeight: 500, textAlign: "center" }}>
                {analysisMsgIndex === 0
                  ? "Analysing with Amazon Rekognition..."
                  : "Generating damage description with Amazon Bedrock..."}
              </p>
            </div>
          )}

          {/* STEP 4: Grading Result */}
          {step === 4 && (
            <div>
              {/* Mock Control for confidence rate toggle */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#f9f9f9", padding: "8px 12px", border: "1px solid #ddd", borderRadius: 4, marginBottom: 16 }}>
                <span style={{ fontSize: 12, color: "#666" }}>Mock AI confidence:</span>
                <div>
                  <button
                    onClick={() => setConfidenceRate(91.2)}
                    style={{
                      padding: "4px 8px",
                      fontSize: 11,
                      backgroundColor: confidenceRate >= 87 ? "#27726b" : "white",
                      color: confidenceRate >= 87 ? "white" : "#333",
                      border: "1px solid #ccc",
                      borderRadius: "4px 0 0 4px",
                      cursor: "pointer",
                    }}
                  >
                    High (91%)
                  </button>
                  <button
                    onClick={() => setConfidenceRate(74.5)}
                    style={{
                      padding: "4px 8px",
                      fontSize: 11,
                      backgroundColor: confidenceRate < 87 ? "#27726b" : "white",
                      color: confidenceRate < 87 ? "white" : "#333",
                      border: "1px solid #ccc",
                      borderRadius: "0 4px 4px 0",
                      cursor: "pointer",
                    }}
                  >
                    Low (74%)
                  </button>
                </div>
              </div>

              <div style={{ display: "flex", gap: 16, flexDirection: "column", marginBottom: 24 }}>
                <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                  <div
                    style={{
                      width: 64,
                      height: 64,
                      borderRadius: "50%",
                      backgroundColor: "#d4edda",
                      color: "#2d7a4f",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 24,
                      fontWeight: "bold",
                    }}
                  >
                    A
                  </div>
                  <div>
                    <div style={{ fontSize: 15, fontWeight: "bold" }}>Grade A Assessed</div>
                    <div style={{ fontSize: 12, color: "#666" }}>Confidence Rate: {confidenceRate}%</div>
                  </div>
                </div>

                <blockquote style={{ margin: 0, padding: 12, backgroundColor: "#fafafa", borderLeft: "3px solid #27726b", fontSize: 13, color: "#555", fontStyle: "italic" }}>
                  Minor surface scratch detected on toe box. Soles are clean and unworn. Structural integrity intact.
                </blockquote>

                <div style={{ display: "flex", gap: 6 }}>
                  <span style={{ fontSize: 11, backgroundColor: "#eee", padding: "2px 8px", borderRadius: 10 }}>Scratch (82%)</span>
                  <span style={{ fontSize: 11, backgroundColor: "#eee", padding: "2px 8px", borderRadius: 10 }}>Clean Sole (94%)</span>
                </div>
              </div>

              {/* OUTCOMES DECISION */}
              {confidenceRate >= 87 ? (
                /* High confidence Outcome */
                <div style={{ border: "1px solid #bce1dd", backgroundColor: "#f0faf8", padding: 16, borderRadius: 6, marginBottom: 24 }}>
                  <div style={{ fontSize: 11, color: "#27726b", textTransform: "uppercase", fontWeight: "bold" }}>AI Recommendation</div>
                  <div style={{ fontSize: 16, fontWeight: "bold", color: "#27726b", margin: "4px 0" }}>🔁 P2P Match found</div>
                  <p style={{ margin: "0 0 12px 0", fontSize: 12, color: "#555", lineHeight: 1.3 }}>
                    Buyer 2.3km away has this item on wishlist. Recovery: ₹552 vs baseline ₹42.
                  </p>
                  <button
                    onClick={handleConfirmPickup}
                    style={{
                      width: "100%",
                      backgroundColor: "#27726b",
                      border: "none",
                      color: "white",
                      padding: "10px 0",
                      borderRadius: 4,
                      fontSize: 14,
                      fontWeight: "bold",
                      cursor: "pointer",
                    }}
                  >
                    Confirm Pickup
                  </button>
                </div>
              ) : (
                /* Low confidence Outcome */
                <div style={{ border: "1px solid #f5c6cb", backgroundColor: "#f8d7da", padding: 16, borderRadius: 6, marginBottom: 24 }}>
                  <div style={{ fontSize: 11, color: "#721c24", textTransform: "uppercase", fontWeight: "bold" }}>AI Status</div>
                  <div style={{ fontSize: 16, fontWeight: "bold", color: "#721c24", margin: "4px 0" }}>⚠️ Low Confidence Escalation</div>
                  <p style={{ margin: "0 0 12px 0", fontSize: 12, color: "#721c24", lineHeight: 1.3 }}>
                    Confidence rate ({confidenceRate}%) below the 87% threshold. Sent to manual review.
                  </p>
                  <button
                    onClick={handleConfirmPickup}
                    style={{
                      width: "100%",
                      backgroundColor: "#c0392b",
                      border: "none",
                      color: "white",
                      padding: "10px 0",
                      borderRadius: 4,
                      fontSize: 14,
                      fontWeight: "bold",
                      cursor: "pointer",
                    }}
                  >
                    Confirm Pickup anyway
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
