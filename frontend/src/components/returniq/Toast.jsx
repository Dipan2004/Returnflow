import React, { useEffect } from "react";

const TYPE_CONFIG = {
  success: { icon: "✅", borderColor: "#27726b" },
  error: { icon: "❌", borderColor: "#c40000" },
};

export default function Toast({ message, type = "success", visible, onDismiss, onClose }) {
  const dismiss = onDismiss || onClose;

  useEffect(() => {
    if (!visible) return;
    const t = setTimeout(dismiss, 3000);
    return () => clearTimeout(t);
  }, [visible, dismiss]);

  const config = TYPE_CONFIG[type] || TYPE_CONFIG.success;

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
        pointerEvents: visible ? "auto" : "none",
      }}
    >
      <div
        style={{
          background: "white",
          borderLeft: `4px solid ${config.borderColor}`,
          borderRadius: 8,
          padding: 16,
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          fontFamily: "sans-serif",
        }}
      >
        <span style={{ fontSize: 20 }}>{config.icon}</span>
        <span style={{ fontSize: 13, color: "#131921", lineHeight: 1.5, flex: 1 }}>{message}</span>
        <button
          onClick={dismiss}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: 16,
            color: "#767676",
            padding: 0,
            lineHeight: 1,
          }}
          aria-label="Dismiss"
        >
          ×
        </button>
      </div>
    </div>
  );
}
