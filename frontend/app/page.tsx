import PriceChart from "@/components/PriceChart";
import RegionSelector from "@/components/RegionSelector";
import ForecastPlanner from "@/components/ForecastPlanner";
import { getPriceHistory } from "@/lib/api";

export default async function Home() {
  const allHistory = await getPriceHistory();
  const history = allHistory.slice(-168);

  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:py-16">
      <header className="mb-8">
        <h1 className="text-sm uppercase tracking-widest text-muted">When should I use electricity?</h1>
        <p className="mt-1 text-sm text-muted">Built on real hourly Ontario market prices from the IESO.</p>
      </header>
      <div className="space-y-4">
        <RegionSelector />
        <PriceChart data={history} />
        <ForecastPlanner />
      </div>
    </main>
  );
}