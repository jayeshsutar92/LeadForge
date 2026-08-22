import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Globe,
  MessagesSquare,
  Target,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/theme-toggle";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "LeadForge — AI-Powered Lead Generation & Sales Intelligence" },
      {
        name: "description",
        content:
          "Automate your client acquisition. LeadForge discovers local businesses, scores opportunities, and generates personalized outreach drafts.",
      },
    ],
  }),
  component: LandingPage,
});

function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <Target className="size-6 text-primary" />
            <span className="font-display text-xl font-bold tracking-tight">LeadForge</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-foreground transition-colors">
              How it Works
            </a>
            <a href="#pricing" className="hover:text-foreground transition-colors">
              Pricing
            </a>
            <a href="#faq" className="hover:text-foreground transition-colors">
              FAQ
            </a>
          </nav>
          <div className="flex items-center gap-4">
            <ModeToggle />
            <Button variant="ghost" asChild className="hidden sm:inline-flex">
              <Link to="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link to="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-24 pb-32 lg:pt-36 lg:pb-40">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background"></div>
          <div className="container relative mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="inline-flex items-center rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-8">
              <SparklesIcon className="size-4 mr-2" />
              The smart way to acquire web design clients
            </div>
            <h1 className="mx-auto max-w-4xl font-display text-5xl font-bold tracking-tight text-foreground sm:text-7xl">
              Turn local searches into{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">
                high-value clients
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
              Stop guessing who needs a website. LeadForge automatically discovers local businesses,
              scores their digital presence, and drafts hyper-personalized outreach.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="w-full sm:w-auto h-12 px-8" asChild>
                <Link to="/register">
                  Start Finding Leads <ArrowRight className="ml-2 size-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="w-full sm:w-auto h-12 px-8">
                <a href="#how-it-works">See how it works</a>
              </Button>
            </div>
          </div>
        </section>

        {/* Trusted By Section */}
        <section className="border-y border-border/50 bg-muted/30 py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-8">
              Trusted by forward-thinking web agencies and freelancers
            </p>
            <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale">
              <div className="flex items-center gap-2 font-display text-xl font-bold">
                <Globe className="size-6" /> WebStudio
              </div>
              <div className="flex items-center gap-2 font-display text-xl font-bold">
                <Zap className="size-6" /> DevCraft
              </div>
              <div className="flex items-center gap-2 font-display text-xl font-bold">
                <Target className="size-6" /> LocalLeads
              </div>
              <div className="flex items-center gap-2 font-display text-xl font-bold">
                <BarChart3 className="size-6" /> GrowthDigital
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 sm:py-32">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
                Everything you need to scale your outreach
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                We've automated the most tedious parts of client acquisition so you can focus on
                closing deals.
              </p>
            </div>
            <div className="grid gap-8 md:grid-cols-3">
              <FeatureCard
                icon={<Globe className="size-6 text-primary" />}
                title="Automated Discovery"
                description="Scan any city and niche to instantly uncover local businesses. We analyze their current digital footprint automatically."
              />
              <FeatureCard
                icon={<BarChart3 className="size-6 text-primary" />}
                title="Smart Scoring"
                description="Our proprietary algorithm scores opportunities based on their missing web presence, saving you hours of manual research."
              />
              <FeatureCard
                icon={<MessagesSquare className="size-6 text-primary" />}
                title="AI-Drafted Outreach"
                description="Generate hyper-personalized DMs and emails based on real business data, perfectly tailored to their specific needs."
              />
            </div>
          </div>
        </section>

        {/* How it Works Section */}
        <section id="how-it-works" className="bg-muted/30 py-24 sm:py-32">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
                How LeadForge works
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                A simple, repeatable process for predictable client generation.
              </p>
            </div>
            <div className="grid gap-12 md:grid-cols-3">
              <Step
                number="01"
                title="Scan your target market"
                description="Enter a location and industry. LeadForge instantly pulls real-time data on hundreds of local businesses."
              />
              <Step
                number="02"
                title="Identify the best opportunities"
                description="We automatically filter out businesses that already have modern websites, leaving only high-intent prospects."
              />
              <Step
                number="03"
                title="Reach out and close"
                description="Use our AI to draft personalized pitches across Email, Instagram, or WhatsApp. Send, follow up, and win the deal."
              />
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-24 sm:py-32">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid gap-12 lg:grid-cols-2 items-center">
              <div>
                <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl mb-6">
                  Stop prospecting. Start closing.
                </h2>
                <p className="text-lg text-muted-foreground mb-8">
                  Manual prospecting is soul-crushing. LeadForge acts as your automated SDR, working
                  24/7 to build a pipeline of businesses that genuinely need your services.
                </p>
                <ul className="space-y-4">
                  <BenefitItem text="Save 15+ hours a week on manual lead research" />
                  <BenefitItem text="Increase response rates with context-aware AI outreach" />
                  <BenefitItem text="Never run out of qualified local businesses to contact" />
                  <BenefitItem text="Manage your entire sales pipeline in one beautiful workspace" />
                </ul>
              </div>
              <div className="relative rounded-2xl border border-border/50 bg-background shadow-2xl overflow-hidden aspect-[4/3] flex items-center justify-center glow-panel">
                {/* Decorative mock UI representation */}
                <div className="w-3/4 space-y-4">
                  <div className="h-8 w-1/3 bg-muted rounded-md mb-8"></div>
                  <div className="flex gap-4">
                    <div className="h-24 w-1/3 bg-primary/20 border border-primary/30 rounded-xl"></div>
                    <div className="h-24 w-1/3 bg-muted rounded-xl"></div>
                    <div className="h-24 w-1/3 bg-muted rounded-xl"></div>
                  </div>
                  <div className="h-48 w-full bg-muted/50 rounded-xl mt-4"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="bg-muted/30 py-24 sm:py-32 text-center">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-muted-foreground mb-8">
              We're currently in closed beta. Join today to lock in early access pricing.
            </p>
            <div className="inline-block rounded-2xl border border-border bg-background p-8 shadow-sm w-full max-w-md mx-auto">
              <div className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-4">
                Beta Access
              </div>
              <h3 className="text-2xl font-bold mb-2">Coming Soon</h3>
              <p className="text-muted-foreground mb-6">
                Create an account today to get early access and begin generating leads immediately.
              </p>
              <Button size="lg" className="w-full" asChild>
                <Link to="/register">Create Free Account</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-24 sm:py-32">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl">
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl text-center mb-12">
              Frequently Asked Questions
            </h2>
            <div className="space-y-8">
              <FaqItem
                question="Where does LeadForge get its data?"
                answer="We aggregate publicly available data from OpenStreetMap, DuckDuckGo searches, and public social media profiles to build a comprehensive view of a business's digital footprint."
              />
              <FaqItem
                question="Does it send the emails for me?"
                answer="LeadForge drafts hyper-personalized outreach messages based on real data, but we believe you should always review and send them yourself to maintain authenticity and protect your sender reputation."
              />
              <FaqItem
                question="Is this only for web design agencies?"
                answer="While LeadForge is optimized for finding businesses that need websites, digital marketing agencies, SEO consultants, and social media managers also use our platform to identify high-intent prospects."
              />
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-background py-12">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Target className="size-5 text-primary" />
            <span className="font-display text-lg font-bold">LeadForge</span>
          </div>
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} LeadForge. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm font-medium text-muted-foreground">
            <a
              href="mailto:support@leadforge.ai"
              className="hover:text-foreground transition-colors"
            >
              Contact Support
            </a>
            <Link to="/login" className="hover:text-foreground transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
      <path d="M5 3v4" />
      <path d="M19 17v4" />
      <path d="M3 5h4" />
      <path d="M17 19h4" />
    </svg>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="panel p-6 flex flex-col gap-4 text-left hover:border-primary/50 transition-colors">
      <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center">
        {icon}
      </div>
      <h3 className="font-display text-xl font-bold">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}

function Step({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="relative flex flex-col items-center text-center">
      <div className="mb-6 flex size-16 items-center justify-center rounded-full bg-primary/10 text-xl font-bold text-primary border border-primary/20">
        {number}
      </div>
      <h3 className="font-display text-xl font-bold mb-3">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}

function BenefitItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <CheckCircle2 className="size-5 text-primary shrink-0 mt-0.5" />
      <span className="text-foreground">{text}</span>
    </li>
  );
}

function FaqItem({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="border-b border-border/50 pb-6 last:border-0 last:pb-0">
      <h4 className="font-display text-lg font-bold mb-3">{question}</h4>
      <p className="text-muted-foreground leading-relaxed">{answer}</p>
    </div>
  );
}
