"use client";

import { Recommendation } from "@/lib/api";

const ACTION_LABEL: Record<string, string> = {
  "good time to use electricity": "Good time to use power",
  "wait if you can": "Wait if you can",
  "about average right now": "About average",
};

export default function RecommendationBanner({ data }: { data: Recommendation }) {
  const isCheap = data.deviation_pct <= -15;
  const isExpensive = data.deviation_pct >= 15;
  const accent = isCheap ? "text-cheap" : isExpensive ? "text-expensive" : "text-ink";
  const dot = isCheap ? "bg-cheap" : isExpensive ? "bg-expensive" : "bg-muted";

  return (
    <div className="border border-hairline bg-surface px-6 py-8 sm:px-10 sm:py-10">
      <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-muted">
        <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
        Toronto zone · live
      </div>

      <div className="mt-4 flex flex-wrap items-end gap-x-4 gap-y-1">
        <span className={`font-mono text-6xl tabular-nums sm:text-7xl ${accent}`}>
          {data.current_price.toFixed(1)}
        </span>
        <span className="pb-2 text-sm text-muted">¢/kWh</span>
      </div>

      <p className={`mt-2 text-lg font-medium ${accent}`}>
        {ACTION_LABEL[data.action] ?? data.action}
      </p>

      <div className="mt-6 flex flex-wrap gap-x-8 gap-y-2 border-t border-hairline pt-4 text-sm text-muted">
        <span>
          Typical for this hour: <span className="font-mono text-ink">{data.typical_price.toFixed(1)}¢</span>
        </span>
        <span>
          Deviation:{" "}
          <span className={`font-mono ${accent}`}>
            {data.deviation_pct > 0 ? "+" : ""}
            {data.deviation_pct.toFixed(1)}%
          </span>
        </span>
        <span>{data.is_weekend ? "Weekend" : "Weekday"} · Hour {data.hour}:00</span>
      </div>
    </div>
  );
}