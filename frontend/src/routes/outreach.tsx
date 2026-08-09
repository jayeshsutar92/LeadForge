import { createFileRoute } from "@tanstack/react-router";
import { Mail, MessageSquare, Plus, Sparkles, Loader2 } from "lucide-react";
import { useMemo } from "react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { useLeads, useBusinesses, useIntelligence, useOpportunity, useGenerateOpportunity, useGenerateOutreach } from "@/lib/api-hooks";
import { useState } from "react";
import { toast } from "sonner";

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
  const { data: leadsData, isLoading: leadsLoading, isError: leadsError } = useLeads({ limit: 100 });
  const { data: businessesData, isLoading: bizLoading } = useBusinesses({ limit: 100 });

  const contactedLeads = useMemo(() => {
    if (!leadsData?.results || !businessesData?.results) return [];
    return leadsData.results.filter(
      (l) => l.status === "contacted" || l.status === "negotiating" || l.status === "qualified"
    ).map(lead => {
      const biz = businessesData.results.find(b => b.id === lead.business_id);
      return { lead, biz };
    }).filter(x => x.biz).sort((a, b) => new Date(b.lead.updated_at).getTime() - new Date(a.lead.updated_at).getTime());
  }, [leadsData, businessesData]);

  const activeCount = contactedLeads.length;

  return (
    <AppShell
      title="Outreach"
      description={`${activeCount} leads actively in pipeline`}
      actions={
        <Button>
          <Plus className="size-4" />
          Start campaign
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
          <StatCard label="Qualified" value={leadsData?.results.filter(l => l.status === "qualified").length.toString() || "0"} />
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
          ) : leadsLoading || bizLoading ? (
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
                <OutreachCard key={lead.id} lead={lead} biz={biz} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </AppShell>
  );
}

function OutreachCard({ lead, biz }: { lead: any; biz: any }) {
  const { data: bi } = useIntelligence(biz?.slug || null);
  const { data: opp } = useOpportunity(biz?.slug || null, bi?.id || null);
  
  const [outreachText, setOutreachText] = useState<any | null>(null);
  
  const generateOpp = useGenerateOpportunity();
  const generateOutreach = useGenerateOutreach();
  
  const isGenerating = generateOpp.isPending || generateOutreach.isPending;
  
  const handleGenerate = async () => {
    if (!biz?.slug || !bi?.id) return;
    try {
      let currentOppId = opp?.id;
      if (!currentOppId) {
        const newOpp = await generateOpp.mutateAsync({ slug: biz.slug, biId: bi.id });
        currentOppId = newOpp.id;
      }
      if (currentOppId) {
        const data = await generateOutreach.mutateAsync({ slug: biz.slug, opportunityId: currentOppId });
        setOutreachText(data);
        toast.success("Outreach drafted successfully");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.message || err.response?.data?.error?.message || "Failed to draft outreach. Please try again.");
    }
  };

  return (
    <li className="rounded-lg border border-border bg-surface-raised p-4 transition-colors hover:border-border-strong">
      <div className="flex items-center justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">{biz.name}</p>
          <p className="mt-1 text-xs text-muted-foreground">Status: <span className="uppercase text-primary">{lead.status}</span></p>
        </div>
        <span className="shrink-0 text-[11px] text-muted-foreground">
          Updated {new Date(lead.updated_at).toLocaleDateString()}
        </span>
      </div>
      
      {outreachText && typeof outreachText === 'object' && (
        <div className="mt-3 rounded-md bg-muted/30 p-3 text-xs text-foreground whitespace-pre-wrap space-y-3 border border-border">
          <div>
            <span className="font-semibold text-primary">Subject Ideas:</span>
            <ul className="list-disc pl-4 mt-1">
              {outreachText.subject_lines?.slice(0, 2).map((s: string, i: number) => <li key={i}>{s}</li>)}
            </ul>
          </div>
          <div>
            <span className="font-semibold text-primary">Personalized Opener:</span>
            <p className="mt-1 italic">{outreachText.personalized_opener}</p>
          </div>
          <div>
            <span className="font-semibold text-primary">Draft (Value Driven):</span>
            <p className="mt-1 bg-background p-2 rounded border border-border">{outreachText.templates?.value_driven}</p>
          </div>
        </div>
      )}
      {outreachText && typeof outreachText === 'string' && (
        <div className="mt-3 rounded-md bg-muted/30 p-3 text-xs text-foreground whitespace-pre-wrap">
          {outreachText}
        </div>
      )}
      
      <div className="mt-3 flex items-center justify-between border-t border-border/50 pt-3">
        <p className="text-xs text-muted-foreground line-clamp-1 flex-1 mr-3">
          {lead.notes || "No notes available."}
        </p>
        <Button 
          variant={outreachText ? "outline" : "default"} 
          size="sm" 
          className="h-7 text-xs shrink-0"
          onClick={handleGenerate}
          disabled={isGenerating || !bi?.id}
        >
          {isGenerating ? <Loader2 className="size-3 mr-1 animate-spin" /> : <Mail className="size-3 mr-1" />}
          {isGenerating ? "Drafting..." : outreachText ? "Re-draft" : "Draft Outreach"}
        </Button>
      </div>
    </li>
  );
}
