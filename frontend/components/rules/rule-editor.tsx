"use client";

import { useState } from "react";
import type { Rule } from "@/types";
import { ruleService } from "@/services";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ApiError } from "@/lib/api";

const SEVERITIES = ["critical", "high", "medium", "low", "informational"];
const CORRELATION_TYPES = ["none", "count", "sequence"];

interface FormState {
  rule_id: string;
  name: string;
  description: string;
  category: string;
  severity: string;
  event_ids: string;
  conditions: string;
  correlation_type: string;
  threshold: string;
  time_window_seconds: string;
  correlation_key: string;
  mitre_technique: string;
  mitre_name: string;
  status: string;
}

const EMPTY: FormState = {
  rule_id: "",
  name: "",
  description: "",
  category: "authentication",
  severity: "high",
  event_ids: "4624,4625",
  conditions: "{}",
  correlation_type: "count",
  threshold: "10",
  time_window_seconds: "300",
  correlation_key: "source_ip",
  mitre_technique: "",
  mitre_name: "",
  status: "enabled",
};

function fromRule(rule: Rule): FormState {
  return {
    rule_id: rule.rule_id,
    name: rule.name,
    description: rule.description ?? "",
    category: rule.category,
    severity: rule.severity,
    event_ids: rule.event_id.join(","),
    conditions: JSON.stringify(rule.conditions ?? {}, null, 2),
    correlation_type: rule.correlation_type,
    threshold: String(rule.threshold),
    time_window_seconds: String(rule.time_window_seconds),
    correlation_key: rule.correlation_key ?? "",
    mitre_technique: rule.mitre_technique ?? "",
    mitre_name: rule.mitre_name ?? "",
    status: rule.status,
  };
}

export function RuleEditorDialog({
  rule,
  open,
  onOpenChange,
  onSaved,
}: {
  rule: Rule | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<FormState>(rule ? fromRule(rule) : EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => setForm((f) => ({ ...f, [key]: value }));

  async function save() {
    setError(null);
    setSaving(true);
    try {
      const body = {
        rule_id: form.rule_id.trim(),
        name: form.name.trim(),
        description: form.description.trim() || null,
        category: form.category.trim(),
        severity: form.severity,
        event_id: form.event_ids
          .split(",")
          .map((s) => Number(s.trim()))
          .filter((n) => Number.isFinite(n) && n > 0),
        conditions: (() => {
          try {
            const parsed = JSON.parse(form.conditions || "{}");
            return typeof parsed === "object" && parsed !== null && !Array.isArray(parsed) ? parsed : {};
          } catch {
            throw new ApiError("INVALID_JSON", "Conditions must be valid JSON object", 400);
          }
        })(),
        correlation_type: form.correlation_type,
        threshold: Number(form.threshold) || 1,
        time_window_seconds: Number(form.time_window_seconds) || 300,
        correlation_key: form.correlation_key.trim() || null,
        mitre_technique: form.mitre_technique.trim() || null,
        mitre_name: form.mitre_name.trim() || null,
        status: form.status,
      };
      if (rule) {
        await ruleService.update(rule.rule_id, body);
      } else {
        await ruleService.create(body as Partial<Rule>);
      }
      onSaved();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save rule");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto max-w-xl">
        <DialogHeader>
          <DialogTitle>{rule ? `Edit Rule · ${rule.rule_id}` : "Create Detection Rule"}</DialogTitle>
          <DialogDescription>
            Define the signature and correlation logic. Conditions use the matcher DSL (eq, contains, regex, exists).
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-xs text-critical">{error}</div>
        )}

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="space-y-1">
            <Label htmlFor="rule_id">Rule ID</Label>
            <Input id="rule_id" value={form.rule_id} onChange={(e) => set("rule_id", e.target.value)} placeholder="SEN-RULE-001" disabled={!!rule} className="font-mono" />
          </div>
          <div className="space-y-1">
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Suspicious Logon Pattern" />
          </div>
          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" value={form.description} onChange={(e) => set("description", e.target.value)} rows={2} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="category">Category</Label>
            <Input id="category" value={form.category} onChange={(e) => set("category", e.target.value)} placeholder="authentication" />
          </div>
          <div className="space-y-1">
            <Label>Severity</Label>
            <Select value={form.severity} onValueChange={(v) => set("severity", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {SEVERITIES.map((s) => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label htmlFor="event_ids">Event IDs (comma separated)</Label>
            <Input id="event_ids" value={form.event_ids} onChange={(e) => set("event_ids", e.target.value)} placeholder="4624,4625" className="font-mono" />
          </div>
          <div className="space-y-1">
            <Label>Correlation Type</Label>
            <Select value={form.correlation_type} onValueChange={(v) => set("correlation_type", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {CORRELATION_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {form.correlation_type !== "none" && (
            <>
              <div className="space-y-1">
                <Label htmlFor="threshold">Threshold</Label>
                <Input id="threshold" value={form.threshold} onChange={(e) => set("threshold", e.target.value)} inputMode="numeric" className="font-mono" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="time_window">Window (seconds)</Label>
                <Input id="time_window" value={form.time_window_seconds} onChange={(e) => set("time_window_seconds", e.target.value)} inputMode="numeric" className="font-mono" />
              </div>
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="correlation_key">Correlation Key</Label>
                <Input id="correlation_key" value={form.correlation_key} onChange={(e) => set("correlation_key", e.target.value)} placeholder="source_ip" className="font-mono" />
              </div>
            </>
          )}
          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="conditions">Conditions (JSON)</Label>
            <Textarea id="conditions" value={form.conditions} onChange={(e) => set("conditions", e.target.value)} rows={5} className="font-mono text-[11px]" />
          </div>
          <div className="space-y-1">
            <Label htmlFor="mitre_technique">MITRE Technique</Label>
            <Input id="mitre_technique" value={form.mitre_technique} onChange={(e) => set("mitre_technique", e.target.value)} placeholder="T1078" className="font-mono" />
          </div>
          <div className="space-y-1">
            <Label htmlFor="mitre_name">MITRE Name</Label>
            <Input id="mitre_name" value={form.mitre_name} onChange={(e) => set("mitre_name", e.target.value)} placeholder="Valid Accounts" />
          </div>
          <div className="space-y-1">
            <Label>Status</Label>
            <Select value={form.status} onValueChange={(v) => set("status", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="enabled">Enabled</SelectItem>
                <SelectItem value="disabled">Disabled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={() => void save()} disabled={saving}>
            {saving ? "Saving…" : rule ? "Save Changes" : "Create Rule"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
