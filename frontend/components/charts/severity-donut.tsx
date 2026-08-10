"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { SeverityBucket } from "@/types";
import { severityColor } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function DonutTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="rounded-md border border-border bg-surface2 px-3 py-2 text-xs shadow-lg">
      <p className="font-medium text-foreground">{item.name}</p>
      <p className="text-muted">
        {item.value} events · {item.payload?.pct ?? 0}%
      </p>
    </div>
  );
}

export function SeverityDonut({ data }: { data: SeverityBucket[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Severity Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-44">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="severity"
                innerRadius={52}
                outerRadius={72}
                paddingAngle={2}
                stroke="none"
              >
                {data.map((entry) => (
                  <Cell key={entry.severity} fill={severityColor(entry.severity).hex} />
                ))}
              </Pie>
              <Tooltip content={<DonutTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-xl font-semibold text-foreground">
              {data.reduce((sum, d) => sum + d.count, 0).toLocaleString()}
            </span>
            <span className="text-[10px] uppercase tracking-wider text-muted">total alerts</span>
          </div>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1.5">
          {data.map((entry) => (
            <div key={entry.severity} className="flex items-center justify-between gap-2 text-xs">
              <span className="flex items-center gap-1.5 capitalize text-slate-400">
                <span className={`h-2 w-2 rounded-full ${severityColor(entry.severity).dot}`} />
                {entry.severity}
              </span>
              <span className="font-mono text-muted">
                {entry.count.toLocaleString()} ({entry.pct}%)
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
