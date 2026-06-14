import React, { useState } from "react";
import { todayDeal } from "../../data/todayDeal";
import ReturnIQBadge from "../returniq/ReturnIQBadge";
import { Link } from "react-router-dom";

export default function TodayDeals() {
  const [startProduct, setStartProduct] = useState(0);

  function handlePrev() {
    if (startProduct < 0) {
      setStartProduct((p) => p + 500);
    }
  }

  function handleNext() {
    if (startProduct > -1500) {
      setStartProduct((p) => p - 500);
    }
  }

  return (
    <section className="today_deals_container" style={{ background: "white", fontFamily: "Arial, sans-serif" }}>
      <div className="today_deals_heading">
        <h2 style={{ fontSize: 20, margin: 0, padding: "10px 0", fontWeight: "bold", color: "#111" }}>Today's Deals</h2>
        <p style={{ margin: 0, paddingLeft: 16 }}>
          <Link to="/" style={{ color: "#007185", textDecoration: "none", fontSize: 13 }}>See all deals</Link>
        </p>
      </div>

      <div className="today_deals_product_container">
        <div className="today_deals_btn_container">
          <button className="today_deal_btn" id="today_deal_btn_prev" onClick={handlePrev}>
            <i className="fa-solid fa-angle-left"></i>
          </button>
          <button className="today_deal_btn" id="today_deal_btn_next" onClick={handleNext}>
            <i className="fa-solid fa-angle-right"></i>
          </button>
        </div>

        <div className="today_deals_product_list">
          {todayDeal.map((item, idx) => (
            <div
              className="today_deals_product_item"
              key={idx}
              style={{
                transform: `translateX(${startProduct}%)`,
                transition: "transform 1s",
                position: "relative",
                cursor: "pointer",
              }}
            >
              <Link to={`/product/${item.productId}`} style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div className="todayDeals_product_image">
                  <img src={item.img} alt={item.desc} style={{ objectFit: "contain", backgroundColor: "white" }} />
                </div>
              </Link>

              {idx === 0 && (
                <ReturnIQBadge
                  grade="A"
                  price={380}
                  distanceKm={2.3}
                  productId={item.productId}
                />
              )}
              {idx === 1 && (
                <ReturnIQBadge
                  grade="B"
                  price={220}
                  distanceKm={1.1}
                  productId={item.productId}
                />
              )}

              <Link to={`/product/${item.productId}`} style={{ textDecoration: "none", color: "inherit", display: "block" }}>
                <div className="discount_Contaienr">
                  <span style={{ backgroundColor: "#cc0c39", color: "white", padding: "2px 6px", borderRadius: "2px", fontSize: "12px", fontWeight: "bold", marginRight: "6px" }}>
                    Up to {item.discount}% off
                  </span>
                  <span style={{ color: "#cc0c39", fontSize: "12px", fontWeight: "bold" }}>{item.DealOfDay}</span>
                </div>
                <p style={{ fontSize: 12, marginTop: 6, color: "#0F1111", height: 36, overflow: "hidden" }}>
                  {item.desc}
                </p>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
