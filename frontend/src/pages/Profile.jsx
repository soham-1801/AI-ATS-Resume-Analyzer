import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { User, Mail, Calendar, Key, Shield, LogOut, Lock, Eye, EyeOff, Check, X, AlertCircle, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useForm, useWatch } from "react-hook-form";
import authService from "../services/authService";

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { register, handleSubmit, control, reset, formState: { errors } } = useForm({
    defaultValues: {
      oldPassword: "",
      newPassword: "",
      confirmPassword: ""
    }
  });

  const newPassword = useWatch({
    control,
    name: "newPassword",
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

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const onSubmit = async (data) => {
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await authService.changePassword(data.oldPassword, data.newPassword);
      setSuccess("Password changed successfully!");
      reset({ oldPassword: "", newPassword: "", confirmPassword: "" });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to change password. Make sure your old password is correct.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Profile Card */}
      <div className="glass-card rounded-2xl p-8 border border-slate-800/60 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-indigo-900/10 rounded-full blur-2xl" />

        <div className="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b border-slate-800/60">
          <div className="w-20 h-20 rounded-2xl bg-indigo-600/10 border border-indigo-500/25 flex items-center justify-center">
            <User className="w-10 h-10 text-indigo-400" />
          </div>
          <div className="text-center sm:text-left space-y-1">
            <h3 className="text-xl font-bold text-slate-100">{user?.name}</h3>
            <p className="text-sm text-slate-400 flex items-center justify-center sm:justify-start gap-2">
              <Mail className="w-4 h-4 text-slate-500" />
              {user?.email}
            </p>
          </div>
        </div>

        {/* Details List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6">
          <div className="space-y-1.5">
            <span className="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              Account Created
            </span>
            <p className="text-sm text-slate-300 font-medium">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' }) : "N/A"}
            </p>
          </div>

          <div className="space-y-1.5">
            <span className="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5" />
              Account Level
            </span>
            <p className="text-sm text-slate-300 font-medium">
              Candidate Workspace (Standard)
            </p>
          </div>
        </div>
      </div>

      {/* Security API settings Panel */}
      <div className="glass-card rounded-2xl p-8 border border-slate-800/60 space-y-4">
        <div className="flex items-center gap-2 text-indigo-400">
          <Key className="w-5 h-5" />
          <h4 className="text-sm font-semibold text-slate-200">API Configurations</h4>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Your resume suggestions are dynamically calculated using Google Gemini AI models. 
          The backend API automatically resolves keys from configuration environments, meaning no local setups are required.
        </p>
        <div className="flex items-center gap-3 p-3 bg-slate-950/40 border border-slate-900 rounded-lg text-xs text-slate-500">
          <Shield className="w-4 h-4 text-indigo-400 flex-shrink-0" />
          <span>Configuration loaded directly from server system.</span>
        </div>
      </div>

      {/* Change Password Card */}
      <div className="glass-card rounded-2xl p-8 border border-slate-800/60 space-y-6">
        <div className="flex items-center gap-2 text-indigo-400 pb-2 border-b border-slate-800/60">
          <Lock className="w-5 h-5" />
          <h4 className="text-sm font-semibold text-slate-200">Change Password</h4>
        </div>

        {error && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3 text-emerald-400 text-sm">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Old Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Old Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showOldPassword ? "text" : "password"}
                placeholder="••••••••"
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.oldPassword ? "border-rose-500/50" : "border-slate-800"
                }`}
                {...register("oldPassword", { required: "Old password is required." })}
              />
              <button
                type="button"
                onClick={() => setShowOldPassword(!showOldPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-400 focus:outline-none"
              >
                {showOldPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.oldPassword && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.oldPassword.message}</p>
            )}
          </div>

          {/* New Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">New Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showNewPassword ? "text" : "password"}
                placeholder="••••••••"
                className={`w-full pl-10 pr-10 py-2 rounded-lg bg-slate-950/60 border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all ${
                  errors.newPassword ? "border-rose-500/50" : "border-slate-800"
                }`}
                {...register("newPassword", {
                  required: "New password is required.",
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
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-400 focus:outline-none"
              >
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.newPassword && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.newPassword.message}</p>
            )}

            {/* Real-time Indicator and Strength Meter */}
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
            <label className="text-xs font-semibold text-slate-300">Confirm New Password</label>
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
                  required: "Please confirm your new password.",
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
            {errors.confirmPassword && (
              <p className="text-rose-400 text-[10px] font-semibold">{errors.confirmPassword.message}</p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 mt-2"
          >
            {loading ? "Updating Password..." : "Update Password"}
          </button>
        </form>
      </div>

      {/* Logout Action Card */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800/60 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-200">Close Workspace</p>
          <p className="text-xs text-slate-500">Log out of your candidate account safely</p>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 rounded-lg bg-rose-600/10 hover:bg-rose-600/20 border border-rose-500/20 text-rose-400 text-xs font-bold transition-all flex items-center gap-2"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default Profile;
