import { createFileRoute, Link } from "@tanstack/react-router";
import { FileText, Sparkles, Loader2 } from "lucide-react";
import { useMemo } from "react";
import { toast } from "sonner";

import { AppShell } from "@/components/app-shell";
import { StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { formatCurrency } from "@/lib/ui-utils";
import { cn } from "@/lib/utils";
import {
  useLeads,
  useBusinesses,
  useIntelligence,
  useOpportunity,
  useGenerateOpportunity,
  useProposal,
  useGenerateProposal,
} from "@/lib/api-hooks";

export const Route = createFileRoute("/proposals")({
  head: () => ({
    meta: [
      { title: "Proposals — LeadForge" },
      {
        name: "description",
        content:
          "AI-drafted proposals tailored to each business opportunity, from draft to accepted.",
      },
    ],
  }),
  component: Proposals,
});

const statusTone: Record<string, string> = {
  qualified: "bg-muted text-muted-foreground border-border",
  contacted: "bg-info/15 text-info border-info/25",
  negotiating: "bg-warning/15 text-warning border-warning/25",
  won: "bg-success/15 text-success border-success/25",
};

function Proposals() {
  const {
    data: leadsData,
    isLoading: leadsLoading,
    isError: leadsError,
  } = useLeads({ limit: 100 });
  const { data: businessesData, isLoading: bizLoading } = useBusinesses({ limit: 100 });

  const activeProposals = useMemo(() => {
    if (!leadsData?.results || !businessesData?.results) return [];
    return leadsData.results
      .filter((l) => ["new", "qualified", "contacted", "negotiating", "won"].includes(l.status))
      .map((lead) => {
        const biz = businessesData.results.find((b) => b.id === lead.business_id);
        return { lead, biz };
      })
      .filter((x) => x.biz)
      .sort((a, b) => {
        const tA = a.lead.updated_at ? new Date(a.lead.updated_at).getTime() : 0;
        const tB = b.lead.updated_at ? new Date(b.lead.updated_at).getTime() : 0;
        return tB - tA;
      });
  }, [leadsData, businessesData]);

  const activeCount = activeProposals.length;
  // Estimate value as opportunity score * 120 (same logic as in Leads)
  const totalValue = activeProposals.reduce(
    (sum, item) => sum + (item.biz?.opportunity_score || 70) * 120,
    0,
  );

  return (
    <AppShell
      title="Proposals"
      description={`${activeCount} active opportunities · ${formatCurrency(totalValue)} in play`}
      actions={
        <Button asChild>
          <Link to="/leads">
            <Sparkles className="size-4" />
            Generate proposal
          </Link>
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Proposals active"
            value={activeCount.toString()}
            icon={<FileText className="size-4" />}
          />
          <StatCard label="Win rate" value="--" hint="Need more data" />
          <StatCard label="Pipeline value" value={formatCurrency(totalValue)} />
          <StatCard label="Avg. draft time" value="42s" hint="AI generated" />
        </section>

        {leadsError ? (
          <div className="flex h-48 items-center justify-center text-sm text-destructive">
            Failed to load proposals data.
          </div>
        ) : leadsLoading || bizLoading ? (
          <div className="flex h-48 items-center justify-center">
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
          </div>
        ) : activeProposals.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
            No active proposals found.
          </div>
        ) : (
          <section className="grid gap-3 md:grid-cols-2">
            {activeProposals.map(({ lead, biz }) => (
              <ProposalCard key={lead.id} lead={lead} biz={biz} />
            ))}
          </section>
        )}
      </div>
    </AppShell>
  );
}

function ProposalCard({
  lead,
  biz,
}: {
  lead: Record<string, unknown>;
  biz: Record<string, unknown>;
}) {
  const { data: bi } = useIntelligence(biz?.slug || null);
  const { data: opp } = useOpportunity(biz?.slug || null, bi?.id || null);
  const { data: proposal, isLoading: proposalLoading } = useProposal(
    biz?.slug || null,
    opp?.id || null,
  );

  const generateOpp = useGenerateOpportunity();
  const generateProp = useGenerateProposal();

  const isGenerating = generateOpp.isPending || generateProp.isPending || proposalLoading;

  const handleGenerate = async () => {
    if (!biz?.slug || !bi?.id) return;
    try {
      let currentOppId = opp?.id;
      if (!currentOppId) {
        const newOpp = await generateOpp.mutateAsync({ slug: biz.slug, biId: bi.id });
        currentOppId = newOpp.id;
      }
      if (currentOppId) {
        await generateProp.mutateAsync({ slug: biz.slug, opportunityId: currentOppId });
        toast.success("Proposal generated successfully");
      }
    } catch (err: unknown) {
      toast.error(
        err.response?.data?.detail?.message ||
          err.response?.data?.error?.message ||
          "Failed to generate proposal. Please try again.",
      );
    }
  };

  const estimatedValue = (biz.opportunity_score || 70) * 120;

  return (
    <article className="panel flex flex-col p-5 transition-colors hover:border-border-strong">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs text-muted-foreground">
            Lead ID: {lead.id.substring(0, 8)}
          </p>
          <h2 className="mt-0.5 truncate text-base font-semibold">{biz.name}</h2>
        </div>
        <span
          className={cn(
            "shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-medium uppercase",
            statusTone[lead.status] ?? statusTone["qualified"],
          )}
        >
          {lead.status}
        </span>
      </div>

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-muted-foreground">
        <Sparkles className="size-3 text-primary" /> Generated by AI · updated{" "}
        {proposal?.updated_at || lead.updated_at
          ? new Date(proposal?.updated_at || lead.updated_at).toLocaleDateString()
          : "N/A"}
      </p>

      {proposal?.content && (
        <div className="mt-4 rounded-md bg-muted/30 p-3 text-xs text-muted-foreground line-clamp-3">
          {proposal.content.executive_summary || proposal.content.title || "Proposal generated"}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between border-t border-border pt-4 mt-auto">
        <p className="text-numeric text-lg font-semibold">{formatCurrency(estimatedValue)}</p>
        <div className="flex gap-2">
          {proposal ? (
            <>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm">
                    Preview
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>{proposal.content.title || "Proposal Preview"}</DialogTitle>
                  </DialogHeader>
                  <div className="mt-4 space-y-4 text-sm">
                    {proposal.content.executive_summary && (
                      <div>
                        <div className="font-semibold text-base mb-1">Executive Summary</div>
                        <div className="whitespace-pre-wrap text-muted-foreground">
                          {proposal.content.executive_summary}
                        </div>
                      </div>
                    )}

                    {proposal.content.sections &&
                      Array.isArray(proposal.content.sections) &&
                      proposal.content.sections.map((sec: Record<string, unknown>, idx: number) => (
                        <div key={idx}>
                          <div className="font-semibold text-base mb-1">
                            {sec.heading || sec.title || `Section ${idx + 1}`}
                          </div>
                          <div className="whitespace-pre-wrap text-muted-foreground">
                            {sec.content || sec.body}
                          </div>
                        </div>
                      ))}

                    {proposal.content.pricing && (
                      <div>
                        <div className="font-semibold text-base mb-1">Pricing & Investment</div>
                        <div className="whitespace-pre-wrap text-muted-foreground">
                          {typeof proposal.content.pricing === "string"
                            ? proposal.content.pricing
                            : JSON.stringify(proposal.content.pricing, null, 2)}
                        </div>
                      </div>
                    )}

                    {proposal.content.next_steps && (
                      <div>
                        <div className="font-semibold text-base mb-1">Next Steps</div>
                        <div className="whitespace-pre-wrap text-muted-foreground">
                          {typeof proposal.content.next_steps === "string"
                            ? proposal.content.next_steps
                            : JSON.stringify(proposal.content.next_steps, null, 2)}
                        </div>
                      </div>
                    )}

                    {/* Fallback for other arbitrary structure */}
                    {!proposal.content.sections && !proposal.content.executive_summary && (
                      <pre className="whitespace-pre-wrap text-xs text-muted-foreground bg-muted p-4 rounded-md">
                        {JSON.stringify(proposal.content, null, 2)}
                      </pre>
                    )}
                  </div>
                </DialogContent>
              </Dialog>
            </>
          ) : (
            <Button size="sm" onClick={handleGenerate} disabled={isGenerating || !bi?.id}>
              {isGenerating ? (
                <Loader2 className="size-3.5 mr-1.5 animate-spin" />
              ) : (
                <Sparkles className="size-3.5 mr-1.5" />
              )}
              {isGenerating ? "Generating..." : "Generate Proposal"}
            </Button>
          )}
        </div>
      </div>
    </article>
  );
}
