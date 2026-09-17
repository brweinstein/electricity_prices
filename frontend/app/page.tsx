import RecommendationBanner from "@/components/RecommendationBanner";
import PriceChart from "@/components/PriceChart";
import RegionSelector from "@/components/RegionSelector";
import ForecastPlanner from "@/components/ForecastPlanner";
import { getForecast, getRecommendation } from "@/lib/api";

export default async function Home() {
  const placeholderPrice = 18.4; // stand-in until a live price feed replaces this

  const start = new Date();
  start.setMinutes(0, 0, 0);
  start.setHours(start.getHours() + 1);

  const [recommendation, history] = await Promise.all([
    getRecommendation(placeholderPrice),
    getForecast(start.toISOString(), 168),
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
        <ForecastPlanner />
        <PriceChart data={history.estimates} />
      </div>
    </main>
  );
}