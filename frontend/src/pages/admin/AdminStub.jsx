import React, { useState } from "react";
import Header from "../../components/layout/Header";
import { MOCK_FLYWHEEL, MOCK_HUMAN_REVIEW } from "../../config/mockData";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid
} from "recharts";

const COLORS = ["#27726b", "#36a2eb", "#ffa41c", "#ff6384"];

export default function AdminStub() {
  const [reviews, setReviews] = useState(MOCK_HUMAN_REVIEW);
  const { returns_processed, value_recovered, waste_diverted_kg, co2_avoided_kg, p2p_match_accuracy_current, route_distribution, accuracy_over_30_days } = MOCK_FLYWHEEL;

  function handleAction(returnId, action) {
    setReviews((prev) => prev.filter((item) => item.return_id !== returnId));
    alert(`Item ${returnId} has been successfully ${action === "approve" ? "approved for disposition route" : "sent back for re-grading"}.`);
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 60 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          {/* Dashboard Header */}
          <div style={{ backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd", marginBottom: 20 }}>
            <h1 style={{ fontSize: 24, fontWeight: 400, margin: "0 0 8px 0" }}>
              ReturnIQ Admin Console
            </h1>
            <p style={{ margin: 0, fontSize: 14, color: "#555" }}>
              Central monitoring console. Track system precision, ecological contributions, and resolve edge cases.
            </p>
          </div>

          {/* Stats Cards Row */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 24 }}>
            <div style={{ flex: "1 1 200px", backgroundColor: "white", padding: 16, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "#777", textTransform: "uppercase", fontWeight: "bold" }}>Returns Processed</div>
              <div style={{ fontSize: 24, fontWeight: "bold", color: "#111", marginTop: 6 }}>{returns_processed}</div>
            </div>
            <div style={{ flex: "1 1 200px", backgroundColor: "white", padding: 16, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "#777", textTransform: "uppercase", fontWeight: "bold" }}>Value Recovered</div>
              <div style={{ fontSize: 24, fontWeight: "bold", color: "#27726b", marginTop: 6 }}>₹{value_recovered.toLocaleString()}</div>
            </div>
            <div style={{ flex: "1 1 200px", backgroundColor: "white", padding: 16, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "#777", textTransform: "uppercase", fontWeight: "bold" }}>Waste Diverted</div>
              <div style={{ fontSize: 24, fontWeight: "bold", color: "#2d7a4f", marginTop: 6 }}>{waste_diverted_kg} kg</div>
            </div>
            <div style={{ flex: "1 1 200px", backgroundColor: "white", padding: 16, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "#777", textTransform: "uppercase", fontWeight: "bold" }}>CO₂ Avoided</div>
              <div style={{ fontSize: 24, fontWeight: "bold", color: "#2d7a4f", marginTop: 6 }}>{co2_avoided_kg} kg</div>
            </div>
            <div style={{ flex: "1 1 200px", backgroundColor: "white", padding: 16, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "#777", textTransform: "uppercase", fontWeight: "bold" }}>P2P Precision</div>
              <div style={{ fontSize: 24, fontWeight: "bold", color: "#ffa41c", marginTop: 6 }}>{Math.round(p2p_match_accuracy_current * 100)}%</div>
            </div>
          </div>

          {/* Charts Row */}
          <div style={{ display: "flex", gap: 20, marginBottom: 24, flexWrap: "wrap" }}>
            {/* Route Distribution */}
            <div style={{ flex: 1, minWidth: 350, backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd" }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 16px 0", color: "#111" }}>Route Distribution Share</h2>
              <div style={{ width: "100%", height: 260 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={route_distribution}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {route_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Match Accuracy Graph */}
            <div style={{ flex: 1, minWidth: 350, backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd" }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 16px 0", color: "#111" }}>Model Matching Precision (30 Days)</h2>
              <div style={{ width: "100%", height: 260 }}>
                <ResponsiveContainer>
                  <LineChart data={accuracy_over_30_days} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: "Day", position: "insideBottom", offset: -2 }} tick={{ fontSize: 10 }} />
                    <YAxis domain={[0.6, 1]} tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="accuracy" stroke="#27726b" strokeWidth={2} activeDot={{ r: 8 }} name="Accuracy Rate" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Human Review Queue */}
          <div style={{ backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: "#111" }}>Human Review Escalations</h2>
              <span style={{ fontSize: 12, backgroundColor: "#eb9834", color: "white", padding: "3px 10px", borderRadius: 12, fontWeight: "bold" }}>
                {reviews.length} pending
              </span>
            </div>

            {reviews.length === 0 ? (
              <div style={{ padding: 40, textAlign: "center", border: "1px dashed #ccc", borderRadius: 4, color: "#777" }}>
                All escalations have been reviewed. Queue clear!
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #eee", backgroundColor: "#f9f9f9" }}>
                      <th style={{ padding: 12 }}>Return ID</th>
                      <th style={{ padding: 12 }}>Product Name</th>
                      <th style={{ padding: 12 }}>Suggested Grade</th>
                      <th style={{ padding: 12 }}>AI Confidence</th>
                      <th style={{ padding: 12 }}>Labels</th>
                      <th style={{ padding: 12, textAlign: "right" }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.map((item) => (
                      <tr key={item.return_id} style={{ borderBottom: "1px solid #eee" }}>
                        <td style={{ padding: 12, fontFamily: "monospace" }}>{item.return_id}</td>
                        <td style={{ padding: 12, fontWeight: 500 }}>{item.product}</td>
                        <td style={{ padding: 12 }}>
                          <span style={{ fontSize: 12, fontWeight: "bold", padding: "2px 6px", borderRadius: 4, backgroundColor: "#fff3cd", color: "#eb9834" }}>
                            Grade {item.ai_grade}
                          </span>
                        </td>
                        <td style={{ padding: 12 }}>{item.confidence}%</td>
                        <td style={{ padding: 12 }}>
                          {item.damage_labels.map((lbl, idx) => (
                            <span key={idx} style={{ fontSize: 11, backgroundColor: "#eee", padding: "2px 6px", borderRadius: 10, marginRight: 4 }}>
                              {lbl}
                            </span>
                          ))}
                        </td>
                        <td style={{ padding: 12, textAlign: "right" }}>
                          <button
                            onClick={() => handleAction(item.return_id, "approve")}
                            style={{
                              backgroundColor: "#2d7a4f",
                              color: "white",
                              border: "none",
                              padding: "6px 12px",
                              borderRadius: 4,
                              cursor: "pointer",
                              fontSize: 11,
                              fontWeight: "bold",
                              marginRight: 6,
                            }}
                          >
                            Approve Route
                          </button>
                          <button
                            onClick={() => handleAction(item.return_id, "regrade")}
                            style={{
                              backgroundColor: "#c0392b",
                              color: "white",
                              border: "none",
                              padding: "6px 12px",
                              borderRadius: 4,
                              cursor: "pointer",
                              fontSize: 11,
                              fontWeight: "bold",
                            }}
                          >
                            Re-grade
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
