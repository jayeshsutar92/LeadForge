import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Building2,
  Globe,
  Mail,
  Phone,
  Plus,
  Search,
  SlidersHorizontal,
  Sparkles,
  Star,
  X,
  Loader2,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { ScoreBadge, StatusPill, WebsiteTag } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatCurrency, statusMeta, type LeadStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { useLeads, useBusinesses, useLeadDetail, useBusinessDetail } from "@/lib/api-hooks";

export const Route = createFileRoute("/leads")({
  head: () => ({
    meta: [
      { title: "Leads — LeadForge" },
      {
        name: "description",
        content: "Filter, score, and work every business opportunity in one CRM table.",
      },
    ],
  }),
  component: LeadsPage,
});

const filters: Array<{ key: LeadStatus | "all"; label: string }> = [
  { key: "all", label: "All" },
  { key: "new", label: "New" },
  { key: "qualified", label: "Qualified" },
  { key: "contacted", label: "Contacted" },
  { key: "negotiating", label: "Negotiating" },
  { key: "won", label: "Won" },
];

function LeadsPage() {
  const [filter, setFilter] = useState<LeadStatus | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);

  const {
    data: leadsData,
    isLoading: leadsLoading,
    isError: leadsError,
  } = useLeads({ limit: 100 });
  const { data: businessesData, isLoading: bizLoading } = useBusinesses({ limit: 100 });

  const { data: selectedLeadDetail, isLoading: leadDetailLoading } = useLeadDetail(selectedLeadId);
  const { data: selectedBizDetail, isLoading: bizDetailLoading } = useBusinessDetail(
    businessesData?.results
      .find((b) => b.id === selectedLeadDetail?.business_id)
      ?.name.toLowerCase()
      .replace(/[^a-z0-9]+/g, "-") || null,
  );

  const rows = useMemo(() => {
    if (!leadsData?.results || !businessesData?.results) return [];

    return leadsData.results
      .map((lead) => {
        const biz = businessesData.results.find((b) => b.id === lead.business_id);
        return {
          ...lead,
          business: biz || {
            name: "Unknown",
            category: "Unknown",
            city: "Unknown",
            website: "",
            opportunity_score: 0,
          },
        };
      })
      .filter((l) => {
        const matchesFilter = filter === "all" || l.status === filter;
        const searchLower = query.toLowerCase();
        const matchesQuery =
          l.business.name.toLowerCase().includes(searchLower) ||
          l.business.category.toLowerCase().includes(searchLower) ||
          l.business.city.toLowerCase().includes(searchLower);
        return matchesFilter && matchesQuery;
      });
  }, [leadsData, businessesData, filter, query]);

  const selectedBiz =
    businessesData?.results.find((b) => b.id === selectedLeadDetail?.business_id) || null;

  if (leadsError) {
    return (
      <AppShell title="Leads">
        <div className="flex h-64 items-center justify-center rounded-lg border border-border bg-card p-6 text-center shadow-sm">
          <p className="text-destructive">Failed to load leads. Please try again later.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Leads"
      description={leadsLoading ? "Loading leads..." : `${rows.length} businesses match your view`}
      actions={
        <Button>
          <Plus className="size-4" />
          Add lead
        </Button>
      }
    >
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="panel flex min-w-0 flex-col overflow-hidden">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border p-3 sm:flex sm:flex-wrap">
            <div className="relative min-w-0 sm:w-64">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search name, category, city"
                aria-label="Search leads"
                className="h-9 pl-9"
              />
            </div>
            <Button variant="outline" size="sm" className="h-9 shrink-0">
              <SlidersHorizontal className="size-4" />
              Filters
            </Button>
            <Tabs
              value={filter}
              onValueChange={(v) => setFilter(v as LeadStatus | "all")}
              className="col-span-2 sm:ml-auto"
            >
              <TabsList className="h-9 overflow-x-auto">
                {filters.map((f) => (
                  <TabsTrigger key={f.key} value={f.key} className="text-xs">
                    {f.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>

          <div className="min-w-0 overflow-x-auto">
            <table className="w-full min-w-[520px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th scope="col" className="px-4 py-2.5 font-medium">
                    Business
                  </th>
                  <th scope="col" className="px-4 py-2.5 font-medium">
                    Website
                  </th>
                  <th scope="col" className="px-4 py-2.5 font-medium">
                    Status
                  </th>
                  <th scope="col" className="hidden px-4 py-2.5 font-medium 2xl:table-cell">
                    Priority
                  </th>
                  <th
                    scope="col"
                    className="hidden px-4 py-2.5 text-right font-medium 2xl:table-cell"
                  >
                    Est. value
                  </th>
                  <th scope="col" className="px-4 py-2.5 text-right font-medium">
                    Score
                  </th>
                </tr>
              </thead>
              <tbody>
                {leadsLoading || bizLoading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center">
                      <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
                    </td>
                  </tr>
                ) : rows.length === 0 ? (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-4 py-10 text-center text-sm text-muted-foreground"
                    >
                      No businesses match this view.
                    </td>
                  </tr>
                ) : (
                  rows.map((lead) => (
                    <tr
                      key={lead.id}
                      onClick={() => setSelectedLeadId(lead.id)}
                      tabIndex={0}
                      onKeyDown={(e) => e.key === "Enter" && setSelectedLeadId(lead.id)}
                      className={cn(
                        "cursor-pointer border-b border-border/70 transition-colors last:border-0 hover:bg-accent/50",
                        selectedLeadId === lead.id && "bg-accent/70",
                      )}
                    >
                      <td className="px-4 py-3">
                        <div className="flex min-w-0 items-center gap-3">
                          <span className="grid size-8 shrink-0 place-items-center rounded-md bg-surface-raised text-[11px] font-semibold">
                            {lead.business.name.slice(0, 2).toUpperCase()}
                          </span>
                          <span className="min-w-0">
                            <span className="block truncate font-medium">{lead.business.name}</span>
                            <span className="block truncate text-xs text-muted-foreground">
                              {lead.business.category} · {lead.business.city}
                            </span>
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <WebsiteTag
                          state={lead.business.website ? "has_website" : "missing_website"}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <StatusPill status={lead.status as LeadStatus} />
                      </td>
                      <td className="hidden px-4 py-3 text-xs text-muted-foreground 2xl:table-cell">
                        P{lead.priority}
                      </td>
                      <td className="text-numeric hidden px-4 py-3 text-right text-xs 2xl:table-cell">
                        {formatCurrency(lead.business.opportunity_score * 120)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <ScoreBadge score={lead.business.opportunity_score} />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {selectedLeadId ? (
          <aside className="panel h-fit xl:sticky xl:top-24">
            {leadDetailLoading || bizDetailLoading ? (
              <div className="grid h-64 place-items-center p-6 text-center">
                <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
              </div>
            ) : selectedBizDetail ? (
              <>
                <div className="flex items-start justify-between gap-3 border-b border-border p-4">
                  <div className="min-w-0">
                    <p className="truncate font-display text-base font-semibold">
                      {selectedBiz?.name}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {selectedBiz?.category} · {selectedBiz?.city}, {selectedBiz?.country}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Close detail panel"
                    className="size-8 shrink-0"
                    onClick={() => setSelectedLeadId(null)}
                  >
                    <X className="size-4" />
                  </Button>
                </div>

                <div className="flex items-center gap-3 border-b border-border p-4">
                  <ScoreBadge score={selectedBiz?.opportunity_score ?? 0} size="lg" />
                  <div className="min-w-0">
                    <p className="text-xs font-medium">Opportunity score</p>
                    <p className="text-xs text-muted-foreground">
                      Est. {formatCurrency((selectedBiz?.opportunity_score ?? 0) * 120)}
                    </p>
                  </div>
                  <span className="ml-auto">
                    <StatusPill status={(selectedLeadDetail?.status as LeadStatus) || "new"} />
                  </span>
                </div>

                <div className="space-y-4 p-4">
                  <div className="rounded-lg border border-primary/20 bg-primary-soft/30 p-3">
                    <p className="flex items-center gap-1.5 text-xs font-semibold text-primary">
                      <Sparkles className="size-3.5" /> Next Follow Up
                    </p>
                    <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
                      {selectedLeadDetail?.next_follow_up
                        ? new Date(selectedLeadDetail.next_follow_up).toLocaleString()
                        : "None scheduled."}
                    </p>
                  </div>

                  {selectedLeadDetail?.notes && (
                    <div>
                      <p className="mb-2 text-xs font-semibold">Notes</p>
                      <p className="text-[11px] text-muted-foreground">
                        {selectedLeadDetail.notes}
                      </p>
                    </div>
                  )}

                  <dl className="space-y-2.5 text-xs">
                    <Row
                      icon={<Globe className="size-3.5" />}
                      label="Website"
                      value={selectedBiz?.website || "None found"}
                    />
                    <Row
                      icon={<Star className="size-3.5" />}
                      label="Rating"
                      value={`${selectedBiz?.rating || 0} · ${selectedBiz?.reviews || 0} reviews`}
                    />
                    <Row
                      icon={<Phone className="size-3.5" />}
                      label="Phone"
                      value={selectedBizDetail?.detail?.phone || "Unknown"}
                    />
                  </dl>

                  <div className="flex gap-2">
                    <Button className="flex-1">
                      <Sparkles className="size-4" />
                      Draft proposal
                    </Button>
                    <Button variant="outline" className="flex-1">
                      Start outreach
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="grid h-64 place-items-center p-6 text-center text-sm text-muted-foreground">
                Lead detail not available.
              </div>
            )}
          </aside>
        ) : (
          <aside className="panel grid h-64 place-items-center p-6 text-center text-sm text-muted-foreground xl:sticky xl:top-24">
            Select a lead to see details.
          </aside>
        )}
      </div>
      <p className="sr-only">{Object.keys(statusMeta).length} lead statuses available.</p>
    </AppShell>
  );
}

function Row({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="flex shrink-0 items-center gap-2 text-muted-foreground">
        {icon}
        {label}
      </dt>
      <dd className="min-w-0 truncate font-medium">{value}</dd>
    </div>
  );
}
