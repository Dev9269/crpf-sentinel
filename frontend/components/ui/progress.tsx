import * as React from "react";

import { cn } from "@/lib/utils";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  colorClass?: string;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, colorClass, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("relative h-1.5 w-full overflow-hidden rounded-full bg-surface2", className)}
      {...props}
    >
      <div
        className={cn("h-full rounded-full bg-accent transition-all", colorClass)}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  ),
);
Progress.displayName = "Progress";

export { Progress };
