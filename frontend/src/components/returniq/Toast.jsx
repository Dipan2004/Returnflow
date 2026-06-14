import React, { useEffect } from "react";

export default function Toast({ message, visible, onDismiss }) {
  useEffect(() => {
    if (!visible) return;
    const t = setTimeout(onDismiss, 5000);
    return () => clearTimeout(t);
  }, [visible, onDismiss]);

  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        zIndex: 200,
        width: 320,
        transform: visible ? "translateX(0)" : "translateX(130%)",
        opacity: visible ? 1 : 0,
        transition: "transform 0.3s ease, opacity 0.3s ease",
      }}
    >
      <div
        style={{
          background: "white",
          borderLeft: "4px solid #27726b",
          borderRadius: 8,
          padding: 16,
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          fontFamily: "sans-serif",
        }}
      >
        <span style={{ fontSize: 20 }}>🎉</span>
        <span style={{ fontSize: 13, color: "#131921", lineHeight: 1.5 }}>{message}</span>
      </div>
    </div>
  );
}
