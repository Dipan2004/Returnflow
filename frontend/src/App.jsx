import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

import LoginPage          from "./components/auth/LoginPage";
import ProtectedRoute     from "./components/auth/ProtectedRoute";
import HomePage           from "./pages/customer/HomePage";
import ProductPage        from "./pages/customer/ProductPage";
import HealthCardPage     from "./components/returniq/HealthCardPage";
import MyReturnsPage      from "./pages/customer/MyReturnsPage";
import DeliveryAgentView  from "./pages/delivery/DeliveryAgentView";
import PickupGradingFlow  from "./pages/delivery/PickupGradingFlow";
import QRScanPage         from "./pages/delivery/QRScanPage";
import SellerStub         from "./pages/seller/SellerStub";
import AdminStub          from "./pages/admin/AdminStub";

// New customer pages
import CartPage           from "./pages/customer/CartPage";
import CheckoutPage       from "./pages/customer/CheckoutPage";
import OrdersPage         from "./pages/customer/OrdersPage";
import WishlistPage       from "./pages/customer/WishlistPage";
import CategoryPage       from "./pages/customer/CategoryPage";
import ReturnFlowPage     from "./pages/customer/ReturnFlowPage";
import HealthCardModal    from "./components/returniq/HealthCardModal";

export default function App() {
  const { user, role } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={
            user
              ? <Navigate to={role === "delivery_agent" ? "/delivery" : role === "seller" ? "/seller" : role === "admin" ? "/admin" : "/"} replace />
              : <LoginPage />
          }
        />

        {/* Customer */}
        <Route path="/" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <HomePage />
          </ProtectedRoute>
        } />
        <Route path="/product/:sku_id" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <ProductPage />
          </ProtectedRoute>
        } />
        <Route path="/cart" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <CartPage />
          </ProtectedRoute>
        } />
        <Route path="/checkout" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <CheckoutPage />
          </ProtectedRoute>
        } />
        <Route path="/orders" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <OrdersPage />
          </ProtectedRoute>
        } />
        <Route path="/wishlist" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <WishlistPage />
          </ProtectedRoute>
        } />
        <Route path="/category/:slug" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <CategoryPage />
          </ProtectedRoute>
        } />
        <Route path="/return/:orderId" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <ReturnFlowPage />
          </ProtectedRoute>
        } />
        <Route path="/my-returns" element={
          <ProtectedRoute allowedRoles={["customer"]}>
            <MyReturnsPage />
          </ProtectedRoute>
        } />
        <Route path="/health-card/:return_id" element={
          <ProtectedRoute allowedRoles={["customer", "delivery_agent"]}>
            <HealthCardPage />
          </ProtectedRoute>
        } />

        {/* Delivery */}
        <Route path="/delivery" element={
          <ProtectedRoute allowedRoles={["delivery_agent"]}>
            <DeliveryAgentView />
          </ProtectedRoute>
        } />
        <Route path="/delivery/pickup/:return_id" element={
          <ProtectedRoute allowedRoles={["delivery_agent"]}>
            <PickupGradingFlow />
          </ProtectedRoute>
        } />
        <Route path="/delivery/scan/:qr_token" element={
          <ProtectedRoute allowedRoles={["delivery_agent"]}>
            <QRScanPage />
          </ProtectedRoute>
        } />

        {/* Seller */}
        <Route path="/seller" element={
          <ProtectedRoute allowedRoles={["seller"]}>
            <SellerStub />
          </ProtectedRoute>
        } />

        {/* Admin */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={["admin"]}>
            <AdminStub />
          </ProtectedRoute>
        } />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <HealthCardModal />
    </BrowserRouter>
  );
}
