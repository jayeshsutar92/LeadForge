import { createFileRoute } from "@tanstack/react-router";
import { MapPin, Radar, Sparkles, Wand2, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useBusinessStats } from "@/lib/api-hooks";

export const Route = createFileRoute("/discover")({
  head: () => ({
    meta: [
      { title: "Discover businesses — LeadForge" },
      {
        name: "description",
        content:
          "Run AI scans to find local businesses with missing, broken, or outdated websites.",
      },
    ],
  }),
  component: Discover,
});

const criteria = [
  "No website",
  "Broken pages",
  "Outdated design",
  "No mobile layout",
  "Slow PageSpeed",
  "Running ads",
];

const scanSchema = z.object({
  query: z.string().min(3, "Business type must be at least 3 characters"),
  region: z.string().min(2, "Region must be at least 2 characters"),
});

type ScanFormValues = z.infer<typeof scanSchema>;

function Discover() {
  const { data: stats, isLoading, isError } = useBusinessStats();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ScanFormValues>({
    resolver: zodResolver(scanSchema),
    defaultValues: {
      query: "Dental practices with poor online presence",
      region: "Portland, US",
    },
  });

  const onSubmit = async (data: ScanFormValues) => {
    // Simulate API call for scanning
    return new Promise((resolve) => {
      setTimeout(() => {
        toast.success("Scan initiated successfully", {
          description: `Scanning for ${data.query} in ${data.region}`,
        });
        resolve(true);
      }, 1000);
    });
  };

  const segments = stats?.by_category
    ? Object.entries(stats.by_category).map(([name, count], i) => ({
        id: i.toString(),
        name,
        region: "All Regions",
        found: count as number,
        avgScore: stats.avg_score || 0,
      }))
    : [];

  return (
    <AppShell
      title="Discover"
      description="Scan a market and let the agent score every business it finds"
    >
      <div className="space-y-6">
        <section className="panel glow-panel p-5 sm:p-6">
          <div className="flex items-center gap-2 text-xs font-semibold text-primary">
            <Sparkles className="size-4" /> AI discovery agent
          </div>
          <h2 className="mt-2 max-w-xl text-xl font-semibold sm:text-2xl">
            Describe the businesses you want and the agent handles the rest.
          </h2>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="mt-5 grid gap-4 md:grid-cols-[1.4fr_1fr_auto] md:items-start"
          >
            <div className="space-y-1.5">
              <Label
                htmlFor="scan-query"
                className={`text-xs ${errors.query ? "text-destructive" : ""}`}
              >
                Business type
              </Label>
              <Input
                id="scan-query"
                {...register("query")}
                disabled={isSubmitting}
                className={`h-10 ${errors.query ? "border-destructive focus-visible:ring-destructive" : ""}`}
                aria-invalid={!!errors.query}
              />
              {errors.query && (
                <p className="text-[11px] font-medium text-destructive">{errors.query.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label
                htmlFor="scan-region"
                className={`text-xs ${errors.region ? "text-destructive" : ""}`}
              >
                Region
              </Label>
              <div className="relative">
                <MapPin className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="scan-region"
                  {...register("region")}
                  disabled={isSubmitting}
                  className={`h-10 pl-9 ${errors.region ? "border-destructive focus-visible:ring-destructive" : ""}`}
                  aria-invalid={!!errors.region}
                />
              </div>
              {errors.region && (
                <p className="text-[11px] font-medium text-destructive">{errors.region.message}</p>
              )}
            </div>
            <Button size="lg" className="h-10 md:mt-[22px]" type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Radar className="size-4" />
                  Run scan
                </>
              )}
            </Button>
          </form>
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

        {isError ? (
          <div className="flex h-32 items-center justify-center rounded-lg border border-border bg-card p-6 text-center shadow-sm">
            <p className="text-destructive">Failed to load discover stats.</p>
          </div>
        ) : isLoading ? (
          <div className="flex h-32 items-center justify-center rounded-lg border border-border bg-card p-6 shadow-sm">
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard label="Scans this month" value="38" delta="+7" hint="vs last month" />
              <StatCard
                label="Businesses indexed"
                value={stats?.total_businesses?.toString() || "0"}
              />
              <StatCard
                label="Avg. opportunity score"
                value={stats?.avg_score?.toString() || "0"}
              />
              <StatCard
                label="Missing websites"
                value={stats?.missing_website?.toString() || "0"}
                hint="across all segments"
              />
            </section>

            <section>
              <SectionHeader
                title="Segments found"
                action={
                  <Button variant="ghost" size="sm">
                    <Wand2 className="size-3.5" />
                    New segment
                  </Button>
                }
              />
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {segments.length > 0 ? (
                  segments.map((s) => (
                    <article
                      key={s.id}
                      className="panel p-4 transition-colors hover:border-border-strong"
                    >
                      <p className="truncate text-sm font-medium">{s.name}</p>
                      <p className="mt-0.5 text-xs text-muted-foreground">{s.region}</p>
                      <div className="mt-4 flex items-end justify-between">
                        <div>
                          <p className="text-numeric text-xl font-semibold">
                            {s.found.toLocaleString()}
                          </p>
                          <p className="text-[11px] text-muted-foreground">businesses</p>
                        </div>
                        <div className="text-right">
                          <p className="text-numeric text-sm font-semibold text-primary">
                            {s.avgScore}
                          </p>
                          <p className="text-[11px] text-muted-foreground">avg score</p>
                        </div>
                      </div>
                    </article>
                  ))
                ) : (
                  <div className="col-span-full py-8 text-center text-sm text-muted-foreground">
                    No segments found.
                  </div>
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}
