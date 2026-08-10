"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Radar } from "lucide-react";
import { ruleService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { Mono } from "@/components/shared/mono";

type Signature = {
  rule_id: string;
  name: string;
  severity: string;
  event_id: number[];
  mitre_name: string | null;
  times_matched: number;
};

export default function ThreatIntelPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["signatures"],
    queryFn: () => ruleService.signatures(),
  });

  const groups = data ? Object.entries(data as Record<string, Signature[]>).sort((a, b) => a[0].localeCompare(b[0])) : [];

  return (
    <div>
      <PageHeader
        title="Threat Intelligence"
        description="Signature library mapped to the MITRE ATT&CK framework."
      />

      {isLoading && <PageLoading rows={8} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && groups.length === 0 && <PageEmpty title="No enabled signatures" />}

      <div className="space-y-4">
        {groups.map(([technique, signatures]) => (
          <Card key={technique}>
            <CardHeader className="pb-1">
              <CardTitle className="flex items-center gap-2 font-mono">
                <Radar className="h-4 w-4 text-accent" />
                {technique}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-border/60">
                {signatures.map((sig) => (
                  <div key={sig.rule_id} className="flex flex-wrap items-center gap-3 px-4 py-2.5">
                    <Link href="/rules" className="min-w-0 flex-1 hover:text-accent">
                      <span className="block truncate text-xs font-medium text-foreground">{sig.name}</span>
                      <span className="block text-[10px] text-muted">
                        {sig.rule_id} · {sig.mitre_name ?? "Unmapped technique"}
                      </span>
                    </Link>
                    <div className="flex items-center gap-1.5">
                      {sig.event_id.map((eid) => (
                        <Badge key={eid} variant="outline" className="font-mono text-[9px]">{eid}</Badge>
                      ))}
                    </div>
                    <SeverityBadge severity={sig.severity} className="text-[9px]" />
                    <Badge variant="accent" className="text-[9px]">{sig.times_matched} matches</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
        {data && groups.length > 0 && (
          <p className="text-[11px] text-muted">
            Mapping source: <Mono>app/detection/mitre.py</Mono> · techniques are advisory classifications, not confirmations.
          </p>
        )}
      </div>
    </div>
  );
}
