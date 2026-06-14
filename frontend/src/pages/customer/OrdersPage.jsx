import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

export default function OrdersPage() {
  const { orders } = useCart();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Filter out orders matching the search query
  const filteredOrders = orders.filter((order) => {
    const product = products.find((p) => p.id === order.productId);
    if (!product) return false;
    return (
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.orderId.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif", paddingBottom: "60px" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "940px", margin: "20px auto 0 auto", padding: "0 20px" }}>
        
        {/* Breadcrumbs */}
        <div style={{ fontSize: "13px", color: "#565959", marginBottom: "16px" }}>
          <Link to="/" style={{ color: "#007185", textDecoration: "none" }}>Your Account</Link>
          <span style={{ margin: "0 6px" }}>&rsaquo;</span>
          <span style={{ color: "#111" }}>Your Orders</span>
        </div>

        {/* Title and Search Row */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "20px" }}>
          <h1 style={{ fontSize: "28px", fontWeight: "400", margin: 0, color: "#111" }}>Your Orders</h1>
          
          <div style={{ display: "flex", gap: "8px", width: "100%", maxWidth: "400px" }}>
            <input 
              type="text" 
              placeholder="Search all orders" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ flex: 1, padding: "7px 10px", border: "1px solid #a6a6a6", borderRadius: "4px 0 0 4px", fontSize: "14px" }}
            />
            <button style={{ backgroundColor: "#333", border: "none", color: "white", padding: "7px 20px", borderRadius: "0 4px 4px 0", cursor: "pointer", fontSize: "14px", fontWeight: "bold" }}>Search Orders</button>
          </div>
        </div>

        {/* Filter Navigation Links */}
        <div style={{ display: "flex", gap: "24px", borderBottom: "1px solid #ddd", paddingBottom: "8px", marginBottom: "20px", fontSize: "14px" }}>
          <span style={{ color: "#111", borderBottom: "2px solid #e47911", paddingBottom: "8px", fontWeight: "bold", cursor: "pointer" }}>Orders</span>
          <span style={{ color: "#565959", cursor: "pointer" }}>Buy Again</span>
          <span style={{ color: "#565959", cursor: "pointer" }}>Not Yet Shipped</span>
          <span style={{ color: "#565959", cursor: "pointer" }}>Cancelled Orders</span>
        </div>

        {/* Orders list container */}
        {filteredOrders.length === 0 ? (
          <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: "4px", padding: "40px", textAlign: "center" }}>
            <h3 style={{ fontSize: "18px", margin: "0 0 10px 0" }}>No orders found.</h3>
            <p style={{ fontSize: "14px", color: "#565959", margin: "0 0 16px 0" }}>You haven't ordered anything matching "{searchQuery}" recently.</p>
            <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "8px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold" }}>
              Start Shopping
            </Link>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {filteredOrders.map((order) => {
              const product = products.find((p) => p.id === order.productId);
              if (!product) return null;

              const price = order.isPreOwned
                ? product.returniqPrice || Math.floor(product.price * 0.75)
                : product.price;

              const orderDateFormatted = new Date(order.orderedAt).toLocaleDateString("en-IN", {
                day: "numeric",
                month: "long",
                year: "numeric"
              });

              return (
                <div key={order.orderId} style={{ backgroundColor: "white", borderRadius: "8px", border: "1px solid #ddd", overflow: "hidden", boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
                  
                  {/* Order header information bar */}
                  <div style={{ backgroundColor: "#F0F2F2", padding: "12px 18px", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "16px", borderBottom: "1px solid #ddd", fontSize: "12px", color: "#565959" }}>
                    <div style={{ display: "flex", gap: "24px" }}>
                      <div>
                        <span style={{ display: "block", textTransform: "uppercase", marginBottom: "2px" }}>Order Placed</span>
                        <strong style={{ color: "#333", fontSize: "13px" }}>{orderDateFormatted}</strong>
                      </div>
                      <div>
                        <span style={{ display: "block", textTransform: "uppercase", marginBottom: "2px" }}>Total</span>
                        <strong style={{ color: "#333", fontSize: "13px" }}>₹{price * order.quantity}</strong>
                      </div>
                      <div>
                        <span style={{ display: "block", textTransform: "uppercase", marginBottom: "2px" }}>Ship To</span>
                        <strong style={{ color: "#007185", fontSize: "13px", cursor: "pointer" }}>Archi &rsaquo;</strong>
                      </div>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <span style={{ display: "block", marginBottom: "2px" }}>Order ID: {order.orderId}</span>
                      <span style={{ color: "#007185", cursor: "pointer" }}>View order details</span>
                    </div>
                  </div>

                  {/* Order card content details */}
                  <div style={{ padding: "18px", display: "flex", gap: "20px", flexWrap: "wrap", alignItems: "flex-start" }}>
                    
                    {/* Image */}
                    <img 
                      src={product.image} 
                      alt={product.name} 
                      style={{ width: "90px", height: "90px", objectFit: "contain", border: "1px solid #eee", borderRadius: "4px" }} 
                    />

                    {/* Product metadata */}
                    <div style={{ flex: 1, minWidth: "250px" }}>
                      <h3 style={{ fontSize: "15px", fontWeight: "bold", margin: "0 0 6px 0", lineHeight: "1.3" }}>
                        <Link to={`/product/${product.id}`} style={{ color: "#007185", textDecoration: "none" }}>
                          {product.name}
                        </Link>
                      </h3>
                      <span style={{ fontSize: "12px", color: "#565959", display: "block", marginBottom: "8px" }}>
                        Size: {order.selectedSize} | Qty: {order.quantity} | Brand: {product.brand}
                      </span>
                      {order.isPreOwned && (
                        <span style={{ fontSize: "11px", color: "#007600", display: "inline-block", backgroundColor: "#e8f5e9", padding: "2px 8px", borderRadius: "10px", fontWeight: "bold", marginBottom: "12px" }}>
                          ♻️ Pre-Owned (Grade {product.returniqGrade})
                        </span>
                      )}

                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "12px" }}>
                        <span style={{
                          width: "8px",
                          height: "8px",
                          borderRadius: "50%",
                          backgroundColor: order.status === "Returned" ? "#B12704" : "#007600",
                          display: "inline-block"
                        }} />
                        <span style={{ fontSize: "14px", fontWeight: "bold", color: order.status === "Returned" ? "#B12704" : "#111" }}>
                          {order.status === "Returned" ? "Returned" : `Delivered on ${order.deliveryDate}`}
                        </span>
                      </div>
                    </div>

                    {/* Actions buttons panel */}
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%", maxWidth: "240px" }}>
                      <button style={{ backgroundColor: "#ffd814", border: "1px solid #fcd200", color: "#111", padding: "7px 0", borderRadius: "20px", fontSize: "13px", cursor: "pointer", outline: "none" }}>Track package</button>
                      
                      {order.status !== "Returned" ? (
                        <Link 
                          to={`/return/${order.orderId}`}
                          style={{ 
                            display: "block",
                            textAlign: "center",
                            backgroundColor: "white", 
                            border: "1px solid #adb1b8", 
                            color: "#111", 
                            padding: "7px 0", 
                            borderRadius: "20px", 
                            fontSize: "13px", 
                            cursor: "pointer", 
                            textDecoration: "none",
                            fontWeight: "normal"
                          }}
                        >
                          Return or replace items
                        </Link>
                      ) : (
                        <Link 
                          to="/my-returns"
                          style={{ 
                            display: "block",
                            textAlign: "center",
                            backgroundColor: "#e8f4fd", 
                            border: "1px solid #bee5eb", 
                            color: "#0c5460", 
                            padding: "7px 0", 
                            borderRadius: "20px", 
                            fontSize: "13px", 
                            cursor: "pointer", 
                            textDecoration: "none",
                            fontWeight: "bold"
                          }}
                        >
                          View return status
                        </Link>
                      )}

                      <button style={{ backgroundColor: "white", border: "1px solid #adb1b8", color: "#111", padding: "7px 0", borderRadius: "20px", fontSize: "13px", cursor: "pointer", outline: "none" }}>Write a product review</button>
                    </div>

                  </div>

                </div>
              );
            })}
          </div>
        )}

      </main>
    </div>
  );
}
