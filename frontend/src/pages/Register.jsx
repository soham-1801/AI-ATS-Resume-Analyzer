import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm, useWatch } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { Sparkles, Mail, Lock, User, AlertCircle, ArrowRight, Eye, EyeOff, Check, X } from "lucide-react";
import GalaxyBackground from "../components/GalaxyBackground";

const Register = () => {
  const { register, handleSubmit, control, formState: { errors } } = useForm({
    defaultValues: {
      firstName: "",
      lastName: "",
      email: "",
      password: "",
      confirmPassword: ""
    }
  });

  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Watch password field to check alignment with confirm password
  const password = useWatch({
    control,
    name: "password",
    defaultValue: ""
  });

  const commonWeak = ["password123", "admin123", "qwerty123", "12345678"];
  const requirements = [
    { label: "Minimum 8 characters", test: (val) => val.length >= 8 },
    { label: "Uppercase letter present", test: (val) => /[A-Z]/.test(val) },
    { label: "Lowercase letter present", test: (val) => /[a-z]/.test(val) },
    { label: "Number present", test: (val) => /[0-9]/.test(val) },
    { label: "Special character present", test: (val) => /[^a-zA-Z0-9\s]/.test(val) }
  ];

  // Calculate which rules are met
  const rulesMet = requirements.map(req => req.test(password));
  const metCount = rulesMet.filter(Boolean).length;
  const isWeakWord = commonWeak.includes(password.toLowerCase());

  // Determine strength label
  let strengthLabel = "";
  let strengthColor = "bg-slate-800";
  let strengthTextColor = "text-slate-550";
  let strengthWidth = "w-0";

  if (password.length > 0) {
    if (isWeakWord || metCount <= 2) {
      strengthLabel = "Weak";
      strengthColor = "bg-rose-500";
      strengthTextColor = "text-rose-400";
      strengthWidth = "w-1/3";
    } else if (metCount === 3 || metCount === 4) {
      strengthLabel = "Medium";
      strengthColor = "bg-amber-500";
      strengthTextColor = "text-amber-400";
      strengthWidth = "w-2/3";
    } else if (metCount === 5) {
      strengthLabel = "Strong";
      strengthColor = "bg-emerald-500";
      strengthTextColor = "text-emerald-400";
      strengthWidth = "w-full";
    }
  }

  const handleSocialLogin = async (provider) => {
    setError("");
    setLoading(true);
    try {
      const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
      const githubClientId = import.meta.env.VITE_GITHUB_CLIENT_ID;

      const isMockEnabled = import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK_OAUTH === 'true';

      if (provider === "google") {
        if (isMockEnabled) {
          // Local development only: Simulate successful OAuth redirect
          window.location.href = "/oauth/callback/google?code=mock_google_code";
          return;
        }

        if (!googleClientId) {
          setError("Google login is not configured. Google Client ID is missing from environment variables.");
          setLoading(false);
          return;
        }

        const redirectUri = encodeURIComponent(`${window.location.origin}/oauth/callback/google`);
        const scope = encodeURIComponent("openid email profile");
        window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=google&prompt=select_account`;
      } else if (provider === "github") {
        if (isMockEnabled) {
          // Local development only: Simulate successful OAuth redirect
          window.location.href = "/oauth/callback/github?code=mock_github_code";
          return;
        }

        if (!githubClientId) {
          setError("GitHub login is not configured. GitHub Client ID is missing from environment variables.");
          setLoading(false);
          return;
        }

        const redirectUri = encodeURIComponent(`${window.location.origin}/oauth/callback/github`);
        const scope = encodeURIComponent("user:email");
        window.location.href = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&redirect_uri=${redirectUri}&scope=${scope}&state=github&prompt=select_account`;
      }
    } catch (err) {
      console.error(`${provider} registration failed:`, err);
      setError(err.response?.data?.detail || `${provider} registration failed. Please try again.`);
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    setError("");
    setLoading(true);

    try {
      const fullName = `${data.firstName.trim()} ${data.lastName.trim()}`;
      const success = await registerUser(fullName, data.email, data.password);
      if (success) {
        navigate("/login", { state: { message: "Registration successful! Please sign in." } });
      }
    } catch (err) {
      console.error("Registration failed:", err);
      let errorMsg = "Registration failed. Try using a different email address.";
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === "string") {
          errorMsg = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail.map(d => d.msg).join(", ");
        }
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#060913] px-4 relative overflow-hidden">
      <GalaxyBackground />

      <div className="w-full max-w-md auth-glass-card rounded-2xl p-8 relative z-10">
        {/* Title */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <div className="w-11 h-11 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
            Create Account
          </h2>
          <p className="text-sm text-slate-400 mt-1">Get started with professional ATS optimizations</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-5 p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form (using React Hook Form!) */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Name Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* First Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">First Name</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                  <User className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  placeholder="John"
                  className={`w-full pl-10 pr-4 py-2 rounded-lg bg-indigo-950/20 border focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-indigo-950/40 text-sm text-indigo-100 placeholder-indigo-300/50 outline-none transition-all ${
                    errors.firstName ? "border-rose-500/50" : "border-indigo-500/20 hover:border-indigo-500/40"
                  }`}
                  {...register("firstName", { required: "Required." })}
                />
              </div>
              {errors.firstName && (
                <p className="text-rose-400 text-[10px] font-semibold">{errors.firstName.message}</p>
              )}
            </div>

            {/* Last Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Last Name</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                  <User className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  placeholder="Doe"
                  className={`w-full pl-10 pr-4 py-2 rounded-lg bg-indigo-950/20 border focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-indigo-950/40 text-sm text-indigo-100 placeholder-indigo-300/50 outline-none transition-all ${
                    errors.lastName ? "border-rose-500/50" : "border-indigo-500/20 hover:border-indigo-500/40"
                  }`}
                  {...register("lastName", { required: "Required." })}
                />
              </div>
              {errors.lastName && (
                <p className="text-rose-400 text-[10px] font-semibold">{errors.lastName.message}</p>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-550">
                <Mail className="w-4 h-4 text-slate-500" />
              </span>
              <input
                type="email"
                placeholder="you@example.com"
                className={`w-full pl-10 pr-4 py-2 rounded-lg bg-indigo-950/20 border focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-indigo-950/40 text-sm text-indigo-100 placeholder-indigo-300/50 outline-none transition-all ${
                  errors.email ? "border-rose-500/50" : "border-indigo-500/20 hover:border-indigo-500/40"
                }`}
                {...register("email", { 
                  required: "Email is required.",
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address."
                  }
                })}
              />
            </div>
            {errors.email && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.email.message}</p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-indigo-950/20 border focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-indigo-950/40 text-sm text-indigo-100 placeholder-indigo-300/50 outline-none transition-all ${
                  errors.password ? "border-rose-500/50" : "border-indigo-500/20 hover:border-indigo-500/40"
                }`}
                {...register("password", { 
                  required: "Password is required.",
                  validate: {
                    length: (val) => val.length >= 8 || "Password must be at least 8 characters long.",
                    uppercase: (val) => /[A-Z]/.test(val) || "Password must contain at least one uppercase letter.",
                    lowercase: (val) => /[a-z]/.test(val) || "Password must contain at least one lowercase letter.",
                    number: (val) => /[0-9]/.test(val) || "Password must contain at least one number.",
                    special: (val) => /[^a-zA-Z0-9\s]/.test(val) || "Password must contain at least one special character.",
                    weak: (val) => !commonWeak.includes(val.toLowerCase()) || "Password is too weak or commonly used."
                  }
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-400 focus:outline-none"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.password.message}</p>
            )}

            {/* Real-time Indicator and Strength Meter */}
            {password.length > 0 && (
              <div className="mt-2.5 space-y-1.5 p-3 rounded-lg bg-slate-950/40 border border-slate-900/60">
                <div className="flex items-center justify-between text-[11px] font-semibold">
                  <span className="text-slate-400">Password Strength:</span>
                  <span className={strengthTextColor}>{strengthLabel}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                  <div className={`h-full transition-all duration-300 ${strengthColor} ${strengthWidth}`} />
                </div>
                
                <div className="grid grid-cols-1 gap-1 pt-1.5 border-t border-slate-900">
                  {requirements.map((req, idx) => {
                    const isMet = rulesMet[idx];
                    return (
                      <div key={idx} className="flex items-center gap-2 text-[10px] font-medium leading-none">
                        {isMet ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
                        )}
                        <span className={isMet ? "text-emerald-400/80" : "text-slate-500"}>
                          {req.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Confirm Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showConfirmPassword ? "text" : "password"}
                placeholder="••••••••"
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-indigo-950/20 border focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-indigo-950/40 text-sm text-indigo-100 placeholder-indigo-300/50 outline-none transition-all ${
                  errors.confirmPassword ? "border-rose-500/50" : "border-indigo-500/20 hover:border-indigo-500/40"
                }`}
                {...register("confirmPassword", { 
                  required: "Please confirm your password.",
                  validate: (val) => val === password || "Passwords do not match."
                })}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-400 focus:outline-none"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.confirmPassword.message}</p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.3)] disabled:opacity-50 mt-2 cursor-pointer"
          >
            {loading ? "Registering..." : "Create Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Social Logins */}
        {(import.meta.env.VITE_GOOGLE_CLIENT_ID || import.meta.env.VITE_GITHUB_CLIENT_ID) && (
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800/60"></div>
              </div>
              <div className="relative flex justify-center text-[11px] font-semibold uppercase tracking-wider">
                <span className="px-3 bg-[#0a0f25] text-slate-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-1 gap-3">
              {import.meta.env.VITE_GOOGLE_CLIENT_ID && (
                <button
                  type="button"
                  onClick={() => handleSocialLogin("google")}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-3 py-2.5 bg-indigo-950/10 border border-indigo-500/20 hover:bg-indigo-900/30 hover:border-indigo-400/40 text-indigo-100 text-sm font-medium rounded-lg transition-all disabled:opacity-50 select-none cursor-pointer"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                  Continue with Google
                </button>
              )}
              {import.meta.env.VITE_GITHUB_CLIENT_ID && (
                <button
                  type="button"
                  onClick={() => handleSocialLogin("github")}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-3 py-2.5 bg-indigo-950/10 border border-indigo-500/20 hover:bg-indigo-900/30 hover:border-indigo-400/40 text-indigo-100 text-sm font-medium rounded-lg transition-all disabled:opacity-50 select-none cursor-pointer"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" /></svg>
                  Continue with GitHub
                </button>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-6 pt-6 border-t border-slate-800/60">
          <p className="text-xs text-slate-400">
            Already have an account?{" "}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
