import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm, useWatch } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { Sparkles, Mail, Lock, User, AlertCircle, ArrowRight, Eye, EyeOff, Check, X } from "lucide-react";

const Register = () => {
  const { register, handleSubmit, control, formState: { errors } } = useForm({
    defaultValues: {
      name: "",
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

  const onSubmit = async (data) => {
    setError("");
    setLoading(true);

    try {
      const success = await registerUser(data.name, data.email, data.password);
      if (success) {
        navigate("/dashboard");
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
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-900/10 rounded-full blur-3xl pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl pulse-glow" />

      <div className="w-full max-w-md glass-card rounded-2xl p-8 shadow-2xl relative z-10 border border-slate-800/80">
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
          {/* Name */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Full Name</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <User className="w-4 h-4" />
              </span>
              <input
                type="text"
                placeholder="John Doe"
                className={`w-full pl-10 pr-4 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.name ? "border-rose-500/50" : "border-slate-800"
                }`}
                {...register("name", { required: "Name is required." })}
              />
            </div>
            {errors.name && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.name.message}</p>
            )}
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
                className={`w-full pl-10 pr-4 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.email ? "border-rose-500/50" : "border-slate-800"
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
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.password ? "border-rose-500/50" : "border-slate-800"
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
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.confirmPassword ? "border-rose-500/50" : "border-slate-800"
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
            className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50 mt-2"
          >
            {loading ? "Registering..." : "Create Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

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
