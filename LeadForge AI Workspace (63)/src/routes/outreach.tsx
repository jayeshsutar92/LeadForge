import { createFileRoute } from "@tanstack/react-router";
import { Mail, MessageSquare, Plus, Sparkles } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { SectionHeader, StatCard } from "@/components/leadforge-ui";
import { Button } from "@/components/ui/button";
import { sequences } from "@/lib/mock-data";

export const Route = createFileRoute("/outreach")({
  head: () => ({
    meta: [
      { title: "Outreach — LeadForge" },
      { name: "description", content: "Track sequences, replies, and follow-ups across every lead you contact." },
      { property: "og:title", content: "Outreach — LeadForge" },
      { property: "og:description", content: "Track sequences, replies, and follow-ups across every lead you contact." },
    ],
  }),
  component: Outreach,
});

const inbox = [
  { id: 1, from: "Harborline Logistics", preview: "Interesting — can you send pricing for the quote portal?", time: "2h", unread: true },
  { id: 2, from: "Aperture Legal Partners", preview: "We reviewed the audit. Let's schedule a call Thursday.", time: "5h", unread: true },
  { id: 3, from: "Cedar & Co. Roasters", preview: "Not right now, revisit us in Q4 please.", time: "1d", unread: false },
  { id: 4, from: "Vantage Roofing Group", preview: "Who handles this internally? Forwarding to our ops lead.", time: "2d", unread: false },
];

function Outreach() {
  return (
    <AppShell
      title="Outreach"
      description="4 sequences running · 423 leads in flight"
      actions={
        <Button>
          <Plus className="size-4" />
          New sequence
        </Button>
      }
    >
      <div className="space-y-6">
        <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Emails sent" value="1,942" delta="+312" hint="this week" icon={<Mail className="size-4" />} />
          <StatCard label="Open rate" value="58.4%" delta="+1.8pt" />
          <StatCard label="Reply rate" value="24.1%" delta="+3.1pt" />
          <StatCard label="Meetings booked" value="17" delta="+5" icon={<MessageSquare className="size-4" />} />
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
          <div className="panel overflow-hidden">
            <div className="border-b border-border px-5 py-3.5">
              <h2 className="text-sm font-semibold">Sequences</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[620px] text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs text-muted-foreground">
                    <th scope="col" className="px-5 py-2.5 font-medium">Sequence</th>
                    <th scope="col" className="px-5 py-2.5 font-medium">Channel</th>
                    <th scope="col" className="px-5 py-2.5 text-right font-medium">Active</th>
                    <th scope="col" className="px-5 py-2.5 text-right font-medium">Open</th>
                    <th scope="col" className="px-5 py-2.5 text-right font-medium">Reply</th>
                  </tr>
                </thead>
                <tbody>
                  {sequences.map((s) => (
                    <tr key={s.id} className="border-b border-border/70 last:border-0 hover:bg-accent/40">
                      <td className="px-5 py-3">
                        <p className="truncate font-medium">{s.name}</p>
                        <p className="text-[11px] text-muted-foreground">
                          <span className={s.status === "Running" ? "text-primary" : "text-muted-foreground"}>●</span> {s.status}
                        </p>
                      </td>
                      <td className="px-5 py-3 text-xs text-muted-foreground">{s.channel}</td>
                      <td className="text-numeric px-5 py-3 text-right text-xs">{s.active}</td>
                      <td className="text-numeric px-5 py-3 text-right text-xs">{s.openRate}%</td>
                      <td className="text-numeric px-5 py-3 text-right text-xs font-semibold text-primary">{s.replyRate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel p-5">
            <SectionHeader
              title="Replies"
              action={<span className="text-xs text-muted-foreground">2 unread</span>}
            />
            <ul className="space-y-3">
              {inbox.map((m) => (
                <li key={m.id} className="rounded-lg border border-border bg-surface-raised p-3">
                  <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2">
                    <p className="truncate text-sm font-medium">{m.from}</p>
                    <span className="shrink-0 text-[11px] text-muted-foreground">{m.time}</span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{m.preview}</p>
                  {m.unread ? (
                    <span className="mt-2 inline-flex items-center gap-1 text-[11px] font-medium text-primary">
                      <Sparkles className="size-3" /> AI reply suggested
                    </span>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
