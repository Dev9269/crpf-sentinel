"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileBarChart, FileJson, FileSpreadsheet, Loader2, Download } from "lucide-react";
import { reportService, unitService } from "@/services";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

const REPORT_TYPES = [
  { key: "daily", title: "Daily Activity Report", description: "Hourly event volume and suspicious activity for the last 24 hours." },
  { key: "weekly", title: "Weekly Security Report", description: "Aggregated event and alert statistics over the last 7 days." },
  { key: "unit", title: "Unit Report", description: "Per-unit deployment, agent count, event volume and status." },
  { key: "alerts", title: "Alerts Report", description: "All generated alerts with severity, status, and risk scores." },
  { key: "rules", title: "Rules Report", description: "Detection rules with match counts and MITRE mappings." },
];

export default function ReportsPage() {
  const { data: units } = useQuery({ queryKey: ["units", "all"], queryFn: () => unitService.list() });
  const [unitId, setUnitId] = useState("all");
  const [downloading, setDownloading] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function download(reportType: string, format: "csv" | "json") {
    setDownloading(`${reportType}:${format}`);
    setNotice(null);
    try {
      const res = await reportService.download(reportType, format, unitId === "all" ? undefined : unitId);
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        setNotice(body?.error?.message ?? `Download failed (${res.status})`);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${reportType}_report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      const rows = res.headers.get("x-report-rows");
      setNotice(`Downloaded ${reportType} report${rows ? ` · ${Number(rows).toLocaleString()} rows` : ""}.`);
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Download failed");
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Reports"
        description="Generate and download operational security reports (CSV / JSON)."
      />

      <div className="mb-4 flex max-w-md items-end gap-3 rounded-md border border-border bg-surface p-3">
        <div className="flex-1 space-y-1">
          <Label>Unit scope</Label>
          <Select value={unitId} onValueChange={setUnitId}>
            <SelectTrigger>
              <SelectValue placeholder="Unit" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All units</SelectItem>
              {units?.map((u) => (
                <SelectItem key={u.id} value={u.id}>{u.unit_code} · {u.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {notice && (
        <div className="mb-4 rounded-md border border-accent/30 bg-accent/5 px-3 py-2 text-xs text-accent">{notice}</div>
      )}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {REPORT_TYPES.map((report) => (
          <Card key={report.key}>
            <CardHeader className="pb-1">
              <CardTitle className="flex items-center gap-2">
                <FileBarChart className="h-4 w-4 text-accent" />
                {report.title}
              </CardTitle>
              <CardDescription>{report.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={downloading === `${report.key}:csv`}
                  onClick={() => void download(report.key, "csv")}
                >
                  {downloading === `${report.key}:csv` ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileSpreadsheet className="h-3.5 w-3.5" />}
                  CSV
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={downloading === `${report.key}:json`}
                  onClick={() => void download(report.key, "json")}
                >
                  {downloading === `${report.key}:json` ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileJson className="h-3.5 w-3.5" />}
                  JSON
                </Button>
                <Download className="ml-auto h-4 w-4 text-slate-600" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
