import React, { createContext, useContext, useState, useEffect } from "react";
import { products } from "../data/products";

const CartContext = createContext(null);
export const useCart = () => useContext(CartContext);

const DEFAULT_ORDERS = [
  { orderId: "ORD-992813", productId: "p009", quantity: 1, selectedSize: "8", isPreOwned: false, status: "Delivered", orderedAt: "2026-06-02T10:00:00.000Z", deliveryDate: "4 Jun 2026" },
  { orderId: "ORD-887711", productId: "p017", quantity: 1, selectedSize: "M", isPreOwned: false, status: "Delivered", orderedAt: "2026-05-28T10:00:00.000Z", deliveryDate: "30 May 2026" }
];

export function CartProvider({ children }) {
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem("returniq_cart");
    return saved ? JSON.parse(saved) : [];
  });

  const [wishlist, setWishlist] = useState(() => {
    const saved = localStorage.getItem("returniq_wishlist");
    return saved ? JSON.parse(saved) : [];
  });

  const [orders, setOrders] = useState(() => {
    const saved = localStorage.getItem("returniq_orders");
    return saved ? JSON.parse(saved) : DEFAULT_ORDERS;
  });

  const [returns, setReturns] = useState(() => {
    const saved = localStorage.getItem("returniq_returns");
    return saved ? JSON.parse(saved) : [];
  });

  // Health Card Modal global states
  const [healthCardProductId, setHealthCardProductId] = useState(null);
  const [healthCardModalOpen, setHealthCardModalOpen] = useState(false);

  // Sync with localStorage
  useEffect(() => {
    localStorage.setItem("returniq_cart", JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    localStorage.setItem("returniq_wishlist", JSON.stringify(wishlist));
  }, [wishlist]);

  useEffect(() => {
    localStorage.setItem("returniq_orders", JSON.stringify(orders));
  }, [orders]);

  useEffect(() => {
    localStorage.setItem("returniq_returns", JSON.stringify(returns));
  }, [returns]);

  // Actions
  function addToCart(productId, quantity = 1, selectedSize = "Free", isPreOwned = false) {
    setCart((prev) => {
      const idx = prev.findIndex(
        (item) =>
          item.productId === productId &&
          item.selectedSize === selectedSize &&
          item.isPreOwned === isPreOwned
      );
      if (idx > -1) {
        const next = [...prev];
        next[idx] = { ...next[idx], quantity: next[idx].quantity + quantity };
        return next;
      }
      return [...prev, { productId, quantity, selectedSize, isPreOwned, addedAt: new Date().toISOString() }];
    });
  }

  function removeFromCart(productId, selectedSize, isPreOwned) {
    setCart((prev) =>
      prev.filter(
        (item) =>
          !(
            item.productId === productId &&
            item.selectedSize === selectedSize &&
            item.isPreOwned === isPreOwned
          )
      )
    );
  }

  function updateQuantity(productId, quantity, selectedSize, isPreOwned) {
    setCart((prev) =>
      prev.map((item) =>
        item.productId === productId &&
        item.selectedSize === selectedSize &&
        item.isPreOwned === isPreOwned
          ? { ...item, quantity: Math.max(1, quantity) }
          : item
      )
    );
  }

  function addToWishlist(productId) {
    setWishlist((prev) => {
      if (prev.some((item) => item.productId === productId)) return prev;
      return [...prev, { productId, savedAt: new Date().toISOString() }];
    });
  }

  function removeFromWishlist(productId) {
    setWishlist((prev) => prev.filter((item) => item.productId !== productId));
  }

  function placeOrder(itemsToOrder) {
    const newOrders = itemsToOrder.map((item) => ({
      orderId: "ORD-" + Math.floor(100000 + Math.random() * 900000),
      productId: item.productId,
      quantity: item.quantity,
      selectedSize: item.selectedSize,
      isPreOwned: item.isPreOwned,
      status: "Delivered", // Instant delivery so they are instantly returnable
      orderedAt: new Date().toISOString(),
      deliveryDate: new Date(Date.now() + 1000 * 60).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
      })
    }));

    setOrders((prev) => [...newOrders, ...prev]);
    // Clear cart
    setCart([]);
  }

  function initiateReturn(orderId, productId, returniqGrade, recoveryValue, carbonAvoided, routeOption, reason) {
    const product = products.find((p) => p.id === productId) || {};
    const lastReturnId = localStorage.getItem("returniq_last_return_id");
    const returnId = lastReturnId || ("ret-" + Math.floor(100000 + Math.random() * 900000));
    const newReturn = {
      return_id: returnId,
      order_id: orderId,
      productId: productId,
      product_name: product.name || "Product",
      image_url: product.image || product.images?.[0] || "",
      mrp: product.price || 0,
      reason: reason,
      status: "PENDING_PICKUP",
      created_at: new Date().toISOString(),
      pickup_window: "Tomorrow, 10 AM – 2 PM",
      reference_num: "RET-" + Math.floor(100000 + Math.random() * 900000),
      grade: returniqGrade,
      recovery_value: recoveryValue,
      carbon_avoided: carbonAvoided,
      route: routeOption
    };

    setReturns((prev) => [newReturn, ...prev]);

    // Also persist to localStorage for MyReturnsPage
    const existing = JSON.parse(localStorage.getItem("returniq_returns") || "[]");
    existing.unshift(newReturn);
    localStorage.setItem("returniq_returns", JSON.stringify(existing));

    // Update status in orders
    setOrders((prev) =>
      prev.map((order) =>
        order.orderId === orderId && order.productId === productId
          ? { ...order, status: "Returned" }
          : order
      )
    );

    return returnId;
  }

  function openHealthCardModal(productId) {
    setHealthCardProductId(productId);
    setHealthCardModalOpen(true);
  }

  function closeHealthCardModal() {
    setHealthCardModalOpen(false);
    setHealthCardProductId(null);
  }

  return (
    <CartContext.Provider
      value={{
        cart,
        wishlist,
        orders,
        returns,
        healthCardProductId,
        healthCardModalOpen,
        addToCart,
        removeFromCart,
        updateQuantity,
        addToWishlist,
        removeFromWishlist,
        placeOrder,
        initiateReturn,
        openHealthCardModal,
        closeHealthCardModal,
        setReturns // to allow background agents to update status
      }}
    >
      {children}
    </CartContext.Provider>
  );
}
