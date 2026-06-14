import { useState, useEffect } from "react";
import { MOCK_DELIVERY_QUEUE, MOCK_QR_VALID, MOCK_QR_TAMPERED } from "../config/mockData";
import { endpoints, apiCall, delay } from "../config/api";
import { useAuth } from "../contexts/AuthContext";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export function useDelivery() {
  const [queue,   setQueue]   = useState([]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const { idToken } = useAuth();

  useEffect(() => {
    if (USE_MOCK) { setQueue(MOCK_DELIVERY_QUEUE); return; }
    apiCall(endpoints.deliveryQueue, {}, idToken)
      .then(setQueue)
      .catch(() => setQueue(MOCK_DELIVERY_QUEUE));
  }, []);

  async function verifyQR(qrToken) {
    setLoading(true);
    try {
      if (USE_MOCK) {
        await delay(1000);
        return qrToken === "demo-valid-token" ? MOCK_QR_VALID : MOCK_QR_TAMPERED;
      }
      return await apiCall(endpoints.verifyQR(qrToken), {}, idToken);
    } catch (e) {
      setError(e.message);
      return MOCK_QR_VALID;
    } finally {
      setLoading(false);
    }
  }

  async function confirmHandoff(returnId) {
    if (USE_MOCK) { await delay(500); return { success: true }; }
    return apiCall(`${endpoints.healthCard(returnId)}/confirm`, { method: "POST" }, idToken);
  }

  return { queue, verifyQR, confirmHandoff, loading, error };
}
