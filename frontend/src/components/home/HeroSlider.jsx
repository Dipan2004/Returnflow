import React from "react";
import bannerImg from "../../assets/returniq-banner.jpg";

export default function HeroSlider() {
  return (
    <section 
      className="hero-carousel" 
      aria-label="Featured shopping banner" 
      style={{ 
        position: "relative", 
        width: "100%", 
        height: "420px", 
        overflow: "hidden",
        backgroundColor: "#EAEDED"
      }}
    >
      <img 
        src={bannerImg} 
        alt="ReturnIQ: Every return gets a second life"
        style={{
          width: "100%",
          height: "420px",
          objectFit: "cover",
          objectPosition: "center",
          display: "block"
        }}
      />

      {/* Chevron Left Arrow */}
      <button 
        style={{
          position: "absolute",
          top: "50%",
          left: "20px",
          transform: "translateY(-50%)",
          background: "rgba(255, 255, 255, 0.4)",
          border: "none",
          borderRadius: "4px",
          width: "44px",
          height: "50px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          zIndex: 10,
          boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
          outline: "none"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <i className="fa-solid fa-angle-left" style={{ fontSize: "24px", color: "#333" }}></i>
      </button>

      {/* Chevron Right Arrow */}
      <button 
        style={{
          position: "absolute",
          top: "50%",
          right: "20px",
          transform: "translateY(-50%)",
          background: "rgba(255, 255, 255, 0.4)",
          border: "none",
          borderRadius: "4px",
          width: "44px",
          height: "50px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          zIndex: 10,
          boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
          outline: "none"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <i className="fa-solid fa-angle-right" style={{ fontSize: "24px", color: "#333" }}></i>
      </button>
    </section>
  );
}
