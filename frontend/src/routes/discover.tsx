import { createFileRoute } from "@tanstack/react-router";
import { MapPin, Radar, Sparkles, Wand2, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useBusinessStats,
  useBusinesses,
  useDiscoverBusinesses,
  type BusinessCard,
} from "@/lib/api-hooks";
import { getErrorMessage } from "@/lib/api";

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
  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
    refetch: refetchStats,
  } = useBusinessStats();
  const {
    data: businessesData,
    isLoading: bizLoading,
    refetch: refetchBiz,
  } = useBusinesses({ limit: 12 });
  const discoverBusinesses = useDiscoverBusinesses();

  const [discoveryMode, setDiscoveryMode] = useState<"official" | "social">("official");

  const [scanState, setScanState] = useState<{
    active: boolean;
    message: string;
    found: number;
    processed: number;
    results: Record<string, unknown>[];
  }>({
    active: false,
    message: "",
    found: 0,
    processed: 0,
    results: [],
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ScanFormValues>({
    resolver: zodResolver(scanSchema),
    defaultValues: {
      query: "Dental practices",
      region: "Portland, US",
    },
  });

  const onSubmit = async (data: ScanFormValues) => {
    setScanState({
      active: true,
      message: "Querying external business database...",
      found: 0,
      processed: 0,
      results: [],
    });

    try {
      const result = await discoverBusinesses.mutateAsync({
        query: data.query,
        region: data.region,
      });

      setScanState((prev) => ({
        ...prev,
        found: result.found,
        processed: result.found, // all processed on backend
        message: result.message,
        results: result.results || [],
      }));

      toast.success("Scan completed successfully", {
        description: `Imported ${result.new_leads} new leads from ${result.found} found businesses.`,
      });

      refetchStats();
      refetchBiz();
    } catch (err: unknown) {
      toast.error("Scan failed", {
        description: getErrorMessage(err) || "An unexpected error occurred during the scan.",
      });
    } finally {
      setScanState((prev) => ({ ...prev, active: false }));
    }
  };

  const segments = stats?.by_category
    ? Object.entries(stats.by_category).map(([name, count], i) => ({
        id: i.toString(),
        name,
        region: "Global",
        found: count as number,
        avgScore: stats.avg_score || 0,
      }))
    : [];

  const displayBusinesses =
    scanState.results.length > 0 ? scanState.results : businessesData?.results || [];

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

          <div className="mt-6 mb-8 flex items-center rounded-md border border-border bg-surface-raised p-1 w-fit">
            <button
              type="button"
              onClick={() => setDiscoveryMode("official")}
              className={`px-4 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                discoveryMode === "official"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Official Businesses
            </button>
            <button
              type="button"
              onClick={() => setDiscoveryMode("social")}
              className={`px-4 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                discoveryMode === "social"
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Social Media Businesses
            </button>
          </div>

          {discoveryMode === "social" ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-primary/10 p-4 mb-4">
                <Radar className="size-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Coming Soon</h3>
              <p className="mt-2 max-w-md text-sm text-muted-foreground">
                We are actively building out our social media discovery engine to source
                high-quality leads directly from platforms like Instagram and Facebook. Check back
                soon!
              </p>
            </div>
          ) : (
            <>
              <form
                onSubmit={handleSubmit(onSubmit)}
                className="grid gap-4 md:grid-cols-[1.4fr_1fr_auto] md:items-start"
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
                    disabled={isSubmitting || scanState.active}
                    className={`h-10 ${errors.query ? "border-destructive focus-visible:ring-destructive" : ""}`}
                    aria-invalid={!!errors.query}
                    placeholder="e.g. Plumbers, Dental clinics..."
                  />
                  {errors.query && (
                    <p className="text-[11px] font-medium text-destructive">
                      {errors.query.message}
                    </p>
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
                      disabled={isSubmitting || scanState.active}
                      className={`h-10 pl-9 ${errors.region ? "border-destructive focus-visible:ring-destructive" : ""}`}
                      aria-invalid={!!errors.region}
                      placeholder="e.g. Portland, US or London, UK"
                    />
                  </div>
                  {errors.region && (
                    <p className="text-[11px] font-medium text-destructive">
                      {errors.region.message}
                    </p>
                  )}
                </div>
                <Button
                  size="lg"
                  className="h-10 md:mt-[22px]"
                  type="submit"
                  disabled={isSubmitting || scanState.active}
                >
                  {isSubmitting || scanState.active ? (
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

              {scanState.active && (
                <div className="mt-4 flex items-center justify-between rounded-md bg-secondary/50 px-4 py-2 text-sm text-secondary-foreground">
                  <div className="flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin text-primary" />
                    <span>{scanState.message}</span>
                  </div>
                  {scanState.found > 0 && (
                    <span className="font-medium">
                      {scanState.processed} / {scanState.found}
                    </span>
                  )}
                </div>
              )}

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
            </>
          )}
        </section>

        {discoveryMode === "official" &&
          (statsError ? (
            <div className="flex h-32 items-center justify-center rounded-lg border border-border bg-card p-6 text-center shadow-sm">
              <p className="text-destructive">Failed to load discover stats.</p>
            </div>
          ) : statsLoading || bizLoading ? (
            <div className="flex h-32 items-center justify-center rounded-lg border border-border bg-card p-6 shadow-sm">
              <Loader2 className="size-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <>
              <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard
                  label="Total Scans"
                  value={(stats?.total_businesses || 0).toString()}
                  hint="lifetime"
                />
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
                  title="Discovered Businesses"
                  action={
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        refetchStats();
                        refetchBiz();
                      }}
                    >
                      <Radar className="size-3.5 mr-2" />
                      Refresh
                    </Button>
                  }
                />
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {displayBusinesses.length > 0 ? (
                    (displayBusinesses as BusinessCard[]).map((b) => (
                      <article
                        key={b.id}
                        className="panel p-4 transition-colors hover:border-border-strong flex flex-col"
                      >
                        <div className="flex items-start justify-between">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium">{b.name}</p>
                            <p className="mt-0.5 text-xs text-muted-foreground truncate">
                              {b.category} · {b.city}
                            </p>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-medium whitespace-nowrap ${b.website ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"}`}
                          >
                            {b.website ? "Has Website" : "No Website"}
                          </span>
                        </div>
                        <div className="mt-4 flex items-end justify-between pt-3 border-t border-border">
                          <div>
                            <p className="text-numeric text-lg font-semibold">
                              {b.opportunity_score}
                            </p>
                            <p className="text-[11px] text-muted-foreground">score</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">
                              {b.created_at ? new Date(b.created_at).toLocaleDateString() : "N/A"}
                            </p>
                          </div>
                        </div>
                      </article>
                    ))
                  ) : (
                    <div className="col-span-full py-8 text-center text-sm text-muted-foreground">
                      No businesses found. Run a scan to discover businesses.
                    </div>
                  )}
                </div>
              </section>
            </>
          ))}
      </div>
    </AppShell>
  );
}
