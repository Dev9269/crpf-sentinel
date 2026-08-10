"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Crosshair, Plus, RotateCcw, Trash2 } from "lucide-react";
import { iocService } from "@/services";
import type { IocEntry } from "@/types";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { StatusBadge } from "@/components/shared/status-badge";
import { PageError, PageLoading, PageEmpty } from "@/components/shared/page-states";
import { Pagination } from "@/components/shared/pagination";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { timeAgo } from "@/lib/utils";

const IOC_TYPES = ["ip", "domain", "hash", "url", "command"];

export default function IocLibraryPage() {
  const queryClient = useQueryClient();
  const [iocType, setIocType] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);

  const params = useMemo(
    () => ({
      ioc_type: iocType === "all" ? undefined : iocType,
      severity: severity === "all" ? undefined : severity,
      q: q || undefined,
      page,
      page_size: 25,
    }),
    [iocType, severity, q, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["ioc", params],
    queryFn: () => iocService.list(params),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => iocService.remove(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["ioc"] });
    },
  });

  return (
    <div>
      <PageHeader
        title="IOC Library"
        description="Threat indicators matched against inbound events during detection."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                void refetch();
                void queryClient.invalidateQueries({ queryKey: ["ioc"] });
              }}
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Refresh
            </Button>
            <AddIocDialog onCreated={() => void queryClient.invalidateQueries({ queryKey: ["ioc"] })} />
          </div>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface p-3">
        <Crosshair className="h-4 w-4 text-muted" />
        <Select value={iocType} onValueChange={(v) => { setIocType(v); setPage(1); }}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            {IOC_TYPES.map((t) => (
              <SelectItem key={t} value={t}>{t.toUpperCase()}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={severity} onValueChange={(v) => { setSeverity(v); setPage(1); }}>
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
        <Input
          placeholder="Search value, ID or description…"
          value={q}
          onChange={(e) => { setQ(e.target.value); setPage(1); }}
          className="w-64 text-xs"
        />
      </div>

      {isLoading && <PageLoading rows={15} />}
      {isError && <PageError message={(error as Error)?.message} onRetry={() => refetch()} />}
      {data && data.items.length === 0 && <PageEmpty title="No IOCs match this view" description="Add an indicator to start matching it against inbound events." />}

      {data && data.items.length > 0 && (
        <>
          <div className="rounded-md border border-border bg-surface">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Indicator</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Threat</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Matches</TableHead>
                  <TableHead>Last match</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((ioc) => (
                  <TableRow key={ioc.id}>
                    <TableCell>
                      <span className="block truncate font-mono text-xs text-foreground">{ioc.value}</span>
                      <span className="block font-mono text-[10px] text-muted">{ioc.ioc_id}</span>
                    </TableCell>
                    <TableCell>
                      <IocTypeBadge type={ioc.ioc_type} />
                    </TableCell>
                    <TableCell><SeverityBadge severity={ioc.severity} /></TableCell>
                    <TableCell className="text-xs">{ioc.threat_type ?? "—"}</TableCell>
                    <TableCell className="text-xs">{ioc.source}</TableCell>
                    <TableCell><StatusBadge status={ioc.status} /></TableCell>
                    <TableCell className="font-mono text-xs">{ioc.times_matched}</TableCell>
                    <TableCell className="text-xs text-muted">{ioc.last_matched_at ? timeAgo(ioc.last_matched_at) : "—"}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="iconSm"
                        aria-label="Delete IOC"
                        disabled={deleteMutation.isPending}
                        onClick={() => deleteMutation.mutate(ioc.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-muted hover:text-critical" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <Pagination page={page} totalPages={data.meta.total_pages} total={data.meta.total} onChange={setPage} />
        </>
      )}
    </div>
  );
}

function IocTypeBadge({ type }: { type: string }) {
  const styles: Record<string, string> = {
    ip: "border-accent/40 bg-accent/10 text-accent",
    domain: "border-medium/40 bg-medium/10 text-amber-300",
    hash: "border-info/40 bg-info/10 text-sky-300",
    url: "border-high/40 bg-high/10 text-orange-300",
    command: "border-critical/40 bg-critical/10 text-red-300",
  };
  return (
    <span className={`inline-block rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase ${styles[type] ?? "border-border bg-surface text-muted"}`}>
      {type}
    </span>
  );
}

function AddIocDialog({ onCreated }: { onCreated: () => void }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    ioc_type: "ip",
    value: "",
    severity: "medium",
    description: "",
    source: "manual",
    threat_type: "",
  });

  const mutation = useMutation({
    mutationFn: () => iocService.create(form as IocEntry),
    onSuccess: () => {
      setOpen(false);
      setForm({ ioc_type: "ip", value: "", severity: "medium", description: "", source: "manual", threat_type: "" });
      void queryClient.invalidateQueries({ queryKey: ["ioc"] });
      onCreated();
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="h-3.5 w-3.5" />
          Add IOC
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Add Indicator of Compromise</DialogTitle>
          <DialogDescription>Indicators are matched against inbound events during detection.</DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-xs">Type</Label>
              <Select value={form.ioc_type} onValueChange={(v) => setForm((f) => ({ ...f, ioc_type: v }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {IOC_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>{t.toUpperCase()}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">Severity</Label>
              <Select value={form.severity} onValueChange={(v) => setForm((f) => ({ ...f, severity: v }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["critical", "high", "medium", "low"].map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label className="text-xs">Value</Label>
            <Input className="mt-1 font-mono text-xs" placeholder="203.0.113.14 / evil.example.com / sha256…" value={form.value} onChange={(e) => setForm((f) => ({ ...f, value: e.target.value }))} />
          </div>
          <div>
            <Label className="text-xs">Threat type</Label>
            <Input className="mt-1 text-xs" placeholder="c2, scanner, brute_force…" value={form.threat_type} onChange={(e) => setForm((f) => ({ ...f, threat_type: e.target.value }))} />
          </div>
          <div>
            <Label className="text-xs">Description</Label>
            <Input className="mt-1 text-xs" placeholder="Optional context…" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>Cancel</Button>
          <Button size="sm" disabled={!form.value.trim() || mutation.isPending} onClick={() => mutation.mutate()}>
            {mutation.isPending ? "Adding…" : "Add IOC"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
