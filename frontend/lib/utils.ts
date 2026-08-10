import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, format } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(value: number | undefined | null): string {
  if (value === undefined || value === null) return "0";
  return new Intl.NumberFormat("en-IN").format(value);
}

export function formatCompact(value: number | undefined | null): string {
  if (value === undefined || value === null) return "0";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

export function formatTime(value: string | Date | null | undefined): string {
  if (!value) return "—";
  const date = typeof value === "string" ? new Date(value) : value;
  return format(date, "HH:mm:ss");
}

export function formatDateTime(value: string | Date | null | undefined): string {
  if (!value) return "—";
  const date = typeof value === "string" ? new Date(value) : value;
  return format(date, "yyyy-MM-dd HH:mm:ss");
}

export function timeAgo(value: string | Date | null | undefined): string {
  if (!value) return "—";
  const date = typeof value === "string" ? new Date(value) : value;
  try {
    return `${formatDistanceToNow(date, { addSuffix: true })}`;
  } catch {
    return "—";
  }
}

export type Severity = "critical" | "high" | "medium" | "low" | "informational";

export const SEVERITY_COLORS: Record<Severity, { text: string; bg: string; border: string; dot: string; hex: string }> = {
  critical: { text: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", dot: "bg-red-500", hex: "#EF4444" },
  high: { text: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30", dot: "bg-orange-500", hex: "#F97316" },
  medium: { text: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30", dot: "bg-amber-500", hex: "#F59E0B" },
  low: { text: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30", dot: "bg-blue-500", hex: "#3B82F6" },
  informational: { text: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/30", dot: "bg-slate-500", hex: "#64748B" },
};

export function severityColor(severity: string): (typeof SEVERITY_COLORS)["critical"] {
  return SEVERITY_COLORS[(severity?.toLowerCase() as Severity) in SEVERITY_COLORS ? (severity.toLowerCase() as Severity) : "informational"];
}

export function statusColor(status: string): string {
  switch (status?.toLowerCase()) {
    case "online":
    case "operational":
    case "open":
    case "resolved":
    case "enabled":
      return "text-emerald-400";
    case "warning":
    case "investigating":
      return "text-yellow-400";
    case "offline":
    case "disabled":
      return "text-slate-500";
    case "false_positive":
    case "false positive":
      return "text-blue-400";
    default:
      return "text-slate-400";
  }
}

export function downloadText(filename: string, content: string, type = "text/plain") {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function eventIdLabel(eventId: number): string {
  const known: Record<number, string> = {
    4624: "Logon Success",
    4625: "Logon Failure",
    4648: "Explicit Credential Use",
    4672: "Special Privileges Assigned",
    4688: "Process Created",
    4720: "User Account Created",
    4728: "Member Added (Global Group)",
    4732: "Member Added (Local Group)",
    1102: "Audit Log Cleared",
    7045: "Service Installed",
  };
  return known[eventId] ?? "Windows Event";
}
