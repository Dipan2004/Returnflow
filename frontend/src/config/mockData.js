export const MOCK_PREDICT_RETURN = {
  return_probability: 0.34,
  category_avg_return_rate: 0.09,
  above_category_avg: true,
  size_warning:
    "Customers with your measurements return size 7 in this brand 34% of the time. Size 8 has a 94% keep rate.",
  recommended_size: "8",
};

export const MOCK_GRADE_RESULT = {
  return_id: "a1b2c3d4-demo",
  grade: "A",
  confidence: 91.2,
  damage_description:
    "Minor surface scratch visible on the toe box area. No structural damage detected.",
  damage_labels: [{ name: "Scratch", confidence: 82.1 }],
  route: "P2P",
  recovery_value: 552.5,
  liquidation_baseline: 42.5,
  value_delta: 510.0,
  route_reason: "Buyer 2.3km away has this SKU on wishlist",
  mrp: 850,
  fraud_flag: false,
  status: "PENDING_BUYER_ACCEPT",
};

export const MOCK_HEALTH_CARD = {
  ...MOCK_GRADE_RESULT,
  product_name: "Nike Air Max 270",
  sku_id: "B08N5WRWNW",
  image_urls: [
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=400&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&fit=crop&auto=format"
  ],
  created_at: new Date().toISOString(),
  status: "P2P_MATCHED",
  qr_scanned: false,
};

export const MOCK_QR_VALID = {
  valid: true,
  return_id: "a1b2c3d4-demo",
  product_name: "Nike Air Max 270",
  grade: "A",
  pickup_address: "14 MG Road, Sector 7, New Delhi",
  delivery_address: "Amazon Locker #4, DLF Mall",
};

export const MOCK_QR_TAMPERED = {
  valid: false,
  reason: "QR_ALREADY_SCANNED",
  scanned_at: "2026-06-13T14:23:11Z",
  alert: "POSSIBLE_TAMPERING",
};

export const MOCK_DELIVERY_QUEUE = [
  {
    return_id: "d001",
    product: "Nike Air Max 270",
    grade: "A",
    pickup: "14 MG Road, Sector 7",
    dropoff: "Amazon Locker #4",
    qr_token: "demo-valid-token",
    buyer_distance_km: 2.3,
  },
  {
    return_id: "d002",
    product: "boAt Rockerz 450",
    grade: "B",
    pickup: "7 Park Street, Connaught Place",
    dropoff: "Amazon Locker #12",
    qr_token: "demo-token-2",
    buyer_distance_km: 1.1,
  },
];

export const MOCK_FLYWHEEL = {
  returns_processed: 1240,
  value_recovered: 480000,
  waste_diverted_kg: 3200,
  co2_avoided_kg: 2944,
  p2p_match_accuracy_current: 0.84,
  route_distribution: [
    { name: "P2P", value: 40 },
    { name: "Resell", value: 35 },
    { name: "Refurbish", value: 15 },
    { name: "Donate", value: 10 },
  ],
  accuracy_over_30_days: Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    accuracy: parseFloat(
      (0.71 + (0.13 * i) / 29 + (Math.random() * 0.02 - 0.01)).toFixed(3)
    ),
  })),
};

export const MOCK_HUMAN_REVIEW = [
  { return_id: "r001", product: 'Samsung 65" TV',    ai_grade: "B", confidence: 72.4, damage_labels: ["Scratch", "Dent"] },
  { return_id: "r002", product: "Levi's Jeans",      ai_grade: "C", confidence: 68.1, damage_labels: ["Tear", "Stain"] },
  { return_id: "r003", product: "boAt Headphones",   ai_grade: "B", confidence: 79.9, damage_labels: ["Crack"] },
];

export const MOCK_SELLER_RETURNS = [
  { return_id: "s001", product: "Nike Air Max 270", grade: "A", route: "P2P",      recovery: 552, status: "Delivered" },
  { return_id: "s002", product: "Campus Shoes",     grade: "B", route: "REFURBISH",recovery: 280, status: "Graded" },
  { return_id: "s003", product: "Puma T-Shirt",     grade: "C", route: "DONATE",   recovery: 0,   status: "Pending Review" },
  { return_id: "s004", product: "Adidas Cap",       grade: "A", route: "RESELL",   recovery: 320, status: "P2P Matched" },
  { return_id: "s005", product: "boAt Earphones",   grade: "B", route: "REFURBISH",recovery: 190, status: "Delivered" },
];

// Mock users for localStorage auth fallback
export const MOCK_USERS = {
  archi_customer: { password: "Demo1234!", role: "customer",       name: "Archi", email: "customer@demo.returniq.in" },
  archi_delivery: { password: "Demo1234!", role: "delivery_agent", name: "Ravi",  email: "delivery@demo.returniq.in" },
  archi_seller:   { password: "Demo1234!", role: "seller",         name: "Priya", email: "seller@demo.returniq.in" },
  archi_admin:    { password: "Demo1234!", role: "admin",          name: "Admin", email: "admin@demo.returniq.in" },
};
