import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import { statusMeta, websiteStateMeta, type LeadStatus, type WebsiteState } from "@/lib/ui-utils";

export function StatusPill({ status }: { status: LeadStatus }) {
  const meta = statusMeta[status];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium",
        meta.tone,
      )}
    >
      {meta.label}
    </span>
  );
}

export function WebsiteTag({ state }: { state: WebsiteState }) {
  const meta = websiteStateMeta[state];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 whitespace-nowrap text-xs font-medium",
        meta.tone,
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {meta.label}
    </span>
  );
}

export function ScoreBadge({ score, size = "sm" }: { score: number; size?: "sm" | "lg" }) {
  const tone =
    score >= 85
      ? "border-primary/30 bg-primary/15 text-primary"
      : score >= 70
        ? "border-warning/30 bg-warning/15 text-warning"
        : "border-border bg-muted text-muted-foreground";
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-md border text-numeric font-semibold",
        tone,
        size === "lg" ? "h-10 min-w-14 px-3 text-lg" : "h-6 min-w-9 px-1.5 text-xs",
      )}
    >
      {score}
    </span>
  );
}

export function StatCard({
  label,
  value,
  delta,
  hint,
  icon,
}: {
  label: string;
  value: string;
  delta?: string;
  hint?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        {icon ? <span className="text-muted-foreground">{icon}</span> : null}
      </div>
      <p className="mt-2 text-numeric text-2xl font-semibold tracking-tight">{value}</p>
      <div className="mt-1 flex items-center gap-2 text-xs">
        {delta ? <span className="font-medium text-primary">{delta}</span> : null}
        {hint ? <span className="text-muted-foreground">{hint}</span> : null}
      </div>
    </div>
  );
}

export function SectionHeader({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-sm font-semibold">{title}</h2>
      {action}
    </div>
  );
}
