"use client";

import { motion } from "framer-motion";
import { Play, ShieldCheck, Crosshair } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Mono } from "@/components/shared/mono";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type ScenarioSeverity = "critical" | "high" | "medium";

export interface ScenarioMeta {
  id: string;
  name: string;
  short: string;
  explanation: string;
  eventIds: number[];
  eventLabel: string;
  mitre: string;
  severity: ScenarioSeverity;
  detail: string;
}

const SEVERITY_TONE: Record<ScenarioSeverity, { badge: "critical" | "high" | "medium"; bar: string; pulse: string }> = {
  critical: { badge: "critical", bar: "bg-critical", pulse: "bg-critical" },
  high: { badge: "high", bar: "bg-high", pulse: "bg-high" },
  medium: { badge: "medium", bar: "bg-medium", pulse: "bg-medium" },
};

export function ScenarioCard({
  scenario,
  running,
  onSimulate,
  disabled,
}: {
  scenario: ScenarioMeta;
  running: boolean;
  onSimulate: () => void;
  disabled: boolean;
}) {
  const tone = SEVERITY_TONE[scenario.severity];
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="group relative flex flex-col overflow-hidden rounded-md border border-border bg-surface transition-colors hover:border-slate-600"
    >
      <div className={cn("h-0.5 w-full", tone.bar)} />
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <Badge variant={tone.badge} className="text-[9px]">
              {scenario.severity}
            </Badge>
            <h3 className="mt-2 text-[14px] font-semibold leading-tight text-foreground">{scenario.name}</h3>
          </div>
          <span className={cn("mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full opacity-70", tone.pulse, running && "animate-pulse-dot")} />
        </div>

        <p className="mt-2 flex-1 text-[11px] leading-relaxed text-muted">{scenario.explanation}</p>

        <div className="mt-3 grid grid-cols-2 gap-2">
          <div className="rounded border border-border bg-surface3 px-2 py-1.5">
            <p className="text-[9px] uppercase tracking-wider text-muted">Event ID</p>
            <p className="mt-0.5 font-mono text-[12px] text-foreground">{scenario.eventLabel}</p>
          </div>
          <div className="rounded border border-border bg-surface3 px-2 py-1.5">
            <p className="text-[9px] uppercase tracking-wider text-muted">MITRE</p>
            <p className="mt-0.5 flex items-center gap-1.5 font-mono text-[12px] text-accent">
              <Crosshair className="h-3 w-3" />
              {scenario.mitre}
            </p>
          </div>
        </div>

        <p className="mt-2 flex items-center gap-1.5 text-[10px] text-muted">
          <ShieldCheck className="h-3 w-3" />
          <Mono>{scenario.detail}</Mono>
        </p>

        <Button
          size="sm"
          className="mt-4 w-full"
          variant={scenario.severity === "critical" ? "destructive" : "default"}
          onClick={onSimulate}
          disabled={running || disabled}
        >
          {running ? (
            <>
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
              Simulating…
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5" />
              Simulate
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
}
