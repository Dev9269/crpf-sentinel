"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} />
      <Topbar collapsed={collapsed} />
      <div
        className={cn(
          "pt-16 transition-[padding] duration-200",
          collapsed ? "lg:pl-[72px]" : "lg:pl-[250px]",
        )}
      >
        <main className="mx-auto max-w-[1600px] p-6">{children}</main>
      </div>
    </div>
  );
}
