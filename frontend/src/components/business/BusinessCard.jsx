import { Link } from "react-router-dom";
import { Instagram, Facebook, Globe, MapPin, Users } from "lucide-react";
import OpportunityGauge from "./OpportunityGauge";

export default function BusinessCard({ biz }) {
    const tierColor =
        biz.tier === "HIGH" ? "bg-accent text-accent-foreground" :
            biz.tier === "MEDIUM" ? "bg-primary text-primary-foreground" :
                "bg-secondary text-secondary-foreground";

    return (
        <Link
            to={`/business/${biz.slug}`}
            data-testid={`business-card-${biz.slug}`}
            className="group border border-border bg-card hover:border-primary/50 hover:-translate-y-0.5 transition-transform duration-200 flex flex-col overflow-hidden"
        >
            <div className="h-32 relative overflow-hidden bg-secondary">
                <img
                    src={biz.cover_image}
                    alt=""
                    loading="lazy"
                    className="w-full h-full object-cover opacity-70 group-hover:opacity-90 transition-opacity duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-card via-card/40 to-transparent" />
                <div className="absolute top-3 left-3 flex gap-1.5">
                    <span className={`text-[10px] tracking-[0.15em] uppercase px-2 py-1 font-semibold ${tierColor}`}>
                        {biz.tier}
                    </span>
                    {!biz.website && (
                        <span className="text-[10px] tracking-[0.15em] uppercase px-2 py-1 font-semibold bg-destructive/90 text-destructive-foreground">
                            No Site
                        </span>
                    )}
                </div>
                <div className="absolute top-3 right-3">
                    <div className="w-14 h-14 rounded-full bg-background/70 backdrop-blur-md border border-border flex items-center justify-center">
                        <div className="text-center">
                            <div className="font-display text-lg leading-none">{biz.opportunity_score}</div>
                            <div className="text-[8px] tracking-[0.15em] uppercase text-muted-foreground mt-0.5">Score</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-4 flex-1 flex flex-col gap-2">
                <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                        <h3 className="font-display font-medium text-base leading-tight truncate">{biz.name}</h3>
                        <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                            <MapPin size={11} />
                            {biz.city}, {biz.country}
                        </div>
                    </div>
                </div>

                <p className="text-xs text-muted-foreground line-clamp-2">{biz.bio}</p>

                <div className="flex items-center justify-between mt-auto pt-3 border-t border-border">
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Users size={11} /> {formatNum(biz.followers)}</span>
                        <span className="font-mono">{biz.engagement_rate.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                        {biz.instagram && <Instagram size={13} />}
                        {biz.facebook && <Facebook size={13} />}
                        {biz.website ? <Globe size={13} className="text-accent" /> : <Globe size={13} className="opacity-30" />}
                    </div>
                </div>

                <div className="text-[10px] tracking-[0.2em] uppercase text-muted-foreground">{biz.category}</div>
            </div>
        </Link>
    );
}

function formatNum(n) {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
    return String(n);
}
