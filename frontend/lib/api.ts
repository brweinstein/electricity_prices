const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export interface Recommendation {
  action: string;
  deviation_pct: number;
  current_price: number;
  typical_price: number;
  is_weekend: boolean;
  hour: number;
}

export interface PricePoint {
  timestamp: string;
  price_toronto: number;
}

export async function getRecommendation(currentPrice: number): Promise<Recommendation> {
  const res = await fetch(`${API_BASE}/recommendation?current_price=${currentPrice}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Recommendation request failed: ${res.status}`);
  return res.json();
}

export async function getPriceHistory(start?: string, end?: string): Promise<PricePoint[]> {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  const res = await fetch(`${API_BASE}/prices/history?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Price history request failed: ${res.status}`);
  return res.json();
}