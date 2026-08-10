"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { useAuth } from "@/hooks/use-auth";
import { PageLoading } from "@/components/shared/page-states";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !token) {
      router.replace("/login");
    }
  }, [loading, token, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <PageLoading rows={2} label="Authenticating…" />
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
}
