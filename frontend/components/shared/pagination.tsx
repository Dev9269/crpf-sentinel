import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Pagination({
  page,
  totalPages,
  total,
  onChange,
}: {
  page: number;
  totalPages: number;
  total: number;
  onChange: (page: number) => void;
}) {
  if (totalPages <= 0) return null;
  return (
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
      <p className="text-xs text-muted">
        Page <span className="font-mono text-foreground">{page}</span> of{" "}
        <span className="font-mono text-foreground">{totalPages}</span> · {total.toLocaleString()} results
      </p>
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="iconSm"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
          aria-label="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {page > 2 && (
          <Button variant="ghost" size="iconSm" onClick={() => onChange(1)}>
            1
          </Button>
        )}
        {page > 3 && <span className="px-1 text-xs text-muted">…</span>}
        {[page - 1, page, page + 1]
          .filter((p) => p >= 1 && p <= totalPages)
          .map((p) => (
            <Button
              key={p}
              variant={p === page ? "default" : "ghost"}
              size="iconSm"
              className={cn(p === page && "pointer-events-none")}
              onClick={() => onChange(p)}
            >
              {p}
            </Button>
          ))}
        {page < totalPages - 2 && <span className="px-1 text-xs text-muted">…</span>}
        {page < totalPages - 1 && (
          <Button variant="ghost" size="iconSm" onClick={() => onChange(totalPages)}>
            {totalPages}
          </Button>
        )}
        <Button
          variant="outline"
          size="iconSm"
          disabled={page >= totalPages}
          onClick={() => onChange(page + 1)}
          aria-label="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
