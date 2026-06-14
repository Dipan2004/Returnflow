import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

export default function WishlistPage() {
  const { wishlist, removeFromWishlist, addToCart } = useCart();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const wishlistItems = wishlist.map((item) => {
    const product = products.find((p) => p.id === item.productId);
    return {
      ...item,
      product
    };
  }).filter(item => item.product);

  const handleAddToCart = (productId) => {
    addToCart(productId, 1, "Standard", false);
    removeFromWishlist(productId);
    alert("Added item to cart!");
  };

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif", paddingBottom: "60px" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "1000px", margin: "20px auto 0 auto", padding: "0 20px" }}>
        
        {/* Title */}
        <h1 style={{ fontSize: "28px", fontWeight: "400", margin: "0 0 20px 0", color: "#111" }}>Your Wish List</h1>

        {wishlistItems.length === 0 ? (
          <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: "4px", padding: "40px", textAlign: "center" }}>
            <h3 style={{ fontSize: "18px", margin: "0 0 10px 0" }}>Your Wish List is empty.</h3>
            <p style={{ fontSize: "14px", color: "#565959", margin: "0 0 16px 0" }}>Save items you want to buy later by clicking "Add to Wish List" on the product detail page.</p>
            <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "8px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold" }}>
              Explore Products
            </Link>
          </div>
        ) : (
          <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: "4px", padding: "20px", display: "flex", flexDirection: "column", gap: "20px" }}>
            {wishlistItems.map((item) => {
              const product = item.product;
              return (
                <div key={product.id} style={{ display: "flex", gap: "20px", borderBottom: "1px solid #eee", paddingBottom: "20px", flexWrap: "wrap" }}>
                  
                  {/* Image */}
                  <img 
                    src={product.image} 
                    alt={product.name} 
                    style={{ width: "120px", height: "120px", objectFit: "contain", border: "1px solid #eee", borderRadius: "4px" }} 
                  />

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: "250px" }}>
                    <h3 style={{ fontSize: "16px", fontWeight: "bold", margin: "0 0 6px 0", lineHeight: "1.3" }}>
                      <Link to={`/product/${product.id}`} style={{ color: "#007185", textDecoration: "none" }}>
                        {product.name}
                      </Link>
                    </h3>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                      <span style={{ fontSize: "13px", color: "#ffd700" }}>{"★".repeat(Math.round(product.rating))}</span>
                      <span style={{ fontSize: "12px", color: "#565959" }}>({product.ratingCount})</span>
                    </div>
                    <div style={{ fontSize: "18px", fontWeight: "bold", color: "#B12704", marginBottom: "12px" }}>
                      ₹{product.price}
                    </div>
                  </div>

                  {/* Actions */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", justifyContent: "center", minWidth: "150px" }}>
                    <button 
                      onClick={() => handleAddToCart(product.id)}
                      style={{
                        backgroundColor: "#ffd814",
                        border: "1px solid #fcd200",
                        color: "#111",
                        padding: "7px 16px",
                        borderRadius: "20px",
                        fontSize: "13px",
                        fontWeight: "bold",
                        cursor: "pointer",
                        outline: "none"
                      }}
                    >
                      Add to Cart
                    </button>
                    <button 
                      onClick={() => removeFromWishlist(product.id)}
                      style={{
                        backgroundColor: "white",
                        border: "1px solid #adb1b8",
                        color: "#111",
                        padding: "7px 16px",
                        borderRadius: "20px",
                        fontSize: "13px",
                        cursor: "pointer",
                        outline: "none"
                      }}
                    >
                      Remove item
                    </button>
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
