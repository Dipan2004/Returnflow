import { useState } from "react";
import { MOCK_HEALTH_CARD } from "../config/mockData";
import { endpoints, apiCall, delay } from "../config/api";
import { useAuth } from "../contexts/AuthContext";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export function useReturnFlow() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { idToken } = useAuth();

  async function getHealthCard(returnId) {
    setLoading(true);
    setError(null);
    try {
      if (USE_MOCK || returnId === "demo" || returnId === "a1b2c3d4-demo") {
        await delay(500);
        return MOCK_HEALTH_CARD;
      }
      return await apiCall(endpoints.healthCard(returnId), {}, idToken);
    } catch (e) {
      setError(e.message);
      return MOCK_HEALTH_CARD; // fallback
    } finally {
      setLoading(false);
    }
  }

  return { getHealthCard, loading, error };
}
