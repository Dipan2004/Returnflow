import React from "react";
import { Link } from "react-router-dom";
import ReturnIQBadge from "../returniq/ReturnIQBadge";

export default function ProductCards() {
  return (
    <div style={{ backgroundColor: "#EAEDED", padding: "20px 0", fontFamily: "Arial, sans-serif" }}>
      <div className="container" style={{ width: "100%", maxWidth: "1440px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "20px" }}>
        
        {/* ROW 1: 4-Column Grid */}
        <div className="amazon-product-grid">
          
          {/* Column 1: Deals related to items you've saved */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Deals related to items you've saved</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <Link to="/product/p001" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1585336139057-3a536e6c7290?auto=format&fit=crop&w=150&h=115&q=80" alt="Finegrip black pens jar" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "12px", margin: "4px 0 0 0", color: "#333", height: "16px", overflow: "hidden" }}>Finegrip black pens</p>
                </Link>
                <Link to="/product/p002" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=150&h=115&q=80" alt="Colored gel pens set" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "12px", margin: "4px 0 0 0", color: "#333", height: "16px", overflow: "hidden" }}>Colored gel pens set</p>
                </Link>
                <Link to="/product/p003" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=150&h=115&q=80" alt="CELXY black pen" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "12px", margin: "4px 0 0 0", color: "#333", height: "16px", overflow: "hidden" }}>CELXY black pen</p>
                </Link>
                <Link to="/product/p004" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1568849676085-51415703900f?auto=format&fit=crop&w=150&h=115&q=80" alt="Pastel colored fine liner" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "12px", margin: "4px 0 0 0", color: "#333", height: "16px", overflow: "hidden" }}>Pastel fine liners</p>
                </Link>
              </div>
            </div>
            <Link to="/category/stationery" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See all deals</Link>
          </div>

          {/* Column 2: Revamp your home in style */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Revamp your home in style</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <Link to="/product/p005" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=150&h=115&q=80" alt="Cushion covers" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Cushion covers, bedsheets</p>
                </Link>
                <Link to="/product/p006" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=150&h=115&q=80" alt="Astronaut figurines" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Figurines, vases & more</p>
                </Link>
                <Link to="/product/p007" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1558997519-83ea9252edf8?auto=format&fit=crop&w=150&h=115&q=80" alt="Home storage" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Home storage</p>
                </Link>
                <Link to="/product/p008" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=150&h=115&q=80" alt="Lighting solutions" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Lighting solutions</p>
                </Link>
              </div>
            </div>
            <Link to="/category/home-improvement" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>Explore all</Link>
          </div>

          {/* Column 3: Up to 60% off | Footwear & handbags */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 60% off | Footwear & handbags</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <Link to="/product/p009" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=150&h=115&q=80" alt="Sports shoes" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Sports shoes</p>
                </Link>
                <Link to="/product/p010" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=150&h=115&q=80" alt="Men's shoes" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Men's shoes</p>
                </Link>
                <Link to="/product/p011" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=150&h=115&q=80" alt="Women's shoes" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Women's shoes</p>
                </Link>
                <Link to="/product/p012" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=150&h=115&q=80" alt="Handbags" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333", lineHeight: "1.2" }}>Handbags</p>
                </Link>
              </div>
            </div>
            <Link to="/category/shoes" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See all offers</Link>
          </div>

          {/* Column 4: Vertical Stack (Amazon Business & Sponsored Card) */}
          <div style={{ display: "flex", flexDirection: "column", gap: "16px", minHeight: "420px" }}>
            
            {/* Top Card - Amazon Business */}
            <div style={{ backgroundColor: "white", padding: "15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", flex: 1, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: "15px", fontWeight: "bold", margin: "0 0 6px 0", lineHeight: "1.3" }}>Bulk discounts + 10% guaranteed cashback!</h3>
                <span style={{ fontSize: "12px", color: "#007185", cursor: "pointer", fontWeight: "bold" }}>Register now</span>
                <span style={{ fontSize: "9px", color: "#777", display: "block", marginTop: "4px" }}>T&C apply</span>
              </div>
              <div style={{
                width: "80px",
                height: "80px",
                backgroundColor: "#ff9900",
                borderRadius: "4px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontWeight: "bold",
                fontSize: "11px",
                padding: "6px",
                textAlign: "center"
              }}>
                amazon business
              </div>
            </div>

            {/* Bottom Card - Zebronics Sponsored */}
            <Link 
              to="/product/p038"
              style={{ backgroundColor: "white", padding: "15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", flex: 1.5, display: "flex", flexDirection: "column", justifyContent: "space-between", cursor: "pointer", textDecoration: "none", color: "inherit" }}
            >
              <div style={{ display: "flex", gap: "10px", alignItems: "start" }}>
                <img 
                  src="https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=150&h=150&q=80" 
                  alt="Zebronics Keyboard" 
                  style={{ width: "80px", height: "80px", objectFit: "contain" }} 
                />
                <div>
                  <h4 style={{ fontSize: "13px", fontWeight: "bold", color: "#007185", margin: 0, textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap", width: "160px" }}>
                    Zebronics Wireless Keyboa...
                  </h4>
                  <span style={{ fontSize: "11px", color: "#777" }}>Zebronics</span>
                  <div style={{ display: "flex", alignItems: "center", gap: "2px", margin: "2px 0" }}>
                    <span style={{ color: "#f08804", fontSize: "12px" }}>⭐⭐⭐⭐½</span>
                    <span style={{ fontSize: "11px", color: "#777" }}>(315)</span>
                  </div>
                  <span style={{ backgroundColor: "#cc0c39", color: "white", fontSize: "9px", fontWeight: "bold", padding: "2px 6px", borderRadius: "2px" }}>
                    Limited time deal
                  </span>
                </div>
              </div>
              <span style={{ fontSize: "10px", color: "#777", alignSelf: "flex-end", marginTop: "4px" }}>Sponsored</span>
            </Link>

          </div>

        </div>

        {/* ROW 2: 4-Column Grid */}
        <div className="amazon-product-grid">
          
          {/* Column 1: Up to 60% off | Furniture & mattresses */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 60% off | Furniture & mattresses</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <Link to="/product/p013" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=150&h=115&q=80" alt="Mattress" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Mattress</p>
                </Link>
                <Link to="/product/p014" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&w=150&h=115&q=80" alt="Office chair" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Office chair</p>
                </Link>
                <Link to="/product/p015" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=150&h=115&q=80" alt="Sofa" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Sofa</p>
                </Link>
                <Link to="/product/p016" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1592078615290-033ee584e267?auto=format&fit=crop&w=150&h=115&q=80" alt="Bean bag" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Bean bag</p>
                </Link>
              </div>
            </div>
            <Link to="/category/furniture" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>Explore all</Link>
          </div>

          {/* Column 2: Up to 75% off | Headphones */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 75% off | Headphones</h2>
              <Link to="/product/p017" style={{ cursor: "pointer", textAlign: "center", display: "block" }}>
                <img src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&h=300&q=80" alt="boAt headphones" style={{ width: "100%", height: "250px", objectFit: "contain" }} />
              </Link>
            </div>
            <Link to="/category/headphones" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>Shop Now</Link>
          </div>

          {/* Column 3: 6 months FREE of unlimited music, ad-free */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>6 months FREE of unlimited music</h2>
              <Link 
                to="/category/headphones"
                style={{ 
                  cursor: "pointer", 
                  background: "linear-gradient(135deg, #1f1c2c 0%, #928dab 100%)", 
                  borderRadius: "6px", 
                  padding: "20px", 
                  textAlign: "center", 
                  color: "white", 
                  height: "250px", 
                  display: "flex", 
                  flexDirection: "column", 
                  justifyContent: "center", 
                  alignItems: "center",
                  textDecoration: "none"
                }} 
              >
                <i className="fa-solid fa-music" style={{ fontSize: "36px", color: "#00a8e0", marginBottom: "12px" }}></i>
                <h3 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 6px 0" }}>Amazon Music</h3>
                <p style={{ fontSize: "12px", color: "#ddd", margin: 0 }}>Ad-free, offline playback, unlimited skips.</p>
                <div style={{ backgroundColor: "#00a8e0", color: "white", padding: "6px 12px", borderRadius: "20px", fontSize: "12px", fontWeight: "bold", marginTop: "16px" }}>Try it free</div>
              </Link>
            </div>
            <Link to="/category/headphones" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>Try it free</Link>
          </div>

          {/* Column 4: Appliances for your home | Up to 55% off */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "420px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Appliances for your home | Up to 55% off</h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <Link to="/product/p018" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=150&h=115&q=80" alt="AC" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>AC</p>
                </Link>
                <Link to="/product/p019" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=150&h=115&q=80" alt="Refrigerator" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Refrigerator</p>
                </Link>
                <Link to="/product/p020" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?auto=format&fit=crop&w=150&h=115&q=80" alt="Microwave" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Microwave</p>
                </Link>
                <Link to="/product/p021" style={{ cursor: "pointer", textDecoration: "none", color: "inherit", display: "block" }}>
                  <img src="https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?auto=format&fit=crop&w=150&h=115&q=80" alt="Washing machine" style={{ width: "100%", height: "115px", objectFit: "cover" }} />
                  <p style={{ fontSize: "11px", margin: "4px 0 0 0", color: "#333" }}>Washing machine</p>
                </Link>
              </div>
            </div>
            <Link to="/category/appliances" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See more</Link>
          </div>

        </div>

        {/* SCROLL RAIL: Based on your cart (with ReturnIQ Integration badges) */}
        <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: "0 0 15px 0", color: "#111" }}>Based on your cart</h2>
          <div style={{ display: "flex", gap: "20px", overflowX: "auto", paddingBottom: "10px", scrollbarWidth: "thin" }}>
            
            {/* Item 1 - with Grade A ReturnIQ Badge */}
            <div style={{ minWidth: "160px", position: "relative" }}>
              <Link to="/product/p022" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div style={{ position: "relative", height: "140px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <img src="https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?auto=format&fit=crop&w=150&h=150&q=80" alt="Pink Pouch" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                  <ReturnIQBadge grade="A" price={220} distanceKm={2.3} productId="p022" />
                </div>
                <p style={{ fontSize: "12px", fontWeight: "bold", color: "#007185", margin: "6px 0 2px 0" }}>₹320 <span style={{ textDecoration: "line-through", color: "#777", fontWeight: "normal", fontSize: "11px" }}>₹450</span></p>
                <p style={{ fontSize: "11px", color: "#333", margin: 0, height: "32px", overflow: "hidden" }}>Premium Canvas Pencil Pouch - Pink</p>
              </Link>
            </div>

            {/* Item 2 - with Grade B ReturnIQ Badge */}
            <div style={{ minWidth: "160px", position: "relative" }}>
              <Link to="/product/p023" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div style={{ position: "relative", height: "140px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <img src="https://images.unsplash.com/photo-1586075010923-2dd4570fb338?auto=format&fit=crop&w=150&h=150&q=80" alt="Desk organizer" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                  <ReturnIQBadge grade="B" price={120} distanceKm={1.1} productId="p023" />
                </div>
                <p style={{ fontSize: "12px", fontWeight: "bold", color: "#007185", margin: "6px 0 2px 0" }}>₹190 <span style={{ textDecoration: "line-through", color: "#777", fontWeight: "normal", fontSize: "11px" }}>₹290</span></p>
                <p style={{ fontSize: "11px", color: "#333", margin: 0, height: "32px", overflow: "hidden" }}>Multi-grid Desktop Pen Stand Organizer</p>
              </Link>
            </div>

            {/* Item 3 */}
            <div style={{ minWidth: "160px" }}>
              <Link to="/product/p024" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div style={{ height: "140px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <img src="https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=150&h=150&q=80" alt="Lunch Box" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                </div>
                <p style={{ fontSize: "12px", fontWeight: "bold", color: "#111", margin: "6px 0 2px 0" }}>₹450</p>
                <p style={{ fontSize: "11px", color: "#333", margin: 0, height: "32px", overflow: "hidden" }}>Stainless Steel Insulated Lunch Box</p>
              </Link>
            </div>

            {/* Item 4 */}
            <div style={{ minWidth: "160px" }}>
              <Link to="/product/p025" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div style={{ height: "140px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <img src="https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=150&h=150&q=80" alt="Water Bottle" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                </div>
                <p style={{ fontSize: "12px", fontWeight: "bold", color: "#111", margin: "6px 0 2px 0" }}>₹380</p>
                <p style={{ fontSize: "11px", color: "#333", margin: 0, height: "32px", overflow: "hidden" }}>Vacuum Insulated Steel Sports Flask</p>
              </Link>
            </div>

            {/* Item 5 */}
            <div style={{ minWidth: "160px" }}>
              <Link to="/product/p026" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div style={{ height: "140px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <img src="https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=150&h=150&q=80" alt="Color Markers" style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                </div>
                <p style={{ fontSize: "12px", fontWeight: "bold", color: "#111", margin: "6px 0 2px 0" }}>₹240</p>
                <p style={{ fontSize: "11px", color: "#333", margin: 0, height: "32px", overflow: "hidden" }}>Gel Pen Pack - 12 Vibrant Colors</p>
              </Link>
            </div>

          </div>
        </div>

        {/* ROW 3: Full-width Horizontal Scroll Banner */}
        <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
            <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: 0, color: "#111" }}>
              Up to 60% off | Cookware, kitchen tool & more | Amazon Launchpad
            </h2>
            <Link to="/category/kitchen" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", textDecoration: "none" }}>See all</Link>
          </div>
          <div style={{ display: "flex", gap: "20px", overflowX: "auto", paddingBottom: "10px", scrollbarWidth: "thin" }}>
            
            {/* Scrollable cookware/kitchen list */}
            {[
              { id: "p027", name: "Non-Stick Wok Pan (26cm)", price: 1290, img: "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=150&h=80&q=80", discount: "35% off" },
              { id: "p028", name: "Premium Chef Knife Set with Block", price: 1850, img: "https://images.unsplash.com/photo-1593618998160-e34014e67546?auto=format&fit=crop&w=150&h=80&q=80", discount: "40% off" },
              { id: "p029", name: "Stainless Steel Kitchen Colander", price: 420, img: "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&w=150&h=80&q=80", discount: "25% off" },
              { id: "p030", name: "Cute Ceramic Cat Mug", price: 350, img: "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=150&h=80&q=80", discount: "15% off" },
              { id: "p031", name: "Leak-Proof Food Lunch Jar", price: 890, img: "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=150&h=80&q=80", discount: "30% off" },
              { id: "p032", name: "Insulated Beverage Flask", price: 790, img: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=150&h=80&q=80", discount: "20% off" },
              { id: "p033", name: "Non-Slip Silicone Pastry Mat", price: 290, img: "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=150&h=80&q=80", discount: "50% off" }
            ].map((prod, idx) => (
              <div 
                key={idx} 
                style={{ minWidth: "160px", cursor: "pointer", display: "flex", flexDirection: "column" }}
              >
                <Link to={`/product/${prod.id}`} style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                  <div style={{ height: "130px", backgroundColor: "#f9f9f9", borderRadius: "4px", display: "flex", alignItems: "center", justifyContent: "center", padding: "10px" }}>
                    <img src={prod.img} alt={prod.name} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                  </div>
                  <div style={{ display: "flex", gap: "6px", alignItems: "center", marginTop: "6px" }}>
                    <span style={{ backgroundColor: "#cc0c39", color: "white", fontSize: "10px", fontWeight: "bold", padding: "1px 5px", borderRadius: "2px" }}>
                      {prod.discount}
                    </span>
                    <span style={{ fontSize: "11px", fontWeight: "bold", color: "#cc0c39" }}>Deal</span>
                  </div>
                  <p style={{ fontSize: "13px", fontWeight: "bold", color: "#111", margin: "4px 0 2px 0" }}>₹{prod.price}</p>
                  <p style={{ fontSize: "11px", color: "#555", margin: 0, height: "32px", overflow: "hidden" }}>{prod.name}</p>
                </Link>
              </div>
            ))}

          </div>
        </div>

        {/* ROW 3 Grid: 4 Columns below scroll banner */}
        <div className="amazon-product-grid">
          
          {/* Column 1: Start your fitness journey */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "380px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 60% off | Start your fitness journey</h2>
              <Link to="/product/p034" style={{ cursor: "pointer", display: "block" }}>
                <img src="https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=300&h=200&q=80" alt="Gym boxing room" style={{ width: "100%", height: "200px", objectFit: "cover", borderRadius: "4px" }} />
              </Link>
            </div>
            <Link to="/category/sports" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See more</Link>
          </div>

          {/* Column 2: Starting at ₹399 | Deals on cookware & dining */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "380px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Starting at ₹399 | Deals on cookware & dining</h2>
              <Link 
                to="/product/p035"
                style={{ cursor: "pointer", textAlign: "center", border: "1px solid #eee", padding: "10px", borderRadius: "4px", display: "block", textDecoration: "none", color: "inherit" }}
              >
                <img src="https://images.unsplash.com/photo-1577937927133-66ef06acdf18?auto=format&fit=crop&w=180&h=180&q=80" alt="Ceramic mugs" style={{ height: "150px", objectFit: "contain" }} />
                <p style={{ fontSize: "13px", fontWeight: "bold", margin: "6px 0 0 0", color: "#B12704" }}>
                  ₹675 <span style={{ textDecoration: "line-through", color: "#777", fontWeight: "normal", fontSize: "11px" }}>MRP ₹1,160</span>
                </p>
                <p style={{ fontSize: "11px", color: "#555", margin: "2px 0 0 0" }}>Set of 6 Premium Ceramic Coffee Mugs</p>
              </Link>
            </div>
            <Link to="/category/kitchen" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>Explore offers</Link>
          </div>

          {/* Column 3: Up to 60% off | Best offers on kitchen products */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "380px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 60% off | Best offers on kitchen products</h2>
              <Link 
                to="/product/p036"
                style={{ cursor: "pointer", textAlign: "center", border: "1px solid #eee", padding: "10px", borderRadius: "4px", display: "block", textDecoration: "none", color: "inherit" }}
              >
                <img src="https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=180&h=180&q=80" alt="Water Bottle" style={{ height: "150px", objectFit: "contain" }} />
                <p style={{ fontSize: "13px", fontWeight: "bold", margin: "6px 0 0 0", color: "#B12704" }}>
                  ₹998 <span style={{ textDecoration: "line-through", color: "#777", fontWeight: "normal", fontSize: "11px" }}>MRP ₹2,199</span>
                </p>
                <p style={{ fontSize: "11px", color: "#555", margin: "2px 0 0 0" }}>Double-Wall Insulated Steel Flask</p>
              </Link>
            </div>
            <Link to="/category/kitchen" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See all deals</Link>
          </div>

          {/* Column 4: Up to 50% off | International brands */}
          <div style={{ backgroundColor: "white", padding: "20px 15px", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", display: "flex", flexDirection: "column", justifyContent: "space-between", minHeight: "380px" }}>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: "bold", margin: "0 0 12px 0", color: "#111" }}>Up to 50% off | International brands</h2>
              <Link to="/product/p037" style={{ cursor: "pointer", display: "block" }}>
                <img src="https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=300&h=200&q=80" alt="Robot vacuum and air purifier" style={{ width: "100%", height: "200px", objectFit: "cover", borderRadius: "4px" }} />
              </Link>
            </div>
            <Link to="/category/appliances" style={{ fontSize: "13px", color: "#007185", cursor: "pointer", fontWeight: "bold", marginTop: "12px", display: "inline-block", textDecoration: "none" }}>See all offers</Link>
          </div>

        </div>

      </div>
    </div>
  );
}
