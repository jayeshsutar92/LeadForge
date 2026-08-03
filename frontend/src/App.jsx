import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import AppLayout from "@/components/layout/AppLayout";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import SearchPage from "@/pages/SearchPage";
import BusinessDetailPage from "@/pages/BusinessDetailPage";
import SearchHistoryPage from "@/pages/SearchHistoryPage";
import { Toaster } from "@/components/ui/sonner";

function Shell({ children }) {
    return (
        <ProtectedRoute>
            <AppLayout>{children}</AppLayout>
        </ProtectedRoute>
    );
}

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/dashboard" element={<Shell><DashboardPage /></Shell>} />
                        <Route path="/search" element={<Shell><SearchPage /></Shell>} />
                        <Route path="/business/:slug" element={<Shell><BusinessDetailPage /></Shell>} />
                        <Route path="/history" element={<Shell><SearchHistoryPage /></Shell>} />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                    <Toaster />
                </BrowserRouter>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
