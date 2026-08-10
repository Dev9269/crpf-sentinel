"use client";

import { useQuery } from "@tanstack/react-query";
import { alertService, dashboardService, unitService } from "@/services";

export function useAlertCount() {
  return useQuery({
    queryKey: ["alerts", "count"],
    queryFn: async () => {
      const res = await alertService.list({ status: "open", page: 1, page_size: 1 });
      return res.meta.total;
    },
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useOpenAlertsSummary() {
  return useQuery({
    queryKey: ["alerts", "open-summary"],
    queryFn: () => dashboardService.summary("24h"),
    refetchInterval: 30000,
  });
}

export function useUnits() {
  return useQuery({
    queryKey: ["units", "all"],
    queryFn: () => unitService.list(),
    staleTime: 60000,
  });
}
