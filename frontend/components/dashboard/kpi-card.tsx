import type { KpiValue, TimelinePoint } from "@/types";
import { formatNumber, cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Database, ShieldAlert, BellRing, Radio, Building2, Gauge, Siren, type LucideIcon } from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  Database,
  ShieldAlert,
  BellRing,
  Radio,
  Building2,
  Gauge,
  Siren,
};

function Sparkline({ points, className }: { points: number[]; className?: string }) {
  if (points.length === 0) return <div className="h-6" />;
  const max = Math.max(...points, 1);
  const min = Math.min(...points, 0);
  const range = max - min || 1;
  const step = 100 / Math.max(points.length - 1, 1);
  const coords = points
    .map((p, i) => `${(i * step).toFixed(1)},${(34 - ((p - min) / range) * 26).toFixed(1)}`)
    .join(" ");
  return (
    <svg viewBox="0 0 100 36" preserveAspectRatio="none" className={cn("h-6 w-full", className)} aria-hidden>
      <polyline
        points={coords}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

export function KpiCard({
  kpi,
  icon,
  spark,
  valueClassName,
  prefix,
}: {
  kpi: KpiValue;
  icon?: string;
  spark?: number[];
  valueClassName?: string;
  prefix?: string;
}) {
  const Icon = (icon && ICONS[icon]) || Database;
  const isNumber = typeof kpi.value === "number";
  const value = isNumber ? formatNumber(kpi.value as number) : String(kpi.value);
  const up = (kpi.change_pct ?? 0) >= 0;
  const negativeIsGood = kpi.label.toLowerCase().includes("critical") || kpi.label.toLowerCase().includes("alert");

  return (
    <Card className="overflow-hidden border-border bg-surface">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">{kpi.label}</p>
          <Icon className="h-4 w-4 shrink-0 text-slate-500" />
        </div>
        <div className="mt-1.5 flex items-baseline gap-2">
          <span className={cn("font-mono text-[22px] font-semibold leading-none tracking-tight", valueClassName)}>
            {prefix ?? ""}
            {value}
          </span>
          {kpi.change_pct !== null && kpi.change_pct !== undefined && (
            <span
              className={cn(
                "rounded border px-1 py-px font-mono text-[10px]",
                up
                  ? negativeIsGood
                    ? "border-critical/30 bg-critical/10 text-critical"
                    : "border-success/30 bg-success/10 text-success"
                  : negativeIsGood
                    ? "border-success/30 bg-success/10 text-success"
                    : "border-critical/30 bg-critical/10 text-critical",
              )}
            >
              {up ? "▲" : "▼"} {Math.abs(kpi.change_pct ?? 0).toFixed(1)}%
            </span>
          )}
        </div>
        <div className="mt-2 text-[11px] text-muted">
          <span className="truncate">{kpi.detail ?? kpi.compare_label}</span>
        </div>
        <div className="mt-2 text-accent/60">
          <Sparkline points={spark ?? []} />
        </div>
      </CardContent>
    </Card>
  );
}
