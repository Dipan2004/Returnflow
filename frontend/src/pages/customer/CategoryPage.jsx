import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { products } from "../../data/products";
import { useCart } from "../../contexts/CartContext";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

export default function CategoryPage() {
  const { slug } = useParams();
  const { addToCart, openHealthCardModal } = useCart();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Filter products by category slug
  const categoryProducts = products.filter(
    (p) => p.category.toLowerCase() === slug.toLowerCase()
  );

  // Friendly title translation
  const categoryTitles = {
    stationery: "Stationery & Office Supplies",
    "home-improvement": "Home Improvement & Decor",
    shoes: "Shoes & Footwear",
    handbags: "Bags & Handbags",
    furniture: "Furniture & Bedding",
    headphones: "Headphones & Audio",
    appliances: "Home & Kitchen Appliances",
    kitchen: "Kitchen & Cookware",
    sports: "Sports & Fitness"
  };

  const displayTitle = categoryTitles[slug.toLowerCase()] || `${slug.toUpperCase()} Products`;

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif", paddingBottom: "60px" }}>
      <Header />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main style={{ maxWidth: "1280px", margin: "20px auto 0 auto", padding: "0 20px" }}>
        
        {/* Breadcrumbs */}
        <div style={{ fontSize: "13px", color: "#565959", marginBottom: "16px" }}>
          <Link to="/" style={{ color: "#007185", textDecoration: "none" }}>All Departments</Link>
          <span style={{ margin: "0 6px" }}>&rsaquo;</span>
          <span style={{ color: "#111" }}>{displayTitle}</span>
        </div>

        {/* Title & Stats */}
        <div style={{ borderBottom: "1px solid #ddd", paddingBottom: "12px", marginBottom: "20px" }}>
          <h1 style={{ fontSize: "22px", fontWeight: "bold", margin: "0 0 4px 0", color: "#111" }}>{displayTitle}</h1>
          <span style={{ fontSize: "13px", color: "#565959" }}>Showing {categoryProducts.length} results</span>
        </div>

        {categoryProducts.length === 0 ? (
          <div style={{ backgroundColor: "white", border: "1px solid #ddd", borderRadius: "4px", padding: "40px", textAlign: "center" }}>
            <h3>No products found in this category.</h3>
            <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "8px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold", marginTop: "12px" }}>
              Back to Home
            </Link>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "20px" }}>
            {categoryProducts.map((product) => {
              return (
                <div 
                  key={product.id} 
                  style={{ 
                    backgroundColor: "white", 
                    border: "1px solid #ddd", 
                    borderRadius: "4px", 
                    padding: "16px", 
                    display: "flex", 
                    flexDirection: "column", 
                    justifyContent: "space-between",
                    position: "relative",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                    transition: "transform 0.15s ease-in-out"
                  }}
                >
                  {/* Image with Link */}
                  <Link to={`/product/${product.id}`} style={{ textDecoration: "none" }}>
                    <div style={{ height: "180px", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "12px" }}>
                      <img 
                        src={product.image} 
                        alt={product.name} 
                        style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} 
                      />
                    </div>
                  </Link>

                  {/* Meta details */}
                  <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                    <div>
                      <h4 style={{ fontSize: "14px", fontWeight: "normal", margin: "0 0 6px 0", height: "38px", overflow: "hidden", lineHeight: "1.3" }}>
                        <Link to={`/product/${product.id}`} style={{ color: "#007185", textDecoration: "none" }}>
                          {product.name}
                        </Link>
                      </h4>
                      
                      {/* Ratings */}
                      <div style={{ display: "flex", alignItems: "center", gap: "4px", marginBottom: "8px" }}>
                        <span style={{ fontSize: "12px", color: "#ffa41c" }}>{"★".repeat(Math.round(product.rating))}</span>
                        <span style={{ fontSize: "11px", color: "#565959" }}>({product.ratingCount})</span>
                      </div>
                    </div>

                    <div>
                      {/* Price row */}
                      <div style={{ display: "flex", alignItems: "baseline", gap: "6px", marginBottom: "8px" }}>
                        <span style={{ fontSize: "18px", fontWeight: "bold" }}>₹{product.price}</span>
                        {product.mrp && (
                          <span style={{ fontSize: "12px", textDecoration: "line-through", color: "#565959" }}>M.R.P: ₹{product.mrp}</span>
                        )}
                      </div>

                      {/* ReturnIQ Grade pill */}
                      {product.returniqGrade && (
                        <div 
                          onClick={() => openHealthCardModal(product.id)}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            backgroundColor: product.returniqGrade === "A" ? "#e8f5e9" : product.returniqGrade === "B" ? "#fff3e0" : "#f5f5f5",
                            color: product.returniqGrade === "A" ? "#007600" : product.returniqGrade === "B" ? "#b78103" : "#616161",
                            border: `1px solid ${product.returniqGrade === "A" ? "#007600" : product.returniqGrade === "B" ? "#ffa726" : "#bdbdbd"}`,
                            borderRadius: "12px",
                            padding: "2px 8px",
                            fontSize: "11px",
                            fontWeight: "bold",
                            marginBottom: "12px",
                            cursor: "pointer"
                          }}
                        >
                          ♻️ Grade {product.returniqGrade} Pre-Owned Available
                        </div>
                      )}

                      {/* Add to Cart Button */}
                      <button
                        onClick={() => {
                          addToCart(product.id, 1, "Standard", false);
                          alert(`Added "${product.name}" to cart!`);
                        }}
                        style={{
                          width: "100%",
                          backgroundColor: "#ffd814",
                          border: "1px solid #fcd200",
                          borderRadius: "20px",
                          color: "#111",
                          padding: "6px 0",
                          fontSize: "12px",
                          fontWeight: "bold",
                          cursor: "pointer",
                          boxShadow: "0 2px 5px rgba(213,217,217,0.5)",
                          outline: "none"
                        }}
                      >
                        Add to Cart
                      </button>
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
