import { createFileRoute } from "@tanstack/react-router";
import { Mail, MessageSquare, Plus, Sparkles, Loader2 } from "lucide-react";
import { useMemo } from "react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { useLeads } from "@/lib/api-hooks";

export const Route = createFileRoute("/outreach")({
  head: () => ({
    meta: [
      { title: "Outreach — LeadForge" },
      {
        name: "description",
        content: "Track sequences, replies, and follow-ups across every lead you contact.",
      },
    ],
  }),
  component: Outreach,
});

function Outreach() {
  const { data: leadsData, isLoading, isError } = useLeads({ limit: 100 });

  const contactedLeads = useMemo(() => {
    if (!leadsData?.results) return [];
    return leadsData.results.filter(
      (l) => l.status === "contacted" || l.status === "negotiating" || l.status === "qualified"
    ).sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  }, [leadsData]);

  const activeCount = contactedLeads.length;

  return (
    <AppShell
      title="Outreach"
      description={`${activeCount} leads actively in pipeline`}
      actions={
        <Button>
          <Plus className="size-4" />
          Start campaign
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Active conversations"
            value={activeCount.toString()}
            icon={<MessageSquare className="size-4" />}
          />
          <StatCard label="Response rate" value="--" hint="Need more data" />
          <StatCard label="Qualified" value={leadsData?.results.filter(l => l.status === "qualified").length.toString() || "0"} />
          <StatCard
            label="Total leads"
            value={leadsData?.total?.toString() || "0"}
            icon={<Mail className="size-4" />}
          />
        </section>

        <section className="panel p-5">
          <SectionHeader
            title="Active Outreach"
            action={<span className="text-xs text-muted-foreground">{activeCount} leads</span>}
          />
          {isError ? (
            <div className="flex h-48 items-center justify-center text-sm text-destructive">
              Failed to load outreach data.
            </div>
          ) : isLoading ? (
            <div className="flex h-48 items-center justify-center">
              <Loader2 className="size-6 animate-spin text-muted-foreground" />
            </div>
          ) : contactedLeads.length === 0 ? (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              No active outreach at the moment.
            </div>
          ) : (
            <ul className="mt-4 space-y-3">
              {contactedLeads.map((lead) => (
                <li key={lead.id} className="rounded-lg border border-border bg-surface-raised p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Lead ID: {lead.id.substring(0, 8)}</p>
                      <p className="mt-1 text-xs text-muted-foreground">Status: <span className="uppercase text-primary">{lead.status}</span></p>
                    </div>
                    <span className="shrink-0 text-[11px] text-muted-foreground">
                      Updated {new Date(lead.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center justify-between border-t border-border/50 pt-3">
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {lead.notes || "No notes available."}
                    </p>
                    <Button variant="ghost" size="sm" className="h-7 text-xs">
                      View details
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </AppShell>
  );
}
