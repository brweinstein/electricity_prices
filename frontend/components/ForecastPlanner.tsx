"use client";

import { FormEvent, useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Forecast, formatOntarioTimestamp, getForecast } from "@/lib/api";

const ACTION_LABEL: Record<string, string> = {
  "good time to use electricity": "Good window to use power",
  "wait if you can": "Consider waiting",
  "about average right now": "About average",
};

const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function nextHour() {
  const date = new Date();
  date.setMinutes(0, 0, 0);
  date.setHours(date.getHours() + 1);
  return date;
}

export default function ForecastPlanner() {
  const [dateParts, setDateParts] = useState({ month: "", day: "", year: "", hour: "" });
  const [windowValue, setWindowValue] = useState(4);
  const [windowUnit, setWindowUnit] = useState<"hours" | "days">("hours");
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const date = nextHour();
    setDateParts({
      month: String(date.getMonth() + 1),
      day: String(date.getDate()),
      year: String(date.getFullYear()),
      hour: String(date.getHours()),
    });
  }, []);

  const targetTime = dateParts.month && dateParts.day && dateParts.year && dateParts.hour
    ? new Date(Number(dateParts.year), Number(dateParts.month) - 1, Number(dateParts.day), Number(dateParts.hour)).toISOString()
    : "";
  const windowHours = windowValue * (windowUnit === "days" ? 24 : 1);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!targetTime) return;
    setLoading(true);
    setError("");
    try {
      setForecast(await getForecast(targetTime, windowHours));
    } catch {
      setError("Could not generate an estimate. Check that the API is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="border border-hairline bg-surface p-6 sm:p-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted">Plan ahead</p>
          <h2 className="mt-2 text-xl font-medium">What will the next few hours look like?</h2>
        </div>
        <span className="border border-hairline px-2 py-1 text-xs text-muted">residual GBM forecast</span>
      </div>

      <form className="mt-6 grid gap-4 sm:grid-cols-[1fr_auto_auto] sm:items-end" onSubmit={handleSubmit}>
        <fieldset className="min-w-0">
          <legend className="text-sm text-muted">Start date and time</legend>
          <div className="mt-2 grid grid-cols-4 gap-2">
            <select aria-label="Month" className="theme-control min-w-0 border border-hairline bg-transparent px-2 py-2 text-sm text-ink outline-none focus:border-cheap" value={dateParts.month} onChange={(event) => setDateParts({ ...dateParts, month: event.target.value })} required>
              <option value="">Month</option>
              {MONTH_NAMES.map((month, index) => <option key={index + 1} value={index + 1}>{month}</option>)}
            </select>
            <select aria-label="Day" className="theme-control min-w-0 border border-hairline bg-transparent px-2 py-2 text-sm text-ink outline-none focus:border-cheap" value={dateParts.day} onChange={(event) => setDateParts({ ...dateParts, day: event.target.value })} required>
              <option value="">Day</option>
              {Array.from({ length: 31 }, (_, index) => <option key={index + 1} value={index + 1}>{index + 1}</option>)}
            </select>
            <select aria-label="Year" className="theme-control min-w-0 border border-hairline bg-transparent px-2 py-2 text-sm text-ink outline-none focus:border-cheap" value={dateParts.year} onChange={(event) => setDateParts({ ...dateParts, year: event.target.value })} required>
              <option value="">Year</option>
              {[new Date().getFullYear(), new Date().getFullYear() + 1].map((year) => <option key={year} value={year}>{year}</option>)}
            </select>
            <select aria-label="Hour" className="theme-control min-w-0 border border-hairline bg-transparent px-2 py-2 text-sm text-ink outline-none focus:border-cheap" value={dateParts.hour} onChange={(event) => setDateParts({ ...dateParts, hour: event.target.value })} required>
              <option value="">Hour</option>
              {Array.from({ length: 24 }, (_, hour) => <option key={hour} value={hour}>{String(hour).padStart(2, "0")}:00</option>)}
            </select>
          </div>
        </fieldset>
        <fieldset className="text-sm text-muted">
          <legend>Look ahead</legend>
          <div className="mt-2 flex gap-2">
            <input
              aria-label="Forecast length"
              className="forecast-length-input theme-control w-20 border border-hairline bg-transparent px-3 py-2 text-sm text-ink outline-none focus:border-cheap"
              type="number"
              min={1}
              max={windowUnit === "days" ? 14 : 336}
              value={windowValue}
              onChange={(event) => setWindowValue(Number(event.target.value))}
              required
            />
            <select
              aria-label="Forecast length unit"
              className="theme-control border border-hairline bg-transparent px-3 py-2 text-sm text-ink outline-none focus:border-cheap"
              value={windowUnit}
              onChange={(event) => setWindowUnit(event.target.value as "hours" | "days")}
            >
              <option value="hours">hours</option>
              <option value="days">days</option>
            </select>
          </div>
        </fieldset>
        <button className="bg-ink px-4 py-2 text-sm text-surface transition-colors hover:bg-cheap" type="submit" disabled={loading}>
          {loading ? "Estimating..." : "Generate estimate"}
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-expensive">{error}</p>}

      {loading && (
        <div className="mt-8 flex items-center gap-4 border-t border-hairline pt-6" role="status" aria-live="polite">
          <span className="estimate-spinner" aria-hidden="true" />
          <div>
            <p className="text-sm font-medium text-ink">Building your estimate</p>
            <p className="mt-1 text-xs text-muted">Checking recent patterns and future price signals...</p>
          </div>
        </div>
      )}

      {forecast && !loading && (
        <div className="mt-8 border-t border-hairline pt-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm text-muted">Estimated average</p>
              <p className="mt-1 font-mono text-5xl tabular-nums text-cheap">${forecast.average_price.toFixed(1)}<span className="ml-2 text-base text-muted">/MWh</span></p>
              <p className="mt-2 text-xs text-muted">{forecast.model}</p>
            </div>
            <p className="text-right text-sm font-medium text-cheap">{ACTION_LABEL[forecast.action] ?? forecast.action}</p>
          </div>
          <div className="mt-5 grid grid-cols-2 gap-4 border-t border-hairline pt-4 text-sm sm:grid-cols-3">
            <span className="text-muted">Low <strong className="ml-1 font-mono font-normal text-ink">${forecast.lowest_price.toFixed(1)}</strong></span>
            <span className="text-muted">High <strong className="ml-1 font-mono font-normal text-ink">${forecast.highest_price.toFixed(1)}</strong></span>
            <span className="text-muted">vs typical <strong className="ml-1 font-mono font-normal text-ink">{forecast.deviation_pct > 0 ? "+" : ""}{forecast.deviation_pct.toFixed(1)}%</strong></span>
          </div>
          <div className="mt-5 h-40 border border-hairline px-2 py-3">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecast.estimates}>
                <XAxis dataKey="timestamp" tickFormatter={(value) => formatOntarioTimestamp(value, { hour: "numeric" })} stroke="#8A948F" fontSize={10} tickLine={false} axisLine={false} minTickGap={24} />
                <YAxis stroke="#8A948F" fontSize={10} tickLine={false} axisLine={false} width={44} tickFormatter={(value) => `$${value}`} />
                <Tooltip contentStyle={{ background: "#171D1A", border: "1px solid #2A322E", fontSize: 11 }} labelFormatter={(value) => formatOntarioTimestamp(value, { weekday: "short", hour: "numeric" })} formatter={(value) => [`$${Number(value).toFixed(1)}/MWh`, "Estimated"]} />
                <Line type="monotone" dataKey="price" stroke="#4FD1AE" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-5 border-t border-hairline pt-5">
            <p className="text-sm text-muted">Best hours in this window</p>
            <div className="mt-3 grid gap-2 sm:grid-cols-3">
              {forecast.best_hours.map((hour) => (
                <div className="border border-hairline px-3 py-2" key={hour.timestamp}>
                  <p className="text-sm text-ink">{formatOntarioTimestamp(hour.timestamp, { weekday: "short", hour: "numeric" })}</p>
                  <p className="mt-1 font-mono text-sm text-cheap">${hour.price.toFixed(1)}/MWh</p>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}
    </section>
  );
}