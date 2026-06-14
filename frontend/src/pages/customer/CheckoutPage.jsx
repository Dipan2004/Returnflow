import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useCart } from "../../contexts/CartContext";
import { products } from "../../data/products";
import Header from "../../components/layout/Header";
import Navbar from "../../components/layout/Navbar";
import Sidebar from "../../components/layout/Sidebar";

export default function CheckoutPage() {
  const { cart, placeOrder } = useCart();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  // Accordion state: 1 = Address, 2 = Payment, 3 = Review
  const [activeStep, setActiveStep] = useState(1);

  // Form states
  const [address, setAddress] = useState({
    fullName: "Archi",
    street: "123 Technology Corridor, Patia",
    city: "Bhubaneswar",
    state: "Odisha",
    zipCode: "751024",
    phone: "+91 98765 43210"
  });

  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [upiId, setUpiId] = useState("archi@okaxis");

  // Resolve cart items
  const cartItems = cart.map((item) => {
    const product = products.find((p) => p.id === item.productId);
    return {
      ...item,
      product
    };
  }).filter(item => item.product);

  if (cartItems.length === 0) {
    return (
      <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
        <Header />
        <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div style={{ maxWidth: "600px", margin: "40px auto", padding: "30px", backgroundColor: "white", borderRadius: "4px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)", textAlign: "center" }}>
          <h2>Your cart is empty</h2>
          <p style={{ color: "#565959", margin: "10px 0 20px 0" }}>Please add some items to your cart before checking out.</p>
          <Link to="/" style={{ display: "inline-block", backgroundColor: "#ffd814", color: "#111", padding: "10px 24px", borderRadius: "20px", textDecoration: "none", fontWeight: "bold" }}>
            Return to Shopping
          </Link>
        </div>
      </div>
    );
  }

  const itemsSubtotal = cartItems.reduce((sum, item) => {
    const price = item.isPreOwned
      ? item.product.returniqPrice || Math.floor(item.product.price * 0.75)
      : item.product.price;
    return sum + price * item.quantity;
  }, 0);

  const shipping = itemsSubtotal > 499 ? 0 : 40;
  const tax = Math.floor(itemsSubtotal * 0.18);
  const orderTotal = itemsSubtotal + shipping + tax;

  const handlePlaceOrder = () => {
    // Triggers placeOrder in context, which adds items to orders list & clears cart
    placeOrder(cartItems);
    alert("🎉 Order placed successfully! Thank you for shopping with ReturnIQ.");
    navigate("/orders");
  };

  return (
    <div style={{ backgroundColor: "#EAEDED", minHeight: "100vh", fontFamily: "Arial, sans-serif", paddingBottom: "60px" }}>
      {/* Custom simple header for checkout */}
      <header style={{ backgroundColor: "#131921", padding: "12px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Link to="/" style={{ textDecoration: "none", color: "white", display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ fontSize: "22px", fontWeight: "bold", tracking: "-1px" }}>amazon</span>
          <span style={{ color: "#ff9900", fontSize: "18px", fontWeight: "bold" }}>.in</span>
          <span style={{ color: "#4ecca3", fontSize: "14px", marginLeft: "12px", borderLeft: "1px solid #555", paddingLeft: "12px", fontWeight: "bold" }}>ReturnIQ Checkout</span>
        </Link>
        <div style={{ color: "#c4c4c4", fontSize: "14px" }}>
          🔒 Secure Checkout
        </div>
      </header>

      <main style={{ maxWidth: "1150px", margin: "30px auto 0 auto", padding: "0 20px", display: "flex", gap: "20px", alignItems: "flex-start" }}>
        
        {/* Accordion container */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
          
          {/* Step 1: Delivery Address */}
          <div style={{ backgroundColor: "white", borderRadius: "4px", border: "1px solid #ddd", overflow: "hidden" }}>
            <div 
              style={{ padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer", backgroundColor: activeStep === 1 ? "#fff" : "#f6f6f6" }}
              onClick={() => setActiveStep(1)}
            >
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: 0, display: "flex", gap: "12px", color: activeStep === 1 ? "#c45500" : "#111" }}>
                <span>1</span>
                <span>Delivery address</span>
              </h2>
              {activeStep !== 1 && (
                <span style={{ fontSize: "13px", color: "#007185" }}>Change</span>
              )}
            </div>
            
            {activeStep === 1 ? (
              <div style={{ padding: "20px 24px", borderTop: "1px solid #eee" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: "12px", maxWidth: "400px" }}>
                  <div>
                    <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "4px" }}>Full Name</label>
                    <input 
                      type="text" 
                      value={address.fullName} 
                      onChange={(e) => setAddress({ ...address, fullName: e.target.value })}
                      style={{ width: "100%", padding: "6px 10px", border: "1px solid #a6a6a6", borderRadius: "3px" }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "4px" }}>Street Address</label>
                    <input 
                      type="text" 
                      value={address.street} 
                      onChange={(e) => setAddress({ ...address, street: e.target.value })}
                      style={{ width: "100%", padding: "6px 10px", border: "1px solid #a6a6a6", borderRadius: "3px" }}
                    />
                  </div>
                  <div style={{ display: "flex", gap: "12px" }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "4px" }}>City</label>
                      <input 
                        type="text" 
                        value={address.city} 
                        onChange={(e) => setAddress({ ...address, city: e.target.value })}
                        style={{ width: "100%", padding: "6px 10px", border: "1px solid #a6a6a6", borderRadius: "3px" }}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: "block", fontSize: "13px", fontWeight: "bold", marginBottom: "4px" }}>Pincode</label>
                      <input 
                        type="text" 
                        value={address.zipCode} 
                        onChange={(e) => setAddress({ ...address, zipCode: e.target.value })}
                        style={{ width: "100%", padding: "6px 10px", border: "1px solid #a6a6a6", borderRadius: "3px" }}
                      />
                    </div>
                  </div>
                  <button 
                    onClick={() => setActiveStep(2)}
                    style={{ backgroundColor: "#ffd814", border: "1px solid #fcd200", padding: "8px 16px", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", alignSelf: "flex-start", marginTop: "8px" }}
                  >
                    Use this address
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ padding: "0 24px 16px 24px", fontSize: "14px", color: "#333" }}>
                <div><strong>{address.fullName}</strong></div>
                <div>{address.street}, {address.city}, {address.state} - {address.zipCode}</div>
              </div>
            )}
          </div>

          {/* Step 2: Payment Method */}
          <div style={{ backgroundColor: "white", borderRadius: "4px", border: "1px solid #ddd", overflow: "hidden" }}>
            <div 
              style={{ padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer", backgroundColor: activeStep === 2 ? "#fff" : "#f6f6f6" }}
              onClick={() => setActiveStep(2)}
            >
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: 0, display: "flex", gap: "12px", color: activeStep === 2 ? "#c45500" : "#111" }}>
                <span>2</span>
                <span>Payment method</span>
              </h2>
              {activeStep !== 2 && activeStep > 2 && (
                <span style={{ fontSize: "13px", color: "#007185" }}>Change</span>
              )}
            </div>

            {activeStep === 2 ? (
              <div style={{ padding: "20px 24px", borderTop: "1px solid #eee", display: "flex", flexDirection: "column", gap: "16px" }}>
                
                {/* UPI Option */}
                <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "4px", backgroundColor: paymentMethod === "UPI" ? "#fcf8f2" : "white" }}>
                  <label style={{ display: "flex", alignItems: "flex-start", gap: "10px", cursor: "pointer" }}>
                    <input 
                      type="radio" 
                      name="payment" 
                      checked={paymentMethod === "UPI"} 
                      onChange={() => setPaymentMethod("UPI")} 
                      style={{ marginTop: "4px" }}
                    />
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: "14px", fontWeight: "bold", display: "block" }}>BHIM UPI (Recommended)</span>
                      <span style={{ fontSize: "12px", color: "#565959" }}>Instant payment via Google Pay, PhonePe, Paytm, or your bank UPI app.</span>
                      
                      {paymentMethod === "UPI" && (
                        <div style={{ marginTop: "12px", display: "flex", gap: "8px", maxWidth: "300px" }}>
                          <input 
                            type="text" 
                            placeholder="Enter UPI ID (e.g. user@okaxis)" 
                            value={upiId}
                            onChange={(e) => setUpiId(e.target.value)}
                            style={{ flex: 1, padding: "6px 10px", border: "1px solid #a6a6a6", borderRadius: "3px", fontSize: "13px" }}
                          />
                          <button style={{ backgroundColor: "#e7e9ec", border: "1px solid #adb1b8", padding: "4px 12px", borderRadius: "3px", fontSize: "12px", cursor: "pointer" }}>Verify</button>
                        </div>
                      )}
                    </div>
                  </label>
                </div>

                {/* Card Option */}
                <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "4px", backgroundColor: paymentMethod === "Card" ? "#fcf8f2" : "white" }}>
                  <label style={{ display: "flex", alignItems: "flex-start", gap: "10px", cursor: "pointer" }}>
                    <input 
                      type="radio" 
                      name="payment" 
                      checked={paymentMethod === "Card"} 
                      onChange={() => setPaymentMethod("Card")}
                      style={{ marginTop: "4px" }}
                    />
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: "14px", fontWeight: "bold", display: "block" }}>Credit or Debit Card</span>
                      <span style={{ fontSize: "12px", color: "#565959" }}>Visa, Mastercard, RuPay, Maestro, etc. supported.</span>
                    </div>
                  </label>
                </div>

                {/* COD Option */}
                <div style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "4px", backgroundColor: paymentMethod === "COD" ? "#fcf8f2" : "white" }}>
                  <label style={{ display: "flex", alignItems: "flex-start", gap: "10px", cursor: "pointer" }}>
                    <input 
                      type="radio" 
                      name="payment" 
                      checked={paymentMethod === "COD"} 
                      onChange={() => setPaymentMethod("COD")}
                      style={{ marginTop: "4px" }}
                    />
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: "14px", fontWeight: "bold", display: "block" }}>Cash on Delivery (COD)</span>
                      <span style={{ fontSize: "12px", color: "#565959" }}>Pay with cash or digital UPI upon receiving the order.</span>
                    </div>
                  </label>
                </div>

                <button 
                  onClick={() => setActiveStep(3)}
                  style={{ backgroundColor: "#ffd814", border: "1px solid #fcd200", padding: "8px 16px", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", alignSelf: "flex-start", marginTop: "8px" }}
                >
                  Use this payment method
                </button>
              </div>
            ) : (
              <div style={{ padding: "0 24px 16px 24px", fontSize: "14px", color: "#333" }}>
                <div>Pay using: <strong>{paymentMethod === "UPI" ? `UPI (${upiId})` : paymentMethod}</strong></div>
              </div>
            )}
          </div>

          {/* Step 3: Review Items and Delivery */}
          <div style={{ backgroundColor: "white", borderRadius: "4px", border: "1px solid #ddd", overflow: "hidden" }}>
            <div 
              style={{ padding: "16px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer", backgroundColor: activeStep === 3 ? "#fff" : "#f6f6f6" }}
              onClick={() => {
                if (activeStep > 2) setActiveStep(3);
              }}
            >
              <h2 style={{ fontSize: "18px", fontWeight: "bold", margin: 0, display: "flex", gap: "12px", color: activeStep === 3 ? "#c45500" : "#111" }}>
                <span>3</span>
                <span>Offers & items review</span>
              </h2>
            </div>

            {activeStep === 3 && (
              <div style={{ padding: "20px 24px", borderTop: "1px solid #eee" }}>
                <h3 style={{ fontSize: "15px", fontWeight: "bold", margin: "0 0 12px 0" }}>Review items for delivery</h3>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {cartItems.map((item, idx) => {
                    const product = item.product;
                    const price = item.isPreOwned
                      ? product.returniqPrice || Math.floor(product.price * 0.75)
                      : product.price;

                    return (
                      <div key={idx} style={{ display: "flex", gap: "12px", borderBottom: "1px solid #eee", paddingBottom: "12px" }}>
                        <img 
                          src={product.image} 
                          alt={product.name} 
                          style={{ width: "60px", height: "60px", objectFit: "contain", border: "1px solid #eee", borderRadius: "4px" }} 
                        />
                        <div style={{ flex: 1 }}>
                          <h4 style={{ fontSize: "14px", fontWeight: "bold", margin: "0 0 4px 0" }}>{product.name}</h4>
                          <span style={{ fontSize: "12px", color: "#565959", display: "block" }}>Qty: {item.quantity} | Size: {item.selectedSize}</span>
                          {item.isPreOwned && (
                            <span style={{ fontSize: "11px", color: "#007600", display: "inline-block", backgroundColor: "#e8f5e9", padding: "1px 6px", borderRadius: "10px", fontWeight: "bold", marginTop: "4px" }}>
                              ♻️ Pre-Owned (Grade {product.returniqGrade})
                            </span>
                          )}
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <span style={{ fontSize: "15px", fontWeight: "bold" }}>₹{price * item.quantity}</span>
                          {item.quantity > 1 && (
                            <span style={{ fontSize: "11px", color: "#565959", display: "block" }}>(₹{price} each)</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div style={{ marginTop: "20px", display: "flex", justifyContent: "flex-end" }}>
                  <button 
                    onClick={handlePlaceOrder}
                    style={{
                      backgroundColor: "#ffd814",
                      border: "1px solid #fcd200",
                      padding: "12px 24px",
                      borderRadius: "24px",
                      cursor: "pointer",
                      fontWeight: "bold",
                      fontSize: "14px",
                      boxShadow: "0 2px 5px rgba(213,217,217,0.5)"
                    }}
                  >
                    Place your order
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>

        {/* Right side order summary sticky bar */}
        <div style={{ width: "300px", backgroundColor: "white", padding: "20px", borderRadius: "4px", border: "1px solid #ddd", position: "sticky", top: "20px" }}>
          
          <button 
            onClick={handlePlaceOrder}
            disabled={activeStep < 3}
            style={{
              width: "100%",
              backgroundColor: activeStep === 3 ? "#ffa41c" : "#e7e9ec",
              border: activeStep === 3 ? "1px solid #ff9900" : "1px solid #adb1b8",
              color: activeStep === 3 ? "#111" : "#888",
              padding: "10px 0",
              borderRadius: "20px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: activeStep === 3 ? "pointer" : "not-allowed",
              boxShadow: activeStep === 3 ? "0 2px 5px rgba(213,217,217,0.5)" : "none",
              outline: "none",
              marginBottom: "16px"
            }}
          >
            Place your order
          </button>
          
          <span style={{ fontSize: "11px", color: "#565959", display: "block", textAlign: "center", marginBottom: "16px" }}>
            By placing your order, you agree to Amazon's conditions of use and privacy policy.
          </span>

          <hr style={{ border: "none", borderTop: "1px solid #ddd", margin: "12px 0" }} />

          <h3 style={{ fontSize: "16px", fontWeight: "bold", margin: "0 0 12px 0" }}>Order Summary</h3>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px", color: "#565959" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Items:</span>
              <span>₹{itemsSubtotal}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Delivery:</span>
              <span>{shipping === 0 ? "FREE" : `₹${shipping}`}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Taxes (GST 18%):</span>
              <span>₹{tax}</span>
            </div>
          </div>

          <hr style={{ border: "none", borderTop: "1px solid #ddd", margin: "12px 0" }} />

          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "18px", fontWeight: "bold", color: "#B12704" }}>
            <span>Order Total:</span>
            <span>₹{orderTotal}</span>
          </div>

          {itemsSubtotal > 499 && (
            <div style={{ marginTop: "12px", fontSize: "12px", color: "#007600", fontWeight: "bold", display: "flex", gap: "6px" }}>
              <span>🌱</span>
              <span>Your order qualifies for Free Green Shipping</span>
            </div>
          )}
        </div>

      </main>
    </div>
  );
}
