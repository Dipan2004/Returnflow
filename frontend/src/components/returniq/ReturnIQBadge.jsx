import React, { useState } from "react";
import { useCart } from "../../contexts/CartContext";

export default function ReturnIQBadge({ grade, price, distanceKm, productId }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const { openHealthCardModal } = useCart();

  const handleBadgeClick = (e) => {
    e.stopPropagation();
    if (productId) {
      openHealthCardModal(productId);
    }
  };

  return (
    <div
      style={{ position: "absolute", bottom: 8, left: 8, zIndex: 15 }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      onClick={handleBadgeClick}
    >
      <div style={{
        background: "#27726b", color: "white", fontSize: 11,
        padding: "3px 8px", borderRadius: 12, cursor: "pointer", display: "inline-block",
      }}>
        ♻ Grade {grade} — ₹{price}
      </div>

      {showTooltip && (
        <div style={{
          position: "absolute", bottom: 28, left: 0,
          background: "white", border: "1px solid #ddd", borderRadius: 4,
          padding: "6px 10px", whiteSpace: "nowrap",
          fontSize: 11, color: "#131921", zIndex: 20,
          boxShadow: "0 2px 4px rgba(0,0,0,0.15)",
        }}>
          {distanceKm}km away
          <span
            onClick={handleBadgeClick}
            style={{ color: "#27726b", display: "block", marginTop: 4, cursor: "pointer", fontWeight: 600 }}
          >
            View Health Card →
          </span>
        </div>
      )}
    </div>
  );
}
