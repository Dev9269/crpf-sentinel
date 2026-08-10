import { Badge, type BadgeProps } from "@/components/ui/badge";

export type StatusKind =
  | "online"
  | "offline"
  | "warning"
  | "disabled"
  | "enabled"
  | "operational"
  | "open"
  | "investigating"
  | "escalated"
  | "resolved"
  | "closed"
  | "triaging"
  | "false_positive"
  | "connected"
  | "ok"
  | "degraded"
  | "new";

const STATUS_VARIANT: Record<StatusKind, BadgeProps["variant"]> = {
  online: "success",
  operational: "success",
  enabled: "success",
  resolved: "success",
  ok: "success",
  connected: "success",
  offline: "default",
  disabled: "default",
  open: "critical",
  new: "accent",
  triaging: "critical",
  investigating: "medium",
  escalated: "high",
  closed: "default",
  false_positive: "info",
  warning: "high",
  degraded: "high",
};

export function StatusBadge({ status, className }: { status?: string | null; className?: string }) {
  const value = (status ?? "").toLowerCase() as StatusKind;
  const variant = STATUS_VARIANT[value] ?? "default";
  return (
    <Badge variant={variant} className={className}>
      {status ?? "unknown"}
    </Badge>
  );
}
