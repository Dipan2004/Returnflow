import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useCart } from "../../contexts/CartContext";
import { Link, useNavigate } from "react-router-dom";

export default function Header({ onReturnClick }) {
  const { user, role, logout } = useAuth();
  const { cart } = useCart();
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  async function handleLogout(e) {
    e.stopPropagation();
    await logout();
    navigate("/login");
  }

  const currentUsername = user ? user.name : "Archi";
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="header" style={{ backgroundColor: "#131921", height: "60px", color: "white", display: "flex", alignItems: "center" }}>
      <div className="container container-header" style={{ width: "100%", padding: "0 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        
        {/* Left: Amazon.in Logo (No Prime) */}
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          <div className="logo-container border-white">
            <div className="logo"></div>
            <span className="dotin">.in</span>
          </div>
        </Link>

        {/* Deliver Block */}
        <div className="address-container border-white" style={{ cursor: "pointer", display: "flex", alignItems: "center", padding: "4px 8px", gap: "6px" }}>
          <i className="fa-solid fa-location-dot" style={{ fontSize: "16px", color: "white", marginTop: "8px" }}></i>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: "12px", color: "#ccc", fontWeight: "normal", lineHeight: "1.2" }}>Deliver to {currentUsername}</span>
            <span style={{ fontSize: "14px", color: "white", fontWeight: "bold", lineHeight: "1.2" }}>Bhubaneswar 751024</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="search-container" style={{ display: "flex", flex: 1, margin: "0 16px", height: "40px", borderRadius: "4px", overflow: "hidden", backgroundColor: "white" }}>
          <select className="search-select" style={{ backgroundColor: "#e6e3e3", border: "none", borderRight: "1px solid #ccc", padding: "0 12px", cursor: "pointer", fontSize: "12px", color: "#555" }}>
            <option>All</option>
          </select>
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search Amazon.in" 
            style={{ flex: 1, padding: "8px 12px", border: "none", outline: "none", fontSize: "15px", color: "#111" }} 
          />
          <div className="search-icon" style={{ backgroundColor: "#febd69", width: "48px", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}>
            <i className="fa-solid fa-magnifying-glass" style={{ color: "#333", fontSize: "17px" }}></i>
          </div>
        </div>

        {/* Right Cluster */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          
          {/* India Flag + EN */}
          <div className="language-container border-white" style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "6px", padding: "6px 8px" }}>
            <img
              src="https://flagcdn.com/w20/in.png"
              alt="India Flag"
              style={{ width: "20px", height: "14px", objectFit: "cover", display: "block" }}
            />
            <span style={{ fontWeight: "bold", fontSize: "14px", color: "white" }}>EN</span>
            <span style={{ fontSize: "8px", color: "#ccc", alignSelf: "center", marginTop: "2px" }}>▼</span>
          </div>

          {/* User Sign-In/Account Dropdown */}
          <div
            className="login-container border-white"
            style={{ position: "relative", cursor: "pointer", padding: "4px 8px" }}
            onClick={() => setShowDropdown((v) => !v)}
          >
            <p style={{ margin: 0, fontSize: "12px", color: "#ccc" }}>Hello, {currentUsername}</p>
            <p className="account" style={{ margin: 0, fontSize: "14px", fontWeight: "bold", color: "white", display: "flex", alignItems: "center", gap: "3px" }}>
              Account & Lists <span style={{ fontSize: "8px", color: "#ccc", marginTop: "2px" }}>▼</span>
            </p>

            {showDropdown && (
              <div className="account-dropdown" onClick={(e) => e.stopPropagation()} style={{ position: "absolute", top: "100%", right: 0, backgroundColor: "white", border: "1px solid #ddd", borderRadius: "4px", zIndex: 50, minWidth: "180px", padding: "8px 0", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
                <div
                  style={{
                    fontSize: 13,
                    padding: "8px 16px",
                    borderBottom: "1px solid #eee",
                    fontWeight: 700,
                    color: "#131921",
                  }}
                >
                  Hello, {currentUsername}
                </div>
                <Link
                  to="/orders"
                  onClick={() => setShowDropdown(false)}
                  style={{
                    display: "block",
                    padding: "8px 16px",
                    color: "#131921",
                    fontSize: 13,
                    textDecoration: "none",
                  }}
                >
                  Your Orders
                </Link>
                <Link
                  to="/wishlist"
                  onClick={() => setShowDropdown(false)}
                  style={{
                    display: "block",
                    padding: "8px 16px",
                    color: "#131921",
                    fontSize: 13,
                    textDecoration: "none",
                  }}
                >
                  Your Wish List
                </Link>
                <Link
                  to="/my-returns"
                  onClick={() => setShowDropdown(false)}
                  style={{
                    display: "block",
                    padding: "8px 16px",
                    color: "#131921",
                    fontSize: 13,
                    textDecoration: "none",
                  }}
                >
                  Your Returns
                </Link>
                <div style={{ height: "1px", backgroundColor: "#eee", margin: "4px 0" }} />
                <button
                  onClick={handleLogout}
                  style={{
                    display: "block",
                    padding: "8px 16px",
                    color: "#131921",
                    fontSize: 13,
                    width: "100%",
                    textAlign: "left",
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Sign out
                </button>
              </div>
            )}
          </div>

          {/* Role-based nav link */}
          {role === "customer" && (
            <Link
              to="/buyer-feed"
              className="border-white"
              style={{ cursor: "pointer", padding: "4px 8px", textDecoration: "none", color: "white", display: "flex", flexDirection: "column" }}
            >
              <p style={{ margin: 0, fontSize: "12px", color: "#ccc" }}>🛍️ Available</p>
              <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold", color: "white", marginTop: "-2px" }}>Near You</p>
            </Link>
          )}
          {role === "delivery_agent" && (
            <Link
              to="/delivery"
              className="border-white"
              style={{ cursor: "pointer", padding: "4px 8px", textDecoration: "none", color: "white", display: "flex", flexDirection: "column" }}
            >
              <p style={{ margin: 0, fontSize: "12px", color: "#ccc" }}>📦 My</p>
              <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold", color: "white", marginTop: "-2px" }}>Queue</p>
            </Link>
          )}
          {role === "warehouse" && (
            <Link
              to="/warehouse"
              className="border-white"
              style={{ cursor: "pointer", padding: "4px 8px", textDecoration: "none", color: "white", display: "flex", flexDirection: "column" }}
            >
              <p style={{ margin: 0, fontSize: "12px", color: "#ccc" }}>🏭 Warehouse</p>
              <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold", color: "white", marginTop: "-2px" }}>Queue</p>
            </Link>
          )}

          {/* Returns & Orders (Links to /orders) */}
          <Link
            to="/orders"
            className="return-order-container border-white"
            style={{ cursor: "pointer", padding: "4px 8px", textDecoration: "none", color: "white" }}
          >
            <p style={{ margin: 0, fontSize: "12px", color: "#ccc" }}>Returns</p>
            <p style={{ margin: 0, fontSize: "14px", fontWeight: "bold", color: "white", marginTop: "-2px" }}>& Orders</p>
          </Link>

          {/* Cart Icon with Orange Badge */}
          <Link 
            to="/cart" 
            className="cart-container border-white" 
            style={{ cursor: "pointer", display: "flex", alignItems: "center", padding: "6px 8px", gap: "2px", textDecoration: "none", color: "white" }}
          >
            <div style={{ position: "relative", display: "flex", alignItems: "center", height: "30px" }}>
              <span style={{
                position: "absolute",
                top: "-6px",
                left: "11px",
                backgroundColor: "#f08804",
                color: "black",
                fontWeight: "bold",
                fontSize: "12px",
                borderRadius: "10px",
                padding: "0 5px",
                height: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 1
              }}>
                {cartCount}
              </span>
              <i className="fa-solid fa-cart-shopping" style={{ fontSize: "22px", color: "white", marginTop: "6px" }}></i>
            </div>
            <span style={{ fontWeight: "bold", fontSize: "14px", color: "white", marginTop: "8px" }}>Cart</span>
          </Link>

        </div>
      </div>
    </header>
  );
}
