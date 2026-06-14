import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useDelivery } from "../../hooks/useDelivery";
import Header from "../../components/layout/Header";

export default function QRScanPage() {
  const { qr_token } = useParams();
  const navigate = useNavigate();
  const { verifyQR, confirmHandoff } = useDelivery();

  const [scanState, setScanState] = useState("scanning"); // scanning, success, error
  const [resultData, setResultData] = useState(null);
  const [loadingAction, setLoadingAction] = useState(false);

  useEffect(() => {
    async function performScan() {
      setScanState("scanning");
      // Simulate scan delay
      const res = await verifyQR(qr_token);
      if (res && res.valid) {
        setScanState("success");
        setResultData(res);
      } else {
        setScanState("error");
        setResultData(res);
      }
    }
    performScan();
  }, [qr_token]);

  async function handleHandoff() {
    if (!resultData) return;
    setLoadingAction(true);
    try {
      await confirmHandoff(resultData.return_id);
      alert("Handoff confirmed successfully!");
      navigate("/delivery");
    } catch (e) {
      alert("Error confirming handoff: " + e.message);
    } finally {
      setLoadingAction(false);
    }
  }

  return (
    <div style={{ backgroundColor: "#f3f3f3", minHeight: "100vh", fontFamily: "sans-serif" }}>
      <Header onReturnClick={() => {}} />

      <main style={{ padding: 24 }}>
        <div
          style={{
            maxWidth: 500,
            margin: "0 auto",
            backgroundColor: "white",
            border: "1px solid #ddd",
            borderRadius: 4,
            padding: 24,
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          }}
        >
          {scanState === "scanning" && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 0" }}>
              <div
                style={{
                  width: 240,
                  height: 240,
                  border: "4px solid #27726b",
                  borderRadius: 8,
                  position: "relative",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  backgroundColor: "#222",
                  marginBottom: 24,
                  overflow: "hidden",
                }}
              >
                {/* Scanner pulse line */}
                <div
                  style={{
                    position: "absolute",
                    width: "100%",
                    height: 2,
                    backgroundColor: "#00ffcc",
                    top: 0,
                    left: 0,
                    animation: "shimmer 2s infinite linear",
                    boxShadow: "0 0 8px #00ffcc",
                  }}
                />
                <span style={{ fontSize: 13, color: "#aaa" }}>Simulating Camera Stream...</span>
              </div>
              <p style={{ fontSize: 15, fontWeight: "bold", color: "#333", margin: 0 }}>
                Aligning ReturnIQ health QR code...
              </p>
            </div>
          )}

          {scanState === "success" && resultData && (
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  backgroundColor: "#d4edda",
                  color: "#2d7a4f",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 28,
                  margin: "0 auto 16px auto",
                  fontWeight: "bold",
                }}
              >
                ✓
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 400, margin: "0 0 16px 0", color: "#111" }}>
                QR Validated Successfully
              </h2>

              <div
                style={{
                  textAlign: "left",
                  fontSize: 13,
                  backgroundColor: "#f9f9f9",
                  padding: 16,
                  borderRadius: 4,
                  border: "1px solid #eee",
                  marginBottom: 24,
                  lineHeight: 1.5,
                }}
              >
                <div style={{ marginBottom: 6 }}>
                  <strong>Item:</strong> {resultData.product_name}
                </div>
                <div style={{ marginBottom: 6 }}>
                  <strong>Condition Grade:</strong> Grade {resultData.grade}
                </div>
                <div style={{ marginBottom: 6 }}>
                  <strong>Pickup location:</strong> {resultData.pickup_address}
                </div>
                <div>
                  <strong>Dropoff location:</strong> {resultData.delivery_address}
                </div>
              </div>

              <button
                disabled={loadingAction}
                onClick={handleHandoff}
                style={{
                  width: "100%",
                  backgroundColor: "#ffa41c",
                  border: "1px solid #ff9900",
                  color: "#111",
                  padding: "10px 0",
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: "pointer",
                  outline: "none",
                }}
              >
                {loadingAction ? "Confirming Handoff..." : "Confirm Handoff"}
              </button>
            </div>
          )}

          {scanState === "error" && resultData && (
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  backgroundColor: "#f8d7da",
                  color: "#c0392b",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 28,
                  margin: "0 auto 16px auto",
                  fontWeight: "bold",
                }}
              >
                !
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 400, margin: "0 0 8px 0", color: "#c0392b" }}>
                Validation Error
              </h2>
              <p style={{ fontSize: 14, color: "#666", margin: "0 0 20px 0" }}>
                This QR code appears invalid or has been modified.
              </p>

              <div
                style={{
                  textAlign: "left",
                  fontSize: 13,
                  backgroundColor: "#fff8f8",
                  padding: 16,
                  borderRadius: 4,
                  border: "1px solid #f8d7da",
                  marginBottom: 24,
                  color: "#c0392b",
                }}
              >
                <div style={{ marginBottom: 6 }}>
                  <strong>Reason:</strong> {resultData.reason || "Invalid verification pass"}
                </div>
                {resultData.scanned_at && (
                  <div style={{ marginBottom: 6 }}>
                    <strong>Scanned At:</strong> {new Date(resultData.scanned_at).toLocaleString()}
                  </div>
                )}
                <div>
                  <strong>Alert Flag:</strong> {resultData.alert || "TAMPERING_DANGER"}
                </div>
              </div>

              <button
                onClick={() => navigate("/delivery")}
                style={{
                  width: "100%",
                  backgroundColor: "white",
                  border: "1px solid #c0392b",
                  color: "#c0392b",
                  padding: "10px 0",
                  borderRadius: 4,
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: "pointer",
                  outline: "none",
                }}
              >
                Return to Pickups List
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
