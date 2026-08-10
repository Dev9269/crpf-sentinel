import { cn } from "@/lib/utils";

export function Mono({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <code className={cn("rounded bg-surface2 px-1.5 py-0.5 font-mono text-[12px] text-accent", className)}>
      {children}
    </code>
  );
}
