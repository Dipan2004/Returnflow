import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

export default function CartPage() {
  const { cart, addToCart, removeFromCart, updateQuantity, openHealthCardModal } = useCart();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [savedForLater, setSavedForLater] = useState([]);
  const navigate = useNavigate();

  // Resolve cart items with product details
  const cartItems = cart.map((item) => {
    const product = products.find((p) => p.id === item.productId);
    return {
      ...item,
      product
    };
  }).filter(item => item.product);

  const subtotal = cartItems.reduce((sum, item) => {
    const price = item.isPreOwned
      ? item.product.returniqPrice || Math.floor(item.product.price * 0.75)
      : item.product.price;
    return sum + price * item.quantity;
  }, 0);

  const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  function handleSaveForLater(item) {
    setSavedForLater((prev) => [...prev, item]);
    removeFromCart(item.productId, item.selectedSize, item.isPreOwned);
  }

  function handleMoveToCart(item) {
    addToCart(item.productId, item.quantity, item.selectedSize, item.isPreOwned);
    setSavedForLater((prev) =>
      prev.filter(
        (i) =>
          !(
            i.productId === item.productId &&
            i.selectedSize === item.selectedSize &&
            i.isPreOwned === item.isPreOwned
          )
      )
    );
  }

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "1440px", margin: "0 auto", padding: "20px", display: "flex", gap: "20px", alignItems: "flex-start" }}>
        
        {/* Left cart items container */}
        <div style={{ flex: 1, backgroundColor: "white", padding: "20px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          <h1 style={{ fontSize: "28px", fontWeight: "400", margin: "0 0 4px 0" }}>Shopping Cart</h1>
          {cartItems.length > 0 ? (
            <span 
              onClick={() => cartItems.forEach(item => removeFromCart(item.productId, item.selectedSize, item.isPreOwned))} 
              style={{ fontSize: "12px", color: "#007185", cursor: "pointer" }}
            >
              Deselect all items
            </span>
          ) : null}
          <hr style={{ border: "none", borderTop: "1px solid #ddd", margin: "12px 0 20px 0" }} />

          {cartItems.length === 0 ? (
            <div style={{ padding: "40px 0", textAlign: "center" }}>
              <h3 style={{ fontSize: "18px", margin: "0 0 12px 0" }}>Your Amazon Cart is empty.</h3>
              <p style={{ fontSize: "14px", color: "#565959", margin: "0 0 16px 0" }}>
                Add items from our catalog to get started.
              </p>
              <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "8px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold" }}>
                Go to Homepage
              </Link>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
              {cartItems.map((item, idx) => {
                const product = item.product;
                const price = item.isPreOwned
                  ? product.returniqPrice || Math.floor(product.price * 0.75)
                  : product.price;

                return (
                  <div key={idx} style={{ display: "flex", gap: "16px", borderBottom: "1px solid #e7e7e7", paddingBottom: "20px" }}>
                    {/* Image */}
                    <img 
                      src={product.image} 
                      alt={product.name} 
                      style={{ width: "120px", height: "120px", objectFit: "contain", border: "1px solid #eee", borderRadius: "4px" }} 
                    />

                    {/* Details */}
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <h3 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 4px 0", lineHeight: "1.3" }}>
                          <Link to={`/product/${product.id}`} style={{ color: "#007185", textDecoration: "none" }}>
                            {product.name}
                          </Link>
                        </h3>
                        <span style={{ fontSize: "18px", fontWeight: "bold" }}>₹{price}</span>
                      </div>
                      
                      <span style={{ fontSize: "12px", color: "#565959", display: "block" }}>Brand: {product.brand}</span>
                      <span style={{ fontSize: "12px", color: "#007600", fontWeight: "bold", display: "block", marginTop: "4px" }}>In Stock</span>
                      
                      {/* ReturnIQ badges */}
                      {item.isPreOwned && (
                        <div 
                          onClick={() => openHealthCardModal(product.id)}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            backgroundColor: "#e8f5e9",
                            color: "#007600",
                            border: "1px solid rgba(0, 118, 0, 0.2)",
                            padding: "3px 8px",
                            borderRadius: "12px",
                            fontSize: "11px",
                            fontWeight: "bold",
                            marginTop: "8px",
                            cursor: "pointer"
                          }}
                        >
                          ♻️ Grade {product.returniqGrade || "A"} Pre-Owned — Condition Report
                        </div>
                      )}

                      {/* Quantity & Actions row */}
                      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginTop: "12px" }}>
                        <div style={{ display: "flex", alignItems: "center", border: "1px solid #ddd", borderRadius: "4px", backgroundColor: "#f0f2f2", overflow: "hidden" }}>
                          <button 
                            onClick={() => updateQuantity(product.id, item.quantity - 1, item.selectedSize, item.isPreOwned)}
                            style={{ border: "none", background: "none", padding: "4px 8px", cursor: "pointer", fontWeight: "bold" }}
                          >
                            -
                          </button>
                          <span style={{ padding: "0 10px", fontSize: "13px", fontWeight: "bold" }}>{item.quantity}</span>
                          <button 
                            onClick={() => updateQuantity(product.id, item.quantity + 1, item.selectedSize, item.isPreOwned)}
                            style={{ border: "none", background: "none", padding: "4px 8px", cursor: "pointer", fontWeight: "bold" }}
                          >
                            +
                          </button>
                        </div>

                        <div style={{ height: "14px", width: "1px", backgroundColor: "#ddd" }} />

                        <span 
                          onClick={() => removeFromCart(product.id, item.selectedSize, item.isPreOwned)}
                          style={{ fontSize: "12px", color: "#007185", cursor: "pointer" }}
                        >
                          Delete
                        </span>

                        <div style={{ height: "14px", width: "1px", backgroundColor: "#ddd" }} />

                        <span 
                          onClick={() => handleSaveForLater(item)}
                          style={{ fontSize: "12px", color: "#007185", cursor: "pointer" }}
                        >
                          Save for later
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right order summary */}
        {cartItems.length > 0 && (
          <div style={{ width: "320px", backgroundColor: "white", padding: "20px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <div style={{ display: "flex", alignItems: "baseline", flexWrap: "wrap", gap: "4px", marginBottom: "16px" }}>
              <span style={{ fontSize: "18px" }}>Subtotal ({totalItems} item{totalItems !== 1 ? "s" : ""}): </span>
              <strong style={{ fontSize: "20px" }}>₹{subtotal}</strong>
            </div>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "#111", marginBottom: "16px", cursor: "pointer" }}>
              <input type="checkbox" />
              This order contains a gift
            </label>

            <button
              onClick={() => navigate("/checkout")}
              style={{
                width: "100%",
                backgroundColor: "#ffa41c",
                border: "1px solid #ff9900",
                color: "#111",
                padding: "10px 0",
                borderRadius: "20px",
                fontSize: "14px",
                fontWeight: "bold",
                cursor: "pointer",
                boxShadow: "0 2px 5px rgba(213,217,217,0.5)",
                outline: "none"
              }}
            >
              Proceed to Buy
            </button>
          </div>
        )}
      </main>

      {/* Saved For Later Section */}
      {savedForLater.length > 0 && (
        <section style={{ maxWidth: "1440px", margin: "20px auto 40px auto", padding: "0 20px" }}>
          <div style={{ backgroundColor: "white", padding: "20px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
            <h2 style={{ fontSize: "20px", fontWeight: "400", margin: "0 0 16px 0" }}>Saved for later</h2>
            <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
              {savedForLater.map((item, idx) => (
                <div key={idx} style={{ border: "1px solid #ddd", borderRadius: "4px", padding: "12px", width: "200px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                  <img src={item.product.image} alt={item.product.name} style={{ height: "120px", objectFit: "contain", marginBottom: "8px" }} />
                  <h4 style={{ fontSize: "13px", height: "36px", overflow: "hidden", margin: "0 0 6px 0" }}>{item.product.name}</h4>
                  <span style={{ fontSize: "14px", fontWeight: "bold", display: "block", marginBottom: "12px" }}>
                    ₹{item.isPreOwned ? item.product.returniqPrice || Math.floor(item.product.price * 0.75) : item.product.price}
                  </span>
                  
                  <button
                    onClick={() => handleMoveToCart(item)}
                    style={{
                      backgroundColor: "white",
                      border: "1px solid #a88734",
                      borderRadius: "4px",
                      padding: "4px 8px",
                      fontSize: "12px",
                      cursor: "pointer",
                      width: "100%"
                    }}
                  >
                    Move to Cart
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
