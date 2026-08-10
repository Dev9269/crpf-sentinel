"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { MonitorSmartphone, RotateCcw } from "lucide-react";
import { assetService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/status-badge";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { Mono } from "@/components/shared/mono";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { timeAgo, severityColor } from "@/lib/utils";

export default function AssetsPage() {
  const [status, setStatus] = useState("all");

  const params = useMemo(() => ({ status: status === "all" ? undefined : status }), [status]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["assets", params],
    queryFn: () => assetService.list(params),
  });

  const stats = useMemo(() => {
    if (!data?.items) return { total: 0, online: 0, highRisk: 0, critical: 0 };
    return {
      total: data.items.length,
      online: data.items.filter((a) => a.status === "online").length,
      highRisk: data.items.filter((a) => a.risk_score >= 50).length,
      critical: data.items.filter((a) => a.max_alert_severity === "critical").length,
    };
  }, [data]);

  return (
    <div>
      <PageHeader
        title="Asset Inventory"
        description="Monitored endpoints aggregated from agent health and observed event activity."
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RotateCcw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        }
      />

      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
        <SummaryCard label="Total assets" value={stats.total} />
        <SummaryCard label="Online" value={stats.online} accent="text-emerald-400" />
        <SummaryCard label="High risk" value={stats.highRisk} accent="text-orange-400" />
        <SummaryCard label="Critical severity" value={stats.critical} accent="text-critical" />
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface p-3">
        <MonitorSmartphone className="h-4 w-4 text-muted" />
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {["online", "warning", "offline", "disabled"].map((s) => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading && <PageLoading rows={15} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && data.items.length === 0 && <PageEmpty title="No assets found" />}

      {data && data.items.length > 0 && (
        <div className="rounded-md border border-border bg-surface">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Host</TableHead>
                <TableHead>Unit</TableHead>
                <TableHead>IP</TableHead>
                <TableHead>OS</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Events</TableHead>
                <TableHead>Open alerts</TableHead>
                <TableHead>Max severity</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Last seen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((asset) => (
                <TableRow key={asset.hostname}>
                  <TableCell className="font-mono text-xs font-medium text-foreground">{asset.hostname}</TableCell>
                  <TableCell className="text-xs">{asset.unit_name ?? "—"}</TableCell>
                  <TableCell className="font-mono text-xs">{asset.ip_address ?? "—"}</TableCell>
                  <TableCell className="max-w-40 truncate text-xs text-muted" title={asset.os_version ?? ""}>
                    {asset.os_version?.split(" (")[0] ?? "—"}
                  </TableCell>
                  <TableCell><StatusBadge status={asset.status} /></TableCell>
                  <TableCell className="font-mono text-xs">{asset.total_events.toLocaleString()}</TableCell>
                  <TableCell className="font-mono text-xs">{asset.open_alerts}</TableCell>
                  <TableCell>{asset.max_alert_severity ? <SeverityBadge severity={asset.max_alert_severity} /> : <span className="text-xs text-muted">—</span>}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress
                        value={asset.risk_score}
                        className="h-1.5 w-14"
                        colorClass={severityColor(asset.max_alert_severity ?? "low").bg}
                      />
                      <Mono>{asset.risk_score}</Mono>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-muted">{timeAgo(asset.last_seen_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <Card>
      <div className="p-4">
        <p className="text-[10px] uppercase tracking-widest text-muted">{label}</p>
        <p className={`mt-1 font-mono text-2xl font-semibold ${accent ?? "text-foreground"}`}>{value.toLocaleString()}</p>
      </div>
    </Card>
  );
}
