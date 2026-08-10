"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Target, RotateCcw } from "lucide-react";
import { mitreService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { cn } from "@/lib/utils";

const SEV_TILE: Record<string, string> = {
  critical: "border-critical/40 bg-critical/10 hover:bg-critical/20",
  high: "border-high/40 bg-high/10 hover:bg-high/20",
  medium: "border-medium/40 bg-medium/10 hover:bg-medium/20",
  low: "border-info/40 bg-info/10 hover:bg-info/20",
};

export default function MitrePage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["mitre", "techniques"],
    queryFn: () => mitreService.techniques(),
  });

  return (
    <div>
      <PageHeader
        title="MITRE ATT&CK"
        description="Technique coverage mapped from enabled detection rules and observed alert activity."
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RotateCcw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        }
      />

      {isLoading && <PageLoading rows={10} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && data.items.length === 0 && <PageEmpty title="No MITRE techniques mapped" description="Enable rules that carry a MITRE technique to populate this view." />}

      {data && data.items.length > 0 && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {data.items.map((tech) => {
            const sev = tech.max_severity ?? "low";
            return (
              <Link key={tech.technique} href="/rules">
                <Card className={cn("transition-colors", SEV_TILE[sev] ?? SEV_TILE.low)}>
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 font-mono">
                        <Target className="h-4 w-4" />
                        {tech.technique}
                      </span>
                      <span className="text-[10px] uppercase tracking-widest text-muted">{sev}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm font-medium text-foreground">{tech.name ?? "Unmapped technique"}</p>
                    {tech.sub && <p className="mt-0.5 text-xs text-muted">{tech.sub}</p>}
                    <div className="mt-3 flex flex-wrap gap-4 text-xs text-muted">
                      <span><span className="font-mono text-foreground">{tech.rules}</span> rules</span>
                      <span><span className="font-mono text-foreground">{tech.alerts}</span> alerts</span>
                      <span><span className="font-mono text-critical">{tech.open_alerts}</span> open</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
