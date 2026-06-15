import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

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

export default function ReturnFlowPage() {
  const { orderId } = useParams();
  const { orders, initiateReturn } = useCart();
  const navigate = useNavigate();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [step, setStep] = useState(1);

  // Return wizard state
  const [reason, setReason] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [photoUploaded, setPhotoUploaded] = useState(false);

  // Four product angles
  const [leftImage, setLeftImage] = useState(null);
  const [rightImage, setRightImage] = useState(null);
  const [topImage, setTopImage] = useState(null);
  const [bottomImage, setBottomImage] = useState(null);

  const handleFileChange = (e, angle) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (angle === "left") setLeftImage(event.target.result);
        if (angle === "right") setRightImage(event.target.result);
        if (angle === "top") setTopImage(event.target.result);
        if (angle === "bottom") setBottomImage(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Find order
  const order = orders.find((o) => o.orderId === orderId) || orders[0];
  const product = order ? products.find((p) => p.id === order.productId) : null;

  // AI Grading Outcome Mock (Dynamic based on product and random/reason)
  const [gradeOutcome, setGradeOutcome] = useState({
    grade: "A",
    recoveryValue: 0,
    carbonAvoided: 2.3,
    route: "Standard Return"
  });

  // API integration state
  const [returnId, setReturnId] = useState(null);
  const [apiGrade, setApiGrade] = useState(null);
  const [apiError, setApiError] = useState(null);

  useEffect(() => {
    if (product) {
      const basePrice = product.price;
      const g = apiGrade ? apiGrade.grade : (reason === "Item damaged" ? "C" : reason === "Performance not met" ? "B" : "A");
      const recoveryMultiplier = { A: 1.0, B: 0.85, C: 0.70, D: 0.0 }[g] || 0.70;
      const co2 = { A: 2.3, B: 1.8, C: 1.2, D: 0.0 }[g] || 1.8;

      setGradeOutcome({
        grade: g,
        recoveryValue: Math.floor(basePrice * recoveryMultiplier),
        carbonAvoided: co2,
        route: "P2P Resell Match"
      });
    }
  }, [reason, product, apiGrade]);

  if (!order || !product) {
    return (
      <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
        <Header />
        <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div style={{ maxWidth: "600px", margin: "40px auto", padding: "30px", backgroundColor: "white", borderRadius: "4px", textAlign: "center" }}>
          <h2>Order Not Found</h2>
          <p>We couldn't locate the order details for ID {orderId}.</p>
          <Link to="/orders">Back to Orders</Link>
        </div>
      </div>
    );
  }

  // Simulation scanning action
  const handleSimulateScan = async () => {
    setIsScanning(true);
    setScanProgress(0);
    setApiError(null);

    // Step 1: Create return via API (before animation)
    let createdReturnId = null;
    try {
      const imageCount = [leftImage, rightImage, topImage, bottomImage].filter(Boolean).length;
      const user = JSON.parse(localStorage.getItem("returniq_user") || "{}");
      const returnResp = await apiFetch(`${BASE}/returns`, {
        method: "POST",
        body: JSON.stringify({
          sku_id: product.id.toString(),
          seller_id: "seller-001",
          buyer_id: user.name || user.username || "customer-001",
          image_count: imageCount,
          reason: reason,
          product_name: product.name,
          original_price: product.price,
        }),
      });
      createdReturnId = returnResp.return_id;
      setReturnId(createdReturnId);
    } catch (err) {
      setApiError("AI grading offline \u2013 using estimated grade");
    }

    // Run progress animation
    const interval = setInterval(() => {
      setScanProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Wait for animation to complete (~2s)
    await new Promise((resolve) => setTimeout(resolve, 2200));

    // Step 2: Call grading API after animation
    if (createdReturnId && !apiError) {
      try {
        const gradeResp = await apiFetch(`${BASE}/grades/process`, {
          method: "POST",
          body: JSON.stringify({ return_id: createdReturnId }),
        });
        setApiGrade({
          grade: gradeResp.grade,
          confidence: gradeResp.confidence,
          damage_description: gradeResp.damage_description,
          damage_labels: gradeResp.damage_labels || [],
        });
      } catch (err) {
        setApiError("AI grading offline \u2013 using estimated grade");
      }
    }

    setTimeout(() => {
      setIsScanning(false);
      setStep(3);
    }, 600);
  };

  const handleConfirmReturn = async (selectedRoute) => {
    const finalRoute = selectedRoute || gradeOutcome.route;

    // Call buyer-match API
    if (returnId) {
      try {
        await apiFetch(`${BASE}/buyer-match/compute`, {
          method: "POST",
          body: JSON.stringify({
            return_id: returnId,
            sku_id: product.id.toString(),
            pincode: "751024",
            grade: gradeOutcome.grade,
          }),
        });
      } catch (_) {}
      localStorage.setItem("returniq_last_return_id", returnId);
    }

    // Keep existing localStorage flow for MyReturns compat
    initiateReturn(
      order.orderId,
      product.id,
      gradeOutcome.grade,
      gradeOutcome.recoveryValue,
      gradeOutcome.carbonAvoided,
      finalRoute,
      reason
    );
    setStep(4);
  };

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif", paddingBottom: "80px" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "800px", margin: "30px auto 0 auto", padding: "0 20px" }}>
        
        {/* Wizard Container */}
        <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: "8px", boxShadow: "0 2px 10px rgba(0,0,0,0.05)", overflow: "hidden" }}>
          
          {/* Header */}
          <div style={{ backgroundColor: "#27726b", color: "white", padding: "20px 24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h1 style={{ fontSize: "20px", fontWeight: "bold", margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                <span>♻️</span> ReturnIQ AI Grading Portal
              </h1>
              <span style={{ fontSize: "13px", opacity: 0.9 }}>Order #{order.orderId}</span>
            </div>
            <p style={{ margin: "6px 0 0 0", fontSize: "13px", opacity: 0.85 }}>
              Powered by Amazon Bedrock condition grading & eco-smart circular logistics.
            </p>
          </div>

          {/* Stepper Wizard Progress */}
          <div style={{ display: "flex", borderBottom: "1px solid #eee", backgroundColor: "#f9f9f9", padding: "12px 24px" }}>
            {[
              { num: 1, label: "Reason" },
              { num: 2, label: "AI Scan" },
              { num: 3, label: "Result" },
              { num: 4, label: "Scheduled" }
            ].map((s) => {
              const active = step === s.num;
              const completed = step > s.num;
              return (
                <div key={s.num} style={{ flex: 1, display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{
                    width: "22px",
                    height: "22px",
                    borderRadius: "50%",
                    backgroundColor: completed ? "#27726b" : active ? "#ffa41c" : "#e0e0e0",
                    color: completed || active ? "white" : "#666",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "11px",
                    fontWeight: "bold"
                  }}>
                    {completed ? "✓" : s.num}
                  </div>
                  <span style={{ fontSize: "12px", fontWeight: active || completed ? "bold" : "normal", color: active ? "#ffa41c" : completed ? "#27726b" : "#666" }}>
                    {s.label}
                  </span>
                  {s.num < 4 && <div style={{ flex: 1, height: "1px", backgroundColor: "#ddd", margin: "0 8px" }} />}
                </div>
              );
            })}
          </div>

          {/* STEP 1: SELECT REASON */}
          {step === 1 && (
            <div style={{ padding: "24px" }}>
              <h2 style={{ fontSize: "16px", fontWeight: "bold", margin: "0 0 16px 0" }}>Why are you returning this item?</h2>
              
              {/* Product mini review */}
              <div style={{ display: "flex", gap: "12px", border: "1px solid #eee", padding: "12px", borderRadius: "6px", marginBottom: "20px", backgroundColor: "#fafafa" }}>
                <img src={product.image} alt={product.name} style={{ width: "60px", height: "60px", objectFit: "contain", mixBlendMode: "multiply" }} />
                <div>
                  <h4 style={{ fontSize: "14px", margin: "0 0 4px 0" }}>{product.name}</h4>
                  <span style={{ fontSize: "12px", color: "#565959" }}>Size: {order.selectedSize} | Price: ₹{product.price}</span>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {[
                  "Wrong size / fits incorrectly",
                  "Performance or quality not met",
                  "Item damaged / physical scuffs",
                  "Accidental order / no longer needed"
                ].map((r) => {
                  const isSelected = reason === r;
                  return (
                    <div 
                      key={r} 
                      onClick={() => setReason(r)}
                      style={{
                        border: isSelected ? "2px solid #27726b" : "1px solid #ddd",
                        padding: "14px 18px",
                        borderRadius: "6px",
                        cursor: "pointer",
                        backgroundColor: isSelected ? "#f0faf8" : "white",
                        transition: "all 0.15s ease",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px"
                      }}
                    >
                      <input type="radio" checked={isSelected} readOnly />
                      <span style={{ fontSize: "14px", fontWeight: isSelected ? "bold" : "normal" }}>{r}</span>
                    </div>
                  );
                })}
              </div>

              <div style={{ marginTop: "24px", display: "flex", justifyContent: "flex-end" }}>
                <button
                  disabled={!reason}
                  onClick={() => setStep(2)}
                  style={{
                    backgroundColor: reason ? "#ffd814" : "#f0f2f2",
                    border: `1px solid ${reason ? "#fcd200" : "#d5d9d9"}`,
                    color: reason ? "#111" : "#a2a6a6",
                    padding: "10px 24px",
                    borderRadius: "20px",
                    fontWeight: "bold",
                    cursor: reason ? "pointer" : "not-allowed"
                  }}
                >
                  Continue to Scan
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: SIMULATE AI SCAN */}
          {step === 2 && (
            <div style={{ padding: "24px", textAlign: "center" }}>
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 8px 0" }}>Condition Verification Scan</h2>
              <p style={{ fontSize: "13px", color: "#565959", margin: "0 0 24px 0" }}>
                Upload photos of your product from multiple angles (Left, Right, Top, Bottom) or run our simulation to verify condition.
              </p>

              {/* 4 Upload Boxes */}
              <div style={{ display: "flex", justifyContent: "center", gap: "16px", flexWrap: "wrap", marginBottom: "24px" }}>
                
                {/* Left Angle view */}
                <div 
                  onClick={() => !isScanning && document.getElementById("file-left").click()}
                  style={{
                    width: "160px",
                    height: "160px",
                    border: "2px dashed #ccc",
                    borderRadius: "12px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: isScanning ? "default" : "pointer",
                    position: "relative",
                    backgroundColor: "#fafafa",
                    overflow: "hidden"
                  }}
                >
                  {leftImage ? (
                    <>
                      <img src={leftImage} alt="Left Profile" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      {!isScanning && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); setLeftImage(null); }}
                          style={{
                            position: "absolute", top: "5px", right: "5px",
                            width: "20px", height: "20px", borderRadius: "50%",
                            background: "rgba(0,0,0,0.6)", color: "white", border: "none",
                            fontSize: "11px", fontWeight: "bold", cursor: "pointer",
                            display: "flex", alignItems: "center", justifyContent: "center"
                          }}
                        >
                          ✕
                        </button>
                      )}
                    </>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", color: "#666" }}>
                      <span style={{ fontSize: "24px" }}>📷</span>
                      <strong style={{ fontSize: "12px" }}>Left Angle View</strong>
                      <span style={{ fontSize: "10px", color: "#888" }}>Click to upload</span>
                    </div>
                  )}
                  <input 
                    type="file" 
                    id="file-left" 
                    accept="image/*" 
                    onChange={(e) => handleFileChange(e, "left")} 
                    style={{ display: "none" }} 
                  />
                  {isScanning && scanProgress < 25 && (
                    <div style={{
                      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                      backgroundColor: "rgba(78, 204, 163, 0.15)"
                    }}>
                      <div style={{
                        position: "absolute", width: "100%", height: "4px", backgroundColor: "#4ecca3",
                        boxShadow: "0 0 10px #4ecca3", top: `${(scanProgress / 25) * 100}%`
                      }} />
                    </div>
                  )}
                </div>

                {/* Right Angle view */}
                <div 
                  onClick={() => !isScanning && document.getElementById("file-right").click()}
                  style={{
                    width: "160px",
                    height: "160px",
                    border: "2px dashed #ccc",
                    borderRadius: "12px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: isScanning ? "default" : "pointer",
                    position: "relative",
                    backgroundColor: "#fafafa",
                    overflow: "hidden"
                  }}
                >
                  {rightImage ? (
                    <>
                      <img src={rightImage} alt="Right Profile" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      {!isScanning && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); setRightImage(null); }}
                          style={{
                            position: "absolute", top: "5px", right: "5px",
                            width: "20px", height: "20px", borderRadius: "50%",
                            background: "rgba(0,0,0,0.6)", color: "white", border: "none",
                            fontSize: "11px", fontWeight: "bold", cursor: "pointer",
                            display: "flex", alignItems: "center", justifyContent: "center"
                          }}
                        >
                          ✕
                        </button>
                      )}
                    </>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", color: "#666" }}>
                      <span style={{ fontSize: "24px" }}>📷</span>
                      <strong style={{ fontSize: "12px" }}>Right Angle View</strong>
                      <span style={{ fontSize: "10px", color: "#888" }}>Click to upload</span>
                    </div>
                  )}
                  <input 
                    type="file" 
                    id="file-right" 
                    accept="image/*" 
                    onChange={(e) => handleFileChange(e, "right")} 
                    style={{ display: "none" }} 
                  />
                  {isScanning && scanProgress >= 25 && scanProgress < 50 && (
                    <div style={{
                      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                      backgroundColor: "rgba(78, 204, 163, 0.15)"
                    }}>
                      <div style={{
                        position: "absolute", width: "100%", height: "4px", backgroundColor: "#4ecca3",
                        boxShadow: "0 0 10px #4ecca3", top: `${((scanProgress - 25) / 25) * 100}%`
                      }} />
                    </div>
                  )}
                </div>

                {/* Top Angle view */}
                <div 
                  onClick={() => !isScanning && document.getElementById("file-top").click()}
                  style={{
                    width: "160px",
                    height: "160px",
                    border: "2px dashed #ccc",
                    borderRadius: "12px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: isScanning ? "default" : "pointer",
                    position: "relative",
                    backgroundColor: "#fafafa",
                    overflow: "hidden"
                  }}
                >
                  {topImage ? (
                    <>
                      <img src={topImage} alt="Top View" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      {!isScanning && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); setTopImage(null); }}
                          style={{
                            position: "absolute", top: "5px", right: "5px",
                            width: "20px", height: "20px", borderRadius: "50%",
                            background: "rgba(0,0,0,0.6)", color: "white", border: "none",
                            fontSize: "11px", fontWeight: "bold", cursor: "pointer",
                            display: "flex", alignItems: "center", justifyContent: "center"
                          }}
                        >
                          ✕
                        </button>
                      )}
                    </>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", color: "#666" }}>
                      <span style={{ fontSize: "24px" }}>📷</span>
                      <strong style={{ fontSize: "12px" }}>Top View</strong>
                      <span style={{ fontSize: "10px", color: "#888" }}>Click to upload</span>
                    </div>
                  )}
                  <input 
                    type="file" 
                    id="file-top" 
                    accept="image/*" 
                    onChange={(e) => handleFileChange(e, "top")} 
                    style={{ display: "none" }} 
                  />
                  {isScanning && scanProgress >= 50 && scanProgress < 75 && (
                    <div style={{
                      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                      backgroundColor: "rgba(78, 204, 163, 0.15)"
                    }}>
                      <div style={{
                        position: "absolute", width: "100%", height: "4px", backgroundColor: "#4ecca3",
                        boxShadow: "0 0 10px #4ecca3", top: `${((scanProgress - 50) / 25) * 100}%`
                      }} />
                    </div>
                  )}
                </div>

                {/* Bottom view */}
                <div 
                  onClick={() => !isScanning && document.getElementById("file-bottom").click()}
                  style={{
                    width: "160px",
                    height: "160px",
                    border: "2px dashed #ccc",
                    borderRadius: "12px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: isScanning ? "default" : "pointer",
                    position: "relative",
                    backgroundColor: "#fafafa",
                    overflow: "hidden"
                  }}
                >
                  {bottomImage ? (
                    <>
                      <img src={bottomImage} alt="Bottom View" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      {!isScanning && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); setBottomImage(null); }}
                          style={{
                            position: "absolute", top: "5px", right: "5px",
                            width: "20px", height: "20px", borderRadius: "50%",
                            background: "rgba(0,0,0,0.6)", color: "white", border: "none",
                            fontSize: "11px", fontWeight: "bold", cursor: "pointer",
                            display: "flex", alignItems: "center", justifyContent: "center"
                          }}
                        >
                          ✕
                        </button>
                      )}
                    </>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px", color: "#666" }}>
                      <span style={{ fontSize: "24px" }}>📷</span>
                      <strong style={{ fontSize: "12px" }}>Bottom View</strong>
                      <span style={{ fontSize: "10px", color: "#888" }}>Click to upload</span>
                    </div>
                  )}
                  <input 
                    type="file" 
                    id="file-bottom" 
                    accept="image/*" 
                    onChange={(e) => handleFileChange(e, "bottom")} 
                    style={{ display: "none" }} 
                  />
                  {isScanning && scanProgress >= 75 && (
                    <div style={{
                      position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                      backgroundColor: "rgba(78, 204, 163, 0.15)"
                    }}>
                      <div style={{
                        position: "absolute", width: "100%", height: "4px", backgroundColor: "#4ecca3",
                        boxShadow: "0 0 10px #4ecca3", top: `${((scanProgress - 75) / 25) * 100}%`
                      }} />
                    </div>
                  )}
                </div>

              </div>

              {/* Status bar */}
              {isScanning ? (
                <div style={{
                  maxWidth: "420px",
                  margin: "0 auto 24px auto",
                  backgroundColor: "rgba(39, 114, 107, 0.9)",
                  color: "white",
                  padding: "8px 16px",
                  borderRadius: "20px",
                  fontSize: "13px",
                  fontWeight: "bold"
                }}>
                  {scanProgress < 25 ? "🔍 Left Profile: " : scanProgress < 50 ? "🔍 Right Profile: " : scanProgress < 75 ? "🔍 Top Face: " : "🔍 Bottom Face: "} 
                  {scanProgress < 25 
                    ? `Scanning... ${Math.round((scanProgress / 25) * 100)}%` 
                    : scanProgress < 50 
                    ? `Scanning... ${Math.round(((scanProgress - 25) / 25) * 100)}%` 
                    : scanProgress < 75
                    ? `Scanning... ${Math.round(((scanProgress - 50) / 25) * 100)}%`
                    : `Scanning... ${Math.round(((scanProgress - 75) / 25) * 100)}%`}
                </div>
              ) : (
                <div style={{ fontSize: "13px", color: "#565959", marginBottom: "20px" }}>
                  Status: {leftImage && rightImage && topImage && bottomImage ? "✅ All angles uploaded. Ready for AI grading!" : "⚠️ Please upload all 4 angles to begin scan."}
                </div>
              )}

              {/* Buttons */}
              <div style={{ display: "flex", justifyContent: "center", gap: "12px" }}>
                <button
                  disabled={isScanning || !(leftImage && rightImage && topImage && bottomImage)}
                  onClick={handleSimulateScan}
                  style={{
                    backgroundColor: (leftImage && rightImage && topImage && bottomImage) && !isScanning ? "#27726b" : "#f0f2f2",
                    border: `1px solid ${(leftImage && rightImage && topImage && bottomImage) && !isScanning ? "#1f5953" : "#d5d9d9"}`,
                    color: (leftImage && rightImage && topImage && bottomImage) && !isScanning ? "white" : "#a2a6a6",
                    padding: "10px 24px",
                    borderRadius: "20px",
                    fontWeight: "bold",
                    cursor: (leftImage && rightImage && topImage && bottomImage) && !isScanning ? "pointer" : "not-allowed"
                  }}
                >
                  {isScanning ? "Scanning..." : "Simulate AI Scan"}
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: DISPLAY GRADED RESULT */}
          {step === 3 && (
            <div style={{ padding: "24px" }}>
              {gradeOutcome.grade === "D" ? (
                <>
                  <div style={{ textAlign: "center", marginBottom: 24 }}>
                    <div style={{ fontSize: 48, marginBottom: 12 }}>❌</div>
                    <h2 style={{ fontSize: "20px", fontWeight: "bold", margin: "0 0 8px 0", color: "#c40000" }}>Return Rejected</h2>
                    <p style={{ fontSize: "14px", color: "#565959", maxWidth: 460, margin: "0 auto", lineHeight: 1.5 }}>
                      Our AI detected customer-caused damage. This item is not eligible for return per Amazon policy.
                    </p>
                  </div>
                  <div style={{
                    backgroundColor: "#f8d7da", border: "1px solid #f5c6cb", borderRadius: 8,
                    padding: 16, marginBottom: 24, fontSize: 13, color: "#721c24",
                  }}>
                    <strong>Assessment:</strong> {apiGrade ? apiGrade.damage_description : "Item shows customer-caused damage."}
                    {apiGrade && (
                      <span style={{ display: "block", marginTop: 4 }}>Confidence: {apiGrade.confidence?.toFixed(1)}%</span>
                    )}
                  </div>
                  <div style={{ display: "flex", justifyContent: "center" }}>
                    <button
                      onClick={async () => {
                        if (returnId) {
                          try { await apiFetch(`${BASE}/returns/${returnId}/status`, { method: "PATCH", body: JSON.stringify({ status: "REJECTED" }) }); } catch {}
                        }
                        navigate("/orders");
                      }}
                      style={{
                        backgroundColor: "#ffd814",
                        border: "1px solid #fcd200",
                        color: "#111",
                        padding: "10px 32px",
                        borderRadius: "20px",
                        fontWeight: "bold",
                        cursor: "pointer",
                      }}
                    >
                      Okay, I understand
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 6px 0", textAlign: "center" }}>AI Grading Assessment Result</h2>
                  <p style={{ fontSize: "13px", color: "#565959", textAlign: "center", margin: "0 0 24px 0" }}>
                    Amazon Bedrock has completed visual and operational inspection analysis.
                  </p>

                  {/* Grade banner */}
                  {gradeOutcome.grade === "A" && (
                    <div style={{ backgroundColor: "#d4edda", border: "1px solid #c3e6cb", borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13, color: "#155724", textAlign: "center" }}>
                      ✅ Item is Like New. You receive <strong>100% refund</strong>.
                    </div>
                  )}
                  {gradeOutcome.grade === "B" && (
                    <div style={{ backgroundColor: "#fff3cd", border: "1px solid #ffeeba", borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13, color: "#856404", textAlign: "center" }}>
                      Item is in Good Condition. You receive <strong>85% refund</strong>.
                    </div>
                  )}
                  {gradeOutcome.grade === "C" && (
                    <div style={{ backgroundColor: "#f8d7da", border: "1px solid #f5c6cb", borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13, color: "#721c24", textAlign: "center" }}>
                      Item has Fair Condition. You receive <strong>70% refund</strong>.
                    </div>
                  )}

                  {/* Result card */}
                  <div style={{
                    backgroundColor: "#f6faf9",
                    border: "1px solid #e3ebe8",
                    borderRadius: "8px",
                    padding: "20px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "24px"
                  }}>
                    <div>
                      <span style={{ fontSize: "11px", color: "#565959", textTransform: "uppercase", fontWeight: "bold", display: "block" }}>Verified Grade</span>
                      <strong style={{ fontSize: "32px", color: "#27726b", display: "block", marginTop: "4px" }}>Grade {gradeOutcome.grade}</strong>
                      <span style={{ fontSize: "12px", color: "#007600", fontWeight: "bold", display: "block", marginTop: "4px" }}>
                        {apiGrade ? apiGrade.damage_description : "Item assessed successfully."}
                      </span>
                      {apiGrade && (
                        <span style={{ fontSize: "11px", color: "#565959", display: "block", marginTop: "2px" }}>
                          Confidence: {apiGrade.confidence?.toFixed(1)}%
                        </span>
                      )}
                      {apiError && (
                        <span style={{ fontSize: "11px", color: "#c45500", display: "block", marginTop: "4px" }}>
                          ⚠️ {apiError}
                        </span>
                      )}
                    </div>
                    <div style={{
                      width: "80px", height: "80px", borderRadius: "50%",
                      backgroundColor: "#27726b", color: "white",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: "36px", fontWeight: "bold",
                      boxShadow: "0 4px 12px rgba(39,114,107,0.2)"
                    }}>
                      {gradeOutcome.grade}
                    </div>
                  </div>

                  {/* Details table */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "14px", marginBottom: "24px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #eee", paddingBottom: "6px" }}>
                      <span style={{ color: "#565959" }}>Original Purchase Price</span>
                      <strong>₹{product.price}</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #eee", paddingBottom: "6px" }}>
                      <span style={{ color: "#565959" }}>Your Refund Amount</span>
                      <strong style={{ color: "#007600" }}>₹{gradeOutcome.recoveryValue}</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #eee", paddingBottom: "6px" }}>
                      <span style={{ color: "#565959" }}>Carbon CO₂ Offset Saving</span>
                      <strong style={{ color: "#27726b" }}>🌱 {gradeOutcome.carbonAvoided} kg CO₂</strong>
                    </div>
                  </div>

                  <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                    <button
                      onClick={() => navigate("/orders")}
                      style={{
                        backgroundColor: "white",
                        border: "1px solid #d5d9d9",
                        color: "#111",
                        padding: "10px 24px",
                        borderRadius: "20px",
                        fontWeight: "bold",
                        cursor: "pointer"
                      }}
                    >
                      Keep Item
                    </button>
                    <button
                      onClick={() => handleConfirmReturn()}
                      style={{
                        backgroundColor: "#ffd814",
                        border: "1px solid #fcd200",
                        color: "#111",
                        padding: "10px 24px",
                        borderRadius: "20px",
                        fontWeight: "bold",
                        cursor: "pointer"
                      }}
                    >
                      Return Item
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* STEP 4: FINAL QR & PICKUP CONFIRMATION */}
          {step === 4 && (
            <div style={{ padding: "30px", textAlign: "center" }}>
              <div style={{ fontSize: "48px", color: "#27726b", marginBottom: "16px" }}>✓</div>
              <h2 style={{ fontSize: "22px", fontWeight: "bold", color: "#111", margin: "0 0 8px 0" }}>Return Pick-Up Scheduled</h2>
              <p style={{ fontSize: "14px", color: "#565959", maxWidth: "500px", margin: "0 auto 24px auto", lineHeight: "1.4" }}>
                Your return route via <strong>ReturnIQ Local Resell</strong> has been registered.
                Please display the QR code below to the Amazon agent when they arrive.
              </p>

              {/* QR Code Graphic Box */}
              <div style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "20px",
                maxWidth: "240px",
                margin: "0 auto 24px auto",
                backgroundColor: "#fff",
                boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
              }}>
                <div style={{
                  width: "160px",
                  height: "160px",
                  margin: "0 auto",
                  backgroundColor: "#f5f5f5",
                  padding: "10px",
                  borderRadius: "4px"
                }}>
                  {/* Mock QR lines */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(8, 1fr)", gap: "2px", width: "100%", height: "100%" }}>
                    {Array.from({ length: 64 }).map((_, i) => (
                      <div key={i} style={{ backgroundColor: Math.random() > 0.4 ? "#27726b" : "#fff" }} />
                    ))}
                  </div>
                </div>
                <strong style={{ display: "block", fontSize: "15px", color: "#27726b", marginTop: "12px" }}>
                  Scan code: {returnId || `RET-${order.orderId}`}
                </strong>
                <span style={{ fontSize: "11px", color: "#767676", display: "block", marginTop: "4px" }}>
                  Scan upon pickup to trigger instant refund
                </span>
              </div>

              {/* Pickup details */}
              <div style={{
                backgroundColor: "#fafafa",
                border: "1px solid #eee",
                borderRadius: "6px",
                padding: "16px",
                maxWidth: "400px",
                margin: "0 auto 24px auto",
                fontSize: "13px",
                textAlign: "left"
              }}>
                <div><strong>Pick-Up Slot:</strong> Tomorrow, 10:00 AM – 2:00 PM</div>
                <div style={{ marginTop: "6px" }}><strong>Address:</strong> Patia, Bhubaneswar, 751024</div>
                <div style={{ marginTop: "6px" }}><strong>Item condition:</strong> Graded Grade {gradeOutcome.grade} (AI-Verified)</div>
              </div>

              <div style={{ display: "flex", justifyContent: "center", gap: "16px" }}>
                <button
                  onClick={() => navigate("/my-returns")}
                  style={{
                    backgroundColor: "#ffd814",
                    border: "1px solid #fcd200",
                    color: "#111",
                    padding: "10px 24px",
                    borderRadius: "20px",
                    fontWeight: "bold",
                    cursor: "pointer"
                  }}
                >
                  Track in My Returns
                </button>
              </div>
            </div>
          )}

        </div>

      </main>
    </div>
  );
}
