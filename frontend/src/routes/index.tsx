import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowUpRight, Radar, Sparkles, Target, TrendingUp, Users, Loader2 } from "lucide-react";
import { useMemo } from "react";

import { AppShell } from "@/components/app-shell";
import {
  ScoreBadge,
  SectionHeader,
  StatCard,
  StatusPill,
  WebsiteTag,
} from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { formatCurrency, type LeadStatus } from "@/lib/ui-utils";
import { useBusinessStats, useLeads, useBusinesses } from "@/lib/api-hooks";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LeadForge — AI lead generation & sales intelligence" },
      {
        name: "description",
        content:
          "Find businesses that need websites. LeadForge scores opportunities, manages leads, tracks outreach, and drafts AI proposals.",
      },
    ],
  }),
  component: Overview,
});

function Overview() {
  const { data: stats, isLoading: statsLoading, isError: statsError } = useBusinessStats();
  const { data: leadsData, isLoading: leadsLoading } = useLeads({ limit: 100 });
  const { data: businessesData } = useBusinesses({ limit: 100 });

  const top = stats?.top_leads || [];

  const pipeline = useMemo(() => {
    if (!leadsData?.results) return [];
    const stages = [
      { stage: "New", key: "new" },
      { stage: "Qualified", key: "qualified" },
      { stage: "Contacted", key: "contacted" },
      { stage: "Negotiating", key: "negotiating" },
    ];

    return stages.map((s) => {
      const stageLeads = leadsData.results.filter((l) => l.status === s.key);
      const count = stageLeads.length;
      let stageValue = 0;
      for (const lead of stageLeads) {
        const biz = businessesData?.results?.find((b) => b.id === lead.business_id);
        stageValue += (biz?.opportunity_score || 70) * 120;
      }
      return {
        stage: s.stage,
        count,
        value: stageValue,
      };
    });
  }, [leadsData, businessesData]);

  const pipelineValue = pipeline.reduce((acc, p) => acc + p.value, 0);

  const recentLeads = useMemo(() => {
    if (!leadsData?.results) return [];
    return [...leadsData.results]
      .sort((a, b) => {
        const tA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const tB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return tB - tA;
      })
      .slice(0, 5);
  }, [leadsData]);

  return (
    <AppShell
      title="Overview"
      description="Dashboard"
      actions={
        <Button asChild>
          <Link to="/discover">
            <Radar className="size-4" />
            New scan
          </Link>
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Businesses scanned"
            value={stats?.total_businesses?.toString() || "0"}
            icon={<Radar className="size-4" />}
          />
          <StatCard
            label="Qualified leads"
            value={stats?.high_opportunity?.toString() || "0"}
            icon={<Target className="size-4" />}
          />
          <StatCard
            label="Est. Pipeline value"
            value={formatCurrency(pipelineValue)}
            hint="open deals"
            icon={<TrendingUp className="size-4" />}
          />
          <StatCard
            label="Total Deals Won"
            value={leadsData?.results?.filter((l) => l.status === "won")?.length.toString() || "0"}
            icon={<Users className="size-4" />}
          />
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
          <div className="panel overflow-hidden">
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3.5">
              <h2 className="text-sm font-semibold">Highest scoring opportunities</h2>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/leads">
                  View all <ArrowUpRight className="size-3.5" />
                </Link>
              </Button>
            </div>
            {statsLoading ? (
              <div className="flex h-32 items-center justify-center">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : statsError ? (
              <div className="p-5 text-center text-sm text-destructive">
                Failed to load opportunities
              </div>
            ) : top.length === 0 ? (
              <div className="p-5 text-center text-sm text-muted-foreground">
                No opportunities found
              </div>
            ) : (
              <ul className="divide-y divide-border">
                {top.map((lead: any) => (
                  <li
                    key={lead.id}
                    className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-5 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{lead.name}</p>
                      <p className="truncate text-xs text-muted-foreground">
                        {lead.category} · {lead.city}, {lead.country}
                      </p>
                    </div>
                    <div className="flex shrink-0 items-center gap-3">
                      <span className="hidden sm:block">
                        <WebsiteTag state={lead.website ? "modern" : "none"} />
                      </span>
                      <span className="hidden md:block">
                        <StatusPill status="new" />
                      </span>
                      <ScoreBadge score={lead.opportunity_score} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="panel p-5">
            <SectionHeader
              title="Pipeline"
              action={<span className="text-xs text-muted-foreground">By stage</span>}
            />
            {leadsLoading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : pipeline.length === 0 ? (
              <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
                No pipeline data
              </div>
            ) : (
              <ul className="space-y-3">
                {pipeline.map((stage, i) => {
                  const maxStageCount = Math.max(...pipeline.map((s) => s.count)) || 1;
                  const width = (stage.count / maxStageCount) * 100;
                  return (
                    <li key={stage.stage}>
                      <div className="flex items-baseline justify-between gap-3 text-sm">
                        <span className="truncate font-medium">{stage.stage}</span>
                        <span className="text-numeric shrink-0 text-xs text-muted-foreground">
                          {stage.count} · {formatCurrency(stage.value)} (est)
                        </span>
                      </div>
                      <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary"
                          style={{ width: `${width}%`, opacity: 1 - i * 0.15 }}
                        />
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <div className="panel p-5">
            <SectionHeader title="Recent Activity" />
            {leadsLoading ? (
              <div className="flex h-32 items-center justify-center">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : recentLeads.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                No recent activity.
              </div>
            ) : (
              <ul className="space-y-4 mt-2">
                {recentLeads.map((lead) => {
                  const bName =
                    businessesData?.results?.find(
                      (b: any) => b.id === lead.business_id,
                    )?.name || "Lead";
                  return (
                    <li key={lead.id} className="flex gap-3">
                      <span className="mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-primary-soft text-primary">
                        <Sparkles className="size-3.5" />
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm leading-snug">
                          <span className="font-medium">{bName}</span>{" "}
                          <span className="text-muted-foreground">was discovered via scan</span>
                        </p>
                        <p className="text-[11px] text-muted-foreground uppercase">
                          {lead.status} ·{" "}
                          {lead.created_at ? new Date(lead.created_at).toLocaleTimeString() : "N/A"}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
