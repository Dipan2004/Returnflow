import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleSignOut() {
    await logout();
    onClose();
    navigate("/login");
  }

  return (
    <div
      className={`sidebar-container-navigation ${isOpen ? "slidebar-show" : ""}`}
      id="sidebar-container-navigation-id"
      onClick={onClose}
    >
      <div className="sidebar-left-part" onClick={(e) => e.stopPropagation()}>
        <div className="sidebar-top">
          <i className="fa-solid fa-circle-user"></i>
          <h2>
            Hello, <span>{user ? user.name : "sign in"}</span>
          </h2>
        </div>
        <div className="sidebar-wrap">
          <div className="sidebar-item">
            <h2>ReturnIQ</h2>
            <p>
              <Link to="/my-returns" onClick={onClose} style={{ color: "#27726b", textDecoration: "none", fontWeight: 500 }}>
                My Returns
              </Link>
            </p>
          </div>
          <div className="sidebar-item">
            <h2>Trending</h2>
            <p>Best Sellers</p>
            <p>New Releases</p>
            <p>Movers and Shakers</p>
          </div>
          <div className="sidebar-item">
            <h2>Digital Content And Devices</h2>
            <p>Echo & Alexa</p>
            <p>Fire TV</p>
            <p>Kindle E-Readers & eBooks</p>
            <p>Audible Audiobooks</p>
            <p>Amazon Prime Video</p>
            <p>Amazon Prime Music</p>
          </div>
          <div className="sidebar-item">
            <h2>Shop By Category</h2>
            <p>Mobiles, Computers</p>
            <p>TV, Appliances, Electronics</p>
            <p>Men's Fashion</p>
            <p>Women's Fashion</p>
            <p>See All</p>
          </div>
          <div className="sidebar-item">
            <h2>Programs & Features</h2>
            <p>Gift Cards & Mobile Recharges</p>
            <p>Flight Tickets</p>
            <p>#FoundIt-OnAmazon</p>
            <p>Clearance store</p>
          </div>
          <div className="sidebar-item">
            <h2>Help & Settings</h2>
            <p>Your Account</p>
            <p>Customer Service</p>
            {user ? (
              <p onClick={handleSignOut} style={{ cursor: "pointer" }}>
                Sign out
              </p>
            ) : (
              <p>
                <Link to="/login" onClick={onClose}>
                  Sign in
                </Link>
              </p>
            )}
          </div>
        </div>
      </div>
      <button id="sidebar-navigation-close" onClick={onClose}>
        <i className="fa-solid fa-xmark"></i>
      </button>
    </div>
  );
}
