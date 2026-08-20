import RecommendationBanner from "@/components/RecommendationBanner";
import PriceChart from "@/components/PriceChart";
import RegionSelector from "@/components/RegionSelector";
import { getRecommendation, getPriceHistory } from "@/lib/api";

export default async function Home() {
  const placeholderPrice = 18.4; // stand-in until a live price feed replaces this

  // const end = new Date();
  // const start = new Date(end);
  const end = new Date("2024-12-31");
  const start = new Date("2024-12-24"); 
  start.setDate(start.getDate() - 7);

  const [recommendation, history] = await Promise.all([
    getRecommendation(placeholderPrice),
    getPriceHistory(start.toISOString().slice(0, 10), end.toISOString().slice(0, 10)),
  ]);

  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:py-16">
      <header className="mb-8">
        <h1 className="text-sm uppercase tracking-widest text-muted">When should I use electricity?</h1>
        <p className="mt-1 text-sm text-muted">Built on real hourly Ontario market prices from the IESO.</p>
      </header>
      <div className="space-y-4">
        <RegionSelector />
        <RecommendationBanner data={recommendation} />
        <PriceChart data={history} />
      </div>
    </main>
  );
}