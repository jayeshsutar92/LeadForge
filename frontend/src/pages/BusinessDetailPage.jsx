import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { ArrowLeft, Instagram, Facebook, Globe, Phone, MapPin, CheckCircle2, XCircle, FileText, ShoppingBag } from "lucide-react";
import OpportunityGauge from "@/components/business/OpportunityGauge";
import ProposalPreview from "@/components/business/ProposalPreview";

export default function BusinessDetailPage() {
    const { slug } = useParams();
    const [data, setData] = useState(null);
    const [showProposal, setShowProposal] = useState(false);

    useEffect(() => {
        api.get(`/api/businesses/${slug}`).then(({ data }) => setData(data));
    }, [slug]);

    if (!data) return <div className="p-10 text-muted-foreground font-mono text-sm">Loading business…</div>;

    const { business: b, detail, recommendation } = data;

    return (
        <div className="max-w-[1400px] px-8 lg:px-12 py-10" data-testid="business-detail-root">
            <Link to="/search" data-testid="back-to-search" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6">
                <ArrowLeft size={14} /> Back to discovery
            </Link>

            {/* Hero */}
            <div className="border border-border">
                <div className="h-56 sm:h-64 relative overflow-hidden bg-secondary">
                    <img src={b.cover_image} alt="" className="w-full h-full object-cover opacity-60" />
                    <div className="absolute inset-0 bg-gradient-to-t from-card via-card/50 to-transparent" />
                    <div className="absolute bottom-6 left-8 right-8 flex items-end justify-between gap-6">
                        <div className="min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                                <span className={`text-[10px] tracking-[0.15em] uppercase px-2 py-1 font-semibold ${b.tier === "HIGH" ? "bg-accent text-accent-foreground" : b.tier === "MEDIUM" ? "bg-primary text-primary-foreground" : "bg-secondary"}`}>
                                    {b.tier} priority
                                </span>
                                {b.verified && <span className="text-[10px] tracking-[0.15em] uppercase px-2 py-1 bg-primary text-primary-foreground font-semibold">Verified</span>}
                                <span className="text-[10px] tracking-[0.15em] uppercase text-muted-foreground">{b.category}</span>
                            </div>
                            <h1 className="font-display text-4xl sm:text-5xl font-light leading-none tracking-tight truncate" data-testid="business-name">{b.name}</h1>
                            <div className="text-sm text-muted-foreground flex items-center gap-1 mt-3">
                                <MapPin size={13} /> {b.city}, {b.country}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Two-column layout */}
            <div className="grid lg:grid-cols-3 border-x border-b border-border">
                {/* Left col: profile */}
                <div className="lg:col-span-2 border-r border-border">
                    {/* Bio */}
                    <div className="p-8 border-b border-border">
                        <div className="label-caps mb-3">About</div>
                        <p className="text-base leading-relaxed text-foreground/90">{b.bio}</p>
                    </div>

                    {/* Stat grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 border-b border-border">
                        <Stat label="Followers" value={formatNum(b.followers)} testid="stat-followers" />
                        <Stat label="Engagement" value={`${b.engagement_rate.toFixed(1)}%`} testid="stat-engagement" />
                        <Stat label="Posts / 30d" value={detail.posts_last_30} testid="stat-posts" />
                        <Stat label="Online orders" value={detail.has_online_orders ? "Yes" : "No"} testid="stat-orders" />
                    </div>

                    {/* Presence */}
                    <div className="p-8 border-b border-border">
                        <div className="label-caps mb-4">Digital presence</div>
                        <div className="space-y-3">
                            <PresenceRow icon={Instagram} label="Instagram" value={b.instagram ? `@${b.instagram}` : "—"} present={!!b.instagram} link={b.instagram ? `https://instagram.com/${b.instagram}` : null} testid="presence-instagram" />
                            <PresenceRow icon={Facebook} label="Facebook" value={b.facebook ? `/${b.facebook}` : "—"} present={!!b.facebook} link={b.facebook ? `https://facebook.com/${b.facebook}` : null} testid="presence-facebook" />
                            <PresenceRow icon={Globe} label="Website" value={b.website || "Not detected"} present={!!b.website} link={b.website} highlight testid="presence-website" />
                            <PresenceRow icon={Phone} label="Phone" value={detail.phone || "—"} present={!!detail.phone} testid="presence-phone" />
                            <PresenceRow icon={ShoppingBag} label="Online ordering" value={detail.has_online_orders ? "Active" : "Not available"} present={detail.has_online_orders} testid="presence-orders" />
                        </div>
                    </div>
                </div>

                {/* Right col: Recommendation */}
                <div className="p-8 bg-secondary/20">
                    <div className="label-caps mb-4">Recommendation</div>

                    <div className="flex items-center justify-between gap-4 border-b border-border pb-6">
                        <div>
                            <div className="label-caps mb-1">Opportunity</div>
                            <div className="font-display text-lg leading-tight">{recommendation.tier} PRIORITY</div>
                            <div className="text-xs text-muted-foreground mt-2 max-w-[180px]">Website recommended based on social signal.</div>
                        </div>
                        <OpportunityGauge score={recommendation.score} tier={recommendation.tier} size={130} />
                    </div>

                    <div className="pt-6">
                        <div className="label-caps mb-2">Design theme</div>
                        <div className="font-display text-2xl leading-tight" data-testid="rec-theme">{recommendation.theme}</div>
                        <div className="mt-3 flex gap-2">
                            {recommendation.palette.map((c) => (
                                <div key={c} className="w-8 h-8 border border-border" style={{ backgroundColor: c }} title={c} />
                            ))}
                        </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-border">
                        <div className="label-caps mb-3">Suggested sections</div>
                        <ul className="space-y-1.5 text-sm">
                            {recommendation.suggested_sections.map((s) => (
                                <li key={s} className="flex items-center gap-2" data-testid={`section-${s}`}>
                                    <span className="w-1 h-1 rounded-full bg-accent" />
                                    {s}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="mt-6 pt-6 border-t border-border">
                        <div className="label-caps mb-2">Est. project price</div>
                        <div className="font-display text-3xl font-light tracking-tight" data-testid="price-range">
                            ${recommendation.price_range.min.toLocaleString()} – ${recommendation.price_range.max.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">USD, one-time build</div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-border">
                        <div className="label-caps mb-3">Why this business</div>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            {recommendation.rationale.map((r, i) => (
                                <li key={i}>— {r}</li>
                            ))}
                        </ul>
                    </div>

                    <button
                        onClick={() => setShowProposal(true)}
                        data-testid="generate-proposal-btn"
                        className="mt-8 w-full inline-flex items-center justify-center gap-2 bg-accent text-accent-foreground px-5 py-3 font-medium hover:bg-accent/90 transition-colors"
                    >
                        <FileText size={16} /> Preview proposal
                    </button>
                </div>
            </div>

            {showProposal && <ProposalPreview slug={slug} onClose={() => setShowProposal(false)} />}
        </div>
    );
}

function Stat({ label, value, testid }) {
    return (
        <div className="p-6 border-r border-border last:border-r-0" data-testid={testid}>
            <div className="label-caps mb-2">{label}</div>
            <div className="font-display text-2xl font-light">{value}</div>
        </div>
    );
}

function PresenceRow({ icon: Icon, label, value, present, link, highlight, testid }) {
    const content = (
        <div className={`flex items-center gap-3 py-2 border-b border-border/50 last:border-b-0 ${link ? "hover:text-accent" : ""}`} data-testid={testid}>
            <Icon size={16} className={present ? "text-foreground" : "text-muted-foreground/50"} />
            <div className="flex-1 text-sm">
                <div className="label-caps mb-0.5">{label}</div>
                <div className={highlight && !present ? "text-destructive-foreground" : "text-foreground"}>{value}</div>
            </div>
            {present ? <CheckCircle2 size={14} className="text-accent" /> : <XCircle size={14} className="text-muted-foreground/50" />}
        </div>
    );
    return link ? <a href={link} target="_blank" rel="noreferrer">{content}</a> : content;
}

function formatNum(n) {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}
