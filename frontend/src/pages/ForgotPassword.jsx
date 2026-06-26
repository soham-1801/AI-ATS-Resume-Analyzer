import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm, useWatch } from "react-hook-form";
import axios from "axios";
import { Mail, Lock, AlertCircle, ArrowRight, CheckCircle, Eye, EyeOff, Check, X, Key } from "lucide-react";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // Step 1: Request, Step 2: Confirm
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [debugToken, setDebugToken] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Initialize form for Step 1 (Request)
  const { register: registerReq, handleSubmit: handleSubmitReq, formState: { errors: errorsReq } } = useForm({
    defaultValues: { email: "" }
  });

  // Initialize form for Step 2 (Reset)
  const { register: registerReset, handleSubmit: handleSubmitReset, control: controlReset, formState: { errors: errorsReset } } = useForm({
    defaultValues: { token: "", password: "", confirmPassword: "" }
  });

  const newPassword = useWatch({
    control: controlReset,
    name: "password",
    defaultValue: ""
  });

  // Password rules logic
  const commonWeak = ["password123", "admin123", "qwerty123", "12345678"];
  const requirements = [
    { label: "Minimum 8 characters", test: (val) => val.length >= 8 },
    { label: "Uppercase letter present", test: (val) => /[A-Z]/.test(val) },
    { label: "Lowercase letter present", test: (val) => /[a-z]/.test(val) },
    { label: "Number present", test: (val) => /[0-9]/.test(val) },
    { label: "Special character present", test: (val) => /[^a-zA-Z0-9\s]/.test(val) }
  ];

  const rulesMet = requirements.map(req => req.test(newPassword));
  const metCount = rulesMet.filter(Boolean).length;
  const isWeakWord = commonWeak.includes(newPassword.toLowerCase());

  let strengthLabel = "";
  let strengthColor = "bg-slate-800";
  let strengthTextColor = "text-slate-500";
  let strengthWidth = "w-0";

  if (newPassword.length > 0) {
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

  // API base url
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

  const handleRequestToken = async (data) => {
    setError("");
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/reset-password-request`, {
        email: data.email
      });
      setEmail(data.email);
      setSuccess("If the email is registered, a reset code has been generated.");
      
      // Collect debug token for local testing convenience
      if (response.data.debug_token) {
        setDebugToken(response.data.debug_token);
      }
      setStep(2);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to request password reset code.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (data) => {
    setError("");
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/auth/reset-password`, {
        email: email,
        token: data.token,
        new_password: data.password
      });
      setSuccess("Password has been reset successfully! Redirecting to login...");
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Password reset failed. Verify your reset code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#060913] px-4 relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-900/10 rounded-full blur-3xl pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl pulse-glow" />

      <div className="w-full max-w-md glass-card rounded-2xl p-8 shadow-2xl relative z-10 border border-slate-800/80">
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <div className="w-11 h-11 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center">
              <Key className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
            Reset Password
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {step === 1 ? "Enter your email to request a reset code" : "Complete security validations to reset password"}
          </p>
        </div>

        {error && (
          <div className="mb-5 p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-5 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3 text-emerald-400 text-sm">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleSubmitReq(handleRequestToken)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  placeholder="you@example.com"
                  className={`w-full pl-10 pr-4 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                    errorsReq.email ? "border-rose-500/50" : "border-slate-800"
                  }`}
                  {...registerReq("email", { 
                    required: "Email is required.",
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: "Invalid email address."
                    }
                  })}
                />
              </div>
              {errorsReq.email && (
                <p className="text-rose-400 text-[10px] font-semibold">{errorsReq.email.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 mt-2"
            >
              {loading ? "Requesting..." : "Send Reset Code"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleSubmitReset(handleResetPassword)} className="space-y-4">
            {debugToken && (
              <div className="p-3 bg-indigo-950/20 border border-indigo-900/50 rounded-lg text-xs text-indigo-400">
                <span className="font-bold">Developer Notice:</span> Reset Token is <code className="bg-slate-950 px-1.5 py-0.5 rounded font-bold border border-slate-900">{debugToken}</code>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Reset Code</label>
              <input
                type="text"
                placeholder="Enter 6-character code"
                className={`w-full px-4 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errorsReset.token ? "border-rose-500/50" : "border-slate-800"
                }`}
                {...registerReset("token", { required: "Reset code is required." })}
              />
              {errorsReset.token && (
                <p className="text-rose-400 text-[10px] font-semibold">{errorsReset.token.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">New Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                    errorsReset.password ? "border-rose-500/50" : "border-slate-800"
                  }`}
                  {...registerReset("password", { 
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
              {errorsReset.password && (
                <p className="text-rose-400 text-[10px] font-semibold">{errorsReset.password.message}</p>
              )}

              {/* Real-time Indicator Checklist and Strength Meter */}
              {newPassword.length > 0 && (
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
                  className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                    errorsReset.confirmPassword ? "border-rose-500/50" : "border-slate-800"
                  }`}
                  {...registerReset("confirmPassword", { 
                    required: "Please confirm your password.",
                    validate: (val) => val === newPassword || "Passwords do not match."
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
              {errorsReset.confirmPassword && (
                <p className="text-rose-400 text-[10px] font-semibold">{errorsReset.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 mt-4"
            >
              {loading ? "Resetting..." : "Confirm New Password"}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}

        <div className="text-center mt-6 pt-6 border-t border-slate-800/60">
          <p className="text-xs text-slate-400">
            Remember your credentials?{" "}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
