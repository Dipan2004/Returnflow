const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const endpoints = {
  createReturn:         `${BASE}/returns`,
  getReturn:            (id)    => `${BASE}/returns/${id}`,
  getReturnStatus:      (id)    => `${BASE}/returns/${id}/status`,
  completeImageUpload:  (id)    => `${BASE}/returns/${id}/images/complete`,
  processGrading:       `${BASE}/grades/process`,
  getGrade:             (id)    => `${BASE}/grades/${id}`,
  orchestrateDisposition: (id)  => `${BASE}/dispositions/calculate/${id}`,
  generateHealthCard:   (id)    => `${BASE}/health-cards/generate/${id}`,
  getHealthCard:        (id)    => `${BASE}/health-cards/${id}`,
  getHealthCardByQR:    (token) => `${BASE}/health-cards/by-qr/${token}`,
  verifyQR:             (token) => `${BASE}/verify/${token}`,
  verificationHistory:  (token) => `${BASE}/verify/${token}/history`,
  predictReturn:        `${BASE}/prevent-iq/predict-return`,
  sizeRecommendation:   `${BASE}/prevent-iq/size-recommendation`,
  assessFraud:          `${BASE}/fraud/assess`,
  matchBuyer:           `${BASE}/buyer-match/compute`,
  getBuyerMatch:        (id)    => `${BASE}/buyer-match/${id}`,
  acceptBuyerMatch:     (buyerId, returnId) => `${BASE}/buyers/${buyerId}/accept/${returnId}`,
  rejectBuyerMatch:     (buyerId, returnId) => `${BASE}/buyers/${buyerId}/reject/${returnId}`,
  flywheel:             `${BASE}/dashboard/flywheel`,
  dashboardMetrics:     `${BASE}/dashboard/metrics`,
  deliveryQueue:        `${BASE}/delivery/queue`,
  confirmHandoff:       (id)    => `${BASE}/health-cards/${id}/confirm-handoff`,
};

export async function apiCall(url, options = {}, idToken = null) {
  const headers = {
    "Content-Type": "application/json",
    "X-API-Key": import.meta.env.VITE_API_KEY || "returniq-dev-key-2026",
    ...options.headers,
  };
  if (idToken) headers["Authorization"] = `Bearer ${idToken}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
