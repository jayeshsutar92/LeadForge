export type LeadStatus = "new" | "qualified" | "contacted" | "negotiating" | "won" | "lost";
export type WebsiteState = "none" | "outdated" | "broken" | "modern";

export const statusMeta: Record<LeadStatus, { label: string; tone: string }> = {
  new: { label: "New", tone: "bg-info/15 text-info border-info/25" },
  qualified: { label: "Qualified", tone: "bg-primary/15 text-primary border-primary/25" },
  contacted: { label: "Contacted", tone: "bg-warning/15 text-warning border-warning/25" },
  negotiating: { label: "Negotiating", tone: "bg-chart-4/15 text-chart-4 border-chart-4/25" },
  won: { label: "Won", tone: "bg-success/15 text-success border-success/25" },
  lost: { label: "Lost", tone: "bg-muted text-muted-foreground border-border" },
};

export const websiteStateMeta: Record<WebsiteState, { label: string; tone: string }> = {
  none: { label: "No website", tone: "text-destructive" },
  broken: { label: "Broken", tone: "text-destructive" },
  outdated: { label: "Outdated", tone: "text-warning" },
  modern: { label: "Modern", tone: "text-success" },
};

export const formatCurrency = (n: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
