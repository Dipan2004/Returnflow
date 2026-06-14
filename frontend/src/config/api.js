const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";

export const endpoints = {
  uploadUrls:    `${BASE}/upload-urls`,
  healthCard:    (id)    => `${BASE}/health-card/${id}`,
  predictReturn: `${BASE}/predict-return`,
  verifyQR:      (token) => `${BASE}/verify/${token}`,
  flywheel:      `${BASE}/dashboard/flywheel`,
  deliveryQueue: `${BASE}/delivery/queue`,
};

export async function apiCall(url, options = {}, idToken = null) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (idToken) headers["Authorization"] = `Bearer ${idToken}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
