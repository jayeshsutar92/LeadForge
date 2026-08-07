export type LeadStatus = "new" | "qualified" | "contacted" | "negotiating" | "won" | "lost";
export type WebsiteState = "none" | "outdated" | "broken" | "modern";

export interface Lead {
  id: string;
  name: string;
  category: string;
  city: string;
  country: string;
  score: number;
  status: LeadStatus;
  website: string | null;
  websiteState: WebsiteState;
  rating: number;
  reviews: number;
  employees: string;
  estValue: number;
  owner: string;
  phone: string;
  email: string;
  lastActivity: string;
  signals: string[];
  summary: string;
}

export const leads: Lead[] = [
  {
    id: "ld-1042",
    name: "Northvale Dental Studio",
    category: "Healthcare · Dental",
    city: "Portland",
    country: "US",
    score: 94,
    status: "qualified",
    website: null,
    websiteState: "none",
    rating: 4.8,
    reviews: 312,
    employees: "11–50",
    estValue: 8400,
    owner: "Maya Chen",
    phone: "+1 503 555 0142",
    email: "hello@northvaledental.com",
    lastActivity: "2h ago",
    signals: ["No website found", "High review velocity", "Runs paid social", "Booking via DM only"],
    summary:
      "High-traffic dental practice with 312 reviews and no owned web presence. Patients book through Instagram DMs — strong case for a booking-first site.",
  },
  {
    id: "ld-1041",
    name: "Harborline Logistics",
    category: "Transport · Freight",
    city: "Rotterdam",
    country: "NL",
    score: 88,
    status: "contacted",
    website: "harborline-logistics.nl",
    websiteState: "outdated",
    rating: 4.3,
    reviews: 87,
    employees: "51–200",
    estValue: 15200,
    owner: "Tomas Fried",
    phone: "+31 10 555 0198",
    email: "info@harborline-logistics.nl",
    lastActivity: "Yesterday",
    signals: ["Site built 2011", "No mobile viewport", "PageSpeed 24/100", "No SSL on forms"],
    summary:
      "Mid-size freight operator running a 2011-era site with no mobile layout. Quote form is unsecured — replatform plus lead capture is the obvious pitch.",
  },
  {
    id: "ld-1040",
    name: "Cedar & Co. Roasters",
    category: "Food & Beverage",
    city: "Austin",
    country: "US",
    score: 81,
    status: "new",
    website: "cedarco.square.site",
    websiteState: "outdated",
    rating: 4.9,
    reviews: 1204,
    employees: "11–50",
    estValue: 6200,
    owner: "Unassigned",
    phone: "+1 512 555 0110",
    email: "orders@cedarco.coffee",
    lastActivity: "4d ago",
    signals: ["Template storefront", "No wholesale page", "Growing 3 locations"],
    summary:
      "Specialty roaster on a locked template storefront. Expanding to a third location with no wholesale funnel — commerce rebuild opportunity.",
  },
  {
    id: "ld-1039",
    name: "Aperture Legal Partners",
    category: "Professional Services",
    city: "Toronto",
    country: "CA",
    score: 76,
    status: "negotiating",
    website: "aperturelegal.ca",
    websiteState: "outdated",
    rating: 4.6,
    reviews: 54,
    employees: "11–50",
    estValue: 22000,
    owner: "Maya Chen",
    phone: "+1 416 555 0177",
    email: "contact@aperturelegal.ca",
    lastActivity: "3h ago",
    signals: ["Flash-era assets", "No case study content", "Hiring 4 associates"],
    summary:
      "Boutique firm scaling headcount fast. Site has no practice-area depth and ranks poorly for local intent keywords.",
  },
  {
    id: "ld-1038",
    name: "Kestrel Fitness Collective",
    category: "Fitness · Wellness",
    city: "Manchester",
    country: "UK",
    score: 72,
    status: "new",
    website: null,
    websiteState: "none",
    rating: 4.7,
    reviews: 198,
    employees: "1–10",
    estValue: 4800,
    owner: "Unassigned",
    phone: "+44 161 555 0123",
    email: "team@kestrelfit.uk",
    lastActivity: "1w ago",
    signals: ["Linktree only", "Class schedule in PDF", "Waitlist demand"],
    summary:
      "Studio operating entirely from Linktree with a PDF timetable. Memberships handled manually — booking site with payments is a fast win.",
  },
  {
    id: "ld-1037",
    name: "Vantage Roofing Group",
    category: "Construction",
    city: "Denver",
    country: "US",
    score: 69,
    status: "contacted",
    website: "vantageroof.com",
    websiteState: "broken",
    rating: 4.1,
    reviews: 143,
    employees: "51–200",
    estValue: 11500,
    owner: "Dev Patel",
    phone: "+1 720 555 0166",
    email: "sales@vantageroof.com",
    lastActivity: "2d ago",
    signals: ["500 errors on 6 pages", "Expired certificate", "Ad spend detected"],
    summary:
      "Actively buying ads that land on erroring pages. Immediate revenue leak — urgency angle for a rapid rebuild engagement.",
  },
  {
    id: "ld-1036",
    name: "Lumen Interiors",
    category: "Design · Retail",
    city: "Lisbon",
    country: "PT",
    score: 63,
    status: "won",
    website: "lumeninteriors.pt",
    websiteState: "modern",
    rating: 4.5,
    reviews: 76,
    employees: "11–50",
    estValue: 9300,
    owner: "Dev Patel",
    phone: "+351 21 555 0121",
    email: "studio@lumeninteriors.pt",
    lastActivity: "5d ago",
    signals: ["Recently redesigned", "Needs CMS migration", "Portfolio heavy"],
    summary:
      "Recently refreshed brand but content is trapped in static HTML. Scoped for a CMS migration and portfolio system.",
  },
  {
    id: "ld-1035",
    name: "Brightpath Tutoring",
    category: "Education",
    city: "Sydney",
    country: "AU",
    score: 58,
    status: "lost",
    website: "brightpath.edu.au",
    websiteState: "outdated",
    rating: 4.2,
    reviews: 41,
    employees: "1–10",
    estValue: 3600,
    owner: "Tomas Fried",
    phone: "+61 2 5550 0134",
    email: "admin@brightpath.edu.au",
    lastActivity: "3w ago",
    signals: ["Low budget signal", "Handled in-house"],
    summary: "Decided to keep the rebuild in-house this quarter. Worth re-engaging after the new school year.",
  },
];

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
  { id: 1, actor: "AI Agent", action: "scored 42 new businesses in Portland, US", time: "12m ago", kind: "ai" },
  { id: 2, actor: "Maya Chen", action: "sent follow-up to Aperture Legal Partners", time: "1h ago", kind: "outreach" },
  { id: 3, actor: "AI Agent", action: "generated a proposal draft for Harborline Logistics", time: "3h ago", kind: "ai" },
  { id: 4, actor: "Dev Patel", action: "moved Lumen Interiors to Won · €9,300", time: "5h ago", kind: "deal" },
  { id: 5, actor: "AI Agent", action: "flagged 6 broken pages on vantageroof.com", time: "8h ago", kind: "signal" },
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
  { id: "sq-2", name: "Broken site urgency", channel: "Email + Call", active: 46, replyRate: 31, openRate: 68, status: "Running" },
  { id: "sq-3", name: "Outdated site audit offer", channel: "Email", active: 212, replyRate: 18, openRate: 54, status: "Running" },
  { id: "sq-4", name: "Re-engage lost leads", channel: "LinkedIn", active: 37, replyRate: 9, openRate: 40, status: "Paused" },
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
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
