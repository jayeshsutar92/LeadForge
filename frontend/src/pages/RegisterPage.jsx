import { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { formatApiError } from "@/lib/api";
import { Zap, ArrowRight } from "lucide-react";

export default function RegisterPage() {
    const { user, initialized, register } = useAuth();
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    if (initialized && user) return <Navigate to="/dashboard" replace />;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setBusy(true);
        try {
            await register(name, email, password);
            navigate("/dashboard", { replace: true });
        } catch (err) {
            setError(formatApiError(err.response?.data?.detail) || err.message);
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-start bg-background text-foreground grain px-8 sm:px-16 py-12">
            <div className="w-full max-w-sm">
                <Link to="/login" className="flex items-center gap-2 mb-10">
                    <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-accent-foreground">
                        <Zap size={16} strokeWidth={2.5} />
                    </div>
                    <div className="font-display text-lg">LeadForge</div>
                </Link>

                <div className="label-caps mb-3">Create account</div>
                <h2 className="font-display text-3xl sm:text-4xl font-light tracking-tight leading-tight">
                    Start finding leads.
                </h2>

                <form onSubmit={handleSubmit} className="mt-10 space-y-5" data-testid="register-form">
                    <Field label="Name">
                        <input type="text" required value={name} data-testid="register-name-input"
                            onChange={(e) => setName(e.target.value)}
                            className="w-full bg-transparent border-b border-border focus:border-accent outline-none py-2 text-base" />
                    </Field>
                    <Field label="Email">
                        <input type="email" required value={email} data-testid="register-email-input"
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-transparent border-b border-border focus:border-accent outline-none py-2 text-base" />
                    </Field>
                    <Field label="Password">
                        <input type="password" required minLength={6} value={password} data-testid="register-password-input"
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-transparent border-b border-border focus:border-accent outline-none py-2 text-base" />
                    </Field>

                    {error && (
                        <div className="text-sm text-destructive-foreground bg-destructive/20 border border-destructive/40 px-3 py-2" data-testid="register-error">
                            {error}
                        </div>
                    )}

                    <button type="submit" disabled={busy} data-testid="register-submit"
                        className="group inline-flex items-center gap-3 bg-accent text-accent-foreground px-6 py-3 font-medium hover:bg-accent/90 transition-colors disabled:opacity-60">
                        {busy ? "Creating…" : "Create account"}
                        <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                </form>

                <div className="mt-8 text-sm text-muted-foreground">
                    Already have one? <Link to="/login" data-testid="link-login" className="text-foreground underline underline-offset-4 hover:text-accent">Sign in</Link>
                </div>
            </div>
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
