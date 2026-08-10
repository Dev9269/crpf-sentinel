import { AlertTriangle, Inbox, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function PageLoading({ rows = 6, label }: { rows?: number; label?: string }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <RefreshCw className="h-4 w-4 animate-spin text-accent" />
        <span className="text-xs text-muted">{label ?? "Loading data…"}</span>
      </div>
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    </div>
  );
}

export function PageEmpty({ title, description }: { title: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-border py-16 text-center">
      <Inbox className="h-8 w-8 text-muted" />
      <p className="text-sm font-medium text-foreground">{title}</p>
      {description && <p className="max-w-sm text-xs text-muted">{description}</p>}
    </div>
  );
}

export function PageError({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-md border border-critical/30 bg-critical/5 py-16 text-center">
      <AlertTriangle className="h-8 w-8 text-critical" />
      <p className="text-sm font-medium text-foreground">Failed to load data</p>
      <p className="max-w-md text-xs text-muted">{message ?? "An unexpected error occurred."}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="h-3.5 w-3.5" />
          Retry
        </Button>
      )}
    </div>
  );
}
