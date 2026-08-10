"use client";

import { motion } from "framer-motion";
import {
  FileText,
  Braces,
  Database,
  ShieldCheck,
  Target,
  BellRing,
  Gauge,
  Siren,
  Check,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface PipelineStage {
  id: string;
  label: string;
  sub: string;
  icon: typeof FileText;
}

export const PIPELINE_STAGES: PipelineStage[] = [
  { id: "event", label: "EVENT", sub: "Windows Event Log", icon: FileText },
  { id: "parser", label: "PARSER", sub: "XML → structured", icon: Braces },
  { id: "normalization", label: "NORMALIZATION", sub: "IngestItem", icon: Database },
  { id: "signature", label: "SIGNATURE", sub: "Rule engine", icon: ShieldCheck },
  { id: "mitre", label: "MITRE", sub: "ATT&CK mapping", icon: Target },
  { id: "alert", label: "ALERT", sub: "Threat raised", icon: BellRing },
  { id: "risk", label: "RISK", sub: "Score 0–100", icon: Gauge },
  { id: "incident", label: "INCIDENT", sub: "Case created", icon: Siren },
];

const isComplete = (stageIndex: number, activeStage: number, done: boolean) =>
  done || stageIndex < activeStage;

const stageTone = (id: string) => {
  switch (id) {
    case "alert":
      return { border: "border-high/50", glow: "shadow-[0_0_20px_-4px_rgba(249,115,22,0.5)]" };
    case "mitre":
      return { border: "border-accent/40", glow: "" };
    default:
      return { border: "border-accent/30", glow: "" };
  }
};

export function DetectionPipeline({
  running,
  activeStage,
  done,
  error,
  onReset,
}: {
  running: boolean;
  activeStage: number;
  done: boolean;
  error: string | null;
  onReset: () => void;
}) {
  return (
    <div className="rounded-md border border-border bg-surface3 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-muted">
          Detection Pipeline
        </p>
        {done ? (
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-success">
            <Check className="h-3 w-3" />
            COMPLETE
          </span>
        ) : running ? (
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-accent">
            <Loader2 className="h-3 w-3 animate-spin" />
            PROCESSING
          </span>
        ) : error ? (
          <span className="font-mono text-[10px] text-critical">FAILED</span>
        ) : (
          <span className="font-mono text-[10px] text-muted">IDLE</span>
        )}
      </div>

      <div className="flex flex-col gap-2">
        {PIPELINE_STAGES.map((stage, i) => {
          const Icon = stage.icon;
          const active = running && activeStage === i;
          const complete = isComplete(i, activeStage, done);
          const tone = stageTone(stage.id);
          return (
            <motion.div
              key={stage.id}
              initial={false}
              animate={{
                opacity: done || i <= activeStage || (running && activeStage >= i) ? 1 : 0.55,
              }}
              className={cn(
                "flex items-center gap-3 rounded-md border border-border bg-surface px-3 py-2 transition-colors",
                active && cn("border-accent/50", tone.border, tone.glow),
                complete && !active && "border-success/20",
              )}
            >
              <div
                className={cn(
                  "flex h-7 w-7 shrink-0 items-center justify-center rounded border",
                  complete
                    ? "border-success/40 bg-success/10 text-success"
                    : active
                      ? "border-accent/50 bg-accent/10 text-accent"
                      : "border-border bg-surface2 text-slate-500",
                )}
              >
                {complete && !active && done ? (
                  <Check className="h-3.5 w-3.5" />
                ) : active ? (
                  <Icon className="h-3.5 w-3.5 animate-pulse-dot" />
                ) : (
                  <Icon className="h-3.5 w-3.5" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p
                  className={cn(
                    "font-mono text-[12px] font-semibold tracking-wide",
                    complete ? "text-foreground" : "text-muted",
                  )}
                >
                  {stage.label}
                </p>
                <p className="text-[10px] text-muted">{stage.sub}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="hidden text-[9px] uppercase tracking-wider text-muted sm:inline">
                  stage {i + 1}/{PIPELINE_STAGES.length}
                </span>
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    complete ? "bg-success" : active ? "bg-accent animate-pulse-dot" : "bg-slate-700",
                  )}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {error && (
        <p className="mt-3 font-mono text-[11px] text-critical">{error}</p>
      )}

      {(running || done) && (
        <div className="mt-3 flex justify-end">
          <button
            onClick={onReset}
            disabled={running}
            className="rounded border border-border px-2.5 py-1 text-[11px] text-muted transition-colors hover:bg-surface hover:text-foreground disabled:opacity-50"
          >
            Reset pipeline
          </button>
        </div>
      )}
    </div>
  );
}
