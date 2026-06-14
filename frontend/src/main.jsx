import React from "react";
import ReactDOM from "react-dom/client";
import { Amplify } from "aws-amplify";
import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";
import { CartProvider } from "./contexts/CartContext";
import "./index.css";

const poolId   = import.meta.env.VITE_COGNITO_POOL_ID   || "";
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID || "";

// Only configure Amplify if real values are present
if (poolId && !poolId.includes("XXXXXXXXX")) {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId:       poolId,
        userPoolClientId: clientId,
      },
    },
  });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <CartProvider>
        <App />
      </CartProvider>
    </AuthProvider>
  </React.StrictMode>
);

