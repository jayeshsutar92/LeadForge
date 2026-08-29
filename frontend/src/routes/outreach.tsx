import { Link, createFileRoute } from "@tanstack/react-router";
import { Mail, MessageSquare, Plus, Sparkles, Loader2 } from "lucide-react";
import { useMemo } from "react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import {
  useLeads,
  useGenerateOpportunity,
  useGenerateOutreach,
  useUpdateLead,
  type LeadResponse,
  type BusinessCard,
} from "@/lib/api-hooks";
import { useState } from "react";
import { toast } from "sonner";
import { getErrorMessage, apiClient } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const Route = createFileRoute("/outreach")({
  head: () => ({
    meta: [
      { title: "Outreach — LeadForge" },
      {
        name: "description",
        content: "Track sequences, replies, and follow-ups across every lead you contact.",
      },
    ],
  }),
  component: Outreach,
});

function Outreach() {
  const {
    data: leadsData,
    isLoading: leadsLoading,
    isError: leadsError,
  } = useLeads({ limit: 100 });

  const contactedLeads = useMemo(() => {
    if (!leadsData?.results) return [];
    return leadsData.results
      .filter((l) => ["new", "qualified", "contacted", "negotiating"].includes(l.status))
      .map((lead) => {
        return { lead, biz: lead.business };
      })
      .filter((x) => x.biz)
      .sort((a, b) => {
        const tA = a.lead.updated_at ? new Date(a.lead.updated_at).getTime() : 0;
        const tB = b.lead.updated_at ? new Date(b.lead.updated_at).getTime() : 0;
        return tB - tA;
      });
  }, [leadsData]);

  const activeCount = contactedLeads.length;

  return (
    <AppShell
      title="Outreach"
      description={`${activeCount} leads actively in pipeline`}
      actions={
        <Button asChild>
          <Link to="/leads">
            <Plus className="size-4" />
            Start campaign
          </Link>
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Active conversations"
            value={activeCount.toString()}
            icon={<MessageSquare className="size-4" />}
          />
          <StatCard label="Response rate" value="--" hint="Need more data" />
          <StatCard
            label="Qualified"
            value={
              leadsData?.results.filter((l) => l.status === "qualified").length.toString() || "0"
            }
          />
          <StatCard
            label="Total leads"
            value={leadsData?.total?.toString() || "0"}
            icon={<Mail className="size-4" />}
          />
        </section>

        <section className="panel p-5">
          <SectionHeader
            title="Active Outreach"
            action={<span className="text-xs text-muted-foreground">{activeCount} leads</span>}
          />
          {leadsError ? (
            <div className="flex h-48 items-center justify-center text-sm text-destructive">
              Failed to load outreach data.
            </div>
          ) : leadsLoading ? (
            <div className="flex h-48 items-center justify-center">
              <Loader2 className="size-6 animate-spin text-muted-foreground" />
            </div>
          ) : contactedLeads.length === 0 ? (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              No active outreach at the moment.
            </div>
          ) : (
            <ul className="mt-4 space-y-3">
              {contactedLeads.map(({ lead, biz }) => (
                <OutreachCard key={lead.id} lead={lead} biz={biz as BusinessCard | undefined} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </AppShell>
  );
}

function OutreachCard({ lead, biz }: { lead: LeadResponse; biz: BusinessCard | undefined }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const queryClient = useQueryClient();

  const [outreachText, setOutreachText] = useState<Record<string, unknown> | null>(null);
  const [strategy, setStrategy] = useState("helpful_observation");
  const [channel, setChannel] = useState("instagram");

  const generateOpp = useGenerateOpportunity();
  const generateOutreach = useGenerateOutreach();
  const updateLead = useUpdateLead();

  const handleGenerate = async () => {
    if (!biz?.slug) return;
    try {
      setIsGenerating(true);

      const biData = await queryClient.fetchQuery({
        queryKey: ["businesses", biz.slug, "intelligence"],
        queryFn: async () =>
          (await apiClient.get(`/businesses/${biz.slug}/intelligence/latest`)).data,
      });

      if (!biData?.id) {
        throw new Error("Could not load business intelligence data.");
      }

      let currentOppId = null;
      try {
        const oppData = await queryClient.fetchQuery({
          queryKey: ["businesses", biz.slug, "opportunity", biData.id],
          queryFn: async () =>
            (await apiClient.get(`/businesses/${biz.slug}/intelligence/${biData.id}/opportunity`))
              .data,
        });
        currentOppId = oppData?.id;
      } catch {
        // Might 404
      }
      if (!currentOppId) {
        const newOpp = await generateOpp.mutateAsync({ slug: biz.slug, biId: biData.id });
        currentOppId = newOpp.id;
      }
      if (currentOppId) {
        const data = await generateOutreach.mutateAsync({
          slug: biz.slug,
          opportunityId: currentOppId,
          strategy,
          channel,
        });
        setOutreachText(data.message || data);
        toast.success("Outreach drafted successfully");
        if (lead.status === "new" || lead.status === "qualified") {
          await updateLead.mutateAsync({ id: lead.id, data: { status: "contacted" } });
        }
      }
    } catch (err: unknown) {
      toast.error(getErrorMessage(err) || "Failed to draft outreach. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <li className="rounded-lg border border-border bg-surface-raised p-4 transition-colors hover:border-border-strong">
      <div className="flex items-center justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">{biz?.name || "Unknown"}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Status: <span className="uppercase text-primary">{lead.status}</span>
          </p>
        </div>
        <span className="shrink-0 text-[11px] text-muted-foreground">
          Updated {lead.updated_at ? new Date(lead.updated_at).toLocaleDateString() : "N/A"}
        </span>
      </div>

      {outreachText && typeof outreachText === "string" && (
        <div className="mt-3 rounded-md bg-muted/30 p-3 text-xs text-foreground whitespace-pre-wrap border border-border">
          {outreachText}
        </div>
      )}

      <div className="mt-3 space-y-3 border-t border-border/50 pt-3">
        <div className="flex gap-2">
          <Select value={strategy} onValueChange={setStrategy}>
            <SelectTrigger className="h-7 text-xs w-[180px]">
              <SelectValue placeholder="Strategy" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="helpful_observation">Helpful Observation</SelectItem>
              <SelectItem value="business_growth">Business Growth</SelectItem>
              <SelectItem value="website_improvement">Website Improvement</SelectItem>
              <SelectItem value="problem_solver">Problem Solver</SelectItem>
              <SelectItem value="founder_to_business">Founder-to-Business</SelectItem>
            </SelectContent>
          </Select>

          <Select value={channel} onValueChange={setChannel}>
            <SelectTrigger className="h-7 text-xs w-[130px]">
              <SelectValue placeholder="Channel" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="instagram">Instagram DM</SelectItem>
              <SelectItem value="facebook">Facebook Message</SelectItem>
              <SelectItem value="whatsapp">WhatsApp</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground line-clamp-1 flex-1 mr-3">
            {lead.notes || "No notes available."}
          </p>
          <Button
            variant={outreachText ? "outline" : "default"}
            size="sm"
            className="h-7 text-xs shrink-0"
            onClick={handleGenerate}
            disabled={isGenerating || !biz?.slug}
          >
            {isGenerating ? (
              <Loader2 className="size-3 mr-1 animate-spin" />
            ) : (
              <Mail className="size-3 mr-1" />
            )}
            {isGenerating ? "Drafting..." : outreachText ? "Re-draft" : "Draft Outreach"}
          </Button>
        </div>
      </div>
    </li>
  );
}
