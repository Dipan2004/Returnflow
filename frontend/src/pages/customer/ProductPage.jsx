import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import SidebarComponent from "../../components/layout/Sidebar";
import PreventIQWidget from "../../components/returniq/PreventIQWidget";
import { products } from "../../data/products";
import { useCart } from "../../contexts/CartContext";

export default function ProductPage() {
  const { sku_id } = useParams();
  const navigate = useNavigate();
  const { addToCart, addToWishlist, openHealthCardModal } = useCart();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedSize, setSelectedSize] = useState("");
  const [selectedQty, setSelectedQty] = useState(1);
  const [preventIQData, setPreventIQData] = useState(null);
  const [preventIQLoading, setPreventIQLoading] = useState(true);

  // Dynamic product look up
  const product = products.find((p) => p.id === sku_id);

  // Image Gallery Viewer state
  const [activeImage, setActiveImage] = useState("");

  useEffect(() => {
    if (product) {
      setActiveImage(product.image);
      // Auto select default size/option based on category
      if (product.category === "shoes") {
        setSelectedSize("8");
      } else if (product.category === "stationery") {
        setSelectedSize("Pack of 12");
      } else {
        setSelectedSize("Standard");
      }
    }
  }, [product]);

  useEffect(() => {
    if (!product) return;
    setPreventIQLoading(true);
    const timer = setTimeout(() => {
      // Simulate size/category specific predictions
      const isShoes = product.category === "shoes";
      const highRate = isShoes && selectedSize === "7.5";
      setPreventIQData({
        return_probability: highRate ? 0.28 : isShoes ? 0.08 : 0.03,
        category_avg_return_rate: isShoes ? 0.12 : 0.04,
        above_category_avg: highRate,
        size_warning: highRate ? "This size has an elevated return rate. Customers note that size 7.5 runs slightly narrower than average." : null,
        recommended_size: highRate ? "8" : null,
      });
      setPreventIQLoading(false);
    }, 400);
    return () => clearTimeout(timer);
  }, [selectedSize, product]);

  if (!product) {
    return (
      <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
        <Header />
        <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
        <SidebarComponent isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div style={{ maxWidth: "600px", margin: "40px auto", padding: "30px", backgroundColor: "white", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", textAlign: "center" }}>
          <h2>Product Not Found</h2>
          <p style={{ color: "#565959", margin: "10px 0 20px 0" }}>The product code you requested doesn't exist in our records.</p>
          <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "10px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold" }}>
            Return to Homepage
          </Link>
        </div>
      </div>
    );
  }

  const sizes = product.category === "shoes" 
    ? ["7", "7.5", "8", "8.5", "9"] 
    : product.category === "stationery" 
    ? ["Pack of 1", "Pack of 5", "Pack of 12", "Pack of 50"]
    : ["Standard"];

  const productImages = product.images && product.images.length > 0 ? product.images : [product.image];

  const preOwnedPrice = product.returniqPrice || Math.floor(product.price * 0.75);

  const handleAddToCart = () => {
    addToCart(product.id, selectedQty, selectedSize, false);
    alert(`Added "${product.name}" (Qty: ${selectedQty}, Size: ${selectedSize}) to your cart.`);
  };

  const handleBuyNow = () => {
    addToCart(product.id, selectedQty, selectedSize, false);
    navigate("/checkout");
  };

  const handleAddPreOwnedToCart = () => {
    addToCart(product.id, 1, selectedSize, true);
    alert(`Added Pre-Owned (Grade ${product.returniqGrade}) version of "${product.name}" to your cart.`);
  };

  const handleAddToWishlist = () => {
    addToWishlist(product.id);
    alert(`Added "${product.name}" to your Wish List.`);
  };

  return (
    <div style={{ backgroundColor: "white", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <SidebarComponent isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "1280px", margin: "20px auto 0 auto", padding: "0 20px 60px 20px", display: "flex", gap: "30px", flexWrap: "wrap", alignItems: "flex-start" }}>
        
        {/* Gallery column (Left) */}
        <div style={{ flex: "1 1 400px", display: "flex", gap: "16px", minWidth: "300px" }}>
          
          {/* Thumbnails list */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {productImages.map((imgUrl, idx) => (
              <div 
                key={idx}
                onClick={() => setActiveImage(imgUrl)}
                style={{
                  width: "50px",
                  height: "50px",
                  border: activeImage === imgUrl ? "2px solid #e77600" : "1px solid #ddd",
                  borderRadius: "4px",
                  cursor: "pointer",
                  padding: "2px",
                  backgroundColor: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}
              >
                <img src={imgUrl} alt={`Thumbnail ${idx}`} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
              </div>
            ))}
          </div>

          {/* Active product viewer box */}
          <div style={{ flex: 1, border: "1px solid #eee", padding: "20px", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center", height: "420px", backgroundColor: "#fff" }}>
            <img src={activeImage || product.image} alt={product.name} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
          </div>
        </div>

        {/* Center column (Info, Rating & PreventIQ Widgets) */}
        <div style={{ flex: "2 2 500px", minWidth: "320px" }}>
          <h1 style={{ fontSize: "22px", fontWeight: "bold", color: "#111", margin: "0 0 6px 0", lineHeight: "1.3" }}>
            {product.name}
          </h1>
          <div style={{ fontSize: "13px", color: "#007185", marginBottom: "8px" }}>
            Brand: {product.brand}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", marginBottom: "12px" }}>
            <span style={{ color: "#ffa41c" }}>{"★".repeat(Math.round(product.rating))}</span>
            <span style={{ color: "#565959" }}>{product.ratingCount} ratings</span>
          </div>

          <hr style={{ border: "none", borderTop: "1px solid #eee", margin: "12px 0" }} />

          {/* Pricing detail */}
          <div style={{ marginBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
              <span style={{ fontSize: "24px", color: "#B12704", fontWeight: "500" }}>₹{product.price}</span>
              {product.mrp && (
                <span style={{ fontSize: "13px", textDecoration: "line-through", color: "#565959" }}>
                  M.R.P.: ₹{product.mrp}
                </span>
              )}
              {product.discount && (
                <span style={{ fontSize: "14px", color: "#CC0C39", fontWeight: "bold" }}>({product.discount}% Off)</span>
              )}
            </div>
            <span style={{ fontSize: "12px", color: "#565959" }}>Inclusive of all taxes</span>
          </div>

          {/* PreventIQ widget */}
          {preventIQLoading ? (
            <div style={{ height: "100px", backgroundColor: "#f3f3f3", borderRadius: "8px", animation: "pulse 1.5s infinite" }} />
          ) : (
            <PreventIQWidget 
              {...preventIQData}
              onSwitchSize={(size) => setSelectedSize(size)}
            />
          )}

          <hr style={{ border: "none", borderTop: "1px solid #eee", margin: "20px 0" }} />

          {/* Size / Variant Option Selectors */}
          {sizes.length > 1 && (
            <div style={{ marginBottom: "20px" }}>
              <h4 style={{ fontSize: "14px", fontWeight: "bold", margin: "0 0 8px 0" }}>Options: {selectedSize}</h4>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {sizes.map((s) => {
                  const active = selectedSize === s;
                  return (
                    <button
                      key={s}
                      onClick={() => setSelectedSize(s)}
                      style={{
                        padding: "8px 16px",
                        border: active ? "2px solid #e77600" : "1px solid #a6a6a6",
                        borderRadius: "4px",
                        backgroundColor: active ? "#fdf8f2" : "white",
                        fontWeight: active ? "bold" : "normal",
                        cursor: "pointer",
                        outline: "none",
                        fontSize: "13px"
                      }}
                    >
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Description */}
          <div style={{ fontSize: "14px", color: "#333", lineHeight: "1.5" }}>
            <h4 style={{ fontSize: "14px", fontWeight: "bold", margin: "0 0 8px 0" }}>About this item</h4>
            <p style={{ margin: 0 }}>{product.description}</p>
          </div>
        </div>

        {/* Right column (Buy Box + Pre-Owned Alternative) */}
        <div style={{ flex: "1 1 280px", display: "flex", flexDirection: "column", gap: "16px", minWidth: "250px" }}>
          
          {/* Main Buy Box */}
          <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px", backgroundColor: "white" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#B12704", marginBottom: "8px" }}>
              ₹{product.price}
            </div>

            <div style={{ fontSize: "13px", color: "#007600", fontWeight: "bold", marginBottom: "12px" }}>
              FREE delivery in 2-3 days
            </div>

            <div style={{ fontSize: "14px", color: "#111", fontWeight: "bold", marginBottom: "16px" }}>
              In Stock
            </div>

            {/* Qty Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
              <span style={{ fontSize: "13px" }}>Qty:</span>
              <select 
                value={selectedQty} 
                onChange={(e) => setSelectedQty(parseInt(e.target.value))}
                style={{ padding: "4px 8px", border: "1px solid #ccc", borderRadius: "4px", backgroundColor: "#f0f2f2", cursor: "pointer" }}
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <button
                onClick={handleAddToCart}
                style={{
                  backgroundColor: "#ffd814",
                  border: "1px solid #fcd200",
                  borderRadius: "20px",
                  color: "#111",
                  padding: "10px 0",
                  fontSize: "14px",
                  fontWeight: "bold",
                  cursor: "pointer",
                  boxShadow: "0 2px 5px rgba(213,217,217,0.5)",
                  outline: "none"
                }}
              >
                Add to Cart
              </button>
              
              <button
                onClick={handleBuyNow}
                style={{
                  backgroundColor: "#ffa41c",
                  border: "1px solid #ff9900",
                  borderRadius: "20px",
                  color: "#111",
                  padding: "10px 0",
                  fontSize: "14px",
                  fontWeight: "bold",
                  cursor: "pointer",
                  boxShadow: "0 2px 5px rgba(213,217,217,0.5)",
                  outline: "none"
                }}
              >
                Buy Now
              </button>
            </div>

            <hr style={{ border: "none", borderTop: "1px solid #eee", margin: "16px 0" }} />

            <button
              onClick={handleAddToWishlist}
              style={{
                width: "100%",
                backgroundColor: "#e7e9ec",
                border: "1px solid #adb1b8",
                borderRadius: "4px",
                color: "#111",
                padding: "6px 0",
                fontSize: "13px",
                cursor: "pointer",
                outline: "none"
              }}
            >
              Add to Wish List
            </button>
          </div>

          {/* Pre-Owned Alternative Box */}
          {product.returniqGrade && (
            <div style={{ border: "2px solid #27726b", borderRadius: "8px", padding: "16px", backgroundColor: "#f0faf8" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "10px" }}>
                <span style={{ fontSize: "14px" }}>♻️</span>
                <strong style={{ fontSize: "13px", color: "#27726b", textTransform: "uppercase" }}>ReturnIQ Pre-Owned</strong>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "8px" }}>
                <strong style={{ fontSize: "18px", color: "#27726b" }}>₹{preOwnedPrice}</strong>
                <span style={{ fontSize: "11px", backgroundColor: "#27726b", color: "white", padding: "2px 6px", borderRadius: "10px", fontWeight: "bold" }}>
                  Grade {product.returniqGrade}
                </span>
              </div>

              <span style={{ fontSize: "11px", color: "#007600", display: "block", marginBottom: "12px", fontWeight: "bold" }}>
                🌱 Saves {product.returniqCO2 || 1.2} kg CO₂ carbon footprint
              </span>

              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <button
                  onClick={() => openHealthCardModal(product.id)}
                  style={{
                    backgroundColor: "white",
                    border: "1px solid #27726b",
                    borderRadius: "20px",
                    color: "#27726b",
                    padding: "6px 0",
                    fontSize: "12px",
                    fontWeight: "bold",
                    cursor: "pointer",
                    outline: "none"
                  }}
                >
                  View Condition Report
                </button>
                <button
                  onClick={handleAddPreOwnedToCart}
                  style={{
                    backgroundColor: "#27726b",
                    border: "1px solid #1f5953",
                    borderRadius: "20px",
                    color: "white",
                    padding: "6px 0",
                    fontSize: "12px",
                    fontWeight: "bold",
                    cursor: "pointer",
                    outline: "none"
                  }}
                >
                  Add Pre-Owned to Cart
                </button>
              </div>
            </div>
          )}

        </div>

      </main>
    </div>
  );
}
