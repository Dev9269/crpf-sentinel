import { Mono } from "@/components/shared/mono";

export function MitreBadge({ technique, name }: { technique?: string | null; name?: string | null }) {
  if (!technique) return <span className="text-xs text-muted">—</span>;
  return (
    <span className="inline-flex items-center gap-1.5">
      <Mono>{technique}</Mono>
      {name && <span className="text-xs text-muted">{name}</span>}
    </span>
  );
}
