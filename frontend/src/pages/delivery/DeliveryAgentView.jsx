import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "../../components/layout/Header";

const DEFAULT_MOCK_PICKUPS = [
  {
    return_id: "d001",
    product: "Nike Air Max 270",
    customer: "Archi",
    pickup: "14 MG Road, Sector 7",
    window: "Tomorrow, 10 AM – 2 PM",
  },
  {
    return_id: "d002",
    product: "boAt Rockerz 450",
    customer: "Sarthak",
    pickup: "7 Park Street, Connaught Place",
    window: "Tomorrow, 2 PM – 6 PM",
  },
];

const DEFAULT_MOCK_DELIVERIES = [
  {
    return_id: "d003",
    product: "Puma T-Shirt",
    buyer: "Rohan",
    dropoff: "Amazon Locker #12",
    qr_token: "demo-valid-token",
    buyer_distance_km: 1.1,
  },
];

export default function DeliveryAgentView() {
  const [pickups, setPickups] = useState([]);
  const [deliveries, setDeliveries] = useState(DEFAULT_MOCK_DELIVERIES);
  const [stats, setStats] = useState({ pickups: 3, graded: 3, flagged: 0 });

  useEffect(() => {
    function loadData() {
      // Load customer scheduled returns
      const returns = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
      const activePickups = returns
        .filter((r) => r.status === "PENDING_PICKUP")
        .map((r) => ({
          return_id: r.return_id,
          product: r.product_name,
          customer: "Customer",
          pickup: "Customer Address",
          window: r.pickup_window || "Tomorrow, 10 AM – 2 PM",
        }));

      // If no customer scheduled returns, show mock ones
      setPickups(activePickups.length > 0 ? activePickups : DEFAULT_MOCK_PICKUPS);

      // Load active deliveries (matched P2P returns)
      const matched = returns
        .filter((r) => r.status === "P2P_MATCHED")
        .map((r) => ({
          return_id: r.return_id,
          product: r.product_name,
          buyer: "Matched Buyer",
          dropoff: "Amazon Locker #4",
          qr_token: "demo-valid-token",
          buyer_distance_km: 2.3,
        }));
      if (matched.length > 0) {
        setDeliveries([...matched, ...DEFAULT_MOCK_DELIVERIES]);
      } else {
        setDeliveries(DEFAULT_MOCK_DELIVERIES);
      }

      // Load stats
      const todayStats = JSON.parse(localStorage.getItem("returniq_delivery_stats") || "null");
      if (todayStats) {
        setStats(todayStats);
      } else {
        const initialStats = { pickups: 3, graded: 3, flagged: 0 };
        localStorage.setItem("returniq_delivery_stats", JSON.stringify(initialStats));
        setStats(initialStats);
      }
    }

    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif", paddingBottom: 80 }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div style={{ maxWidth: 700, margin: "0 auto" }}>
          
          {/* SECTION 1: Pending Customer Pickups */}
          <div style={{ marginBottom: 32 }}>
            <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0, color: "#111" }}>
                Pending Customer Pickups
              </h2>
              <span style={{ backgroundColor: "#fff3cd", color: "#856404", padding: "2px 8px", borderRadius: 12, fontSize: 12, marginLeft: 12, fontWeight: "bold" }}>
                {pickups.length} scheduled
              </span>
            </div>

            {pickups.map((item) => (
              <div
                key={item.return_id}
                style={{
                  backgroundColor: "white",
                  borderLeft: "4px solid #27726b",
                  borderRadius: 4,
                  padding: 16,
                  marginBottom: 12,
                  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                  border: "1px solid #ddd",
                  borderLeftWidth: 4,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                  <span style={{ fontSize: 15, fontWeight: "bold", color: "#111" }}>{item.product}</span>
                  <span style={{ fontSize: 11, color: "#767676" }}>Window: {item.window}</span>
                </div>
                <div style={{ fontSize: 13, color: "#555", marginBottom: 12 }}>
                  <strong>📍 Address: </strong> {item.pickup}
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <Link
                    to={`/delivery/pickup/${item.return_id}`}
                    style={{
                      backgroundColor: "#27726b",
                      color: "white",
                      border: "none",
                      padding: "8px 20px",
                      borderRadius: 4,
                      fontSize: 13,
                      fontWeight: "bold",
                      textDecoration: "none",
                      textAlign: "center",
                    }}
                  >
                    Start Pickup
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* SECTION 2: Active P2P Deliveries (Leg 2) */}
          <div>
            <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
              <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0, color: "#111" }}>
                P2P Matched Deliveries
              </h2>
              <span style={{ backgroundColor: "#d4edda", color: "#155724", padding: "2px 8px", borderRadius: 12, fontSize: 12, marginLeft: 12, fontWeight: "bold" }}>
                {deliveries.length} active
              </span>
            </div>

            {deliveries.map((item) => (
              <div
                key={item.return_id}
                style={{
                  backgroundColor: "white",
                  borderLeft: "4px solid #0056b3",
                  borderRadius: 4,
                  padding: 16,
                  marginBottom: 12,
                  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                  border: "1px solid #ddd",
                  borderLeftWidth: 4,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                  <span style={{ fontSize: 15, fontWeight: "bold", color: "#111" }}>{item.product}</span>
                  <span style={{ fontSize: 11, color: "#0056b3", fontWeight: "bold" }}>P2P Direct</span>
                </div>
                <div style={{ fontSize: 13, color: "#555", marginBottom: 12 }}>
                  <strong>📦 Locker/Dropoff: </strong> {item.dropoff} ({item.buyer_distance_km}km distance)
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <Link
                    to={`/delivery/scan/${item.qr_token}`}
                    style={{
                      backgroundColor: "#ffa41c",
                      border: "1px solid #ff9900",
                      color: "#111",
                      padding: "8px 20px",
                      borderRadius: 4,
                      fontSize: 13,
                      fontWeight: "bold",
                      textDecoration: "none",
                      textAlign: "center",
                    }}
                  >
                    Scan QR to Deliver
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Stats Bottom Bar */}
      <footer
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: "#131921",
          color: "white",
          padding: "14px 24px",
          display: "flex",
          justifyContent: "space-around",
          zIndex: 50,
          borderTop: "2px solid #27726b",
          fontFamily: "monospace",
          fontSize: 13,
        }}
      >
        <span>Picked up today: <strong>{stats.pickups}</strong></span>
        <span>Graded: <strong>{stats.graded}</strong></span>
        <span>Flagged: <strong>{stats.flagged}</strong></span>
      </footer>
    </div>
  );
}
