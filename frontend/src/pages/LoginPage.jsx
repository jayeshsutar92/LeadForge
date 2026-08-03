import { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { formatApiError } from "@/lib/api";
import { Zap, ArrowRight } from "lucide-react";

export default function LoginPage() {
    const { user, initialized, login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("jayeshsutar76@gmail.com");
    const [password, setPassword] = useState("admin123");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    if (initialized && user) return <Navigate to="/dashboard" replace />;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setBusy(true);
        try {
            await login(email, password);
            navigate("/dashboard", { replace: true });
        } catch (err) {
            setError(formatApiError(err.response?.data?.detail) || err.message);
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="min-h-screen grid lg:grid-cols-2 bg-background text-foreground grain">
            {/* Left: Brand panel */}
            <div className="hidden lg:flex flex-col justify-between p-12 border-r border-border bg-secondary/30 relative overflow-hidden">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-accent-foreground">
                        <Zap size={16} strokeWidth={2.5} />
                    </div>
                    <div className="font-display text-lg">LeadForge</div>
                </div>

                <div className="max-w-md relative z-10">
                    <div className="label-caps mb-4">Signal Layer / v1.0</div>
                    <h1 className="font-display text-5xl xl:text-6xl font-light leading-[0.95] tracking-tighter">
                        Find the businesses that <span className="text-accent">need a website</span> before they know it.
                    </h1>
                    <p className="mt-6 text-muted-foreground leading-relaxed max-w-sm">
                        LeadForge surfaces Instagram and Facebook-first businesses ready to convert their social audience into owned traffic.
                    </p>

                    <div className="mt-12 grid grid-cols-3 gap-6 border-t border-border pt-6">
                        <Stat label="Leads" value="30+" />
                        <Stat label="Categories" value="10" />
                        <Stat label="Score depth" value="0–100" />
                    </div>
                </div>

                <div className="text-xs text-muted-foreground font-mono">© 2026 LeadForge</div>

                <div className="absolute -bottom-20 -right-20 w-96 h-96 bg-accent/10 blur-3xl rounded-full pointer-events-none" />
            </div>

            {/* Right: Form */}
            <div className="flex items-center justify-start px-8 sm:px-16 py-12">
                <div className="w-full max-w-sm">
                    <div className="lg:hidden flex items-center gap-2 mb-10">
                        <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-accent-foreground">
                            <Zap size={16} strokeWidth={2.5} />
                        </div>
                        <div className="font-display text-lg">LeadForge</div>
                    </div>

                    <div className="label-caps mb-3">Sign in</div>
                    <h2 className="font-display text-3xl sm:text-4xl font-light tracking-tight leading-tight">
                        Welcome back.
                    </h2>
                    <p className="text-muted-foreground mt-2 text-sm">Access your lead workspace.</p>

                    <form onSubmit={handleSubmit} className="mt-10 space-y-5" data-testid="login-form">
                        <Field label="Email" testid="login-email">
                            <input
                                type="email"
                                required
                                value={email}
                                data-testid="login-email-input"
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-transparent border-b border-border focus:border-accent outline-none py-2 text-base"
                            />
                        </Field>
                        <Field label="Password" testid="login-password">
                            <input
                                type="password"
                                required
                                value={password}
                                data-testid="login-password-input"
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-transparent border-b border-border focus:border-accent outline-none py-2 text-base"
                            />
                        </Field>

                        {error && (
                            <div className="text-sm text-destructive-foreground bg-destructive/20 border border-destructive/40 px-3 py-2" data-testid="login-error">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={busy}
                            data-testid="login-submit"
                            className="group inline-flex items-center gap-3 bg-accent text-accent-foreground px-6 py-3 font-medium hover:bg-accent/90 transition-colors disabled:opacity-60"
                        >
                            {busy ? "Signing in…" : "Sign in"}
                            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                    </form>

                    <div className="mt-8 text-sm text-muted-foreground">
                        No account? <Link to="/register" data-testid="link-register" className="text-foreground underline underline-offset-4 hover:text-accent">Create one</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Stat({ label, value }) {
    return (
        <div>
            <div className="font-display text-2xl">{value}</div>
            <div className="label-caps mt-1">{label}</div>
        </div>
    );
}

function Field({ label, children }) {
    return (
        <label className="block">
            <div className="label-caps mb-2">{label}</div>
            {children}
        </label>
    );
}
