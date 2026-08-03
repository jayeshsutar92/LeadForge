import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { Search, Trash2, ChevronRight } from "lucide-react";

export default function SearchHistoryPage() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAll = async () => {
        setLoading(true);
        const { data } = await api.get("/api/history");
        setItems(data.results);
        setLoading(false);
    };

    useEffect(() => { fetchAll(); }, []);

    const clearAll = async () => {
        await api.delete("/api/history");
        setItems([]);
    };

    return (
        <div className="max-w-[1200px] px-8 lg:px-12 py-10" data-testid="history-root">
            <div className="border-b border-border pb-6 flex items-end justify-between">
                <div>
                    <div className="label-caps mb-2">History / Searches</div>
                    <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tighter leading-none">
                        Your <span className="text-accent">discovery trail</span>.
                    </h1>
                </div>
                {items.length > 0 && (
                    <button
                        onClick={clearAll}
                        data-testid="clear-history"
                        className="inline-flex items-center gap-2 border border-border px-4 py-2 text-sm text-muted-foreground hover:text-destructive-foreground hover:border-destructive transition-colors"
                    >
                        <Trash2 size={14} /> Clear all
                    </button>
                )}
            </div>

            {loading ? (
                <div className="py-10 text-muted-foreground font-mono text-sm">Loading history…</div>
            ) : items.length === 0 ? (
                <div className="border border-dashed border-border p-16 text-center text-muted-foreground mt-8" data-testid="history-empty">
                    You haven't run any searches yet.
                    <div className="mt-4">
                        <Link to="/search" className="inline-flex items-center gap-1 text-accent hover:underline">Start discovering →</Link>
                    </div>
                </div>
            ) : (
                <div className="mt-4">
                    {items.map((item, i) => {
                        const params = new URLSearchParams();
                        if (item.query) params.set("q", item.query);
                        const f = item.filters || {};
                        if (f.category) params.set("category", f.category);
                        if (f.website_status) params.set("website_status", f.website_status);
                        if (f.min_followers) params.set("min_followers", String(f.min_followers));
                        if (f.min_score) params.set("min_score", String(f.min_score));

                        return (
                            <Link
                                key={i}
                                to={`/search?${params.toString()}`}
                                data-testid={`history-item-${i}`}
                                className="flex items-center gap-4 p-4 border-b border-border hover:bg-secondary/40 transition-colors group"
                            >
                                <div className="w-9 h-9 border border-border flex items-center justify-center text-muted-foreground">
                                    <Search size={14} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium text-base truncate">
                                        {item.query || <span className="text-muted-foreground italic">All businesses</span>}
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-1 flex flex-wrap gap-x-3">
                                        {f.category && <span>{f.category}</span>}
                                        {f.website_status === "missing" && <span>No website</span>}
                                        {f.website_status === "has" && <span>Has website</span>}
                                        {f.min_followers ? <span>{f.min_followers}+ followers</span> : null}
                                        {f.min_score ? <span>Score {f.min_score}+</span> : null}
                                        <span>· {new Date(item.created_at).toLocaleString()}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="font-display text-lg">{item.result_count}</div>
                                    <div className="label-caps">results</div>
                                </div>
                                <ChevronRight size={16} className="text-muted-foreground group-hover:text-accent transition-colors" />
                            </Link>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
