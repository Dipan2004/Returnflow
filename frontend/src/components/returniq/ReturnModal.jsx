import React, { useState } from "react";

const DEFAULT_ORDERS = [
  { id: 1, name: "Nike Air Max 270",   date: "2 Jun 2026",  orderId: "#402-1234567", img: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=150&h=150&q=80", mrp: 850 },
  { id: 2, name: "boAt Rockerz 450",   date: "28 May 2026", orderId: "#402-7654321", img: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=150&h=150&q=80", mrp: 399 },
  { id: 3, name: "Puma T-Shirt",       date: "20 May 2026", orderId: "#402-1122334", img: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=150&h=150&q=80", mrp: 499 },
];

const REASONS = [
  "Wrong size",
  "Defective/Does not work",
  "Changed my mind",
  "Better price available",
  "Item damaged on arrival",
  "Performance not met",
];

export default function ReturnModal({ isOpen, onClose, onComplete }) {
  if (!isOpen) return null;

  const [step, setStep] = useState(1);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [selectedReason, setSelectedReason] = useState("");
  const [referenceNum, setReferenceNum] = useState("");

  const [orders] = useState(() => {
    const saved = localStorage.getItem("returniq_orders");
    return saved ? JSON.parse(saved) : DEFAULT_ORDERS;
  });

  function handleReset() {
    setStep(1);
    setSelectedOrder(null);
    setSelectedReason("");
    setReferenceNum("");
  }

  function handleClose() {
    handleReset();
    onClose();
  }

  function handleConfirm() {
    const ref = "RET-" + Math.floor(100000 + Math.random() * 900000);
    setReferenceNum(ref);

    // Save scheduled return to local storage for end-to-end mock flow
    const returnObj = {
      return_id: "ret-" + Date.now(),
      product_name: selectedOrder.name,
      order_id: selectedOrder.orderId,
      reason: selectedReason,
      status: "PENDING_PICKUP", // Pickup Scheduled
      created_at: new Date().toISOString(),
      pickup_window: "Tomorrow, 10 AM – 2 PM",
      reference_num: ref,
      mrp: selectedOrder.mrp,
      image_url: selectedOrder.img,
      grade: null,
      recovery_value: null,
      value_delta: null,
      route: null,
    };

    const currentReturns = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    currentReturns.push(returnObj);
    localStorage.setItem("returniq_returns", JSON.stringify(currentReturns));

    setStep(3);
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: 40,
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: 4,
          width: "100%",
          maxWidth: 600,
          maxHeight: "90vh",
          overflowY: "auto",
          boxShadow: "0 4px 20px rgba(0,0,0,0.25)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Header */}
        <div
          style={{
            backgroundColor: "#131921",
            padding: "16px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            color: "white",
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 700 }}>Return your item</span>
          <button
            onClick={handleClose}
            style={{
              background: "transparent",
              color: "white",
              fontSize: 22,
              border: "none",
              cursor: "pointer",
              lineHeight: 1,
            }}
          >
            &times;
          </button>
        </div>

        {/* Indicator */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            padding: "12px 0",
            gap: 8,
            backgroundColor: "#fcfcfc",
            borderBottom: "1px solid #eee",
          }}
        >
          {[1, 2, 3].map((s) => {
            let bg = "#ddd";
            let opacity = 1;
            if (s < step) {
              bg = "#27726b";
              opacity = 0.5;
            } else if (s === step) {
              bg = "#27726b";
            }
            return (
              <div
                key={s}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  backgroundColor: bg,
                  opacity: opacity,
                }}
              />
            );
          })}
        </div>

        {/* Content */}
        <div style={{ padding: 24, flex: 1 }}>
          {step === 1 && (
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 400, margin: "0 0 16px 0", color: "#111" }}>
                Select the item you want to return
              </h2>
              <div>
                {orders.map((order) => {
                  const isSelected = selectedOrder?.id === order.id;
                  return (
                    <div
                      key={order.id}
                      onClick={() => setSelectedOrder(order)}
                      style={{
                        display: "flex",
                        gap: 16,
                        padding: "14px 20px",
                        borderBottom: "1px solid #eee",
                        cursor: "pointer",
                        backgroundColor: isSelected ? "#f0faf8" : "white",
                        borderLeft: isSelected ? "3px solid #27726b" : "3px solid transparent",
                        transition: "all 0.2s",
                      }}
                    >
                      <img
                        src={order.img}
                        alt={order.name}
                        style={{ width: 64, height: 64, objectFit: "contain", border: "1px solid #eee", borderRadius: 4 }}
                      />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 14, fontWeight: 600, color: "#111" }}>{order.name}</div>
                        <div style={{ fontSize: 12, color: "#555", marginTop: 4 }}>
                          Ordered on: {order.date} | ID: {order.orderId}
                        </div>
                      </div>
                      {isSelected && (
                        <span style={{ color: "#27726b", fontWeight: "bold", fontSize: 18 }}>✓</span>
                      )}
                    </div>
                  );
                })}
              </div>

              <div style={{ marginTop: 24, display: "flex", justifyContent: "flex-end" }}>
                <button
                  disabled={!selectedOrder}
                  onClick={() => setStep(2)}
                  style={{
                    backgroundColor: selectedOrder ? "#ffa41c" : "#e7e9ec",
                    border: `1px solid ${selectedOrder ? "#ff9900" : "#adb1b8"}`,
                    color: selectedOrder ? "#111" : "#888",
                    padding: "8px 24px",
                    borderRadius: 4,
                    fontSize: 14,
                    cursor: selectedOrder ? "pointer" : "not-allowed",
                    fontWeight: 500,
                  }}
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 400, margin: "0 0 16px 0", color: "#111" }}>
                Why are you returning this?
              </h2>

              <select
                value={selectedReason}
                onChange={(e) => setSelectedReason(e.target.value)}
                style={{
                  width: "100%",
                  padding: 10,
                  fontSize: 14,
                  border: "1px solid #aaa",
                  borderRadius: 4,
                  outline: "none",
                  backgroundColor: "white",
                }}
              >
                <option value="">-- Select a reason --</option>
                {REASONS.map((r, idx) => (
                  <option key={idx} value={r}>
                    {r}
                  </option>
                ))}
              </select>

              <div style={{ marginTop: 32, display: "flex", justifyContent: "space-between" }}>
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
                  disabled={!selectedReason}
                  onClick={handleConfirm}
                  style={{
                    backgroundColor: selectedReason ? "#ffa41c" : "#e7e9ec",
                    border: `1px solid ${selectedReason ? "#ff9900" : "#adb1b8"}`,
                    color: selectedReason ? "#111" : "#888",
                    padding: "8px 24px",
                    borderRadius: 4,
                    fontSize: 14,
                    cursor: selectedReason ? "pointer" : "not-allowed",
                    fontWeight: 500,
                  }}
                >
                  Schedule Pickup
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div style={{ textAlign: "center", padding: "20px 0" }}>
              <div
                style={{
                  width: 50,
                  height: 50,
                  borderRadius: "50%",
                  backgroundColor: "#d4edda",
                  color: "#2d7a4f",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 24,
                  margin: "0 auto 16px auto",
                  fontWeight: "bold",
                }}
              >
                ✓
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 500, margin: "0 0 8px 0", color: "#111" }}>
                Your return has been scheduled
              </h2>
              <span style={{ fontSize: 13, color: "#565959" }}>Reference Number: {referenceNum}</span>

              <div
                style={{
                  backgroundColor: "#f9f9f9",
                  padding: 16,
                  borderRadius: 4,
                  border: "1px solid #eee",
                  margin: "24px 0",
                  fontSize: 14,
                  lineHeight: 1.5,
                  textAlign: "left",
                }}
              >
                <div style={{ marginBottom: 8 }}>
                  <strong>Scheduled Pickup:</strong> Tomorrow, 10 AM – 2 PM
                </div>
                <div style={{ color: "#555", fontSize: 13 }}>
                  Our delivery partner will pick up the item and assess its condition. You'll receive an update within 2 hours of pickup.
                </div>
              </div>

              <button
                onClick={() => {
                  if (onComplete) onComplete();
                  handleClose();
                }}
                style={{
                  backgroundColor: "white",
                  border: "1px solid #27726b",
                  color: "#27726b",
                  padding: "8px 36px",
                  borderRadius: 4,
                  fontSize: 14,
                  cursor: "pointer",
                  fontWeight: 600,
                  outline: "none",
                }}
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
