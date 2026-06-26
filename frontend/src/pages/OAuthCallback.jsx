import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import authService from "../services/authService";
import { Sparkles, AlertCircle, ArrowLeft } from "lucide-react";

const OAuthCallback = () => {
  const { provider } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { completeOAuthLogin } = useAuth();
  
  const [error, setError] = useState("");
  const [loadingMsg, setLoadingMsg] = useState("Validating authentication credentials...");

  useEffect(() => {
    const processOAuth = async () => {
      // 1. Parse authorization code and id_token from query params OR hash fragment
      const queryParams = new URLSearchParams(location.search);
      let code = queryParams.get("code");
      let idToken = queryParams.get("id_token");
      
      // Also check hash fragment (e.g. for Apple response_mode=fragment)
      if (location.hash) {
        const hashParams = new URLSearchParams(location.hash.substring(1));
        if (!code) code = hashParams.get("code");
        if (!idToken) idToken = hashParams.get("id_token");
      }

      if (!code && !idToken) {
        setError(`Authorization code or identifier was not found in the callback request from ${provider}.`);
        return;
      }

      // 2. Perform code/token exchange with FastAPI backend
      try {
        setLoadingMsg(`Exchanging OAuth credentials with ${provider.charAt(0).toUpperCase() + provider.slice(1)}...`);
        
        // Define redirect URI that was sent to the provider
        const redirectUri = `${window.location.origin}/oauth/callback/${provider}`;
        
        const response = await authService.exchangeOAuthCode(provider, code || "", redirectUri, idToken || "");
        const { access_token, refresh_token } = response.data;

        // 3. Update application context state and redirect to dashboard
        completeOAuthLogin(access_token, refresh_token);
        navigate("/dashboard", { replace: true });
      } catch (err) {
        console.error("Social authentication exchange failed:", err);
        let errorMsg = `Failed to complete login using ${provider}. Please try again.`;
        if (err.response?.data?.detail) {
          errorMsg = err.response.data.detail;
        }
        setError(errorMsg);
      }
    };

    if (provider) {
      processOAuth();
    }
  }, [provider, location, completeOAuthLogin, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#060913] px-4 relative overflow-hidden">
      {/* Glow Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-900/10 rounded-full blur-3xl pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl pulse-glow" />

      <div className="w-full max-w-md glass-card rounded-2xl p-8 shadow-2xl relative z-10 border border-slate-800/85 text-center">
        {error ? (
          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-rose-400" />
              </div>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-slate-200">Authentication Failed</h2>
              <p className="text-sm text-slate-400 leading-relaxed">{error}</p>
            </div>

            <button
              onClick={() => navigate("/login")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 border border-slate-850 hover:bg-slate-800 text-slate-200 text-sm font-semibold transition-all select-none cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              Return to Login
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-indigo-605/10 border border-indigo-500/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
                </div>
                {/* Circular spinner border */}
                <div className="absolute inset-0 w-12 h-12 border-2 border-indigo-500/30 border-t-indigo-500 rounded-xl animate-spin pointer-events-none" />
              </div>
            </div>

            <div className="space-y-2">
              <h2 className="text-lg font-bold text-slate-200">Securing Session</h2>
              <p className="text-xs text-slate-500 animate-pulse">{loadingMsg}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;
