
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import ResumeUpload from "./pages/ResumeUpload";
import JobDescription from "./pages/JobDescription";
import ATSAnalysis from "./pages/ATSAnalysis";
import Profile from "./pages/Profile";
import OAuthCallback from "./pages/OAuthCallback";

// Public Route wrapper (redirects to dashboard if logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#080c14]">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Route wrapper mapping DashboardLayout around protected sub-pages
const ProtectedLayoutWrapper = ({ children }) => {
  return (
    <ProtectedRoute>
      <DashboardLayout>{children}</DashboardLayout>
    </ProtectedRoute>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public login/register endpoints */}
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
          <Route path="/oauth/callback/:provider" element={<PublicRoute><OAuthCallback /></PublicRoute>} />
          
          {/* Protected dashboard endpoints wrapped in layout shell */}
          <Route path="/dashboard" element={<ProtectedLayoutWrapper><Dashboard /></ProtectedLayoutWrapper>} />
          <Route path="/resumes" element={<ProtectedLayoutWrapper><ResumeUpload /></ProtectedLayoutWrapper>} />
          <Route path="/job-descriptions" element={<ProtectedLayoutWrapper><JobDescription /></ProtectedLayoutWrapper>} />
          <Route path="/ats-analysis" element={<ProtectedLayoutWrapper><ATSAnalysis /></ProtectedLayoutWrapper>} />
          <Route path="/profile" element={<ProtectedLayoutWrapper><Profile /></ProtectedLayoutWrapper>} />
          
          {/* Default Route redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
