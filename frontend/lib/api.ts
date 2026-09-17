function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_BASE) return process.env.NEXT_PUBLIC_API_BASE;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}/api`;
  return "http://localhost:8000";
}

const API_BASE = getApiBase();

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

export interface ForecastPoint {
  timestamp: string;
  price: number;
}

export interface Forecast {
  start_time: string;
  end_time: string;
  window_hours: number;
  estimates: ForecastPoint[];
  average_price: number;
  lowest_price: number;
  highest_price: number;
  action: string;
  deviation_pct: number;
  typical_price: number;
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

export async function getForecast(targetTime: string, windowHours: number): Promise<Forecast> {
  const params = new URLSearchParams({ target_time: targetTime, window_hours: String(windowHours) });
  const res = await fetch(`${API_BASE}/forecast?${params.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Forecast request failed: ${res.status}`);
  return res.json();
}