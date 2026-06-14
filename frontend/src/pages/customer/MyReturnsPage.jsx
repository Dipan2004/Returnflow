import React, { useState, useEffect } from "react";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

const STATUS_BADGES = {
  PENDING_PICKUP: { text: "Pickup Scheduled", color: "#856404", bg: "#fff3cd" },
  GRADED: { text: "Graded", color: "#004085", bg: "#cce5ff" },
  P2P_MATCHED: { text: "Matched/Reselling", color: "#27726b", bg: "#f0faf8" },
  DELIVERED: { text: "Completed", color: "#155724", bg: "#d4edda" },
};

const STEPPER_STEPS = ["Submitted", "Graded", "Matched", "Delivered"];

const STATUS_INDEX = {
  PENDING_PICKUP: 0,
  GRADED: 1,
  P2P_MATCHED: 2,
  DELIVERED: 3,
};

export default function MyReturnsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [returns, setReturns] = useState([]);
  const [selectedReturn, setSelectedReturn] = useState(null);

  useEffect(() => {
    function loadReturns() {
      let current = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
      // Pre-populate with a demo return if empty
      if (current.length === 0) {
        const demo = {
          return_id: "ret-demo-123",
          product_name: "Nike Air Max 270",
          order_id: "#402-1234567",
          reason: "Wrong size",
          status: "PENDING_PICKUP",
          created_at: new Date(Date.now() - 3600000).toISOString(),
          pickup_window: "Tomorrow, 10 AM – 2 PM",
          reference_num: "RET-992813",
          mrp: 850,
          image_url: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&fit=crop&auto=format",
          grade: null,
          recovery_value: null,
          value_delta: null,
          route: null,
        };
        current = [demo];
        localStorage.setItem("returniq_returns", JSON.stringify(current));
      }
      setReturns(current);
      // Select the first return by default
      if (current.length > 0) {
        setSelectedReturn(current[0]);
      }
    }
    loadReturns();

    // Set up storage listener to respond to background updates
    window.addEventListener("storage", loadReturns);
    const interval = setInterval(loadReturns, 2000); // Poll localstorage

    return () => {
      window.removeEventListener("storage", loadReturns);
      clearInterval(interval);
    };
  }, []);

  const badge = selectedReturn ? STATUS_BADGES[selectedReturn.status] : null;
  const currentStepIndex = selectedReturn ? STATUS_INDEX[selectedReturn.status] : 0;

  return (
    <div style={{ backgroundColor: "#fcfcfc", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 60 }}>
      <Header onReturnClick={() => {}} />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: 940, margin: "0 auto", padding: "24px 16px" }}>
        {/* Breadcrumbs */}
        <div style={{ fontSize: 13, color: "#0066c0", marginBottom: 16 }}>
          <span style={{ cursor: "pointer" }}>Your Account</span> ›{" "}
          <span style={{ color: "#111" }}>Your Returns</span>
        </div>

        <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
          {/* LEFT: Returns Queue */}
          <div style={{ flex: "0 0 320px", display: "flex", flexDirection: "column", gap: 12 }}>
            <h2 style={{ fontSize: 18, margin: "0 0 4px 0", color: "#111", fontWeight: 500 }}>Active Returns</h2>
            {returns.map((item) => {
              const isSelected = selectedReturn?.return_id === item.return_id;
              const itemBadge = STATUS_BADGES[item.status] || { text: item.status, color: "#333", bg: "#eee" };
              return (
                <div
                  key={item.return_id}
                  onClick={() => setSelectedReturn(item)}
                  style={{
                    backgroundColor: "white",
                    border: isSelected ? "1px solid #27726b" : "1px solid #ddd",
                    borderRadius: 4,
                    padding: 12,
                    cursor: "pointer",
                    boxShadow: isSelected ? "0 2px 8px rgba(39,114,107,0.15)" : "0 1px 3px rgba(0,0,0,0.05)",
                    borderLeft: isSelected ? "4px solid #27726b" : "4px solid transparent",
                    display: "flex",
                    gap: 12,
                  }}
                >
                  <img
                    src={item.image_url}
                    alt={item.product_name}
                    style={{ width: 50, height: 50, objectFit: "contain", border: "1px solid #eee", borderRadius: 4 }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: "bold", color: "#111", height: 18, overflow: "hidden" }}>
                      {item.product_name}
                    </div>
                    <div style={{ display: "inline-block", fontSize: 10, padding: "2px 6px", borderRadius: 10, backgroundColor: itemBadge.bg, color: itemBadge.color, marginTop: 6, fontWeight: "bold" }}>
                      {itemBadge.text}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* RIGHT: Selected Return Detail Outcome */}
          <div style={{ flex: 1 }}>
            {selectedReturn ? (
              <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: 4, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
                {/* Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", borderBottom: "1px solid #eee", paddingBottom: 16, marginBottom: 20 }}>
                  <div>
                    <h1 style={{ fontSize: 20, fontWeight: 500, margin: "0 0 4px 0", color: "#111" }}>
                      Return Details
                    </h1>
                    <span style={{ fontSize: 12, color: "#565959" }}>Ref: {selectedReturn.reference_num}</span>
                  </div>
                  <span style={{ fontSize: 12, padding: "4px 10px", borderRadius: 12, fontWeight: "bold", backgroundColor: badge.bg, color: badge.color }}>
                    {badge.text}
                  </span>
                </div>

                {/* Info summary */}
                <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
                  <img
                    src={selectedReturn.image_url}
                    alt={selectedReturn.product_name}
                    style={{ width: 80, height: 80, objectFit: "contain", border: "1px solid #eee", borderRadius: 4 }}
                  />
                  <div>
                    <h2 style={{ fontSize: 16, fontWeight: "bold", margin: "0 0 6px 0", color: "#0066c0" }}>
                      {selectedReturn.product_name}
                    </h2>
                    <div style={{ fontSize: 13, color: "#555" }}>
                      <strong>Order ID:</strong> {selectedReturn.order_id} <br />
                      <strong>Return Reason:</strong> {selectedReturn.reason}
                    </div>
                  </div>
                </div>

                {/* Stepper timeline */}
                <div style={{ margin: "32px 0", padding: "0 20px" }}>
                  <div style={{ display: "flex", alignItems: "center", position: "relative" }}>
                    {STEPPER_STEPS.map((stepName, idx) => {
                      const isCompleted = idx < currentStepIndex;
                      const isCurrent = idx === currentStepIndex;
                      return (
                        <React.Fragment key={idx}>
                          <div
                            style={{
                              width: 24,
                              height: 24,
                              borderRadius: "50%",
                              border: isCompleted || isCurrent ? "2px solid #27726b" : "2px solid #ddd",
                              backgroundColor: isCompleted ? "#27726b" : "white",
                              color: isCompleted ? "white" : isCurrent ? "#27726b" : "#aaa",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: 11,
                              fontWeight: "bold",
                              zIndex: 2,
                            }}
                          >
                            {isCompleted ? "✓" : idx + 1}
                          </div>
                          {idx < STEPPER_STEPS.length - 1 && (
                            <div
                              style={{
                                flex: 1,
                                height: 3,
                                backgroundColor: idx < currentStepIndex ? "#27726b" : "#ddd",
                                margin: "0 -2px",
                                zIndex: 1,
                              }}
                            />
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                  {/* Stepper Labels */}
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
                    {STEPPER_STEPS.map((stepName, idx) => {
                      const isCurrent = idx === currentStepIndex;
                      return (
                        <span
                          key={idx}
                          style={{
                            fontSize: 11,
                            color: isCurrent ? "#27726b" : "#565959",
                            fontWeight: isCurrent ? "bold" : "normal",
                            width: 60,
                            textAlign: "center",
                          }}
                        >
                          {stepName}
                        </span>
                      );
                    })}
                  </div>
                </div>

                {/* Outcome details conditional */}
                {selectedReturn.status === "PENDING_PICKUP" && (
                  <div style={{ backgroundColor: "#fdf8e2", border: "1px solid #f7e1b5", padding: 16, borderRadius: 4, fontSize: 13, color: "#664d03", lineHeight: 1.5 }}>
                    <strong>Pickup Scheduled:</strong> {selectedReturn.pickup_window} <br />
                    Our delivery partner will collect the item. You'll receive a notification and update here once assessment completes.
                  </div>
                )}

                {selectedReturn.status === "GRADED" && (
                  <div style={{ backgroundColor: "#e8f4fd", border: "1px solid #bee5eb", padding: 16, borderRadius: 4, fontSize: 13, color: "#0c5460", lineHeight: 1.5 }}>
                    <strong>Grading Completed:</strong> <br />
                    Your return has been assessed as <strong>Grade {selectedReturn.grade}</strong>. We are matching it with nearby demand. Your refund will process shortly.
                  </div>
                )}

                {(selectedReturn.status === "P2P_MATCHED" || selectedReturn.status === "DELIVERED") && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    {/* Grade Outcome */}
                    <div style={{ borderLeft: "4px solid #27726b", backgroundColor: "#f9f9f9", padding: 16, borderRadius: "0 4px 4px 0" }}>
                      <div style={{ fontSize: 13, color: "#111", lineHeight: 1.5 }}>
                        Your item was assessed as <strong>Grade {selectedReturn.grade}</strong>. We found a buyer nearby.
                        <br />
                        <span style={{ color: "#767676", fontSize: 12 }}>Matched with a shopper 2.3km away. Expected delivery: 4 hours.</span>
                      </div>
                    </div>

                    {/* Refund Outcome */}
                    <div style={{ border: "1px solid #eee", padding: 16, borderRadius: 4, backgroundColor: "white", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ fontSize: 13 }}>
                        <strong>Refund Status:</strong> Completed <br />
                        <span style={{ color: "#767676", fontSize: 12 }}>Credited back to your original payment method.</span>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 11, color: "#767676", textTransform: "uppercase" }}>Amount Refunded</div>
                        <div style={{ fontSize: 20, fontWeight: "bold", color: "#27726b", marginTop: 4 }}>₹{selectedReturn.recovery_value}</div>
                      </div>
                    </div>

                    {/* Carbon Impact */}
                    <div style={{ backgroundColor: "#27726b", color: "white", padding: 12, borderRadius: 4, display: "flex", alignItems: "center", gap: 10, fontSize: 13 }}>
                      <span>♻️</span>
                      <span>
                        <strong>2.3 kg CO₂ avoided</strong> — equivalent to 1 tree planted by bypassing warehouse back-shipping.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: 40, backgroundColor: "white", textAlign: "center", borderRadius: 4, border: "1px solid #ddd" }}>
                Select a return item to view details.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
