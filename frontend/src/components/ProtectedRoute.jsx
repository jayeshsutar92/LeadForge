import { Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

export default function ProtectedRoute({ children }) {
    const { user, initialized } = useAuth();
    if (!initialized || user === null) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-muted-foreground font-mono text-sm">Loading…</div>
            </div>
        );
    }
    if (!user) return <Navigate to="/login" replace />;
    return children;
}
