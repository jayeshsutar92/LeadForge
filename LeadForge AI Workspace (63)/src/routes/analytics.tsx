import { createFileRoute } from "@tanstack/react-router";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { formatCurrency, pipeline, weeklyScans } from "@/lib/mock-data";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — LeadForge" },
      { name: "description", content: "Conversion, sourcing, and revenue analytics across your lead generation pipeline." },
      { property: "og:title", content: "Analytics — LeadForge" },
      { property: "og:description", content: "Conversion, sourcing, and revenue analytics for your pipeline." },
    ],
  }),
  component: Analytics,
});

const sources = [
  { name: "No-website scans", share: 42 },
  { name: "Broken site alerts", share: 26 },
  { name: "Outdated design", share: 19 },
  { name: "Referrals", share: 13 },
];

const maxScan = Math.max(...weeklyScans.map((d) => d.scanned));

function Analytics() {
  return (
    <AppShell title="Analytics" description="Performance across discovery, outreach, and revenue">
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Won revenue" value={formatCurrency(96400)} delta="+12.6%" hint="this quarter" />
          <StatCard label="Lead → deal" value="7.3%" delta="+0.9pt" />
          <StatCard label="Avg. cycle" value="18 days" delta="-3 days" />
          <StatCard label="Cost per lead" value="$1.84" delta="-$0.22" />
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <div className="panel p-5">
            <SectionHeader title="Funnel conversion" />
            <ul className="space-y-4">
              {pipeline.map((stage, i) => {
                const prev = pipeline[i - 1];
                const rate = prev ? Math.round((stage.count / prev.count) * 100) : 100;
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
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${(stage.count / pipeline[0]!.count) * 100}%` }}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="panel p-5">
            <SectionHeader title="Lead sources" />
            <ul className="space-y-4">
              {sources.map((s) => (
                <li key={s.name} className="flex items-center gap-3">
                  <span className="min-w-0 flex-1 truncate text-sm">{s.name}</span>
                  <span className="h-2 w-32 overflow-hidden rounded-full bg-muted">
                    <span className="block h-full rounded-full bg-chart-2" style={{ width: `${s.share}%` }} />
                  </span>
                  <span className="text-numeric w-10 text-right text-xs text-muted-foreground">{s.share}%</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="panel p-5">
          <SectionHeader title="Scan throughput" action={<span className="text-xs text-muted-foreground">Last 7 days</span>} />
          <div className="flex h-44 items-end gap-3">
            {weeklyScans.map((d) => (
              <div key={d.day} className="flex h-full min-w-0 flex-1 flex-col justify-end items-center gap-2">
                <div
                  className="w-full rounded-t-md bg-primary/80"
                  style={{ height: `${(d.scanned / maxScan) * 100}%` }}
                />
                <span className="text-[11px] text-muted-foreground">{d.day}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
