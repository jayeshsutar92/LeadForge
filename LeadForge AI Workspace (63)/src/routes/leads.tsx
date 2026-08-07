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
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { ScoreBadge, StatusPill, WebsiteTag } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatCurrency, leads, statusMeta, type LeadStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/leads")({
  head: () => ({
    meta: [
      { title: "Leads — LeadForge" },
      { name: "description", content: "Filter, score, and work every business opportunity in one CRM table." },
      { property: "og:title", content: "Leads — LeadForge" },
      { property: "og:description", content: "Filter, score, and work every business opportunity in one CRM table." },
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
  const [selectedId, setSelectedId] = useState<string | null>(leads[0]?.id ?? null);

  const rows = useMemo(
    () =>
      leads.filter(
        (l) =>
          (filter === "all" || l.status === filter) &&
          (l.name.toLowerCase().includes(query.toLowerCase()) ||
            l.category.toLowerCase().includes(query.toLowerCase()) ||
            l.city.toLowerCase().includes(query.toLowerCase())),
      ),
    [filter, query],
  );

  const selected = leads.find((l) => l.id === selectedId) ?? null;

  return (
    <AppShell
      title="Leads"
      description={`${rows.length} of ${leads.length} businesses match your view`}
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
            <Tabs value={filter} onValueChange={(v) => setFilter(v as LeadStatus | "all")} className="col-span-2 sm:ml-auto">
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
                  <th scope="col" className="px-4 py-2.5 font-medium">Business</th>
                  <th scope="col" className="px-4 py-2.5 font-medium">Website</th>
                  <th scope="col" className="px-4 py-2.5 font-medium">Status</th>
                  <th scope="col" className="hidden px-4 py-2.5 font-medium 2xl:table-cell">Owner</th>
                  <th scope="col" className="hidden px-4 py-2.5 text-right font-medium 2xl:table-cell">Est. value</th>
                  <th scope="col" className="px-4 py-2.5 text-right font-medium">Score</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelectedId(lead.id)}
                    tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && setSelectedId(lead.id)}
                    className={cn(
                      "cursor-pointer border-b border-border/70 transition-colors last:border-0 hover:bg-accent/50",
                      selectedId === lead.id && "bg-accent/70",
                    )}
                  >
                    <td className="px-4 py-3">
                      <div className="flex min-w-0 items-center gap-3">
                        <span className="grid size-8 shrink-0 place-items-center rounded-md bg-surface-raised text-[11px] font-semibold">
                          {lead.name.slice(0, 2).toUpperCase()}
                        </span>
                        <span className="min-w-0">
                          <span className="block truncate font-medium">{lead.name}</span>
                          <span className="block truncate text-xs text-muted-foreground">
                            {lead.category} · {lead.city}
                          </span>
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3"><WebsiteTag state={lead.websiteState} /></td>
                    <td className="px-4 py-3"><StatusPill status={lead.status} /></td>
                    <td className="hidden px-4 py-3 text-xs text-muted-foreground 2xl:table-cell">{lead.owner}</td>
                    <td className="text-numeric hidden px-4 py-3 text-right text-xs 2xl:table-cell">{formatCurrency(lead.estValue)}</td>
                    <td className="px-4 py-3 text-right"><ScoreBadge score={lead.score} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {rows.length === 0 ? (
              <p className="px-4 py-10 text-center text-sm text-muted-foreground">No businesses match this view.</p>
            ) : null}
          </div>
        </div>

        {selected ? (
          <aside className="panel h-fit xl:sticky xl:top-24">
            <div className="flex items-start justify-between gap-3 border-b border-border p-4">
              <div className="min-w-0">
                <p className="truncate font-display text-base font-semibold">{selected.name}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {selected.category} · {selected.city}, {selected.country}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Close detail panel"
                className="size-8 shrink-0"
                onClick={() => setSelectedId(null)}
              >
                <X className="size-4" />
              </Button>
            </div>

            <div className="flex items-center gap-3 border-b border-border p-4">
              <ScoreBadge score={selected.score} size="lg" />
              <div className="min-w-0">
                <p className="text-xs font-medium">Opportunity score</p>
                <p className="text-xs text-muted-foreground">
                  Est. {formatCurrency(selected.estValue)} · {selected.employees} employees
                </p>
              </div>
              <span className="ml-auto"><StatusPill status={selected.status} /></span>
            </div>

            <div className="space-y-4 p-4">
              <div className="rounded-lg border border-primary/20 bg-primary-soft/30 p-3">
                <p className="flex items-center gap-1.5 text-xs font-semibold text-primary">
                  <Sparkles className="size-3.5" /> AI summary
                </p>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{selected.summary}</p>
              </div>

              <div>
                <p className="mb-2 text-xs font-semibold">Detected signals</p>
                <div className="flex flex-wrap gap-1.5">
                  {selected.signals.map((s) => (
                    <span key={s} className="rounded-md border border-border bg-surface-raised px-2 py-1 text-[11px] text-muted-foreground">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <dl className="space-y-2.5 text-xs">
                <Row icon={<Globe className="size-3.5" />} label="Website" value={selected.website ?? "None found"} />
                <Row icon={<Star className="size-3.5" />} label="Rating" value={`${selected.rating} · ${selected.reviews} reviews`} />
                <Row icon={<Building2 className="size-3.5" />} label="Owner" value={selected.owner} />
                <Row icon={<Mail className="size-3.5" />} label="Email" value={selected.email} />
                <Row icon={<Phone className="size-3.5" />} label="Phone" value={selected.phone} />
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
              <p className="text-center text-[11px] text-muted-foreground">Last activity {selected.lastActivity}</p>
            </div>
          </aside>
        ) : (
          <aside className="panel grid h-64 place-items-center p-6 text-center text-sm text-muted-foreground xl:sticky xl:top-24">
            Select a business to see its intelligence profile.
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
