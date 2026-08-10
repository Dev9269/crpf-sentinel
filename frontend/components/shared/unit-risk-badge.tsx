import { cn } from "@/lib/utils";

export function UnitRiskBadge({ risk, className }: { risk: number; className?: string }) {
  return (
    <span
      className={cn(
        "rounded px-1.5 py-0.5 font-mono text-xs font-semibold",
        risk >= 60 ? "bg-critical/15 text-critical" : risk >= 35 ? "bg-medium/15 text-medium" : "bg-success/15 text-success",
        className,
      )}
    >
      {risk}
    </span>
  );
}
