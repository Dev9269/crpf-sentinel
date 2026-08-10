import { Badge, type BadgeProps } from "@/components/ui/badge";

const SEVERITY_VARIANT: Record<string, BadgeProps["variant"]> = {
  critical: "critical",
  high: "high",
  medium: "medium",
  low: "low",
  informational: "info",
  info: "info",
};

export function SeverityBadge({ severity, className }: { severity?: string | null; className?: string }) {
  const value = severity?.toLowerCase() ?? "informational";
  return (
    <Badge variant={SEVERITY_VARIANT[value] ?? "default"} className={className}>
      {value}
    </Badge>
  );
}
