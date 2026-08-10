"use client";

import { useMemo } from "react";
import { useLiveStream } from "@/hooks/use-live-stream";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { Mono } from "@/components/shared/mono";
import { formatTime, eventIdLabel, severityColor } from "@/lib/utils";

export default function LiveEventsPage() {
  const { events, connection } = useLiveStream();

  const stats = useMemo(() => {
    const sevCounts: Record<string, number> = {};
    const hosts = new Set<string>();
    const users = new Set<string>();
    const rules = new Set<string>();
    for (const e of events) {
      sevCounts[e.severity] = (sevCounts[e.severity] ?? 0) + 1;
      if (e.hostname) hosts.add(e.hostname);
      if (e.username) users.add(e.username);
      if (e.matched_rule_id) rules.add(e.matched_rule_id);
    }
    return { sevCounts, hosts: hosts.size, users: users.size, rules: rules.size };
  }, [events]);

  const sevOrder = ["critical", "high", "medium", "low", "informational"];

  return (
    <div>
      <PageHeader
        title="Live Events"
        description="Real-time stream of normalized events as they are ingested."
        actions={
          <Badge variant={connection === "live" ? "success" : "medium"} className="text-[10px]">
            {connection === "live" ? "LIVE" : connection.toUpperCase()}
          </Badge>
        }
      />

      <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-5">
        {sevOrder.map((sev) => (
          <Card key={sev}>
            <CardContent className="flex items-center justify-between p-4">
              <span className="text-xs text-muted capitalize">{sev}</span>
              <span className="font-mono text-lg font-semibold text-foreground">{stats.sevCounts[sev] ?? 0}</span>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              Event Stream
              <span className="relative flex h-1.5 w-1.5">
                {connection === "live" && (
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                )}
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {events.length === 0 ? (
              <div className="flex h-72 items-center justify-center">
                <p className="text-xs text-muted">Waiting for incoming events…</p>
              </div>
            ) : (
              <ScrollArea className="h-72">
                <div className="divide-y divide-border/60">
                  {events.map((event) => {
                    const sc = severityColor(event.severity);
                    const eventId = typeof event.event_id === "number" ? event.event_id : Number(event.event_id ?? 0);
                    return (
                      <div key={event.id ?? event.timestamp + event.hostname} className="flex items-center gap-3 py-2">
                        <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${sc.dot}`} />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="truncate font-mono text-[13px] text-foreground">
                              {eventId} · {eventIdLabel(eventId)}
                            </span>
                            {event.matched_rule_id && (
                              <Badge variant="accent" className="shrink-0 text-[9px]">
                                {event.matched_rule_id}
                              </Badge>
                            )}
                          </div>
                          <div className="truncate text-[11px] text-muted">
                            {event.hostname ?? "—"} · {event.unit_name ?? "—"}
                            {event.username ? ` · ${event.username}` : ""}
                          </div>
                        </div>
                        <span className="shrink-0 font-mono text-[11px] text-muted">{formatTime(event.timestamp)}</span>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Session Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs text-muted">
              <div className="flex justify-between"><span>Events in buffer</span><Mono>{events.length}</Mono></div>
              <div className="flex justify-between"><span>Unique hosts</span><Mono>{stats.hosts}</Mono></div>
              <div className="flex justify-between"><span>Unique users</span><Mono>{stats.users}</Mono></div>
              <div className="flex justify-between"><span>Rules matched</span><Mono>{stats.rules}</Mono></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Connection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs text-muted">
              <div className="flex items-center justify-between">
                <span>Feed</span>
                <span className="font-mono text-foreground">centralized.winlog</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Status</span>
                <SeverityBadge severity={connection === "live" ? "informational" : "medium"} />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
