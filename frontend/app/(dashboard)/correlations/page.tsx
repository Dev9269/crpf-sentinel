"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Network } from "lucide-react";
import { ruleService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { Mono } from "@/components/shared/mono";

export default function CorrelationsPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["correlations"],
    queryFn: () => ruleService.list({}),
  });

  const correlations = data?.filter((r) => r.correlation_type !== "none") ?? [];

  return (
    <div>
      <PageHeader
        title="Correlation Rules"
        description="Multi-event correlation logic: count-based aggregation and sequence detection."
      />

      {isLoading && <PageLoading rows={6} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && correlations.length === 0 && <PageEmpty title="No correlation rules configured" />}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {correlations.map((rule) => (
          <Card key={rule.id}>
            <CardHeader className="pb-1">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="flex items-center gap-2 font-mono">
                  <Network className="h-4 w-4 text-accent" />
                  {rule.rule_id}
                </CardTitle>
                <SeverityBadge severity={rule.severity} className="text-[9px]" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm font-medium text-foreground">{rule.name}</p>
              <p className="mt-1 line-clamp-2 text-xs text-muted">{rule.description}</p>

              <div className="mt-3 space-y-1.5 rounded-md border border-border/60 bg-surface2/40 p-3">
                <Row label="Correlation type" value={rule.correlation_type} mono />
                <Row label="Threshold" value={`≥ ${rule.threshold} events`} mono />
                <Row label="Window" value={`${rule.time_window_seconds}s`} mono />
                <Row label="Correlation key" value={rule.correlation_key ?? "global"} mono />
                <Row label="Event IDs" value={rule.event_id.join(", ")} mono />
              </div>

              <div className="mt-3 flex items-center justify-between">
                <Badge variant="outline" className="text-[9px]">{rule.times_matched} matches</Badge>
                <Link href="/rules" className="text-[11px] text-accent hover:underline">View rules →</Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="mt-4 text-[11px] text-muted">
        Correlation windows are evaluated against the database by <Mono>app/detection/correlation.py</Mono>.
      </p>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-2 text-xs">
      <span className="text-muted">{label}</span>
      <span className={`font-mono text-foreground ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}
