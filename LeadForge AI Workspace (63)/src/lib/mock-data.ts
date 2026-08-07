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

export const pipeline = [
  { stage: "Discovered", count: 428, value: 1_240_000 },
  { stage: "Qualified", count: 164, value: 820_000 },
  { stage: "Contacted", count: 92, value: 510_000 },
  { stage: "Negotiating", count: 31, value: 240_000 },
  { stage: "Won", count: 12, value: 96_400 },
];

export const activity = [
  {
    id: 1,
    actor: "AI Agent",
    action: "scored 42 new businesses in Portland, US",
    time: "12m ago",
    kind: "ai",
  },
  {
    id: 2,
    actor: "Maya Chen",
    action: "sent follow-up to Aperture Legal Partners",
    time: "1h ago",
    kind: "outreach",
  },
  {
    id: 3,
    actor: "AI Agent",
    action: "generated a proposal draft for Harborline Logistics",
    time: "3h ago",
    kind: "ai",
  },
  {
    id: 4,
    actor: "Dev Patel",
    action: "moved Lumen Interiors to Won · €9,300",
    time: "5h ago",
    kind: "deal",
  },
  {
    id: 5,
    actor: "AI Agent",
    action: "flagged 6 broken pages on vantageroof.com",
    time: "8h ago",
    kind: "signal",
  },
];

export const weeklyScans = [
  { day: "Mon", scanned: 320, qualified: 62 },
  { day: "Tue", scanned: 410, qualified: 84 },
  { day: "Wed", scanned: 388, qualified: 71 },
  { day: "Thu", scanned: 520, qualified: 118 },
  { day: "Fri", scanned: 470, qualified: 96 },
  { day: "Sat", scanned: 210, qualified: 38 },
  { day: "Sun", scanned: 180, qualified: 27 },
];

export const sequences = [
  {
    id: "sq-1",
    name: "No-website cold intro",
    channel: "Email",
    active: 128,
    replyRate: 24,
    openRate: 61,
    status: "Running",
  },
  {
    id: "sq-2",
    name: "Broken site urgency",
    channel: "Email + Call",
    active: 46,
    replyRate: 31,
    openRate: 68,
    status: "Running",
  },
  {
    id: "sq-3",
    name: "Outdated site audit offer",
    channel: "Email",
    active: 212,
    replyRate: 18,
    openRate: 54,
    status: "Running",
  },
  {
    id: "sq-4",
    name: "Re-engage lost leads",
    channel: "LinkedIn",
    active: 37,
    replyRate: 9,
    openRate: 40,
    status: "Paused",
  },
];

export const proposals = [
  {
    id: "pr-208",
    lead: "Harborline Logistics",
    title: "Replatform + freight quote portal",
    value: 15200,
    status: "Sent",
    updated: "2h ago",
    model: "Drafted by AI",
  },
  {
    id: "pr-207",
    lead: "Aperture Legal Partners",
    title: "Practice-area site & content system",
    value: 22000,
    status: "In review",
    updated: "Yesterday",
    model: "Drafted by AI",
  },
  {
    id: "pr-206",
    lead: "Northvale Dental Studio",
    title: "Booking-first practice website",
    value: 8400,
    status: "Draft",
    updated: "3d ago",
    model: "Drafted by AI",
  },
  {
    id: "pr-205",
    lead: "Lumen Interiors",
    title: "CMS migration & portfolio build",
    value: 9300,
    status: "Accepted",
    updated: "5d ago",
    model: "Edited by Dev Patel",
  },
];

export const discoverySegments = [
  { id: "sg-1", name: "Dentists · no website", region: "US West", found: 1240, avgScore: 82 },
  { id: "sg-2", name: "Trades · broken sites", region: "UK & IE", found: 684, avgScore: 74 },
  { id: "sg-3", name: "Restaurants · template only", region: "EU", found: 2130, avgScore: 66 },
  { id: "sg-4", name: "Legal · outdated", region: "CA", found: 412, avgScore: 71 },
];

export const formatCurrency = (n: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
