"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart as BarChartIcon, PieChart, Globe, User, MonitorSmartphone } from "lucide-react";
import { analyticsService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/shared/page-states";
import { Mono } from "@/components/shared/mono";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { Badge } from "@/components/ui/badge";
import { Cell, Pie, PieChart as RePieChart, ResponsiveContainer, Tooltip } from "recharts";

const SEV_COLORS: Record<string, string> = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#FACC15",
  low: "#38BDF8",
};

const TECH_COLORS = ["#22D3EE", "#F97316", "#A78BFA", "#FACC15", "#34D399", "#FB7185"];

export default function ThreatAnalyticsPage() {
  const topQuery = useQuery({
    queryKey: ["analytics", "top"],
    queryFn: () => analyticsService.top(),
  });
  const activityQuery = useQuery({
    queryKey: ["analytics", "activity"],
    queryFn: () => analyticsService.threatActivity(),
  });

  const loading = topQuery.isLoading || activityQuery.isLoading;
  const error = topQuery.isError || activityQuery.isError;

  return (
    <div>
      <PageHeader
        title="Threat Analytics"
        description="Top indicators, hosts and detection activity across the monitored estate."
      />

      {loading && <PageLoading rows={10} />}
      {error && (
        <PageError
          message={(topQuery.error as Error)?.message ?? (activityQuery.error as Error)?.message}
          onRetry={() => {
            void topQuery.refetch();
            void activityQuery.refetch();
          }}
        />
      )}

      {topQuery.data && activityQuery.data && (
        <div className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-3">
            <TopList
              icon={Globe}
              title="Top Source IPs"
              items={topQuery.data.top_source_ips}
              color="text-cyan-400"
            />
            <TopList
              icon={User}
              title="Top Usernames"
              items={topQuery.data.top_usernames}
              color="text-violet-400"
            />
            <TopList
              icon={MonitorSmartphone}
              title="Top Hosts"
              items={topQuery.data.top_hosts}
              color="text-emerald-400"
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <BarChartIcon className="h-4 w-4 text-accent" />
                  Alerts by Rule
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-2.5">
                  {activityQuery.data.alerts_by_rule.map((rule) => (
                    <div key={rule.rule_id} className="flex items-center gap-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="truncate text-xs font-medium text-foreground">{rule.rule_name}</span>
                          <span className="font-mono text-xs text-muted">{rule.count}</span>
                        </div>
                        <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface2">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${Math.min(100, (rule.count / Math.max(1, activityQuery.data.alerts_by_rule[0].count)) * 100)}%`,
                              background: SEV_COLORS[rule.severity] ?? "#22D3EE",
                            }}
                          />
                        </div>
                      </div>
                      <SeverityBadge severity={rule.severity} />
                    </div>
                  ))}
                  {activityQuery.data.alerts_by_rule.length === 0 && (
                    <p className="py-6 text-center text-xs text-muted">No alert activity yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <PieChart className="h-4 w-4 text-accent" />
                  Alerts by MITRE Technique
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {activityQuery.data.alerts_by_technique.length === 0 ? (
                  <p className="py-6 text-center text-xs text-muted">No technique-mapped alerts yet.</p>
                ) : (
                  <div className="flex items-center gap-4">
                    <div className="h-52 w-52 shrink-0">
                      <ResponsiveContainer width="100%" height="100%">
                        <RePieChart>
                          <Pie
                            data={activityQuery.data.alerts_by_technique}
                            dataKey="count"
                            nameKey="technique"
                            innerRadius={50}
                            outerRadius={80}
                            paddingAngle={2}
                          >
                            {activityQuery.data.alerts_by_technique.map((t, i) => (
                              <Cell key={t.technique} fill={TECH_COLORS[i % TECH_COLORS.length]} stroke="transparent" />
                            ))}
                          </Pie>
                          <Tooltip content={<PieTooltip />} />
                        </RePieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="min-w-0 flex-1 space-y-1.5">
                      {activityQuery.data.alerts_by_technique.map((t, i) => (
                        <div key={t.technique} className="flex items-center justify-between gap-2 text-xs">
                          <span className="flex min-w-0 items-center gap-1.5">
                            <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: TECH_COLORS[i % TECH_COLORS.length] }} />
                            <Mono>{t.technique}</Mono>
                            <span className="truncate text-muted">{t.name}</span>
                          </span>
                          <span className="font-mono">{t.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

function TopList({
  icon: Icon,
  title,
  items,
  color,
}: {
  icon: React.ElementType;
  title: string;
  items: { value: string; count: number }[];
  color: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Icon className={`h-4 w-4 ${color}`} />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {items.length === 0 ? (
          <p className="py-6 text-center text-xs text-muted">No data yet.</p>
        ) : (
          <div className="space-y-2.5">
            {items.map((item, i) => (
              <div key={item.value} className="flex items-center gap-3">
                <Badge variant="outline" className="w-5 justify-center font-mono text-[10px]">{i + 1}</Badge>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-xs text-foreground">{item.value}</p>
                  <div className="mt-1 h-1 overflow-hidden rounded-full bg-surface2">
                    <div
                      className="h-full rounded-full bg-accent"
                      style={{ width: `${Math.min(100, (item.count / Math.max(1, items[0].count)) * 100)}%` }}
                    />
                  </div>
                </div>
                <span className="font-mono text-xs text-muted">{item.count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function PieTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="rounded-md border border-border bg-surface2 px-3 py-2 text-xs shadow-lg">
      <p className="font-mono text-foreground">{item.payload.technique}</p>
      <p className="text-muted">{item.payload.name}</p>
      <p className="font-mono text-foreground">{item.value} alerts</p>
    </div>
  );
}
