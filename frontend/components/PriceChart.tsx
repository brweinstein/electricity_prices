"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { PricePoint } from "@/lib/api";

export default function PriceChart({ data }: { data: PricePoint[] }) {
  const formatted = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleDateString("en-CA", { month: "short", day: "numeric" }),
    fullTime: new Date(d.timestamp).toLocaleString("en-CA", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
    }),
    price: d.price_toronto,
  }));

  return (
    <div className="border border-hairline bg-surface p-6">
      <p className="text-xs uppercase tracking-widest text-muted">Latest available observations · Darlington nodal price · $/MWh</p>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formatted}>
            <CartesianGrid stroke="#2A322E" strokeDasharray="2 4" vertical={false} />
            <XAxis dataKey="time" stroke="#8A948F" fontSize={11} tickLine={false} axisLine={{ stroke: "#2A322E" }} interval={Math.floor(formatted.length / 6)} />
            <YAxis stroke="#8A948F" fontSize={11} tickLine={false} axisLine={false} width={48} tickFormatter={(v) => `$${v}`} />
            <Tooltip
              contentStyle={{ background: "#171D1A", border: "1px solid #2A322E", fontSize: 12 }}
              labelStyle={{ color: "#8A948F" }}
              labelFormatter={(_, payload) => payload[0]?.payload.fullTime ?? _}
            />
            <Line type="monotone" dataKey="price" stroke="#F2A93B" strokeWidth={1.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}