import { Link, useRouterState } from "@tanstack/react-router";
import {
  BarChart3,
  Bell,
  FileText,
  LayoutDashboard,
  Radar,
  Search,
  Send,
  Settings,
  Sparkles,
  Users,
  LogOut,
} from "lucide-react";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth";

import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/discover", label: "Discover", icon: Radar },
  { to: "/leads", label: "Leads", icon: Users },
  { to: "/outreach", label: "Outreach", icon: Send },
  { to: "/proposals", label: "Proposals", icon: FileText },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export function AppShell({
  title,
  description,
  actions,
  children,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar lg:flex">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <div className="grid size-8 shrink-0 place-items-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="size-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate font-display text-sm font-bold tracking-tight">LeadForge</p>
            <p className="truncate text-[11px] text-muted-foreground">Sales intelligence</p>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-2">
          {nav.map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <item.icon className={cn("size-4 shrink-0", active && "text-primary")} />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <UserSidebarProfile />
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-5 py-3.5 sm:px-7">
            <div className="min-w-0">
              <h1 className="truncate text-lg font-semibold sm:text-xl">{title}</h1>
              {description ? (
                <p className="truncate text-xs text-muted-foreground sm:text-sm">{description}</p>
              ) : null}
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <div className="hidden items-center gap-2 rounded-lg border border-border bg-surface px-3 py-1.5 text-xs text-muted-foreground md:flex">
                <Search className="size-3.5" />
                <span>Search businesses</span>
                <kbd className="rounded border border-border px-1 text-[10px]">⌘K</kbd>
              </div>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Notifications"
                className="min-h-9 min-w-9"
              >
                <Bell className="size-4" />
              </Button>
              <ModeToggle />
              {actions}
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-2 lg:hidden">
            {nav.map((item) => {
              const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    "shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium",
                    active ? "bg-sidebar-accent text-primary" : "text-muted-foreground",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </header>

        <main className="min-w-0 flex-1 px-5 py-6 sm:px-7">{children}</main>
      </div>
    </div>
  );
}

function UserSidebarProfile() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const initials = user.name ? user.name.substring(0, 2).toUpperCase() : "U";

  return (
    <div className="flex items-center gap-2.5 border-t border-sidebar-border px-4 py-3">
      <div className="grid size-8 shrink-0 place-items-center rounded-full bg-primary-soft text-xs font-semibold text-primary">
        {initials}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-medium">{user.name}</p>
        <p className="truncate text-[11px] text-muted-foreground">{user.email}</p>
      </div>
      <Button
        variant="ghost"
        size="icon"
        aria-label="Log out"
        className="size-8 text-muted-foreground hover:text-foreground"
        onClick={() => logout()}
      >
        <LogOut className="size-4" />
      </Button>
    </div>
  );
}
