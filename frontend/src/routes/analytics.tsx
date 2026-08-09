import { createFileRoute } from "@tanstack/react-router";
import { useMemo } from "react";
import { Loader2 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { formatCurrency } from "@/lib/ui-utils";
import { useLeads, useBusinessStats } from "@/lib/api-hooks";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — LeadForge" },
      {
        name: "description",
        content:
          "Conversion, sourcing, and revenue analytics across your lead generation pipeline.",
      },
    ],
  }),
  component: Analytics,
});

function Analytics() {
  const {
    data: leadsData,
    isLoading: leadsLoading,
    isError: leadsError,
  } = useLeads({ limit: 1000 });
  
  const { data: statsData } = useBusinessStats();

  const pipeline = useMemo(() => {
    if (!leadsData?.results) return [];
    const stages = [
      { stage: "New", key: "new" },
      { stage: "Qualified", key: "qualified" },
      { stage: "Contacted", key: "contacted" },
      { stage: "Negotiating", key: "negotiating" },
      { stage: "Won", key: "won" },
    ];

    return stages.map((s) => {
      const count = leadsData.results.filter((l) => l.status === s.key).length;
      return { stage: s.stage, count };
    });
  }, [leadsData]);

  // Aggregate stats from pipeline
  const wonCount = pipeline.find((p) => p.stage === "Won")?.count || 0;
  const newCount = pipeline.find((p) => p.stage === "New")?.count || 0;
  
  const totalLeads = leadsData?.total || 0;

  const wonRevenue = wonCount * 15000; // Simplified estimation for now
  const leadToDeal = totalLeads > 0 ? (wonCount / totalLeads) * 100 : 0;

  return (
    <AppShell title="Analytics" description="Performance across discovery, outreach, and revenue">
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Est. Won revenue"
            value={formatCurrency(wonRevenue)}
            hint="based on $15k avg"
          />
          <StatCard label="Lead → deal" value={`${leadToDeal.toFixed(1)}%`} />
          <StatCard label="Total Leads" value={totalLeads.toString()} />
          <StatCard label="Missing Websites" value={statsData?.missing_website?.toString() || "0"} />
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <div className="panel p-5">
            <SectionHeader title="Funnel conversion" />
            {leadsError ? (
              <div className="flex h-48 items-center justify-center text-sm text-destructive">
                Failed to load pipeline data.
              </div>
            ) : leadsLoading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : pipeline.length === 0 ? (
              <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
                No leads found.
              </div>
            ) : (
              <ul className="space-y-4">
                {pipeline.map((stage, i) => {
                  const prev = pipeline[i - 1];
                  const rate =
                    prev && prev.count > 0 ? Math.round((stage.count / prev.count) * 100) : (i > 0 ? 0 : 100);
                  return (
                    <li key={stage.stage}>
                      <div className="flex items-baseline justify-between text-sm">
                        <span className="font-medium">{stage.stage}</span>
                        <span className="text-numeric text-xs text-muted-foreground">
                          {stage.count} {prev ? `· ${rate}% step` : ""}
                        </span>
                      </div>
                      <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${totalLeads > 0 ? (stage.count / totalLeads) * 100 : 0}%` }}
                        />
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          
          <div className="panel p-5">
            <SectionHeader title="Category breakdown" />
            {statsData?.by_category ? (
              <ul className="space-y-4">
                {Object.entries(statsData.by_category).map(([name, count]) => {
                  const share = Math.round((count / (statsData.total_businesses || 1)) * 100);
                  return (
                    <li key={name} className="flex items-center gap-3">
                      <span className="min-w-0 flex-1 truncate text-sm">{name}</span>
                      <span className="h-2 w-32 overflow-hidden rounded-full bg-muted">
                        <span
                          className="block h-full rounded-full bg-chart-2 transition-all"
                          style={{ width: `${share}%` }}
                        />
                      </span>
                      <span className="text-numeric w-10 text-right text-xs text-muted-foreground">
                        {share}%
                      </span>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
                No category data available.
              </div>
            )}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
