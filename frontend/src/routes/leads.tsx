import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
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
  Copy,
  Check,
  Radar,
  Trash2,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
  MapPin,
  ExternalLink,
} from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { ScoreBadge, StatusPill, WebsiteTag } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatCurrency, statusMeta, type LeadStatus } from "@/lib/ui-utils";
import { cn } from "@/lib/utils";
import {
  useLeads,
  useLeadDetail,
  useBusinessDetail,
  useUpdateLead,
  useDeleteLead,
  useSocialIntelligence,
  useContactDiscovery,
  useGenerateContactDiscovery,
  useGenerateContactDiscoveryOutreach,
  type ContactDiscoveryCandidate,
} from "@/lib/api-hooks";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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

function PlatformIcon({ platform, className }: { platform: string; className?: string }) {
  switch (platform.toLowerCase()) {
    case "facebook":
      return <Facebook className={className} />;
    case "instagram":
      return <Instagram className={className} />;
    case "linkedin":
      return <Linkedin className={className} />;
    case "x":
    case "twitter":
      return <Twitter className={className} />;
    case "google_maps":
      return <MapPin className={className} />;
    default:
      return <Globe className={className} />;
  }
}

function ContactCandidateCard({
  candidate,
  isRecommended,
}: {
  candidate: ContactDiscoveryCandidate;
  isRecommended: boolean;
}) {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedUser, setCopiedUser] = useState(false);

  const copyToClipboard = (text: string, type: "url" | "user") => {
    navigator.clipboard.writeText(text);
    if (type === "url") {
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2000);
    } else {
      setCopiedUser(true);
      setTimeout(() => setCopiedUser(false), 2000);
    }
  };

  return (
    <div className="flex flex-col gap-2 rounded-md border border-border bg-card p-3 shadow-sm relative">
      {isRecommended && (
        <div className="absolute -top-2 -right-2 bg-primary text-primary-foreground text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm flex items-center gap-1">
          <Star className="size-3" fill="currentColor" /> Recommended
        </div>
      )}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="bg-primary/10 text-primary p-1.5 rounded-md">
            <PlatformIcon platform={candidate.platform} className="size-4" />
          </div>
          <div className="min-w-0">
            <span className="font-semibold text-sm capitalize leading-none truncate block">
              {candidate.platform.replace("_", " ")}
            </span>
            <p
              className="text-[10px] text-muted-foreground mt-0.5 font-medium line-clamp-1 break-all"
              title={candidate.display_name || candidate.title}
            >
              {candidate.display_name || candidate.title}
            </p>
          </div>
        </div>
        <span
          className={cn(
            "text-[10px] font-semibold px-1.5 py-0.5 rounded whitespace-nowrap",
            candidate.confidence >= 70
              ? "bg-success/10 text-success"
              : candidate.confidence >= 40
                ? "bg-warning/10 text-warning"
                : "bg-muted text-muted-foreground",
          )}
        >
          {candidate.status} ({candidate.confidence}%)
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-muted-foreground">
        <div className="flex items-center gap-1 flex-1 min-w-[100px]">
          <span className="font-medium truncate text-foreground">
            {candidate.username ? `@${candidate.username}` : "Unknown User"}
          </span>
          {candidate.username && (
            <button
              onClick={() => copyToClipboard(candidate.username!, "user")}
              className="hover:text-foreground hover:bg-muted p-1 rounded transition-colors"
              title="Copy Username"
            >
              {copiedUser ? <Check className="size-3 text-success" /> : <Copy className="size-3" />}
            </button>
          )}
        </div>

        <div className="flex items-center gap-1 flex-1 min-w-[100px] justify-end">
          <a
            href={candidate.href}
            target="_blank"
            rel="noreferrer"
            className="hover:underline truncate text-primary inline-flex items-center gap-1 max-w-[120px]"
          >
            Open Profile <ExternalLink className="size-3 shrink-0" />
          </a>
          <button
            onClick={() => copyToClipboard(candidate.href, "url")}
            className="hover:text-foreground hover:bg-muted p-1 rounded transition-colors"
            title="Copy URL"
          >
            {copiedUrl ? <Check className="size-3 text-success" /> : <Copy className="size-3" />}
          </button>
        </div>
      </div>

      {candidate.evidence && candidate.evidence.length > 0 && (
        <details className="mt-2 group">
          <summary className="text-[10px] uppercase text-muted-foreground font-semibold cursor-pointer select-none flex items-center gap-1 hover:text-foreground transition-colors">
            <span className="group-open:rotate-90 transition-transform text-[8px]">▶</span>
            Verification Evidence
          </summary>
          <div className="mt-1.5 flex flex-col gap-1 pl-3 border-l-2 border-border ml-1 py-1">
            {candidate.evidence.map((ev, idx) => (
              <span
                key={idx}
                className="text-[10px] text-muted-foreground flex items-center gap-1.5"
              >
                <Check className="size-3 text-success" /> {ev}
              </span>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

function LeadsPage() {
  const [filter, setFilter] = useState<LeadStatus | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const navigate = useNavigate();
  const updateLead = useUpdateLead();
  const deleteLead = useDeleteLead();

  const {
    data: leadsData,
    isLoading: leadsLoading,
    isError: leadsError,
  } = useLeads({ limit: 100 });

  const { data: selectedLeadDetail, isLoading: leadDetailLoading } = useLeadDetail(selectedLeadId);
  const { data: selectedBizDetail, isLoading: bizDetailLoading } = useBusinessDetail(
    selectedLeadDetail?.business?.slug || null,
  );

  const selectedBiz = selectedLeadDetail?.business || null;
  const { data: socialIntel, isLoading: socialIntelLoading } = useSocialIntelligence(
    !selectedBiz?.website ? selectedBiz?.id : undefined,
  );
  const { data: contactDiscovery, isLoading: contactDiscoveryLoading } = useContactDiscovery(
    !selectedBiz?.website ? selectedBiz?.slug : undefined,
  );
  const generateContactDiscovery = useGenerateContactDiscovery();
  const generateContactOutreach = useGenerateContactDiscoveryOutreach();

  const handleGenerateContactDiscovery = async () => {
    if (!selectedBiz?.slug) return;
    try {
      await generateContactDiscovery.mutateAsync({ slug: selectedBiz.slug, force: true });
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateContactOutreach = async () => {
    if (!selectedBiz?.slug) return;
    try {
      await generateContactOutreach.mutateAsync({ slug: selectedBiz.slug, force: true });
    } catch (e) {
      console.error(e);
    }
  };

  const rows = useMemo(() => {
    if (!leadsData?.results) return [];

    return leadsData.results
      .map((lead) => ({
        ...lead,
        business: lead.business || {
          id: lead.business_id,
          slug: "",
          name: "Unknown Business",
          category: "N/A",
          city: "N/A",
          country: "N/A",
          bio: "",
          followers: 0,
          engagement_rate: 0,
          website: "",
          instagram: undefined,
          facebook: undefined,
          cover_image: "",
          opportunity_score: 0,
          tier: "none",
          verified: false,
          created_at: "",
        },
      }))
      .filter((l) => {
        const matchesFilter = filter === "all" || l.status === filter;
        const searchLower = query.toLowerCase();
        const matchesQuery =
          l.business.name.toLowerCase().includes(searchLower) ||
          l.business.category.toLowerCase().includes(searchLower) ||
          l.business.city.toLowerCase().includes(searchLower);
        return matchesFilter && matchesQuery;
      });
  }, [leadsData, filter, query]);

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
        <Button asChild>
          <Link to="/discover">
            <Plus className="size-4" />
            Add lead
          </Link>
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
                {leadsLoading ? (
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
                        <WebsiteTag state={lead.business.website ? "modern" : "none"} />
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
                  <div className="flex shrink-0 items-center gap-1.5 ml-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label="Delete lead"
                      className="size-8 shrink-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                      onClick={() => {
                        if (
                          selectedLeadDetail?.id &&
                          window.confirm("Are you sure you want to delete this lead?")
                        ) {
                          deleteLead.mutate(selectedLeadDetail.id, {
                            onSuccess: () => {
                              setSelectedLeadId(null);
                            },
                          });
                        }
                      }}
                      disabled={deleteLead.isPending}
                    >
                      <Trash2 className="size-4" />
                    </Button>
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
                    <Select
                      value={selectedLeadDetail?.status || "new"}
                      onValueChange={(value) => {
                        if (selectedLeadDetail?.id) {
                          updateLead.mutate({ id: selectedLeadDetail.id, data: { status: value } });
                        }
                      }}
                      disabled={updateLead.isPending}
                    >
                      <SelectTrigger className="h-7 text-xs w-[120px]">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="new">New</SelectItem>
                        <SelectItem value="qualified">Qualified</SelectItem>
                        <SelectItem value="contacted">Contacted</SelectItem>
                        <SelectItem value="negotiating">Negotiating</SelectItem>
                        <SelectItem value="won">Won</SelectItem>
                        <SelectItem value="lost">Lost</SelectItem>
                      </SelectContent>
                    </Select>
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

                  {!selectedBiz?.website && (
                    <>
                      <div className="mt-4 border-t border-border pt-4">
                        <div className="flex items-center justify-between">
                          <p className="flex items-center gap-1.5 text-xs font-semibold">
                            <Search className="size-3.5 text-primary" /> Contact Discovery
                          </p>
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-6 text-[10px]"
                            onClick={handleGenerateContactDiscovery}
                            disabled={generateContactDiscovery.isPending || contactDiscoveryLoading}
                          >
                            {generateContactDiscovery.isPending ? (
                              <Loader2 className="size-3 animate-spin mr-1" />
                            ) : null}
                            {contactDiscovery?.data ? "Re-discover" : "Discover Contacts"}
                          </Button>
                        </div>

                        {generateContactDiscovery.isError && (
                          <div className="mt-2 text-xs text-destructive bg-destructive/10 p-2 rounded">
                            Failed to discover contacts. Please try again.
                          </div>
                        )}

                        {contactDiscoveryLoading ? (
                          <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                            <Loader2 className="size-3 animate-spin" /> Searching public profiles...
                          </div>
                        ) : contactDiscovery?.data ? (
                          <div className="mt-3 space-y-4">
                            {(() => {
                              const verified = contactDiscovery.data.candidates.filter(
                                (c) => c.confidence >= 70,
                              );
                              const possible = contactDiscovery.data.candidates.filter(
                                (c) => c.confidence < 70,
                              );

                              if (verified.length === 0 && possible.length === 0) {
                                return (
                                  <p className="text-xs text-muted-foreground italic text-center py-4">
                                    No public contact profiles found for this business.
                                  </p>
                                );
                              }

                              return (
                                <>
                                  {verified.length > 0 && (
                                    <div className="space-y-2">
                                      <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                        Verified Profiles
                                      </p>
                                      {verified.map((p, i) => (
                                        <ContactCandidateCard
                                          key={i}
                                          candidate={p}
                                          isRecommended={
                                            p.platform ===
                                            contactDiscovery.data.recommended_platform
                                          }
                                        />
                                      ))}
                                    </div>
                                  )}

                                  {possible.length > 0 && (
                                    <div className="space-y-2">
                                      <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                        Possible Matches
                                      </p>
                                      {possible.map((p, i) => (
                                        <ContactCandidateCard
                                          key={i}
                                          candidate={p}
                                          isRecommended={false}
                                        />
                                      ))}
                                    </div>
                                  )}

                                  {/* AI Outreach Section */}
                                  <div className="mt-4 pt-4 border-t border-border/50">
                                    <div className="flex items-center justify-between mb-3">
                                      <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                        AI Outreach Message
                                      </p>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        className="h-6 text-[10px]"
                                        onClick={handleGenerateContactOutreach}
                                        disabled={
                                          generateContactOutreach.isPending ||
                                          contactDiscoveryLoading
                                        }
                                      >
                                        {generateContactOutreach.isPending ? (
                                          <Loader2 className="size-3 animate-spin mr-1" />
                                        ) : null}
                                        {contactDiscovery.data.messages &&
                                        Object.keys(contactDiscovery.data.messages).length > 0
                                          ? "Regenerate Message"
                                          : "Generate Message"}
                                      </Button>
                                    </div>

                                    {generateContactOutreach.isError && (
                                      <div className="mb-2 text-xs text-destructive bg-destructive/10 p-2 rounded">
                                        Failed to generate outreach messages. Please try again.
                                      </div>
                                    )}

                                    {contactDiscovery.data.messages &&
                                    Object.keys(contactDiscovery.data.messages).length > 0 ? (
                                      <div className="space-y-2">
                                        {Object.entries(contactDiscovery.data.messages).map(
                                          ([platform, msg], i) => (
                                            <MessageCopyCard
                                              key={i}
                                              platform={platform}
                                              message={msg as string}
                                            />
                                          ),
                                        )}
                                      </div>
                                    ) : (
                                      <p className="text-[11px] text-muted-foreground text-center py-2 italic bg-secondary/20 rounded">
                                        {generateContactOutreach.isPending
                                          ? "Generating tailored outreach messages..."
                                          : "Click Generate to create tailored outreach messages."}
                                      </p>
                                    )}
                                  </div>
                                </>
                              );
                            })()}
                          </div>
                        ) : null}
                      </div>

                      <div className="mt-4 border-t border-border pt-4">
                        <p className="flex items-center gap-1.5 text-xs font-semibold">
                          <Radar className="size-3.5 text-primary" /> Social Intelligence
                        </p>

                        {socialIntelLoading ? (
                          <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                            <Loader2 className="size-3 animate-spin" /> Scanning social presence...
                          </div>
                        ) : socialIntel?.data ? (
                          <div className="mt-3 space-y-3">
                            {socialIntel.data.profiles?.length > 0 ? (
                              <div className="space-y-4">
                                {socialIntel.data.profiles.filter(p => p.status === "Verified" || p.confidence >= 65).length > 0 && (
                                  <div className="space-y-2">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Verified Profiles</p>
                                    {socialIntel.data.profiles.filter(p => p.status === "Verified" || p.confidence >= 65).map((p, i) => (
                                      <div
                                        key={i}
                                        className="flex flex-col gap-1.5 rounded bg-secondary/30 p-2 text-xs border border-success/20"
                                      >
                                        <div className="flex items-center justify-between">
                                          <span className="font-medium capitalize text-foreground">{p.platform}</span>
                                          <span className="text-success font-medium">Verified ({p.confidence}%)</span>
                                        </div>
                                        {p.url && p.url !== "#" ? (
                                          <a
                                            href={p.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-primary hover:underline truncate"
                                          >
                                            @{p.username || "Profile"}
                                          </a>
                                        ) : (
                                          <span className="text-muted-foreground truncate">
                                            @{p.username || "Unknown ID"}
                                          </span>
                                        )}
                                        {p.evidence && p.evidence.length > 0 && (
                                          <div className="mt-1 pt-1 border-t border-border/50">
                                            <p className="text-[10px] font-medium text-muted-foreground mb-1">Verification Evidence:</p>
                                            <div className="flex flex-wrap gap-1">
                                              {p.evidence.map((ev, idx) => (
                                                <span key={idx} className="bg-primary/10 text-primary text-[9px] px-1.5 py-0.5 rounded">
                                                  {ev}
                                                </span>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}
                                
                                {socialIntel.data.profiles.filter(p => p.status !== "Verified" && p.confidence < 65).length > 0 && (
                                  <div className="space-y-2">
                                    <p className="text-[10px] uppercase text-muted-foreground font-semibold">Possible Matches</p>
                                    {socialIntel.data.profiles.filter(p => p.status !== "Verified" && p.confidence < 65).map((p, i) => (
                                      <div
                                        key={i}
                                        className="flex flex-col gap-1.5 rounded bg-secondary/20 p-2 text-xs opacity-75"
                                      >
                                        <div className="flex items-center justify-between">
                                          <span className="font-medium capitalize text-muted-foreground">{p.platform}</span>
                                          <span className="text-warning">Possible Match ({p.confidence}%)</span>
                                        </div>
                                        {p.url && p.url !== "#" ? (
                                          <a
                                            href={p.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-muted-foreground hover:underline truncate"
                                          >
                                            @{p.username || "Profile"}
                                          </a>
                                        ) : (
                                          <span className="text-muted-foreground truncate">
                                            @{p.username || "Unknown ID"}
                                          </span>
                                        )}
                                        {p.evidence && p.evidence.length > 0 && (
                                          <div className="mt-1 flex flex-wrap gap-1">
                                            {p.evidence.map((ev, idx) => (
                                              <span key={idx} className="bg-secondary text-muted-foreground text-[9px] px-1.5 py-0.5 rounded">
                                                {ev}
                                              </span>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <p className="text-xs text-muted-foreground italic">
                                No public profiles found.
                              </p>
                            )}

                            {socialIntel.data.recommended_platform ? (
                              <div className="rounded border border-primary/20 bg-primary/5 p-2">
                                <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                  Recommended Channel
                                </p>
                                <p className="text-xs font-medium capitalize mt-0.5">
                                  {socialIntel.data.recommended_platform}
                                </p>
                              </div>
                            ) : (
                              <div className="rounded border border-border/50 bg-secondary/10 p-2">
                                <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                  Recommended Channel
                                </p>
                                <p className="text-xs font-medium text-muted-foreground mt-0.5 italic">
                                  No Verified Profile
                                </p>
                              </div>
                            )}

                            {socialIntel.data.messages &&
                              Object.entries(socialIntel.data.messages).length > 0 && (
                                <div className="space-y-2">
                                  <p className="text-[10px] uppercase text-muted-foreground font-semibold">
                                    Generated Outreach
                                  </p>
                                  {Object.entries(socialIntel.data.messages).map(
                                    ([platform, msg], i) => (
                                      <MessageCopyCard
                                        key={i}
                                        platform={platform}
                                        message={msg as string}
                                      />
                                    ),
                                  )}
                                </div>
                              )}
                          </div>
                        ) : (
                          <p className="mt-2 text-xs text-muted-foreground">
                            Waiting for analysis...
                          </p>
                        )}
                      </div>
                    </>
                  )}

                  <div className="flex gap-2">
                    <Button className="flex-1" onClick={() => navigate({ to: "/proposals" })}>
                      <Sparkles className="size-4" />
                      Draft proposal
                    </Button>
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => navigate({ to: "/outreach" })}
                    >
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

function MessageCopyCard({ platform, message }: { platform: string; message: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group rounded bg-card border border-border p-3">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-bold capitalize text-primary">{platform}</span>
        <button
          onClick={handleCopy}
          className="text-muted-foreground hover:text-foreground transition-colors"
          title="Copy message"
        >
          {copied ? <Check className="size-3 text-success" /> : <Copy className="size-3" />}
        </button>
      </div>
      <p className="text-[11px] leading-relaxed text-muted-foreground line-clamp-4 group-hover:line-clamp-none transition-all">
        {message}
      </p>
    </div>
  );
}
