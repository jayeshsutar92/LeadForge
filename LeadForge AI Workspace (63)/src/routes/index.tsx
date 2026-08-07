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
import { formatCurrency, weeklyScans, activity, type LeadStatus } from "@/lib/mock-data";
import { useBusinessStats, useLeads } from "@/lib/api-hooks";

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

const maxScan = Math.max(...weeklyScans.map((d) => d.scanned));

function Overview() {
  const { data: stats, isLoading: statsLoading, isError: statsError } = useBusinessStats();
  const { data: leadsData, isLoading: leadsLoading } = useLeads({ limit: 100 });

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
      // We don't have business opportunity_score in LeadResponse easily without joining, so we just estimate value
      // or set it to 0 if we can't join. But we have top_leads from stats.
      const count = stageLeads.length;
      return {
        stage: s.stage,
        count,
        value: count * 15000, // Estimated avg value
      };
    });
  }, [leadsData]);

  const pipelineValue = pipeline.reduce((acc, p) => acc + p.value, 0);

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
            delta="+18.2%"
            hint="this week"
            icon={<Radar className="size-4" />}
          />
          <StatCard
            label="Qualified leads"
            value={stats?.high_opportunity?.toString() || "0"}
            delta="+24"
            hint="vs last week"
            icon={<Target className="size-4" />}
          />
          <StatCard
            label="Pipeline value"
            value={formatCurrency(pipelineValue)}
            delta="+9.4%"
            hint="open deals"
            icon={<TrendingUp className="size-4" />}
          />
          <StatCard
            label="Reply rate"
            value="24.1%"
            delta="+3.1pt"
            hint="all sequences"
            icon={<Users className="size-4" />}
          />
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
          <div className="panel p-5">
            <SectionHeader
              title="Scan volume & qualification"
              action={<span className="text-xs text-muted-foreground">Last 7 days</span>}
            />
            <div className="flex h-52 items-end gap-3">
              {weeklyScans.map((d) => (
                <div key={d.day} className="flex h-full min-w-0 flex-1 flex-col items-center gap-2">
                  <div className="flex w-full flex-1 items-end justify-center gap-1">
                    <div
                      className="w-1/2 rounded-t-md bg-muted"
                      style={{ height: `${(d.scanned / maxScan) * 100}%` }}
                      title={`${d.scanned} scanned`}
                    />
                    <div
                      className="w-1/2 rounded-t-md bg-primary"
                      style={{ height: `${(d.qualified / maxScan) * 100}%` }}
                      title={`${d.qualified} qualified`}
                    />
                  </div>
                  <span className="text-[11px] text-muted-foreground">{d.day}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="size-2 rounded-sm bg-muted" /> Scanned
              </span>
              <span className="flex items-center gap-1.5">
                <span className="size-2 rounded-sm bg-primary" /> Qualified
              </span>
            </div>
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
            ) : (
              <ul className="space-y-3">
                {pipeline.map((stage, i) => (
                  <li key={stage.stage}>
                    <div className="flex items-baseline justify-between gap-3 text-sm">
                      <span className="truncate font-medium">{stage.stage}</span>
                      <span className="text-numeric shrink-0 text-xs text-muted-foreground">
                        {stage.count} · {formatCurrency(stage.value)}
                      </span>
                    </div>
                    <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${100 - i * 18}%`, opacity: 1 - i * 0.15 }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
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
                        <WebsiteTag state={lead.website ? "has_website" : "missing_website"} />
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
            <SectionHeader title="Activity" />
            <ul className="space-y-4">
              {activity.map((item) => (
                <li key={item.id} className="flex gap-3">
                  <span
                    className={
                      item.kind === "ai"
                        ? "mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-primary-soft text-primary"
                        : "mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-muted text-muted-foreground"
                    }
                  >
                    <Sparkles className="size-3.5" />
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm leading-snug">
                      <span className="font-medium">{item.actor}</span>{" "}
                      <span className="text-muted-foreground">{item.action}</span>
                    </p>
                    <p className="text-[11px] text-muted-foreground">{item.time}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
