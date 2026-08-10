"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TimelinePoint } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-border bg-surface2 px-3 py-2 text-xs shadow-lg">
      <p className="mb-1 font-mono text-foreground">{label}</p>
      {payload.map((entry: any) => (
        <p key={entry.dataKey} className="flex items-center gap-2 text-muted">
          <span className="h-1.5 w-1.5 rounded-full" style={{ background: entry.color }} />
          {entry.name}: <span className="font-mono text-foreground">{entry.value}</span>
        </p>
      ))}
    </div>
  );
}

export function TimelineChart({ data }: { data: TimelinePoint[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Event & Alert Volume</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 8, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="eventsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22D3EE" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#22D3EE" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="alertsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#EF4444" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#EF4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1E293B" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="bucket" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip content={<ChartTooltip />} />
              <Area
                type="monotone"
                dataKey="events"
                name="Events"
                stroke="#22D3EE"
                strokeWidth={1.5}
                fill="url(#eventsGrad)"
              />
              <Area
                type="monotone"
                dataKey="alerts"
                name="Alerts"
                stroke="#EF4444"
                strokeWidth={1.5}
                fill="url(#alertsGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
