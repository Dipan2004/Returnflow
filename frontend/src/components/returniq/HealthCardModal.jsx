import React from "react";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";

export default function HealthCardModal() {
  const { healthCardProductId, healthCardModalOpen, closeHealthCardModal, addToCart } = useCart();

  if (!healthCardModalOpen || !healthCardProductId) return null;

  const product = products.find((p) => p.id === healthCardProductId);
  if (!product) return null;

  // Fallback defaults if grade is missing
  const grade = product.returniqGrade || "A";
  const preOwnedPrice = product.returniqPrice || Math.floor(product.price * 0.75);
  const co2Avoided = product.returniqCO2 || 1.1;

  // Condition reports details based on grade
  const condition = {
    A: {
      exterior: "Excellent — no scratches, like new condition",
      functionality: "100% verified — fully tested and operational",
      accessories: "Original packaging and all accessories included"
    },
    B: {
      exterior: "Very Good — minor scuffs, barely visible",
      functionality: "100% verified — fully tested and operational",
      accessories: "Original packaging showing shelf wear, accessories included"
    },
    C: {
      exterior: "Good — moderate signs of use/cosmetic scratches",
      functionality: "100% verified — fully tested and operational",
      accessories: "Generic packaging, standard charging cables included"
    }
  }[grade] || {
    exterior: "Verified good condition",
    functionality: "Tested and functional",
    accessories: "Standard accessories included"
  };

  const badgeColor = {
    A: "#007600",
    B: "#f0a500",
    C: "#767676"
  }[grade] || "#007600";

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: 16
      }}
      onClick={closeHealthCardModal}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: 12,
          width: "100%",
          maxWidth: "520px",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: 24,
          position: "relative",
          boxShadow: "0 10px 30px rgba(0,0,0,0.25)",
          color: "#0F1111",
          fontFamily: "Arial, sans-serif"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={closeHealthCardModal}
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            background: "none",
            border: "none",
            fontSize: 24,
            cursor: "pointer",
            color: "#565959"
          }}
        >
          &times;
        </button>

        {/* Modal Title */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
          <span style={{ fontSize: 20 }}>♻️</span>
          <h2 style={{ fontSize: 18, fontWeight: "bold", margin: 0, color: "#27726b" }}>
            ReturnIQ Certified Health Card
          </h2>
        </div>

        {/* Product Info Row */}
        <div style={{ display: "flex", gap: 16, borderBottom: "1px solid #e7e7e7", paddingBottom: 16, marginBottom: 16 }}>
          <img
            src={product.image}
            alt={product.name}
            style={{ width: 80, height: 80, objectFit: "contain", border: "1px solid #eee", borderRadius: 6 }}
          />
          <div>
            <span style={{ fontSize: 12, color: "#565959" }}>{product.brand}</span>
            <h3 style={{ fontSize: 15, fontWeight: "bold", margin: "2px 0 6px 0", lineHeight: "1.3" }}>
              {product.name}
            </h3>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span style={{ fontSize: 18, fontWeight: "bold", color: badgeColor }}>₹{preOwnedPrice}</span>
              <span style={{ fontSize: 13, textDecoration: "line-through", color: "#565959" }}>
                Original: ₹{product.price}
              </span>
            </div>
          </div>
        </div>

        {/* Grade Large circle graphic */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", backgroundColor: "#f6faf9", border: "1px solid #e3ebe8", borderRadius: 8, padding: 16, marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 12, textTransform: "uppercase", fontWeight: "bold", color: "#565959" }}>
              Certified Condition
            </div>
            <div style={{ fontSize: 22, fontWeight: "bold", color: badgeColor, marginTop: 4 }}>
              Grade {grade}
            </div>
            <span style={{ fontSize: 12, color: "#007600", display: "inline-block", marginTop: 4, fontWeight: "bold" }}>
              🌱 {co2Avoided} kg CO₂ Saved
            </span>
          </div>

          <div style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            backgroundColor: badgeColor,
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 28,
            fontWeight: "bold",
            boxShadow: "0 4px 10px rgba(0,0,0,0.15)"
          }}>
            {grade}
          </div>
        </div>

        {/* Condition details checklist */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 24 }}>
          <h4 style={{ fontSize: 14, fontWeight: "bold", margin: 0 }}>Assessment Breakdown</h4>
          
          <div style={{ display: "flex", gap: 10, fontSize: 13 }}>
            <span style={{ color: "#007600" }}>✓</span>
            <div>
              <strong>Exterior:</strong> {condition.exterior}
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, fontSize: 13 }}>
            <span style={{ color: "#007600" }}>✓</span>
            <div>
              <strong>Functionality:</strong> {condition.functionality}
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, fontSize: 13 }}>
            <span style={{ color: "#007600" }}>✓</span>
            <div>
              <strong>In the Box:</strong> {condition.accessories}
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div style={{ display: "flex", gap: 12, alignItems: "center", borderTop: "1px solid #e7e7e7", paddingTop: 16 }}>
          {/* QR validation */}
          <div style={{ textAlign: "center" }}>
            <div style={{
              width: 70,
              height: 70,
              border: "1px solid #ddd",
              padding: 4,
              borderRadius: 4,
              backgroundColor: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 10,
              color: "#aaa",
              fontWeight: "bold"
            }}>
              {/* QR Mockup */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 2, width: "100%", height: "100%" }}>
                {Array.from({ length: 25 }).map((_, i) => (
                  <div key={i} style={{ backgroundColor: Math.random() > 0.4 ? "#000" : "#fff" }} />
                ))}
              </div>
            </div>
            <span style={{ fontSize: 10, color: "#565959", display: "block", marginTop: 4 }}>
              Scan to Verify
            </span>
          </div>

          {/* Add to Cart button */}
          <div style={{ flex: 1 }}>
            <button
              onClick={() => {
                addToCart(product.id, 1, "Standard", true);
                closeHealthCardModal();
                alert(`Added Pre-Owned Grade ${grade} version of "${product.name}" to your cart!`);
              }}
              style={{
                width: "100%",
                backgroundColor: "#ffd814",
                border: "1px solid #fcd200",
                borderRadius: 20,
                color: "#0f1111",
                padding: "10px 16px",
                fontSize: 14,
                fontWeight: "bold",
                cursor: "pointer",
                boxShadow: "0 2px 5px rgba(213,217,217,0.5)",
                outline: "none"
              }}
            >
              Add Pre-Owned to Cart
            </button>
            <div style={{ fontSize: 11, color: "#565959", textAlign: "center", marginTop: 6 }}>
              Backed by Amazon's 7-Day Return Guarantee
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
