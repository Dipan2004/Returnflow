import React from "react";
import { useAuth } from "../../contexts/AuthContext";
import Header from "../../components/layout/Header";
import { MOCK_SELLER_RETURNS } from "../../config/mockData";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function SellerStub() {
  const { user } = useAuth();

  // Summary calculations
  const totalReturns = MOCK_SELLER_RETURNS.length;
  const totalRecovery = MOCK_SELLER_RETURNS.reduce((sum, item) => sum + item.recovery, 0);

  // Transform data for Recharts
  const chartData = MOCK_SELLER_RETURNS.map((item) => ({
    name: item.product.length > 15 ? item.product.slice(0, 12) + "..." : item.product,
    Recovery: item.recovery,
  }));

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif" }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          {/* Header section */}
          <div style={{ backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd", marginBottom: 20 }}>
            <h1 style={{ fontSize: 24, fontWeight: 400, margin: "0 0 8px 0" }}>
              Seller Returns Dashboard
            </h1>
            <p style={{ margin: 0, fontSize: 14, color: "#555" }}>
              Welcome back, <strong>{user?.name || "Seller"}</strong>. Monitor item returns and route recoveries.
            </p>
          </div>

          {/* Cards Grid */}
          <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
            <div style={{ flex: 1, backgroundColor: "white", padding: 20, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 12, color: "#666", textTransform: "uppercase", fontWeight: "bold" }}>Total Returns</div>
              <div style={{ fontSize: 28, fontWeight: "bold", color: "#111", marginTop: 8 }}>{totalReturns}</div>
            </div>
            <div style={{ flex: 1, backgroundColor: "white", padding: 20, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 12, color: "#666", textTransform: "uppercase", fontWeight: "bold" }}>Value Recovered</div>
              <div style={{ fontSize: 28, fontWeight: "bold", color: "#27726b", marginTop: 8 }}>₹{totalRecovery}</div>
            </div>
            <div style={{ flex: 1, backgroundColor: "white", padding: 20, borderRadius: 4, border: "1px solid #ddd", textAlign: "center" }}>
              <div style={{ fontSize: 12, color: "#666", textTransform: "uppercase", fontWeight: "bold" }}>Sustainability Index</div>
              <div style={{ fontSize: 28, fontWeight: "bold", color: "#2d7a4f", marginTop: 8 }}>A+ (100%)</div>
            </div>
          </div>

          {/* Chart Section */}
          <div style={{ backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd", marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 16px 0", color: "#111" }}>
              Recovery Value by Product
            </h2>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Recovery" fill="#27726b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Table section */}
          <div style={{ backgroundColor: "white", padding: 24, borderRadius: 4, border: "1px solid #ddd" }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, margin: "0 0 16px 0", color: "#111" }}>
              Return Shipments Queue
            </h2>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #eee", backgroundColor: "#f9f9f9" }}>
                    <th style={{ padding: 12 }}>ID</th>
                    <th style={{ padding: 12 }}>Product</th>
                    <th style={{ padding: 12 }}>Grade</th>
                    <th style={{ padding: 12 }}>Route Strategy</th>
                    <th style={{ padding: 12 }}>Recovery</th>
                    <th style={{ padding: 12 }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {MOCK_SELLER_RETURNS.map((item) => (
                    <tr key={item.return_id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: 12, fontFamily: "monospace" }}>{item.return_id}</td>
                      <td style={{ padding: 12, fontWeight: 500 }}>{item.product}</td>
                      <td style={{ padding: 12 }}>
                        <span
                          style={{
                            fontSize: 11,
                            fontWeight: "bold",
                            padding: "2px 6px",
                            borderRadius: 4,
                            backgroundColor:
                              item.grade === "A" ? "#d4edda" : item.grade === "B" ? "#fff3cd" : "#f8d7da",
                            color:
                              item.grade === "A" ? "#2d7a4f" : item.grade === "B" ? "#eb9834" : "#c0392b",
                          }}
                        >
                          Grade {item.grade}
                        </span>
                      </td>
                      <td style={{ padding: 12 }}>{item.route}</td>
                      <td style={{ padding: 12, fontWeight: "bold", color: item.recovery > 0 ? "#27726b" : "#777" }}>
                        ₹{item.recovery}
                      </td>
                      <td style={{ padding: 12 }}>{item.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
