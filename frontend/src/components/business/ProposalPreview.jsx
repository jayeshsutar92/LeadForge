import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { X, Download, FileText } from "lucide-react";

export default function ProposalPreview({ slug, onClose }) {
    const [proposal, setProposal] = useState(null);

    useEffect(() => {
        api.get(`/api/businesses/${slug}/proposal`).then(({ data }) => setProposal(data));
    }, [slug]);

    return (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-md flex items-start justify-center p-4 sm:p-8 overflow-y-auto" onClick={onClose} data-testid="proposal-overlay">
            <div
                className="relative w-full max-w-3xl bg-card border border-border shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            >
                <button
                    onClick={onClose}
                    data-testid="proposal-close"
                    className="absolute top-4 right-4 w-9 h-9 border border-border hover:border-accent hover:text-accent flex items-center justify-center transition-colors"
                >
                    <X size={16} />
                </button>

                {!proposal ? (
                    <div className="p-16 text-center text-muted-foreground font-mono text-sm">Generating proposal…</div>
                ) : (
                    <div className="p-8 sm:p-12">
                        {/* Header */}
                        <div className="flex items-center justify-between border-b border-border pb-6 mb-8">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-accent flex items-center justify-center text-accent-foreground">
                                    <FileText size={18} />
                                </div>
                                <div>
                                    <div className="label-caps">Proposal / Draft</div>
                                    <div className="font-display text-lg">LeadForge Studio</div>
                                </div>
                            </div>
                            <div className="text-right text-xs text-muted-foreground font-mono">
                                {proposal.date}
                            </div>
                        </div>

                        {/* Prepared for */}
                        <div className="grid grid-cols-2 gap-6 mb-8">
                            <div>
                                <div className="label-caps mb-1">Prepared for</div>
                                <div className="font-display text-2xl" data-testid="proposal-prepared-for">{proposal.prepared_for}</div>
                            </div>
                            <div>
                                <div className="label-caps mb-1">Prepared by</div>
                                <div className="font-display text-2xl">{proposal.prepared_by}</div>
                            </div>
                        </div>

                        {/* Summary */}
                        <div className="mb-8">
                            <div className="label-caps mb-3">Executive summary</div>
                            <p className="text-base leading-relaxed text-foreground/90">{proposal.summary}</p>
                        </div>

                        {/* Deliverables */}
                        <div className="mb-8">
                            <div className="label-caps mb-3">Deliverables</div>
                            <div className="grid grid-cols-2 gap-2">
                                {proposal.deliverables.map((d) => (
                                    <div key={d} className="flex items-center gap-2 text-sm py-2 border-b border-border/50">
                                        <span className="w-1 h-1 rounded-full bg-accent" /> {d}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Details grid */}
                        <div className="grid grid-cols-3 border border-border mb-8">
                            <Cell label="Design theme" value={proposal.theme} />
                            <Cell label="Timeline" value={`${proposal.timeline_weeks} weeks`} />
                            <Cell label="Opportunity" value={`${proposal.score} / 100`} />
                        </div>

                        {/* Price */}
                        <div className="border border-border p-6 flex items-center justify-between">
                            <div>
                                <div className="label-caps mb-1">Investment</div>
                                <div className="font-display text-4xl font-light" data-testid="proposal-price">
                                    ${proposal.price_range.min.toLocaleString()} – ${proposal.price_range.max.toLocaleString()}
                                </div>
                                <div className="text-xs text-muted-foreground mt-1">USD · one-time · scope-dependent</div>
                            </div>
                            <div className="flex gap-2">
                                {proposal.palette.map((c) => (
                                    <div key={c} className="w-10 h-10 border border-border" style={{ backgroundColor: c }} />
                                ))}
                            </div>
                        </div>

                        <div className="mt-8 flex items-center justify-between">
                            <div className="text-xs text-muted-foreground font-mono">Draft — Ready to send</div>
                            <button
                                onClick={() => window.print()}
                                data-testid="proposal-print"
                                className="inline-flex items-center gap-2 border border-border px-4 py-2 text-sm hover:border-accent hover:text-accent transition-colors"
                            >
                                <Download size={14} /> Print / Save PDF
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function Cell({ label, value }) {
    return (
        <div className="p-4 border-r border-border last:border-r-0">
            <div className="label-caps mb-1">{label}</div>
            <div className="font-display text-lg">{value}</div>
        </div>
    );
}
