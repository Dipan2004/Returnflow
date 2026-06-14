import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useReturnFlow } from "../../hooks/useReturnFlow";
import { MOCK_HEALTH_CARD } from "../../config/mockData";
import Header from "../layout/Header";
import Navbar from "../layout/Navbar";
import Sidebar from "../layout/Sidebar";

const ROUTE_EMOJIS = {
  P2P: "🔁",
  RESELL: "🛒",
  REFURBISH: "🔧",
  DONATE: "🤝",
};

export default function HealthCardPage() {
  const { return_id } = useParams();
  const { getHealthCard, loading, error } = useReturnFlow();
  const [data, setData] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    async function fetchData() {
      const result = await getHealthCard(return_id);
      setData(result || MOCK_HEALTH_CARD);
    }
    fetchData();
  }, [return_id]);

  if (loading || !data) {
    return (
      <div style={{ minHeight: "100vh", backgroundColor: "white" }}>
        <Header onReturnClick={() => {}} />
        <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: "50%",
              border: "4px solid #f3f3f3",
              borderTopColor: "#27726b",
              animation: "spin 1s linear infinite",
            }}
          />
        </div>
      </div>
    );
  }

  // Stepper steps configuration
  const steps = ["Submitted", "Graded"];
  if (data.status === "PENDING_HUMAN_REVIEW") {
    steps.push("Pending Review");
  }
  steps.push("Matched", "Delivered");

  const statusIndex = {
    PENDING_BUYER_ACCEPT: 1,
    PENDING_HUMAN_REVIEW: 2,
    P2P_MATCHED: 2,
    DELIVERED: steps.length - 1,
  }[data.status] ?? 1;

  return (
    <div style={{ backgroundColor: "#fcfcfc", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 60 }}>
      <Header onReturnClick={() => {}} />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div style={{ maxWidth: 940, margin: "0 auto", padding: "24px 16px" }}>
        {/* Breadcrumb */}
        <div style={{ fontSize: 13, color: "#0066c0", marginBottom: 16 }}>
          <Link to="/" style={{ color: "inherit", textDecoration: "none" }}>Your Account</Link> ›{" "}
          <span style={{ cursor: "pointer" }}>Returns & Orders</span> ›{" "}
          <span style={{ color: "#111" }}>Return #{data.return_id.slice(0, 8)}</span>
        </div>

        {/* Content Box */}
        <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: 4, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          {/* Header Row */}
          <div style={{ borderBottom: "1px solid #eee", paddingBottom: 16, marginBottom: 20 }}>
            <h1 style={{ fontSize: 24, fontWeight: 400, margin: "0 0 4px 0", color: "#111" }}>
              Return Health Card
            </h1>
            <span style={{ fontSize: 13, color: "#565959" }}>ID: {data.return_id}</span>
          </div>

          {/* Product Section */}
          <div style={{ display: "flex", gap: 20, marginBottom: 24 }}>
            <div style={{ display: "flex", gap: 8 }}>
              {data.image_urls.map((img, idx) => (
                <div key={idx} style={{ width: 80, height: 80, border: "1px solid #eee", borderRadius: 4, overflow: "hidden" }}>
                  <img src={img} alt={`Product thumbnail ${idx}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                </div>
              ))}
            </div>
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 600, margin: "0 0 6px 0", color: "#0066c0" }}>
                {data.product_name}
              </h2>
              <div style={{ fontSize: 13, color: "#565959" }}>
                SKU: <code>{data.sku_id}</code> | Created: {new Date(data.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Timeline Horizontal Stepper */}
          <div style={{ margin: "32px 0 24px 0", padding: "0 10px" }}>
            <div style={{ display: "flex", alignItems: "center", position: "relative" }}>
              {steps.map((stepName, idx) => {
                const isCompleted = idx < statusIndex;
                const isCurrent = idx === statusIndex;
                return (
                  <React.Fragment key={idx}>
                    {/* Circle */}
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: "50%",
                        border: isCompleted || isCurrent ? "2px solid #27726b" : "2px solid #ddd",
                        backgroundColor: isCompleted ? "#27726b" : "white",
                        color: isCompleted ? "white" : isCurrent ? "#27726b" : "#aaa",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 12,
                        fontWeight: "bold",
                        zIndex: 2,
                      }}
                    >
                      {isCompleted ? "✓" : idx + 1}
                    </div>

                    {/* Connecting line */}
                    {idx < steps.length - 1 && (
                      <div
                        style={{
                          flex: 1,
                          height: 3,
                          backgroundColor: idx < statusIndex ? "#27726b" : "#ddd",
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
              {steps.map((stepName, idx) => {
                const isCurrent = idx === statusIndex;
                return (
                  <span
                    key={idx}
                    style={{
                      fontSize: 12,
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

          {/* Review Banner */}
          {data.status === "PENDING_HUMAN_REVIEW" && (
            <div
              style={{
                backgroundColor: "#fff3cd",
                padding: "12px 16px",
                borderRadius: 4,
                fontSize: 13,
                color: "#856404",
                marginBottom: 20,
                border: "1px solid #ffeeba",
              }}
            >
              ℹ️ Our team is reviewing this item. Estimated: 2–4 hours.
            </div>
          )}

          {/* Grid Cards Container */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Condition Card */}
            <div style={{ borderLeft: "4px solid #27726b", backgroundColor: "#f9f9f9", padding: 16, borderRadius: "0 4px 4px 0" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 15, fontWeight: 700, color: "#111" }}>Condition Metrics</h3>
              <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                <div
                  style={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 24,
                    fontWeight: "bold",
                    backgroundColor:
                      data.grade === "A" ? "#d4edda" : data.grade === "B" ? "#fff3cd" : "#f8d7da",
                    color:
                      data.grade === "A" ? "#2d7a4f" : data.grade === "B" ? "#eb9834" : "#c0392b",
                  }}
                >
                  {data.grade}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, color: "#666" }}>
                    Verified grade: <strong>Grade {data.grade}</strong> ({data.confidence}% AI confidence)
                  </div>
                  <blockquote style={{ margin: "8px 0 0 0", padding: "6px 10px", backgroundColor: "#fff", borderLeft: "2px solid #ccc", fontSize: 12, color: "#555", fontStyle: "italic" }}>
                    {data.damage_description}
                  </blockquote>
                </div>
              </div>
            </div>

            {/* Disposition Card */}
            <div style={{ border: "1px solid #eee", padding: 16, borderRadius: 4, backgroundColor: "white" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 15, fontWeight: 700, color: "#111" }}>Disposition Strategy</h3>
              <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 16, fontWeight: "bold", color: "#27726b" }}>
                    <span>{ROUTE_EMOJIS[data.route] || "🔁"}</span>
                    <span>{data.route} Match</span>
                  </div>
                  <p style={{ margin: "8px 0 0 0", fontSize: 12, color: "#565959", fontStyle: "italic", lineHeight: 1.4 }}>
                    {data.route_reason}
                  </p>
                </div>
                <div style={{ display: "flex", gap: 12 }}>
                  <div style={{ backgroundColor: "#f0faf8", border: "1px solid #bce1dd", borderRadius: 4, padding: "8px 12px", textAlign: "center", minWidth: 100 }}>
                    <div style={{ fontSize: 10, color: "#27726b", textTransform: "uppercase", fontWeight: "bold" }}>Recovery Value</div>
                    <div style={{ fontSize: 16, fontWeight: "bold", color: "#27726b", marginTop: 4 }}>₹{data.recovery_value}</div>
                  </div>
                  <div style={{ backgroundColor: "#eafaf1", border: "1px solid #c7f3d6", borderRadius: 4, padding: "8px 12px", textAlign: "center", minWidth: 100 }}>
                    <div style={{ fontSize: 10, color: "#2d7a4f", textTransform: "uppercase", fontWeight: "bold" }}>Value Saved</div>
                    <div style={{ fontSize: 16, fontWeight: "bold", color: "#2d7a4f", marginTop: 4 }}>+₹{data.value_delta}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* QR Section */}
            {data.route === "P2P" && (
              <div style={{ border: "1px solid #eee", padding: 16, borderRadius: 4, display: "flex", flexDirection: "column", alignItems: "center", backgroundColor: "white" }}>
                <h3 style={{ margin: "0 0 12px 0", fontSize: 15, fontWeight: 700, color: "#111", alignSelf: "flex-start" }}>Verification Pass</h3>
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${data.return_id}`}
                  alt="Validation QR"
                  style={{ width: 140, height: 140, padding: 6, border: "1px solid #eee", borderRadius: 4 }}
                />
                <span style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
                  Scan code during carrier handoff to validate condition integrity.
                </span>
              </div>
            )}

            {/* CO₂ Carbon Offset Card */}
            <div style={{ backgroundColor: "#27726b", color: "white", padding: 14, borderRadius: 4, display: "flex", alignItems: "center", gap: 10, fontSize: 13 }}>
              <span>♻️</span>
              <span>
                <strong>2.3 kg CO₂ avoided</strong> — equivalent to 1 tree planted by bypassing warehouse back-shipping.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
