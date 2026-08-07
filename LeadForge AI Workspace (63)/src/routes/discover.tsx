import { createFileRoute } from "@tanstack/react-router";
import { MapPin, Radar, Sparkles, Wand2 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { discoverySegments } from "@/lib/mock-data";

export const Route = createFileRoute("/discover")({
  head: () => ({
    meta: [
      { title: "Discover businesses — LeadForge" },
      { name: "description", content: "Run AI scans to find local businesses with missing, broken, or outdated websites." },
      { property: "og:title", content: "Discover businesses — LeadForge" },
      { property: "og:description", content: "Run AI scans across categories and regions to surface website opportunities." },
    ],
  }),
  component: Discover,
});

const criteria = ["No website", "Broken pages", "Outdated design", "No mobile layout", "Slow PageSpeed", "Running ads"];

function Discover() {
  return (
    <AppShell title="Discover" description="Scan a market and let the agent score every business it finds">
      <div className="space-y-6">
        <section className="panel glow-panel p-5 sm:p-6">
          <div className="flex items-center gap-2 text-xs font-semibold text-primary">
            <Sparkles className="size-4" /> AI discovery agent
          </div>
          <h2 className="mt-2 max-w-xl text-xl font-semibold sm:text-2xl">
            Describe the businesses you want and the agent handles the rest.
          </h2>
          <div className="mt-5 grid gap-4 md:grid-cols-[1.4fr_1fr_auto] md:items-end">
            <div className="space-y-1.5">
              <Label htmlFor="scan-query" className="text-xs">Business type</Label>
              <Input id="scan-query" defaultValue="Dental practices with poor online presence" className="h-10" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="scan-region" className="text-xs">Region</Label>
              <div className="relative">
                <MapPin className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input id="scan-region" defaultValue="Portland, US" className="h-10 pl-9" />
              </div>
            </div>
            <Button size="lg" className="h-10">
              <Radar className="size-4" />
              Run scan
            </Button>
          </div>
          <div className="mt-4 flex flex-wrap gap-1.5">
            {criteria.map((c, i) => (
              <button
                key={c}
                type="button"
                className={
                  i < 3
                    ? "rounded-full border border-primary/30 bg-primary/15 px-3 py-1 text-xs font-medium text-primary"
                    : "rounded-full border border-border bg-surface-raised px-3 py-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
                }
              >
                {c}
              </button>
            ))}
          </div>
        </section>

        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Scans this month" value="38" delta="+7" hint="vs last month" />
          <StatCard label="Businesses indexed" value="18,402" />
          <StatCard label="Avg. opportunity score" value="73.6" delta="+2.4" />
          <StatCard label="Credits per scan" value="~24" hint="based on region size" />
        </section>

        <section>
          <SectionHeader
            title="Saved segments"
            action={
              <Button variant="ghost" size="sm">
                <Wand2 className="size-3.5" />
                New segment
              </Button>
            }
          />
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {discoverySegments.map((s) => (
              <article key={s.id} className="panel p-4 transition-colors hover:border-border-strong">
                <p className="truncate text-sm font-medium">{s.name}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{s.region}</p>
                <div className="mt-4 flex items-end justify-between">
                  <div>
                    <p className="text-numeric text-xl font-semibold">{s.found.toLocaleString()}</p>
                    <p className="text-[11px] text-muted-foreground">businesses</p>
                  </div>
                  <div className="text-right">
                    <p className="text-numeric text-sm font-semibold text-primary">{s.avgScore}</p>
                    <p className="text-[11px] text-muted-foreground">avg score</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
