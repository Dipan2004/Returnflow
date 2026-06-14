import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Navbar({ onSidebarOpen }) {
  const { role } = useAuth();

  if (role !== "customer") return null;

  return (
    <nav className="nav" style={{ height: "40px", backgroundColor: "#232f3d", display: "flex", alignItems: "center", padding: "0 16px" }}>
      <div className="container container-nav" style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", height: "100%" }}>
        <ul className="nav-menu-list" style={{ display: "flex", alignItems: "center", gap: "6px", listStyle: "none", margin: 0, padding: 0, height: "100%", overflowX: "auto", whiteSpace: "nowrap" }}>
          
          {/* All sidebar trigger */}
          <li
            className="border-white"
            id="open-nav-sidebar"
            onClick={onSidebarOpen}
            style={{ cursor: "pointer", color: "white", padding: "5px 8px", fontSize: "13px", fontWeight: "bold", display: "flex", alignItems: "center" }}
          >
            <span className="open-nav-slider" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <i className="fa-solid fa-bars"></i>
              All
            </span>
          </li>

          {/* Rufus Capsule Pill */}
          <li className="border-white" style={{ padding: "0 4px", display: "flex", alignItems: "center" }}>
            <a href="#" style={{ 
              color: "black", 
              textDecoration: "none", 
              backgroundColor: "white", 
              padding: "2px 10px", 
              borderRadius: "12px", 
              display: "flex", 
              alignItems: "center", 
              gap: "4px",
              fontWeight: "800",
              fontSize: "12px",
              height: "22px",
              boxShadow: "0 1px 2px rgba(0,0,0,0.15)"
            }}>
              {/* Rufus logo icon: blue bubble + orange dot */}
              <span style={{ display: "inline-flex", position: "relative", width: "12px", height: "12px", alignItems: "center" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#3b82f6", display: "block" }}></span>
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", backgroundColor: "#f08804", display: "block", position: "absolute", left: "-2px", top: "2px" }}></span>
              </span>
              Rufus
            </a>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <Link to="/category/kitchen" style={{ color: "white", textDecoration: "none" }}>Fresh</Link>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <a href="#" style={{ color: "white", textDecoration: "none" }}>MX Player</a>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <a href="#" style={{ color: "white", textDecoration: "none" }}>Sell</a>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <a href="#" style={{ color: "white", textDecoration: "none" }}>Amazon Pay</a>
          </li>



          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <Link to="/orders" style={{ color: "white", textDecoration: "none" }}>Buy Again</Link>
          </li>

          {/* Prime Dropdown */}
          <li className="border-white prime-image-hover" style={{ padding: "5px 8px", fontSize: "13px", position: "relative" }}>
            <a href="#" style={{ color: "white", textDecoration: "none", display: "flex", alignItems: "center", gap: "2px" }}>
              Prime <span style={{ fontSize: "8px", color: "#ccc" }}>▼</span>
            </a>
            <div className="prime-image" style={{ display: "none", position: "absolute", top: "100%", left: 0, zIndex: 10, width: "320px", background: "white", boxShadow: "0 4px 12px rgba(0,0,0,0.15)", borderRadius: "4px" }}>
              <img
                src="https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&fit=crop&auto=format"
                alt="Prime Offer"
                style={{ width: "100%", height: "auto", borderRadius: "4px" }}
              />
            </div>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <Link to="/category/stationery" style={{ color: "white", textDecoration: "none" }}>AmazonBasics</Link>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <a href="#" style={{ color: "white", textDecoration: "none" }}>Subscribe & Save</a>
          </li>

          {/* Amazon Business Dropdown */}
          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <a href="#" style={{ color: "white", textDecoration: "none", display: "flex", alignItems: "center", gap: "2px" }}>
              Amazon Business <span style={{ fontSize: "8px", color: "#ccc" }}>▼</span>
            </a>
          </li>



          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <Link to="/category/home-improvement" style={{ color: "white", textDecoration: "none" }}>Home Improvement</Link>
          </li>

          <li className="border-white" style={{ padding: "5px 8px", fontSize: "13px" }}>
            <Link to="/" style={{ color: "white", textDecoration: "none", fontWeight: "bold" }}>Today's Deals</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}
