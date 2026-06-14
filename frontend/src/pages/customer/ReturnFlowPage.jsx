import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

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

  useEffect(() => {
    if (product) {
      // Calculate graded values
      const basePrice = product.price;
      const calculatedGrade = reason === "Item damaged" ? "C" : reason === "Performance not met" ? "B" : "A";
      const recoveryMultiplier = { A: 0.85, B: 0.70, C: 0.50 }[calculatedGrade];
      const co2 = { A: 2.3, B: 1.8, C: 1.2 }[calculatedGrade];

      setGradeOutcome({
        grade: calculatedGrade,
        recoveryValue: Math.floor(basePrice * recoveryMultiplier),
        carbonAvoided: co2,
        route: "P2P Resell Match"
      });
    }
  }, [reason, product]);

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
  const handleSimulateScan = () => {
    setIsScanning(true);
    setScanProgress(0);
    const interval = setInterval(() => {
      setScanProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setIsScanning(false);
            setStep(3); // Go to step 3 (grade details)
          }, 600);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleConfirmReturn = (selectedRoute) => {
    // Save to context
    const finalRoute = selectedRoute || gradeOutcome.route;
    initiateReturn(
      order.orderId,
      product.id,
      gradeOutcome.grade,
      gradeOutcome.recoveryValue,
      gradeOutcome.carbonAvoided,
      finalRoute,
      reason
    );
    setStep(5); // Go to QR Confirmation Step
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
              { num: 4, label: "Routing" },
              { num: 5, label: "Scheduled" }
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
                  {s.num < 5 && <div style={{ flex: 1, height: "1px", backgroundColor: "#ddd", margin: "0 8px" }} />}
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
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 6px 0", textAlign: "center" }}>AI Grading Assessment Result</h2>
              <p style={{ fontSize: "13px", color: "#565959", textAlign: "center", margin: "0 0 24px 0" }}>
                Amazon Bedrock has completed visual and operational inspection analysis.
              </p>

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
                    🌱 Very Minor Wear - Fully functional and resellable.
                  </span>
                </div>
                
                <div style={{
                  width: "80px",
                  height: "80px",
                  borderRadius: "50%",
                  backgroundColor: "#27726b",
                  color: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "36px",
                  fontWeight: "bold",
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
                  <span style={{ color: "#565959" }}>ReturnIQ Resell Valuation</span>
                  <strong style={{ color: "#007600" }}>₹{gradeOutcome.recoveryValue}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #eee", paddingBottom: "6px" }}>
                  <span style={{ color: "#565959" }}>Carbon CO₂ Offset Saving</span>
                  <strong style={{ color: "#27726b" }}>🌱 {gradeOutcome.carbonAvoided} kg CO₂</strong>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
                <button
                  onClick={() => setStep(4)}
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
                  Review Refund Routes
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: ROUTE RECOMMENDATION OPTIONS */}
          {step === 4 && (
            <div style={{ padding: "24px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 6px 0" }}>Choose Refund Option</h2>
              <p style={{ fontSize: "13px", color: "#565959", margin: "0 0 20px 0" }}>
                Based on current matching logistics, choose how to route your returned item.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "24px" }}>
                
                {/* Peer to Peer Resell route (RECOMMENDED) */}
                <div style={{
                  border: "2px solid #27726b",
                  borderRadius: "8px",
                  padding: "18px",
                  backgroundColor: "#f0faf8",
                  cursor: "pointer"
                }}
                  onClick={() => handleConfirmReturn("P2P Resell Match")}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                    <div>
                      <span style={{ fontSize: "11px", backgroundColor: "#27726b", color: "white", padding: "2px 8px", borderRadius: "10px", fontWeight: "bold", textTransform: "uppercase" }}>Recommended Option</span>
                      <h3 style={{ fontSize: "16px", fontWeight: "bold", margin: "6px 0 2px 0", color: "#27726b" }}>♻️ ReturnIQ Instant Local Resell Match</h3>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: "11px", color: "#565959", textTransform: "uppercase" }}>Refund Amount</span>
                      <div style={{ fontSize: "20px", fontWeight: "bold", color: "#27726b" }}>₹{gradeOutcome.recoveryValue}</div>
                    </div>
                  </div>
                  <p style={{ fontSize: "13px", color: "#333", margin: "0 0 10px 0", lineHeight: "1.4" }}>
                    We've matched your item with a buyer <strong>2.3 km away</strong>. Your item bypasses shipping back to the hub. Refund will clear instantly upon delivery agent pickup verification tomorrow!
                  </p>
                  <span style={{ fontSize: "12px", color: "#007600", fontWeight: "bold" }}>🌱 Saves {gradeOutcome.carbonAvoided} kg CO₂ and bypasses the landfill entirely!</span>
                </div>

                {/* Standard Return */}
                <div style={{
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  padding: "18px",
                  backgroundColor: "white",
                  cursor: "pointer"
                }}
                  onClick={() => handleConfirmReturn("Standard Return")}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                    <h3 style={{ fontSize: "15px", fontWeight: "bold", margin: 0, color: "#111" }}>📦 Standard Return shipping</h3>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: "11px", color: "#565959", textTransform: "uppercase" }}>Refund Amount</span>
                      <div style={{ fontSize: "18px", fontWeight: "bold" }}>₹{Math.floor(gradeOutcome.recoveryValue * 0.9)}</div>
                    </div>
                  </div>
                  <p style={{ fontSize: "12px", color: "#565959", margin: "0", lineHeight: "1.4" }}>
                    Ship back to Amazon's fulfillment center. Refund processed in 5–7 business days after item inspection. (Deducts ₹40 return processing fee).
                  </p>
                </div>

              </div>
            </div>
          )}

          {/* STEP 5: FINAL QR & PICKUP CONFIRMATION */}
          {step === 5 && (
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
                  Scan code: RET-{order.orderId}
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
