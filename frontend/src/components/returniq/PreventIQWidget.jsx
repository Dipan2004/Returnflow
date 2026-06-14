import React from "react";

export default function PreventIQWidget({
  return_probability,
  category_avg_return_rate,
  above_category_avg,
  size_warning,
  recommended_size,
  onSwitchSize,
}) {
  const probPercent = Math.round(return_probability * 100);
  const avgPercent = Math.round(category_avg_return_rate * 100);

  return (
    <div
      style={{
        borderLeft: "4px solid #27726b",
        backgroundColor: "white",
        padding: "12px 16px",
        margin: "16px 0",
        borderRadius: "0 4px 4px 0",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        fontFamily: "sans-serif",
      }}
    >
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <span style={{ fontSize: 13, color: "#27726b", fontWeight: 500 }}>ReturnIQ Insight</span>
        <span style={{ fontSize: 11, color: "#767676" }}>Powered by AI</span>
      </div>

      {/* Return rate bar */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <span style={{ fontSize: 12, color: "#767676" }}>Return rate for this item</span>
          <span
            style={{
              fontSize: 10,
              padding: "2px 6px",
              borderRadius: 8,
              fontWeight: "bold",
              backgroundColor: above_category_avg ? "#f8d7da" : "#d4edda",
              color: above_category_avg ? "#c0392b" : "#2d7a4f",
            }}
          >
            {above_category_avg ? "↑ Above average" : "↓ Below average"}
          </span>
        </div>

        {/* Bar container */}
        <div style={{ width: "100%", height: 8, backgroundColor: "#eee", borderRadius: 4, position: "relative", overflow: "hidden" }}>
          {/* Average bar (Green) */}
          <div
            style={{
              height: "100%",
              width: `${avgPercent}%`,
              backgroundColor: "#2d7a4f",
              position: "absolute",
              left: 0,
              top: 0,
            }}
          />
          {/* Predict bar (Orange) */}
          <div
            style={{
              height: "100%",
              width: `${probPercent}%`,
              backgroundColor: "#eb9834",
              opacity: 0.75,
              position: "absolute",
              left: 0,
              top: 0,
            }}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#767676", marginTop: 4 }}>
          <span>{probPercent}% of buyers return this</span>
          <span>Category avg {avgPercent}%</span>
        </div>
      </div>

      {/* Warning box */}
      {size_warning && (
        <div
          style={{
            backgroundColor: "#fff3cd",
            padding: "10px 12px",
            borderRadius: 4,
            marginTop: 8,
            border: "1px solid #ffeeba",
          }}
        >
          <p style={{ margin: 0, fontSize: 12, color: "#856404", lineHeight: 1.4 }}>
            {size_warning}
          </p>
          {recommended_size && onSwitchSize && (
            <button
              onClick={() => onSwitchSize(recommended_size)}
              style={{
                marginTop: 8,
                backgroundColor: "white",
                border: "1px solid #27726b",
                color: "#27726b",
                padding: "4px 8px",
                fontSize: 11,
                borderRadius: 3,
                cursor: "pointer",
                fontWeight: 500,
              }}
            >
              Switch to Size {recommended_size}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
