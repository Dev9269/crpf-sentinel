"use client";

import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, ShieldAlert, Trash2, PlayCircle, Pencil } from "lucide-react";
import { ruleService } from "@/services";
import type { Rule } from "@/types";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { RuleEditorDialog } from "@/components/rules/rule-editor";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn, timeAgo } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";

export default function RulesPage() {
  const { can } = useAuth();
  const queryClient = useQueryClient();
  const [category, setCategory] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");
  const [editing, setEditing] = useState<Rule | null>(null);
  const [creating, setCreating] = useState(false);
  const [testing, setTesting] = useState<Rule | null>(null);

  const params = useMemo(
    () => ({
      category: category === "all" ? undefined : category,
      severity: severity === "all" ? undefined : severity,
      status: status === "all" ? undefined : status,
    }),
    [category, severity, status],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["rules", params],
    queryFn: () => ruleService.list(params),
  });

  async function removeRule(rule: Rule) {
    if (!confirm(`Delete rule ${rule.rule_id}?`)) return;
    await ruleService.remove(rule.rule_id);
    void queryClient.invalidateQueries({ queryKey: ["rules"] });
  }

  return (
    <div>
      <PageHeader
        title="Detection Rules"
        description="Signature and correlation rules that drive alert generation."
        actions={
          can("rules.create") && (
            <Button size="sm" onClick={() => setCreating(true)}>
              <Plus className="h-3.5 w-3.5" />
              New Rule
            </Button>
          )
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface p-3">
        <ShieldAlert className="h-4 w-4 text-muted" />
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {["account_management", "authentication", "credential_usage", "privilege_assignment", "process_creation", "security_audit", "service_installation"].map((cat) => (
              <SelectItem key={cat} value={cat}>{cat.replace(/_/g, " ")}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={severity} onValueChange={setSeverity}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All severities</SelectItem>
            {["critical", "high", "medium", "low"].map((s) => (
              <SelectItem key={s} value={s}>{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="enabled">Enabled</SelectItem>
            <SelectItem value="disabled">Disabled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading && <PageLoading rows={10} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && data.length === 0 && <PageEmpty title="No rules found" />}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {data?.map((rule) => (
          <Card key={rule.id} className={cn("transition-colors", rule.status !== "enabled" && "opacity-60")}>
            <CardHeader className="flex flex-row items-start justify-between gap-2 pb-1">
              <div className="min-w-0">
                <p className="font-mono text-[10px] text-accent">{rule.rule_id}</p>
                <CardTitle className="mt-0.5 truncate">{rule.name}</CardTitle>
              </div>
              <div className="flex shrink-0 items-center gap-1">
                <SeverityBadge severity={rule.severity} className="text-[9px]" />
                <Badge variant={rule.status === "enabled" ? "success" : "default"} className="text-[9px]">
                  {rule.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="line-clamp-2 min-h-[32px] text-xs text-muted">{rule.description ?? "No description."}</p>
              <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[10px] text-muted">
                <Badge variant="outline" className="text-[9px]">{rule.category}</Badge>
                <Badge variant="outline" className="font-mono text-[9px]">
                  EID {rule.event_id.join(", ")}
                </Badge>
                {rule.correlation_type !== "none" && (
                  <Badge variant="accent" className="text-[9px]">
                    {rule.correlation_type}
                    {rule.threshold > 1 ? ` ×${rule.threshold}` : ""}
                  </Badge>
                )}
                {rule.mitre_technique && (
                  <Badge variant="outline" className="font-mono text-[9px]">{rule.mitre_technique}</Badge>
                )}
              </div>
              <div className="mt-3 flex items-center justify-between border-t border-border pt-2.5">
                <span className="text-[10px] text-muted">
                  {rule.times_matched} matches{rule.last_matched_at ? ` · ${timeAgo(rule.last_matched_at)}` : ""}
                </span>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="iconSm" title="Test rule" onClick={() => setTesting(rule)}>
                    <PlayCircle className="h-4 w-4" />
                  </Button>
                  {can("rules.create") && (
                    <>
                      <Button variant="ghost" size="iconSm" title="Edit rule" onClick={() => setEditing(rule)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="iconSm" title="Delete rule" className="text-critical hover:text-critical" onClick={() => void removeRule(rule)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {(creating || editing) && (
        <RuleEditorDialog
          rule={editing}
          open
          onOpenChange={(open) => {
            if (!open) {
              setCreating(false);
              setEditing(null);
            }
          }}
          onSaved={() => {
            setCreating(false);
            setEditing(null);
            void queryClient.invalidateQueries({ queryKey: ["rules"] });
          }}
        />
      )}

      {testing && <RuleTesterDialog rule={testing} onClose={() => setTesting(null)} />}
    </div>
  );
}

function RuleTesterDialog({ rule, onClose }: { rule: Rule; onClose: () => void }) {
  const [hostname, setHostname] = useState("");
  const [username, setUsername] = useState("");
  const [sourceIp, setSourceIp] = useState("");
  const [commandLine, setCommandLine] = useState("");
  const [count, setCount] = useState("1");
  const [result, setResult] = useState<{ matched: boolean; reason: string; will_create_alert: boolean } | null>(null);
  const [running, setRunning] = useState(false);

  async function run() {
    setRunning(true);
    setResult(null);
    try {
      const res = await ruleService.test(rule.rule_id, {
        hostname: hostname || undefined,
        username: username || undefined,
        source_ip: sourceIp || undefined,
        command_line: commandLine || undefined,
        count: Number(count) || 1,
      });
      setResult(res);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-md border border-border bg-surface p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-base font-semibold text-foreground">
          Test Rule <span className="font-mono text-accent">{rule.rule_id}</span>
        </h3>
        <p className="mt-1 text-xs text-muted">Simulate an event against this rule.</p>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Field label="Hostname"><input className={inputCls} value={hostname} onChange={(e) => setHostname(e.target.value)} placeholder="PC-01-0123" /></Field>
          <Field label="Username"><input className={inputCls} value={username} onChange={(e) => setUsername(e.target.value)} placeholder="admin" /></Field>
          <Field label="Source IP"><input className={inputCls} value={sourceIp} onChange={(e) => setSourceIp(e.target.value)} placeholder="10.0.0.5" /></Field>
          <Field label="Event count"><input className={inputCls} value={count} onChange={(e) => setCount(e.target.value)} inputMode="numeric" /></Field>
          <div className="sm:col-span-2">
            <Field label="Command line (optional)">
              <input className={inputCls} value={commandLine} onChange={(e) => setCommandLine(e.target.value)} placeholder="powershell.exe -enc …" />
            </Field>
          </div>
        </div>

        {result && (
          <div className={cn("mt-4 rounded-md border px-3 py-2.5 text-xs", result.matched ? "border-critical/30 bg-critical/10 text-critical" : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400")}>
            <p className="font-semibold">{result.matched ? "MATCHED" : "NO MATCH"} · {result.will_create_alert ? "alert would fire" : "no alert"}</p>
            <p className="mt-1 text-muted">{result.reason}</p>
          </div>
        )}

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>Close</Button>
          <Button onClick={() => void run()} disabled={running}>
            <PlayCircle className="h-4 w-4" />
            {running ? "Testing…" : "Run Test"}
          </Button>
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <label className="text-[11px] font-medium uppercase tracking-wider text-muted">{label}</label>
      {children}
    </div>
  );
}

const inputCls =
  "flex h-9 w-full rounded-md border border-border bg-surface2 px-3 py-2 text-sm text-foreground placeholder:text-slate-600 focus:border-accent/60 focus:outline-none focus:ring-1 focus:ring-accent/40";
