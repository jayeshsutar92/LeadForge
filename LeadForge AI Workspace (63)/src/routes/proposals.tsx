import { createFileRoute } from "@tanstack/react-router";
import { FileText, Sparkles } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { formatCurrency, proposals } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/proposals")({
  head: () => ({
    meta: [
      { title: "Proposals — LeadForge" },
      {
        name: "description",
        content:
          "AI-drafted proposals tailored to each business opportunity, from draft to accepted.",
      },
      { property: "og:title", content: "Proposals — LeadForge" },
      {
        property: "og:description",
        content: "AI-drafted proposals tailored to each business opportunity.",
      },
    ],
  }),
  component: Proposals,
});

const statusTone: Record<string, string> = {
  Draft: "bg-muted text-muted-foreground border-border",
  Sent: "bg-info/15 text-info border-info/25",
  "In review": "bg-warning/15 text-warning border-warning/25",
  Accepted: "bg-success/15 text-success border-success/25",
};

function Proposals() {
  return (
    <AppShell
      title="Proposals"
      description="4 active proposals · $54,900 in play"
      actions={
        <Button>
          <Sparkles className="size-4" />
          Generate proposal
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Proposals sent"
            value="46"
            delta="+8"
            hint="this quarter"
            icon={<FileText className="size-4" />}
          />
          <StatCard label="Acceptance rate" value="31%" delta="+4pt" />
          <StatCard label="Avg. deal size" value={formatCurrency(11200)} />
          <StatCard label="Avg. draft time" value="42s" hint="AI generated" />
        </section>

        <section className="grid gap-3 md:grid-cols-2">
          {proposals.map((p) => (
            <article
              key={p.id}
              className="panel flex flex-col p-5 transition-colors hover:border-border-strong"
            >
              <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
                <div className="min-w-0">
                  <p className="truncate text-xs text-muted-foreground">{p.lead}</p>
                  <h2 className="mt-0.5 truncate text-base font-semibold">{p.title}</h2>
                </div>
                <span
                  className={cn(
                    "shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-medium",
                    statusTone[p.status] ?? statusTone["Draft"],
                  )}
                >
                  {p.status}
                </span>
              </div>

              <p className="mt-4 flex items-center gap-1.5 text-[11px] text-muted-foreground">
                <Sparkles className="size-3 text-primary" /> {p.model} · updated {p.updated}
              </p>

              <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
                <p className="text-numeric text-lg font-semibold">{formatCurrency(p.value)}</p>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm">
                    Preview
                  </Button>
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>
    </AppShell>
  );
}
