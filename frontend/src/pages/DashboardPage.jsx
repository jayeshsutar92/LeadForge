import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { Building2, Globe, Flame, Gauge, ArrowUpRight } from "lucide-react";
import BusinessCard from "@/components/business/BusinessCard";

export default function DashboardPage() {
    const [stats, setStats] = useState(null);
    const [err, setErr] = useState("");

    useEffect(() => {
        api.get("/api/businesses/stats")
            .then(({ data }) => setStats(data))
            .catch((e) => setErr(e.message));
    }, []);

    if (err) return <div className="p-8 text-destructive-foreground">{err}</div>;
    if (!stats) return <div className="p-8 text-muted-foreground font-mono text-sm">Loading dashboard…</div>;

    const missingPct = Math.round((stats.missing_website / Math.max(1, stats.total_businesses)) * 100);

    return (
        <div className="max-w-[1400px] px-8 lg:px-12 py-10" data-testid="dashboard-root">
            {/* Header */}
            <div className="flex items-end justify-between border-b border-border pb-6">
                <div>
                    <div className="label-caps mb-2">Dashboard / Overview</div>
                    <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tighter leading-none">
                        Signal <span className="text-accent">/</span> Opportunity
                    </h1>
                </div>
                <Link
                    to="/search"
                    data-testid="dashboard-discover-btn"
                    className="hidden sm:inline-flex items-center gap-2 bg-accent text-accent-foreground px-5 py-3 font-medium hover:bg-accent/90 transition-colors"
                >
                    Discover leads <ArrowUpRight size={16} />
                </Link>
            </div>

            {/* Bento grid: KPIs */}
            <div className="grid grid-cols-2 lg:grid-cols-4 border-b border-border">
                <KPI icon={Building2} label="Total businesses" value={stats.total_businesses} sub="in database" testid="kpi-total" />
                <KPI icon={Globe} label="Missing website" value={stats.missing_website} sub={`${missingPct}% of total`} highlight testid="kpi-missing" />
                <KPI icon={Flame} label="High opportunity" value={stats.high_opportunity} sub="Score ≥ 75" accent testid="kpi-high" />
                <KPI icon={Gauge} label="Avg score" value={stats.avg_score} sub="Across catalog" testid="kpi-avg" />
            </div>

            {/* Middle bento */}
            <div className="grid lg:grid-cols-3 border-b border-border">
                <div className="lg:col-span-2 p-8 border-r border-border">
                    <div className="label-caps mb-4">Top 5 Leads This Week</div>
                    <div className="grid sm:grid-cols-2 gap-4">
                        {stats.top_leads.slice(0, 4).map((b, i) => (
                            <div key={b.slug} className="fade-up" style={{ animationDelay: `${i * 80}ms` }}>
                                <BusinessCard biz={b} />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="p-8">
                    <div className="label-caps mb-4">By Category</div>
                    <div className="space-y-3">
                        {Object.entries(stats.by_category)
                            .sort((a, b) => b[1] - a[1])
                            .map(([cat, n]) => {
                                const max = Math.max(...Object.values(stats.by_category));
                                const pct = (n / max) * 100;
                                return (
                                    <div key={cat} data-testid={`cat-${cat}`}>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span>{cat}</span>
                                            <span className="font-mono text-muted-foreground">{n}</span>
                                        </div>
                                        <div className="h-1 bg-secondary overflow-hidden">
                                            <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                </div>
            </div>

            {/* CTA row */}
            <div className="grid lg:grid-cols-2 gap-0">
                <div className="p-8 border-r border-border">
                    <div className="label-caps mb-3">Next best action</div>
                    <h3 className="font-display text-2xl font-light leading-tight max-w-md">
                        Filter for businesses without a website and reach out with a tailored proposal.
                    </h3>
                    <Link
                        to="/search?website_status=missing&min_score=75"
                        data-testid="cta-hot-leads"
                        className="mt-6 inline-flex items-center gap-2 border border-border px-5 py-3 text-sm hover:border-accent hover:text-accent transition-colors"
                    >
                        View hot leads <ArrowUpRight size={14} />
                    </Link>
                </div>
                <div className="p-8">
                    <div className="label-caps mb-3">Coming soon</div>
                    <ul className="text-sm text-muted-foreground space-y-2">
                        <li>— Real-time social discovery via Instagram/Facebook</li>
                        <li>— AI-authored proposal generation</li>
                        <li>— Built-in CRM &amp; outreach automation</li>
                        <li>— Cohort analytics &amp; conversion tracking</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

function KPI({ icon: Icon, label, value, sub, highlight, accent, testid }) {
    return (
        <div className="p-6 lg:p-8 border-r border-border last:border-r-0" data-testid={testid}>
            <div className="flex items-center justify-between">
                <div className="label-caps">{label}</div>
                <Icon size={16} className="text-muted-foreground" />
            </div>
            <div className={`font-display text-4xl lg:text-5xl mt-4 font-light tracking-tight leading-none ${accent ? "text-accent" : highlight ? "text-primary" : ""}`}>
                {value}
            </div>
            <div className="text-xs text-muted-foreground mt-2">{sub}</div>
        </div>
    );
}
