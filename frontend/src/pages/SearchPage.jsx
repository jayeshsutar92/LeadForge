import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";
import BusinessCard from "@/components/business/BusinessCard";
import { Search, Filter, X } from "lucide-react";

export default function SearchPage() {
    const [params, setParams] = useSearchParams();
    const [categories, setCategories] = useState([]);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const q = params.get("q") || "";
    const category = params.get("category") || "All";
    const website_status = params.get("website_status") || "";
    const min_followers = params.get("min_followers") || "";
    const min_score = params.get("min_score") || "";
    const sort = params.get("sort") || "score_desc";

    useEffect(() => {
        api.get("/api/businesses/categories").then(({ data }) => setCategories(["All", ...data.categories]));
    }, []);

    const fetchResults = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await api.get("/api/businesses", {
                params: {
                    q: q || undefined,
                    category: category !== "All" ? category : undefined,
                    website_status: website_status || undefined,
                    min_followers: min_followers || undefined,
                    min_score: min_score || undefined,
                    sort,
                },
            });
            setResults(data.results);
        } finally {
            setLoading(false);
        }
    }, [q, category, website_status, min_followers, min_score, sort]);

    useEffect(() => { fetchResults(); }, [fetchResults]);

    const updateParam = (k, v) => {
        const p = new URLSearchParams(params);
        if (!v || v === "All") p.delete(k); else p.set(k, v);
        setParams(p, { replace: true });
    };

    const clearAll = () => setParams({}, { replace: true });

    const activeFilterCount = [q, category !== "All" && category, website_status, min_followers, min_score].filter(Boolean).length;

    return (
        <div className="max-w-[1400px] px-8 lg:px-12 py-10" data-testid="search-root">
            {/* Header */}
            <div className="border-b border-border pb-6 mb-0">
                <div className="label-caps mb-2">Discover / Search</div>
                <h1 className="font-display text-4xl sm:text-5xl font-light tracking-tighter leading-none">
                    Find businesses <span className="text-accent">worth building for</span>.
                </h1>

                {/* Search bar */}
                <div className="mt-8 flex items-center gap-3 border border-border focus-within:border-accent bg-card px-4 py-3">
                    <Search size={18} className="text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search by name, city, category…"
                        data-testid="search-input"
                        value={q}
                        onChange={(e) => updateParam("q", e.target.value)}
                        className="flex-1 bg-transparent outline-none text-base"
                    />
                    {activeFilterCount > 0 && (
                        <button
                            onClick={clearAll}
                            data-testid="clear-filters"
                            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                        >
                            <X size={14} /> Clear ({activeFilterCount})
                        </button>
                    )}
                </div>
            </div>

            {/* Filters row */}
            <div className="grid grid-cols-2 lg:grid-cols-5 border-b border-border">
                <FilterPicker
                    label="Category" testid="filter-category" value={category}
                    options={categories.map((c) => ({ value: c, label: c }))}
                    onChange={(v) => updateParam("category", v)}
                />
                <FilterPicker
                    label="Website" testid="filter-website" value={website_status || "any"}
                    options={[{ value: "any", label: "Any" }, { value: "missing", label: "Missing website" }, { value: "has", label: "Has website" }]}
                    onChange={(v) => updateParam("website_status", v === "any" ? "" : v)}
                />
                <FilterPicker
                    label="Min followers" testid="filter-followers" value={min_followers || "0"}
                    options={[
                        { value: "0", label: "Any" },
                        { value: "1000", label: "1K+" },
                        { value: "10000", label: "10K+" },
                        { value: "50000", label: "50K+" },
                    ]}
                    onChange={(v) => updateParam("min_followers", v === "0" ? "" : v)}
                />
                <FilterPicker
                    label="Min score" testid="filter-score" value={min_score || "0"}
                    options={[
                        { value: "0", label: "Any" },
                        { value: "50", label: "50+" },
                        { value: "75", label: "75+ (HOT)" },
                    ]}
                    onChange={(v) => updateParam("min_score", v === "0" ? "" : v)}
                />
                <FilterPicker
                    label="Sort" testid="filter-sort" value={sort}
                    options={[
                        { value: "score_desc", label: "Highest score" },
                        { value: "followers_desc", label: "Most followers" },
                        { value: "name_asc", label: "Name (A–Z)" },
                    ]}
                    onChange={(v) => updateParam("sort", v)}
                />
            </div>

            {/* Result count */}
            <div className="py-6 flex items-center justify-between">
                <div className="label-caps" data-testid="result-count">
                    {loading ? "Searching…" : `${results.length} businesses found`}
                </div>
                <div className="text-xs text-muted-foreground hidden sm:flex items-center gap-2">
                    <Filter size={12} />
                    {activeFilterCount > 0 ? `${activeFilterCount} filters active` : "No filters"}
                </div>
            </div>

            {/* Grid */}
            {results.length === 0 && !loading ? (
                <div className="border border-dashed border-border p-16 text-center text-muted-foreground" data-testid="empty-state">
                    No businesses match these filters.
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {results.map((b, i) => (
                        <div key={b.slug} className="fade-up" style={{ animationDelay: `${Math.min(i, 8) * 40}ms` }}>
                            <BusinessCard biz={b} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function FilterPicker({ label, testid, value, options, onChange }) {
    return (
        <div className="p-4 lg:p-6 border-r border-border last:border-r-0">
            <div className="label-caps mb-2">{label}</div>
            <select
                value={value}
                data-testid={testid}
                onChange={(e) => onChange(e.target.value)}
                className="w-full bg-transparent border-none outline-none text-sm font-medium py-1 cursor-pointer"
            >
                {options.map((o) => (
                    <option key={o.value} value={o.value} className="bg-card text-foreground">
                        {o.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
