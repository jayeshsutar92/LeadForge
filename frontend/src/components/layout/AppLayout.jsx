import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Search, History, LogOut, Sun, Moon, Zap } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";

const items = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, tid: "nav-dashboard" },
    { to: "/search", label: "Discover", icon: Search, tid: "nav-search" },
    { to: "/history", label: "Search History", icon: History, tid: "nav-history" },
];

export default function AppLayout({ children }) {
    const { user, logout } = useAuth();
    const { theme, toggle } = useTheme();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate("/login", { replace: true });
    };

    return (
        <div className="min-h-screen flex bg-background text-foreground grain">
            {/* Sidebar */}
            <aside className="w-60 shrink-0 border-r border-border flex flex-col" data-testid="app-sidebar">
                <div className="h-16 px-5 flex items-center gap-2 border-b border-border">
                    <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-accent-foreground">
                        <Zap size={16} strokeWidth={2.5} />
                    </div>
                    <div className="font-display text-lg leading-none">
                        <div>LeadForge</div>
                        <div className="text-[10px] tracking-[0.2em] text-muted-foreground uppercase mt-1">Signal Layer</div>
                    </div>
                </div>

                <nav className="flex-1 px-3 py-6 space-y-1">
                    {items.map(({ to, label, icon: Icon, tid }) => (
                        <NavLink
                            key={to}
                            to={to}
                            data-testid={tid}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2.5 text-sm rounded-md transition-colors duration-150 ${isActive
                                    ? "bg-secondary text-foreground border-l-2 border-primary pl-[10px]"
                                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                                }`
                            }
                        >
                            <Icon size={16} />
                            <span>{label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-3 border-t border-border space-y-2">
                    <div className="px-2 py-2">
                        <div className="label-caps mb-1">Signed in</div>
                        <div className="text-sm truncate" data-testid="user-email">{user?.email}</div>
                    </div>
                    <button
                        onClick={toggle}
                        data-testid="theme-toggle"
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary/60 transition-colors"
                    >
                        {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
                        <span>{theme === "dark" ? "Light mode" : "Dark mode"}</span>
                    </button>
                    <button
                        onClick={handleLogout}
                        data-testid="logout-btn"
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                    >
                        <LogOut size={16} />
                        <span>Log out</span>
                    </button>
                </div>
            </aside>

            <main className="flex-1 min-w-0">{children}</main>
        </div>
    );
}
